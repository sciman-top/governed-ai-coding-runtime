# HTTP Control Plane, Postgres Metadata, and Adapter Event Ingestion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land a minimal but real service slice for the governed runtime: optional dependency management, a FastAPI control plane, a Postgres-backed metadata path for `verification_runs` and `adapter_events`, durable adapter-event ingestion, and synchronized engineering-state documentation.

**Architecture:** Keep the governance kernel and current CLI/facade path intact, then add a second service path alongside it. The HTTP app must call the existing `RuntimeServiceFacade`, the facade must gain injectable metadata and adapter-event dependencies, and the session/adapter path must emit normalized durable events without changing canonical governance semantics.

**Tech Stack:** Python 3.x, `unittest`, optional `fastapi`, optional `uvicorn`, optional `psycopg`, existing `packages/contracts`, existing `packages/agent-runtime`, PowerShell verification gates, Markdown docs.

---

## File Structure

### New Files
- `pyproject.toml`
  - repository dependency manifest with optional extras for service/runtime features
- `apps/control-plane/http_app.py`
  - FastAPI app factory and HTTP route wiring
- `packages/agent-runtime/adapter_event_sink.py`
  - durable write/read adapter-event sink over the metadata store
- `tests/service/test_persistence_postgres.py`
  - unit tests for `PostgresMetadataStore`
- `tests/service/test_adapter_event_sink.py`
  - unit tests for event sink write/read behavior
- `tests/service/test_http_control_plane.py`
  - FastAPI endpoint tests for `/health`, `/session`, `/operator`
- `docs/change-evidence/20260420-http-control-plane-postgres-adapter-ingestion.md`
  - evidence log for this slice

### Modified Files
- `apps/control-plane/main.py`
  - dual-mode entrypoint: compatibility one-shot mode plus HTTP serve mode
- `apps/control-plane/app.py`
  - dispatch helper reused by both one-shot and HTTP paths
- `apps/control-plane/routes/session.py`
  - payload normalization for session route
- `apps/control-plane/routes/operator.py`
  - add `inspect_adapter_events` action
- `packages/agent-runtime/persistence.py`
  - metadata store protocol and Postgres implementation
- `packages/agent-runtime/service_facade.py`
  - dependency injection for metadata store and adapter-event sink
- `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
  - optional adapter-event sink hook during governed execution
- `packages/contracts/src/governed_ai_coding_runtime_contracts/codex_adapter.py`
  - durable-event payload normalization support
- `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_queries.py`
  - operator read model for adapter events
- `tests/service/test_session_api.py`
  - facade parity with metadata backend visibility
- `tests/service/test_operator_api.py`
  - operator route coverage for adapter events
- `tests/runtime/test_codex_adapter.py`
  - normalized adapter-event payload expectations
- `docs/architecture/hybrid-final-state-master-outline.md`
- `docs/architecture/local-baseline-to-hybrid-final-state-migration-matrix.md`
- `docs/product/codex-cli-app-integration-guide.md`
- `docs/product/codex-cli-app-integration-guide.zh-CN.md`
- `docs/product/codex-direct-adapter.md`
- `docs/product/codex-direct-adapter.zh-CN.md`

## Task 1: Add Dependency Manifest And Postgres Metadata Store

**Files:**
- Create: `pyproject.toml`
- Modify: `packages/agent-runtime/persistence.py`
- Create: `tests/service/test_persistence_postgres.py`

- [ ] **Step 1: Write the failing Postgres metadata-store tests**

```python
import importlib.util
import sys
import tempfile
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load_module(relative_path: str, module_name: str):
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class _FakeCursor:
    def __init__(self, rows):
        self._rows = rows
        self.executed = []

    def execute(self, query, params=None):
        self.executed.append((" ".join(query.split()), params))
        return self

    def fetchone(self):
        return self._rows[0] if self._rows else None

    def fetchall(self):
        return list(self._rows)


class _FakeConnection:
    def __init__(self, rows):
        self.cursor_obj = _FakeCursor(rows)
        self.committed = False
        self.closed = False

    def execute(self, query, params=None):
        return self.cursor_obj.execute(query, params)

    def commit(self):
        self.committed = True

    def close(self):
        self.closed = True


