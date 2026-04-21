"""Service-shaped facade over session and operator runtime surfaces."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))

from governed_ai_coding_runtime_contracts.policy_decision import build_policy_decision
from governed_ai_coding_runtime_contracts.session_bridge import (  # noqa: E402
    build_session_bridge_command,
    handle_session_bridge_command,
    session_bridge_result_to_dict,
)


class RuntimeServiceFacade:
    def __init__(
        self,
        *,
        repo_root: str | Path,
        task_root: str | Path | None = None,
        tracer: Any | None = None,
    ) -> None:
        self._repo_root = Path(repo_root)
        self._task_root = Path(task_root) if task_root else self._repo_root / ".runtime" / "tasks"
        self._tracer = tracer

    def session_command(
        self,
        *,
        command_type: str,
        task_id: str,
        repo_binding_id: str,
        adapter_id: str = "codex-cli",
        risk_tier: str = "low",
        payload: dict | None = None,
        command_id: str | None = None,
        policy_status: str = "allow",
        attachment_root: str | Path | None = None,
        attachment_runtime_state_root: str | Path | None = None,
    ) -> dict:
        command_id_value = command_id or f"api-{command_type}-{task_id}"
        command_payload = dict(payload or {})
        policy_decision = None
        if command_type in {"run_quick_gate", "run_full_gate", "write_execute"}:
            policy_decision = build_policy_decision(
                task_id=task_id,
                action_id=f"api:{command_type}",
                risk_tier=risk_tier,
                subject=f"api_command:{command_type}",
                status=policy_status,
                decision_basis=[f"service facade policy status is {policy_status}"],
                evidence_ref=f"artifacts/{task_id}/policy/service-{command_type}-{policy_status}.json",
            )

        context = {"command_type": command_type, "task_id": task_id}
        if self._tracer is None:
            return self._execute_session_command(
                command_type=command_type,
                task_id=task_id,
                repo_binding_id=repo_binding_id,
                adapter_id=adapter_id,
                risk_tier=risk_tier,
                payload=command_payload,
                command_id=command_id_value,
                policy_decision=policy_decision,
                attachment_root=attachment_root,
                attachment_runtime_state_root=attachment_runtime_state_root,
            )
        with self._tracer.start_span("service.session_command", attributes=context):
            return self._execute_session_command(
                command_type=command_type,
                task_id=task_id,
                repo_binding_id=repo_binding_id,
                adapter_id=adapter_id,
                risk_tier=risk_tier,
                payload=command_payload,
                command_id=command_id_value,
                policy_decision=policy_decision,
                attachment_root=attachment_root,
                attachment_runtime_state_root=attachment_runtime_state_root,
            )

    def operator_status(
        self,
        *,
        attachment_root: str | Path | None = None,
        attachment_runtime_state_root: str | Path | None = None,
    ) -> dict:
        return self.session_command(
            command_type="inspect_status",
            task_id="operator-status",
            repo_binding_id="operator-status",
            adapter_id="codex-cli",
            risk_tier="low",
            payload={},
            command_id="api-operator-status",
            attachment_root=attachment_root,
            attachment_runtime_state_root=attachment_runtime_state_root,
        )

    def operator_inspect_evidence(
        self,
        *,
        task_id: str,
        run_id: str | None = None,
    ) -> dict:
        payload = {"run_id": run_id} if run_id else {}
        return self.session_command(
            command_type="inspect_evidence",
            task_id=task_id,
            repo_binding_id=f"binding-{task_id}",
            adapter_id="codex-cli",
            risk_tier="low",
            payload=payload,
            command_id=f"api-operator-evidence-{task_id}",
        )

    def operator_inspect_handoff(
        self,
        *,
        task_id: str,
        run_id: str | None = None,
        handoff_ref: str | None = None,
    ) -> dict:
        payload: dict[str, str] = {}
        if run_id:
            payload["run_id"] = run_id
        if handoff_ref:
            payload["handoff_ref"] = handoff_ref
        return self.session_command(
            command_type="inspect_handoff",
            task_id=task_id,
            repo_binding_id=f"binding-{task_id}",
            adapter_id="codex-cli",
            risk_tier="low",
            payload=payload,
            command_id=f"api-operator-handoff-{task_id}",
        )

    def operator_write_status(
        self,
        *,
        task_id: str,
        approval_id: str | None = None,
        target_path: str | None = None,
        execution_id: str | None = None,
        attachment_runtime_state_root: str | Path | None = None,
    ) -> dict:
        payload: dict[str, str] = {}
        if approval_id:
            payload["approval_id"] = approval_id
        if target_path:
            payload["target_path"] = target_path
        if execution_id:
            payload["execution_id"] = execution_id
        return self.session_command(
            command_type="write_status",
            task_id=task_id,
            repo_binding_id=f"binding-{task_id}",
            adapter_id="codex-cli",
            risk_tier="low",
            payload=payload,
            command_id=f"api-operator-write-status-{task_id}",
            attachment_runtime_state_root=attachment_runtime_state_root,
        )

    def _execute_session_command(
        self,
        *,
        command_type: str,
        task_id: str,
        repo_binding_id: str,
        adapter_id: str,
        risk_tier: str,
        payload: dict,
        command_id: str,
        policy_decision: object | None,
        attachment_root: str | Path | None,
        attachment_runtime_state_root: str | Path | None,
    ) -> dict:
        command = build_session_bridge_command(
            command_id=command_id,
            command_type=command_type,
            task_id=task_id,
            repo_binding_id=repo_binding_id,
            adapter_id=adapter_id,
            risk_tier=risk_tier,
            payload=payload,
            policy_decision=policy_decision,
        )
        result = handle_session_bridge_command(
            command,
            task_root=self._task_root,
            repo_root=self._repo_root,
            attachment_root=attachment_root,
            attachment_runtime_state_root=attachment_runtime_state_root,
        )
        payload_dict = session_bridge_result_to_dict(result)
        payload_dict["service_boundary"] = "control-plane"
        return payload_dict

    def health(self) -> dict:
        return {
            "service": "control-plane",
            "repo_root": self._repo_root.as_posix(),
            "task_root": self._task_root.as_posix(),
            "status": "ok",
        }
