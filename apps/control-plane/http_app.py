"""FastAPI control-plane entrypoint for runtime service APIs."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

try:
    from fastapi import FastAPI
except ModuleNotFoundError:  # pragma: no cover - exercised when service extras are missing
    FastAPI = None  # type: ignore[assignment]

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


def create_app(
    *,
    repo_root: str | Path,
    task_root: str | Path | None = None,
    metadata_store=None,
    adapter_event_sink=None,
) -> "FastAPI":
    if FastAPI is None:
        raise RuntimeError("FastAPI is required. Install optional dependency group: service")
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
            return facade.operator_inspect_adapter_events(
                task_id=body["task_id"],
                execution_id=body.get("execution_id"),
                continuation_id=body.get("continuation_id"),
            )
        if action == "inspect_evidence":
            return facade.operator_inspect_evidence(task_id=body["task_id"], run_id=body.get("run_id"))
        if action == "inspect_handoff":
            return facade.operator_inspect_handoff(
                task_id=body["task_id"],
                run_id=body.get("run_id"),
                handoff_ref=body.get("handoff_ref"),
            )
        msg = f"unsupported operator action: {action}"
        raise ValueError(msg)

    return app
