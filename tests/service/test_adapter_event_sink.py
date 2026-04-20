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


class _MemoryMetadataStore:
    def __init__(self) -> None:
        self.rows: dict[tuple[str, str], dict] = {}

    def upsert(self, *, namespace: str, key: str, payload: dict):
        self.rows[(namespace, key)] = dict(payload)
        return types.SimpleNamespace(namespace=namespace, key=key, payload=dict(payload), updated_at="now")

    def list_namespace(self, *, namespace: str):
        records = []
        for (item_namespace, key), payload in sorted(self.rows.items(), key=lambda item: item[0][1]):
            if item_namespace != namespace:
                continue
            records.append(
                types.SimpleNamespace(
                    namespace=item_namespace,
                    key=key,
                    payload=dict(payload),
                    updated_at="now",
                )
            )
        return records


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
            created_at="2026-04-21T00:00:00+00:00",
        )

        self.assertEqual(record["task_id"], "task-1")
        self.assertEqual(record["adapter_id"], "codex-cli")
        self.assertEqual(record["event_type"], "adapter_tool_call")
        self.assertEqual(record["payload"]["tool"], "apply_patch")
        self.assertTrue(record["event_id"].startswith("task-1:2026-04-21T00:00:00+00:00:"))

    def test_sink_lists_events_for_task_with_stable_order(self) -> None:
        module = _load_module("packages/agent-runtime/adapter_event_sink.py", "adapter_event_sink_list")
        store = _MemoryMetadataStore()
        sink = module.AdapterEventSink(metadata_store=store)
        sink.write_event(
            task_id="task-1",
            event_type="adapter_gate_run",
            payload={"gate": "test"},
            adapter_id="codex-cli",
            adapter_tier="native_attach",
            flow_kind="live_attach",
            execution_id="task-1:run-1",
            continuation_id="task-1:run-1",
            event_source="live_adapter",
            created_at="2026-04-21T00:00:02+00:00",
        )
        sink.write_event(
            task_id="task-2",
            event_type="adapter_tool_call",
            payload={"tool": "noop"},
            adapter_id="codex-cli",
            adapter_tier="manual_handoff",
            flow_kind="manual_handoff",
            execution_id="task-2:run-1",
            continuation_id="task-2:run-1",
            event_source="manual_handoff",
            created_at="2026-04-21T00:00:01+00:00",
        )
        sink.write_event(
            task_id="task-1",
            event_type="adapter_tool_call",
            payload={"tool": "apply_patch"},
            adapter_id="codex-cli",
            adapter_tier="native_attach",
            flow_kind="live_attach",
            execution_id="task-1:run-1",
            continuation_id="task-1:run-1",
            event_source="live_adapter",
            created_at="2026-04-21T00:00:01+00:00",
        )

        rows = sink.list_events(task_id="task-1")

        self.assertEqual(len(rows), 2)
        self.assertEqual([row["event_type"] for row in rows], ["adapter_tool_call", "adapter_gate_run"])
        self.assertTrue(all(row["task_id"] == "task-1" for row in rows))

    def test_sink_validates_required_fields(self) -> None:
        module = _load_module("packages/agent-runtime/adapter_event_sink.py", "adapter_event_sink_validate")
        store = _MemoryMetadataStore()
        sink = module.AdapterEventSink(metadata_store=store)

        with self.assertRaises(ValueError):
            sink.write_event(
                task_id="",
                event_type="adapter_tool_call",
                payload={"tool": "apply_patch"},
                adapter_id="codex-cli",
                adapter_tier="process_bridge",
                flow_kind="process_bridge",
                execution_id="task-1:run-1",
                continuation_id="task-1:run-1",
                event_source="live_adapter",
            )

        with self.assertRaises(ValueError):
            sink.write_event(
                task_id="task-1",
                event_type="adapter_tool_call",
                payload=[],  # type: ignore[arg-type]
                adapter_id="codex-cli",
                adapter_tier="process_bridge",
                flow_kind="process_bridge",
                execution_id="task-1:run-1",
                continuation_id="task-1:run-1",
                event_source="live_adapter",
            )

    def test_sink_can_use_sqlite_store_without_psycopg(self) -> None:
        persistence_module = _load_module("packages/agent-runtime/persistence.py", "service_persistence_for_event_sink")
        sink_module = _load_module("packages/agent-runtime/adapter_event_sink.py", "adapter_event_sink_with_sqlite")

        with tempfile.TemporaryDirectory() as tmp_dir:
            sqlite_store = persistence_module.SqliteMetadataStore(Path(tmp_dir) / "runtime.db")
            sink = sink_module.AdapterEventSink(metadata_store=sqlite_store)
            sink.write_event(
                task_id="task-sqlite",
                event_type="adapter_tool_call",
                payload={"tool": "apply_patch"},
                adapter_id="codex-cli",
                adapter_tier="process_bridge",
                flow_kind="process_bridge",
                execution_id="task-sqlite:run-1",
                continuation_id="task-sqlite:run-1",
                event_source="live_adapter",
                created_at="2026-04-21T00:00:00+00:00",
            )

            rows = sink.list_events(task_id="task-sqlite")
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["payload"]["tool"], "apply_patch")


if __name__ == "__main__":
    unittest.main()