class PostgresMetadataStoreTests(unittest.TestCase):
    def test_postgres_store_upsert_and_get_round_trip(self) -> None:
        module = _load_module("packages/agent-runtime/persistence.py", "service_persistence_pg")
        fake_connection = _FakeConnection(
            [("verification_runs", "task-1:run-1", '{"status": "pass"}', "2026-04-20T00:00:00+00:00")]
        )
        module.psycopg = types.SimpleNamespace(connect=lambda dsn: fake_connection)

        store = module.PostgresMetadataStore("postgresql://runtime:test@localhost/runtime")
        record = store.upsert(
            namespace="verification_runs",
            key="task-1:run-1",
            payload={"status": "pass"},
        )
        loaded = store.get(namespace="verification_runs", key="task-1:run-1")

        self.assertEqual(record.namespace, "verification_runs")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.payload["status"], "pass")
        self.assertTrue(fake_connection.committed)
        self.assertTrue(fake_connection.closed)

    def test_postgres_store_lists_namespace_in_key_order(self) -> None:
        module = _load_module("packages/agent-runtime/persistence.py", "service_persistence_pg_list")
        fake_connection = _FakeConnection(
            [
                ("adapter_events", "a", '{"task_id": "task-a"}', "2026-04-20T00:00:00+00:00"),
                ("adapter_events", "b", '{"task_id": "task-b"}', "2026-04-20T00:01:00+00:00"),
            ]
        )
        module.psycopg = types.SimpleNamespace(connect=lambda dsn: fake_connection)

        store = module.PostgresMetadataStore("postgresql://runtime:test@localhost/runtime")
        rows = store.list_namespace(namespace="adapter_events")

        self.assertEqual([item.key for item in rows], ["a", "b"])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```powershell
python -m unittest tests.service.test_persistence_postgres -v
```

Expected:
- `ERROR` or `FAIL` because `PostgresMetadataStore` does not exist yet.

- [ ] **Step 3: Add the minimal dependency manifest and Postgres store implementation**

`pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "governed-ai-coding-runtime"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = []

[project.optional-dependencies]
service = [
  "fastapi>=0.115,<1",
  "uvicorn>=0.30,<1",
  "psycopg[binary]>=3.2,<4",
]
```

`packages/agent-runtime/persistence.py`

```python
try:
    import psycopg  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    psycopg = None


class PostgresMetadataStore:
    def __init__(self, dsn: str) -> None:
        self._dsn = _required_string(dsn, "dsn")
        if psycopg is None:
            raise RuntimeError("psycopg is required for PostgresMetadataStore")

    def upsert(self, *, namespace: str, key: str, payload: dict) -> MetadataRecord:
        namespace_value = _required_string(namespace, "namespace")
        key_value = _required_string(key, "key")
        updated_at = datetime.now(UTC).isoformat()
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO runtime_metadata(namespace, key, payload, updated_at)
                VALUES (%s, %s, %s::jsonb, %s::timestamptz)
                ON CONFLICT(namespace, key) DO UPDATE SET
                    payload = EXCLUDED.payload,
                    updated_at = EXCLUDED.updated_at
                """,
                (namespace_value, key_value, json.dumps(payload, sort_keys=True), updated_at),
            )
        return MetadataRecord(namespace=namespace_value, key=key_value, payload=dict(payload), updated_at=updated_at)

    def get(self, *, namespace: str, key: str) -> MetadataRecord | None:
        with self._connection() as conn:
            row = conn.execute(
                "SELECT namespace, key, payload::text, updated_at::text FROM runtime_metadata WHERE namespace = %s AND key = %s",
                (_required_string(namespace, "namespace"), _required_string(key, "key")),
            ).fetchone()
        if row is None:
            return None
        return MetadataRecord(namespace=row[0], key=row[1], payload=json.loads(row[2]), updated_at=row[3])

    def list_namespace(self, *, namespace: str) -> list[MetadataRecord]:
        with self._connection() as conn:
            rows = conn.execute(
                "SELECT namespace, key, payload::text, updated_at::text FROM runtime_metadata WHERE namespace = %s ORDER BY key",
                (_required_string(namespace, "namespace"),),
            ).fetchall()
        return [MetadataRecord(namespace=row[0], key=row[1], payload=json.loads(row[2]), updated_at=row[3]) for row in rows]

    @contextmanager
    def _connection(self):
        conn = psycopg.connect(self._dsn)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()
```

- [ ] **Step 4: Run the test to verify it passes**

Run:

```powershell
python -m unittest tests.service.test_persistence_postgres -v
```

Expected:
- `Ran 2 tests`
- `OK`

- [ ] **Step 5: Commit**

```powershell
git add pyproject.toml packages/agent-runtime/persistence.py tests/service/test_persistence_postgres.py
git commit -m "feat: add optional service manifest and postgres metadata store"
```

## Task 2: Add Durable Adapter Event Sink

**Files:**
- Create: `packages/agent-runtime/adapter_event_sink.py`
- Create: `tests/service/test_adapter_event_sink.py`

- [ ] **Step 1: Write the failing adapter-event sink tests**

```python
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load_module(relative_path: str, module_name: str):
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class _MemoryMetadataStore:
    def __init__(self):
        self.rows = {}

    def upsert(self, *, namespace: str, key: str, payload: dict):
        self.rows[(namespace, key)] = payload
        return type("MetadataRecord", (), {"namespace": namespace, "key": key, "payload": payload, "updated_at": "now"})()

    def get(self, *, namespace: str, key: str):
        payload = self.rows.get((namespace, key))
        if payload is None:
            return None
        return type("MetadataRecord", (), {"namespace": namespace, "key": key, "payload": payload, "updated_at": "now"})()

    def list_namespace(self, *, namespace: str):
        result = []
        for (item_namespace, key), payload in sorted(self.rows.items()):
            if item_namespace == namespace:
                result.append(type("MetadataRecord", (), {"namespace": namespace, "key": key, "payload": payload, "updated_at": "now"})())
        return result


class AdapterEventSinkTests(unittest.TestCase):
    def test_sink_persists_normalized_event(self) -> None:
        module = _load_module("packages/agent-runtime/adapter_event_sink.py", "adapter_event_sink")
        store = _MemoryMetadataStore()
        sink = module.AdapterEventSink(metadata_store=store)

        record = sink.write_event(
            task_id="task-1",
            event_type="adapter_tool_call",
            payload={"tool": "apply_patch"},
            adapter_id="codex-cli",
            adapter_tier="process_bridge",
            flow_kind="process_bridge",
            execution_id="task-1:run-1",
            continuation_id="task-1:run-1",
            event_source="live_adapter",
        )

        self.assertEqual(record["task_id"], "task-1")
        self.assertEqual(record["adapter_id"], "codex-cli")
        self.assertEqual(record["event_type"], "adapter_tool_call")

    def test_sink_lists_events_for_task(self) -> None:
        module = _load_module("packages/agent-runtime/adapter_event_sink.py", "adapter_event_sink_list")
        store = _MemoryMetadataStore()
        sink = module.AdapterEventSink(metadata_store=store)
        sink.write_event(
            task_id="task-1",
            event_type="adapter_file_change",
            payload={"path": "src/app.py"},
            adapter_id="codex-cli",
            adapter_tier="native_attach",
            flow_kind="live_attach",
            execution_id="task-1:run-1",
            continuation_id="task-1:run-1",
            event_source="live_adapter",
        )

        rows = sink.list_events(task_id="task-1")

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["payload"]["path"], "src/app.py")
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```powershell
python -m unittest tests.service.test_adapter_event_sink -v
```

Expected:
- `ERROR` because `AdapterEventSink` does not exist yet.

- [ ] **Step 3: Implement the minimal sink**

`packages/agent-runtime/adapter_event_sink.py`

```python
from __future__ import annotations

from datetime import UTC, datetime
import json


class AdapterEventSink:
    def __init__(self, *, metadata_store) -> None:
        self._metadata_store = metadata_store

    def write_event(
        self,
        *,
        task_id: str,
        event_type: str,
        payload: dict,
        adapter_id: str,
        adapter_tier: str,
        flow_kind: str,
        execution_id: str,
        continuation_id: str,
        event_source: str,
    ) -> dict:
        created_at = datetime.now(UTC).isoformat()
        key = f"{task_id}:{execution_id}:{event_type}:{created_at}"
        record = {
            "task_id": task_id,
            "event_type": event_type,
            "payload": dict(payload),
            "adapter_id": adapter_id,
            "adapter_tier": adapter_tier,
            "flow_kind": flow_kind,
            "execution_id": execution_id,
            "continuation_id": continuation_id,
            "event_source": event_source,
            "created_at": created_at,
        }
        self._metadata_store.upsert(namespace="adapter_events", key=key, payload=record)
        return record

    def list_events(self, *, task_id: str) -> list[dict]:
        rows = self._metadata_store.list_namespace(namespace="adapter_events")
        return [row.payload for row in rows if row.payload.get("task_id") == task_id]
```

- [ ] **Step 4: Run the test to verify it passes**

Run:

```powershell
python -m unittest tests.service.test_adapter_event_sink -v
```

Expected:
- `Ran 2 tests`
- `OK`

- [ ] **Step 5: Commit**

```powershell
git add packages/agent-runtime/adapter_event_sink.py tests/service/test_adapter_event_sink.py
git commit -m "feat: add durable adapter event sink"
```

## Task 3: Extend Service Facade And Operator Surface For Metadata And Adapter Events

**Files:**
- Modify: `packages/agent-runtime/service_facade.py`
- Modify: `apps/control-plane/routes/operator.py`
- Modify: `tests/service/test_session_api.py`
- Modify: `tests/service/test_operator_api.py`

- [ ] **Step 1: Write the failing facade/operator tests**

Add to `tests/service/test_session_api.py`:

```python
    def test_health_reports_active_metadata_backend(self) -> None:
        service_facade_module = _load_module("packages/agent-runtime/service_facade.py", "service_facade_health")

        class _Store:
            pass

        facade = service_facade_module.RuntimeServiceFacade(
            repo_root=ROOT,
            task_root=ROOT / ".runtime" / "tasks",
            metadata_store=_Store(),
        )

        health = facade.health()

        self.assertEqual(health["metadata_backend"], "_Store")
```

Add to `tests/service/test_operator_api.py`:

```python
    def test_operator_route_exposes_adapter_event_reads(self) -> None:
        service_facade_module = _load_module("packages/agent-runtime/service_facade.py", "service_facade_operator_events")
        app_module = _load_module("apps/control-plane/app.py", "control_plane_app_events")

        class _Sink:
            def list_events(self, *, task_id: str):
                return [
                    {
                        "task_id": task_id,
                        "event_type": "adapter_tool_call",
                        "payload": {"tool": "apply_patch"},
                    }
                ]

        facade = service_facade_module.RuntimeServiceFacade(
            repo_root=ROOT,
            task_root=ROOT / ".runtime" / "tasks",
            adapter_event_sink=_Sink(),
        )
        app = app_module.ControlPlaneApplication(facade=facade)

        result = app.dispatch(
            route="/operator",
            payload={"action": "inspect_adapter_events", "task_id": "task-operator-api"},
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["payload"]["adapter_events"][0]["event_type"], "adapter_tool_call")
```

- [ ] **Step 2: Run the tests to verify they fail**

Run:

```powershell
python -m unittest tests.service.test_session_api tests.service.test_operator_api -v
```

Expected:
- failures because `metadata_store`, `adapter_event_sink`, and `inspect_adapter_events` are not supported yet.

- [ ] **Step 3: Implement the minimal facade and operator changes**

`packages/agent-runtime/service_facade.py`

```python
class RuntimeServiceFacade:
    def __init__(
        self,
        *,
        repo_root: str | Path,
        task_root: str | Path | None = None,
        tracer: Any | None = None,
        metadata_store: Any | None = None,
        adapter_event_sink: Any | None = None,
    ) -> None:
        self._repo_root = Path(repo_root)
        self._task_root = Path(task_root) if task_root else self._repo_root / ".runtime" / "tasks"
        self._tracer = tracer
        self._metadata_store = metadata_store
        self._adapter_event_sink = adapter_event_sink

    def operator_inspect_adapter_events(self, *, task_id: str) -> dict:
        events = []
        if self._adapter_event_sink is not None:
            events = self._adapter_event_sink.list_events(task_id=task_id)
        return {
            "command_id": f"api-operator-adapter-events-{task_id}",
            "command_type": "inspect_adapter_events",
            "status": "ok",
            "payload": {"task_id": task_id, "adapter_events": events},
            "service_boundary": "control-plane",
        }

    def health(self) -> dict:
        backend_name = type(self._metadata_store).__name__ if self._metadata_store is not None else "none"
        return {
            "service": "control-plane",
            "repo_root": self._repo_root.as_posix(),
            "task_root": self._task_root.as_posix(),
            "status": "ok",
            "metadata_backend": backend_name,
        }
```

`apps/control-plane/routes/operator.py`

```python
    if action == "inspect_adapter_events":
        return facade.operator_inspect_adapter_events(
            task_id=_required_string(payload.get("task_id"), "task_id"),
        )
```

- [ ] **Step 4: Run the tests to verify they pass**

Run:

```powershell
python -m unittest tests.service.test_session_api tests.service.test_operator_api -v
```

Expected:
- updated service tests pass
- `OK`

- [ ] **Step 5: Commit**

```powershell
git add packages/agent-runtime/service_facade.py apps/control-plane/routes/operator.py tests/service/test_session_api.py tests/service/test_operator_api.py
git commit -m "feat: expose metadata backend and adapter event reads from service facade"
```

## Task 4: Add Real FastAPI Control Plane

**Files:**
- Create: `apps/control-plane/http_app.py`
- Modify: `apps/control-plane/main.py`
- Create: `tests/service/test_http_control_plane.py`

- [ ] **Step 1: Write the failing HTTP tests**

```python
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

try:
    from fastapi.testclient import TestClient
except ModuleNotFoundError:
    TestClient = None


def _load_module(relative_path: str, module_name: str):
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


@unittest.skipIf(TestClient is None, "service extras not installed")
class HttpControlPlaneTests(unittest.TestCase):
    def test_health_endpoint_returns_status(self) -> None:
        module = _load_module("apps/control-plane/http_app.py", "http_control_plane")
        client = TestClient(module.create_app(repo_root=ROOT))

        response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_operator_endpoint_returns_adapter_events(self) -> None:
        module = _load_module("apps/control-plane/http_app.py", "http_control_plane_operator")
        client = TestClient(module.create_app(repo_root=ROOT))

        response = client.post("/operator", json={"action": "inspect_adapter_events", "task_id": "task-http"})

        self.assertEqual(response.status_code, 200)
        self.assertIn("payload", response.json())
```

- [ ] **Step 2: Run the tests to verify they fail**

Run:

```powershell
python -m unittest tests.service.test_http_control_plane -v
```

Expected:
- failure because `http_app.py` and `create_app(...)` do not exist yet.

- [ ] **Step 3: Implement the minimal FastAPI app and dual-mode entrypoint**

`apps/control-plane/http_app.py`

```python
from __future__ import annotations

import importlib.util
from fastapi import FastAPI
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]


def _load_runtime_service_facade():
    path = ROOT / "packages" / "agent-runtime" / "service_facade.py"
    spec = importlib.util.spec_from_file_location("agent_runtime_service_facade_http", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["agent_runtime_service_facade_http"] = module
    spec.loader.exec_module(module)
    return module.RuntimeServiceFacade


RuntimeServiceFacade = _load_runtime_service_facade()


def create_app(*, repo_root: str | Path, task_root: str | Path | None = None, metadata_store=None, adapter_event_sink=None) -> FastAPI:
    facade = RuntimeServiceFacade(
        repo_root=repo_root,
        task_root=task_root,
        metadata_store=metadata_store,
        adapter_event_sink=adapter_event_sink,
    )
    app = FastAPI(title="Governed AI Coding Runtime Control Plane")

    @app.get("/health")
    def health():
        return facade.health()

    @app.post("/session")
    def session(body: dict):
        return facade.session_command(
            command_type=body["command_type"],
            task_id=body["task_id"],
            repo_binding_id=body["repo_binding_id"],
            adapter_id=body.get("adapter_id", "codex-cli"),
            risk_tier=body.get("risk_tier", "low"),
            payload=body.get("payload", {}),
            command_id=body.get("command_id"),
            policy_status=body.get("policy_status", "allow"),
            attachment_root=body.get("attachment_root"),
            attachment_runtime_state_root=body.get("attachment_runtime_state_root"),
        )

    @app.post("/operator")
    def operator(body: dict):
        action = body.get("action", "status")
        if action == "status":
            return facade.operator_status(
                attachment_root=body.get("attachment_root"),
                attachment_runtime_state_root=body.get("attachment_runtime_state_root"),
            )
        if action == "inspect_adapter_events":
            return facade.operator_inspect_adapter_events(task_id=body["task_id"])
        if action == "inspect_evidence":
            return facade.operator_inspect_evidence(task_id=body["task_id"], run_id=body.get("run_id"))
        return facade.operator_inspect_handoff(task_id=body["task_id"], run_id=body.get("run_id"), handoff_ref=body.get("handoff_ref"))

    return app
```

`apps/control-plane/main.py`

```python
    parser = argparse.ArgumentParser(description="Control-plane entrypoint.")
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
```

```python
    if args.serve:
        import uvicorn
        http_module = _load_module(repo_root / "apps" / "control-plane" / "http_app.py", "control_plane_http_app")
        app = http_module.create_app(repo_root=repo_root, task_root=args.task_root)
        uvicorn.run(app, host=args.host, port=args.port)
        return 0
```

- [ ] **Step 4: Run the tests to verify they pass**

Run:

```powershell
python -m unittest tests.service.test_http_control_plane -v
```

Expected:
- if `fastapi` extras are installed: `Ran 2 tests`, `OK`
- if extras are absent: tests are skipped with a clear reason

- [ ] **Step 5: Commit**

```powershell
git add apps/control-plane/http_app.py apps/control-plane/main.py tests/service/test_http_control_plane.py
git commit -m "feat: add fastapi control plane entrypoint"
```

## Task 5: Wire Session Bridge And Codex Adapter To Durable Adapter Events

**Files:**
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/codex_adapter.py`
- Modify: `tests/runtime/test_codex_adapter.py`

- [ ] **Step 1: Write the failing durable-event expectation test**

Add to `tests/runtime/test_codex_adapter.py`:

```python
    def test_codex_session_evidence_can_be_normalized_for_durable_sink(self) -> None:
        module = self._module()

        session = module.CodexSessionEvidence(
            task_id="task-durable",
            adapter_id="codex-cli",
            adapter_tier="process_bridge",
            flow_kind="process_bridge",
            file_changes=["src/service.py"],
            tool_calls=[{"tool": "apply_patch"}],
            gate_runs=["artifacts/task-durable/run-1/verification-output/test.txt"],
            approvals=["approval-1"],
            handoff_refs=["artifacts/task-durable/run-1/handoff/package.json"],
            unsupported_capabilities=[],
            execution_id="task-durable:run-1",
            continuation_id="task-durable:run-1",
            event_source="live_adapter",
        )

        payloads = module.codex_session_events_to_records(session)

        self.assertGreaterEqual(len(payloads), 5)
        self.assertTrue(all(item["task_id"] == "task-durable" for item in payloads))
        self.assertTrue(all(item["execution_id"] == "task-durable:run-1" for item in payloads))
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```powershell
python -m unittest tests.runtime.test_codex_adapter -v
```

Expected:
- failure because `codex_session_events_to_records(...)` does not exist yet.

- [ ] **Step 3: Implement normalized durable records and optional session-bridge sink hook**

Add to `packages/contracts/src/governed_ai_coding_runtime_contracts/codex_adapter.py`:

```python
def codex_session_events_to_records(session: CodexSessionEvidence) -> list[dict]:
    records: list[dict] = []

    def _record(event_type: str, payload: dict) -> None:
        records.append(
            {
                "task_id": session.task_id,
                "adapter_id": session.adapter_id,
                "adapter_tier": session.adapter_tier,
                "flow_kind": session.flow_kind,
                "event_type": event_type,
                "payload": dict(payload),
                "execution_id": session.execution_id,
                "continuation_id": session.continuation_id,
                "event_source": session.event_source,
            }
        )

    _record("codex_adapter_posture", {"unsupported_capabilities": session.unsupported_capabilities})
    for path in session.file_changes:
        _record("adapter_file_change", {"path": path})
    for tool_call in session.tool_calls:
        _record("adapter_tool_call", tool_call)
    for gate_run in session.gate_runs:
        _record("adapter_gate_run", {"artifact_ref": gate_run})
    for approval in session.approvals:
        _record("adapter_approval_event", {"approval_id": approval})
    for handoff in session.handoff_refs:
        _record("adapter_handoff", {"handoff_ref": handoff})
    return records
```

Update `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`:

```python
def _record_adapter_events(
    *,
    command: SessionBridgeCommand,
    artifact_store: LocalArtifactStore,
    task_id: str,
    run_id: str,
    execution_id: str,
    continuation_id: str,
    file_changes: list[str],
    tool_calls: list[dict],
    gate_runs: list[str],
    approvals: list[str],
    handoff_refs: list[str],
    unsupported_events: list[dict],
    adapter_event_sink=None,
) -> tuple[str | None, dict | None]:
```

```python
    session = CodexSessionEvidence(
        task_id=task_id,
        adapter_id=command.adapter_id,
        adapter_tier=str(identity.get("adapter_tier", "manual_handoff")),
        flow_kind=flow_kind,
        file_changes=file_changes,
        tool_calls=tool_calls,
        gate_runs=gate_runs,
        approvals=[approval for approval in approvals if approval],
        handoff_refs=handoff_refs,
        unsupported_capabilities=[str(item) for item in unsupported_capabilities if isinstance(item, str)],
        execution_id=execution_id,
        continuation_id=continuation_id,
        event_source=event_source,
        unsupported_events=unsupported_events,
    )
    if adapter_event_sink is not None:
        for record in codex_session_events_to_records(session):
            adapter_event_sink.write_event(**record)
```

- [ ] **Step 4: Run the test to verify it passes**

Run:

```powershell
python -m unittest tests.runtime.test_codex_adapter -v
```

Expected:
- codex adapter test suite passes
- `OK`

- [ ] **Step 5: Commit**

```powershell
git add packages/contracts/src/governed_ai_coding_runtime_contracts/codex_adapter.py packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py tests/runtime/test_codex_adapter.py
git commit -m "feat: normalize and persist codex adapter events"
```

## Task 6: Wire Postgres/HTTP Path End To End And Refresh Docs

**Files:**
- Modify: `apps/control-plane/http_app.py`
- Modify: `packages/agent-runtime/service_facade.py`
- Modify: `docs/architecture/hybrid-final-state-master-outline.md`
- Modify: `docs/architecture/local-baseline-to-hybrid-final-state-migration-matrix.md`
- Modify: `docs/product/codex-cli-app-integration-guide.md`
- Modify: `docs/product/codex-cli-app-integration-guide.zh-CN.md`
- Modify: `docs/product/codex-direct-adapter.md`
- Modify: `docs/product/codex-direct-adapter.zh-CN.md`
- Create: `docs/change-evidence/20260420-http-control-plane-postgres-adapter-ingestion.md`

- [ ] **Step 1: Write the failing end-to-end service-path test**

Add to `tests/service/test_http_control_plane.py`:

```python
    def test_operator_adapter_events_flow_through_http_with_injected_sink(self) -> None:
        module = _load_module("apps/control-plane/http_app.py", "http_control_plane_e2e")

        class _Sink:
            def __init__(self):
                self.rows = [{"task_id": "task-http", "event_type": "adapter_tool_call", "payload": {"tool": "apply_patch"}}]

            def list_events(self, *, task_id: str):
                return [row for row in self.rows if row["task_id"] == task_id]

        client = TestClient(module.create_app(repo_root=ROOT, adapter_event_sink=_Sink()))
        response = client.post("/operator", json={"action": "inspect_adapter_events", "task_id": "task-http"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["payload"]["adapter_events"][0]["payload"]["tool"], "apply_patch")
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```powershell
python -m unittest tests.service.test_http_control_plane -v
```

Expected:
- failure because `create_app(...)` does not yet accept or propagate the injected sink/backend cleanly.

- [ ] **Step 3: Implement end-to-end wiring and update docs**

Update `apps/control-plane/http_app.py`:

```python
def create_app(*, repo_root: str | Path, task_root: str | Path | None = None, metadata_store=None, adapter_event_sink=None) -> FastAPI:
    facade = RuntimeServiceFacade(
        repo_root=repo_root,
        task_root=task_root,
        metadata_store=metadata_store,
        adapter_event_sink=adapter_event_sink,
    )
```

Update `packages/agent-runtime/service_facade.py` so HTTP and direct-facade paths both pass `adapter_event_sink` through `handle_session_bridge_command(...)`.

Update docs with these concrete wording changes:

`docs/architecture/hybrid-final-state-master-outline.md`

```md
## Current Landed Runtime
- local governed runtime kernel
- local facade control surface
- SQLite/filesystem compatibility path

## Transition Runtime Target
- real FastAPI control plane
- optional Postgres metadata backend for `verification_runs` and `adapter_events`
- durable adapter event sink reused by operator reads

## North-Star Best-Practice Runtime
- broader service decomposition
- richer workflow orchestration
- broader host adapter family beyond Codex-first productization
```

`docs/product/codex-direct-adapter.md`

```md
## Engineering State
- Codex is the first-class direct adapter priority.
- Durable adapter-event persistence now exists through the transition service path.
- Claude Code remains supported by the generic adapter contract, but is not yet a first-class direct adapter.
```

`docs/change-evidence/20260420-http-control-plane-postgres-adapter-ingestion.md`

```md
# 20260420 HTTP Control Plane, Postgres Metadata, and Adapter Event Ingestion

## Goal
Land a real transition runtime slice with FastAPI, optional Postgres metadata, and durable adapter-event ingestion.

## Verification
- `python -m unittest tests.service.test_persistence_postgres tests.service.test_adapter_event_sink tests.service.test_session_api tests.service.test_operator_api tests.service.test_http_control_plane -v`
- `python -m unittest tests.runtime.test_codex_adapter -v`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
```

- [ ] **Step 4: Run the full verification set**

Run:

```powershell
python -m unittest tests.service.test_persistence_postgres tests.service.test_adapter_event_sink tests.service.test_session_api tests.service.test_operator_api tests.service.test_http_control_plane -v
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
```

Expected:
- targeted service tests pass, with HTTP tests running when service extras are installed
- existing gates remain green

- [ ] **Step 5: Commit**

```powershell
git add apps/control-plane/http_app.py packages/agent-runtime/service_facade.py docs/architecture/hybrid-final-state-master-outline.md docs/architecture/local-baseline-to-hybrid-final-state-migration-matrix.md docs/product/codex-cli-app-integration-guide.md docs/product/codex-cli-app-integration-guide.zh-CN.md docs/product/codex-direct-adapter.md docs/product/codex-direct-adapter.zh-CN.md docs/change-evidence/20260420-http-control-plane-postgres-adapter-ingestion.md tests/service/test_http_control_plane.py
git commit -m "feat: land transition service path for runtime control plane"
```

## Self-Review

### Spec Coverage
- Real FastAPI control plane: covered by Task 4 and Task 6.
- Optional Postgres metadata store: covered by Task 1 and Task 6.
- Durable adapter-event sink: covered by Task 2 and Task 5.
- Operator adapter-event reads: covered by Task 3 and Task 6.
- Honest Codex vs Claude Code compatibility docs: covered by Task 6.

### Placeholder Scan
- No `TBD`, `TODO`, or deferred unnamed steps remain.
- Every task has exact file paths, concrete commands, and code snippets.

### Type And Naming Consistency
- Metadata namespaces are consistently `verification_runs` and `adapter_events`.
- Runtime service path consistently uses `metadata_store` and `adapter_event_sink`.
- HTTP app factory is consistently named `create_app(...)`.

## Execution Handoff
Plan complete and saved to `docs/superpowers/plans/2026-04-20-http-control-plane-postgres-adapter-ingestion-plan.md`.

Two execution options:

1. Subagent-Driven (recommended) - I dispatch a fresh subagent per task, review between tasks, fast iteration

2. Inline Execution - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
