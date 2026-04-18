"""Stable session bridge command contract for interactive governed actions."""

import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from governed_ai_coding_runtime_contracts.attached_write_execution import (
    decide_attached_write_request,
    execute_attached_write_request,
)
from governed_ai_coding_runtime_contracts.attached_write_governance import govern_attached_write_request
from governed_ai_coding_runtime_contracts.policy_decision import PolicyDecision
from governed_ai_coding_runtime_contracts.repo_attachment import inspect_attachment_posture, validate_light_pack
from governed_ai_coding_runtime_contracts.repo_profile import load_repo_profile
from governed_ai_coding_runtime_contracts.runtime_status import RuntimeStatusStore
from governed_ai_coding_runtime_contracts.task_store import FileTaskStore
from governed_ai_coding_runtime_contracts.verification_runner import (
    VerificationPlan,
    build_repo_profile_verification_plan,
    build_verification_plan,
)


CommandType = Literal[
    "bind_task",
    "show_repo_posture",
    "request_approval",
    "run_quick_gate",
    "run_full_gate",
    "write_request",
    "write_approve",
    "write_execute",
    "write_status",
    "inspect_evidence",
    "inspect_handoff",
    "inspect_status",
]
ExecutionMode = Literal["read_only", "execute", "requires_approval"]
RiskTier = Literal["low", "medium", "high"]
SessionBridgeResultStatus = Literal[
    "ok",
    "bound",
    "approval_required",
    "verification_requested",
    "launch_completed",
    "manual_handoff",
    "degraded",
    "write_requested",
    "approval_recorded",
    "write_executed",
    "denied",
]

DEFAULT_SCHEMA_VERSION = "1.0"
COMMAND_TYPES = {
    "bind_task",
    "show_repo_posture",
    "request_approval",
    "run_quick_gate",
    "run_full_gate",
    "write_request",
    "write_approve",
    "write_execute",
    "write_status",
    "inspect_evidence",
    "inspect_handoff",
    "inspect_status",
}
EXECUTION_COMMAND_TYPES = {"run_quick_gate", "run_full_gate", "write_execute"}
RISK_TIERS = {"low", "medium", "high"}
EXECUTION_MODES = {"read_only", "execute", "requires_approval"}


@dataclass(frozen=True, slots=True)
class SessionBridgeCommand:
    schema_version: str
    command_id: str
    command_type: CommandType
    task_id: str
    repo_binding_id: str
    adapter_id: str
    risk_tier: RiskTier
    execution_mode: ExecutionMode
    payload: dict
    policy_decision_ref: str | None = None
    escalation_context: dict | None = None


@dataclass(frozen=True, slots=True)
class SessionBridgeResult:
    command_id: str
    command_type: CommandType
    status: SessionBridgeResultStatus
    payload: dict
    policy_decision_ref: str | None = None
    unsupported_capability_behavior: str | None = None
    reason: str | None = None


def build_session_bridge_command(
    *,
    command_id: str,
    command_type: CommandType,
    task_id: str,
    repo_binding_id: str,
    adapter_id: str,
    risk_tier: RiskTier,
    payload: dict | None = None,
    policy_decision: PolicyDecision | None = None,
    policy_decision_ref: str | None = None,
    escalation_context: dict | None = None,
    schema_version: str = DEFAULT_SCHEMA_VERSION,
) -> SessionBridgeCommand:
    normalized_command_type = _required_enum(command_type, "command_type", COMMAND_TYPES)
    normalized_risk_tier = _required_enum(risk_tier, "risk_tier", RISK_TIERS)
    normalized_payload = _payload_dict(payload, "payload")
    normalized_escalation_context = _optional_context(escalation_context, "escalation_context")
    normalized_policy_ref = _optional_string(policy_decision_ref, "policy_decision_ref")
    execution_mode: ExecutionMode = "read_only"

    if normalized_command_type in EXECUTION_COMMAND_TYPES:
        if policy_decision is None and normalized_policy_ref is None:
            msg = "execution commands require PolicyDecision or policy_decision_ref"
            raise ValueError(msg)
        if policy_decision is not None:
            _validate_policy_decision_matches_command(
                policy_decision,
                task_id=task_id,
                risk_tier=normalized_risk_tier,
            )
            normalized_policy_ref = normalized_policy_ref or policy_decision.evidence_ref
            if policy_decision.status == "deny":
                msg = "deny PolicyDecision fails closed for execution commands"
                raise ValueError(msg)
            if policy_decision.status == "escalate":
                execution_mode = "requires_approval"
                normalized_escalation_context = _escalation_context_from_policy(
                    policy_decision,
                    policy_decision_ref=normalized_policy_ref,
                    provided_context=normalized_escalation_context,
                )
            else:
                execution_mode = "execute"
        else:
            execution_mode = "execute"

    if normalized_command_type == "request_approval":
        if normalized_escalation_context is None:
            msg = "request_approval requires escalation_context"
            raise ValueError(msg)
        execution_mode = "requires_approval"

    return SessionBridgeCommand(
        schema_version=_required_string(schema_version, "schema_version"),
        command_id=_required_string(command_id, "command_id"),
        command_type=normalized_command_type,
        task_id=_required_string(task_id, "task_id"),
        repo_binding_id=_required_string(repo_binding_id, "repo_binding_id"),
        adapter_id=_required_string(adapter_id, "adapter_id"),
        risk_tier=normalized_risk_tier,
        execution_mode=execution_mode,
        payload=normalized_payload,
        policy_decision_ref=normalized_policy_ref,
        escalation_context=normalized_escalation_context,
    )


def is_execution_command(command: SessionBridgeCommand) -> bool:
    return command.execution_mode == "execute"


def requires_human_approval(command: SessionBridgeCommand) -> bool:
    return command.execution_mode == "requires_approval"


def handle_session_bridge_command(
    command: SessionBridgeCommand,
    *,
    task_root: str | Path,
    repo_root: str | Path,
    attachment_root: str | Path | None = None,
    attachment_runtime_state_root: str | Path | None = None,
) -> SessionBridgeResult:
    if command.adapter_id == "unsupported-adapter":
        return _degraded(command, reason="adapter capability is unsupported")

    if command.command_type == "bind_task":
        store = FileTaskStore(Path(task_root))
        record = store.load(command.task_id)
        return SessionBridgeResult(
            command_id=command.command_id,
            command_type=command.command_type,
            status="bound",
            payload={
                "task_id": record.task_id,
                "task_state": record.current_state,
                "repo_binding_id": command.repo_binding_id,
                "adapter_id": command.adapter_id,
            },
        )

    if command.command_type == "show_repo_posture":
        if attachment_root is None or attachment_runtime_state_root is None:
            return _degraded(command, reason="attachment_root and attachment_runtime_state_root are required")
        posture = inspect_attachment_posture(
            target_repo_root=str(attachment_root),
            runtime_state_root=str(attachment_runtime_state_root),
        )
        return SessionBridgeResult(
            command_id=command.command_id,
            command_type=command.command_type,
            status="ok",
            payload={
                "repo_id": posture.repo_id,
                "binding_id": posture.binding_id,
                "binding_state": posture.binding_state,
                "light_pack_path": posture.light_pack_path,
                "adapter_preference": posture.adapter_preference,
                "gate_profile": posture.gate_profile,
                "reason": posture.reason,
            },
        )

    if command.command_type == "inspect_status":
        attachment_roots = [Path(attachment_root)] if attachment_root else None
        snapshot = RuntimeStatusStore(
            Path(task_root),
            Path(repo_root),
            attachment_roots=attachment_roots,
            attachment_runtime_state_root=Path(attachment_runtime_state_root) if attachment_runtime_state_root else None,
        ).snapshot()
        return SessionBridgeResult(
            command_id=command.command_id,
            command_type=command.command_type,
            status="ok",
            payload={
                "total_tasks": snapshot.total_tasks,
                "maintenance_stage": snapshot.maintenance.stage,
                "attachments": [
                    {
                        "repo_id": attachment.repo_id,
                        "binding_state": attachment.binding_state,
                        "adapter_preference": attachment.adapter_preference,
                    }
                    for attachment in snapshot.attachments
                ],
            },
        )

    if command.command_type == "inspect_evidence":
        return _inspect_evidence(command, task_root=Path(task_root))

    if command.command_type == "inspect_handoff":
        return _inspect_handoff(command, task_root=Path(task_root))

    if command.command_type == "write_request":
        if attachment_root is None or attachment_runtime_state_root is None:
            return _degraded(command, reason="attachment_root and attachment_runtime_state_root are required")
        try:
            governance = govern_attached_write_request(
                attachment_root=attachment_root,
                attachment_runtime_state_root=attachment_runtime_state_root,
                task_id=command.task_id,
                tool_name=_payload_required_string(command.payload, "tool_name"),
                target_path=_payload_required_string(command.payload, "target_path"),
                tier=_payload_required_string(command.payload, "tier"),
                rollback_reference=_payload_required_string(command.payload, "rollback_reference"),
            )
        except ValueError as exc:
            return _degraded(command, reason=str(exc))

        result_status: SessionBridgeResultStatus
        if governance.policy_decision.status == "deny":
            result_status = "denied"
        elif governance.policy_decision.status == "escalate":
            result_status = "approval_required"
        else:
            result_status = "write_requested"

        return SessionBridgeResult(
            command_id=command.command_id,
            command_type=command.command_type,
            status=result_status,
            payload={
                "execution_id": _execution_id(command),
                "repo_id": governance.repo_id,
                "binding_id": governance.binding_id,
                "task_id": governance.task_id,
                "target_path": governance.target_path,
                "write_tier": governance.write_tier,
                "governance_status": governance.governance_status,
                "approval_id": governance.approval_id,
                "task_state": governance.task_state,
                "policy_status": governance.policy_decision.status,
                "policy_decision_ref": governance.policy_decision.evidence_ref,
                "reason": governance.reason,
            },
            policy_decision_ref=governance.policy_decision.evidence_ref,
        )

    if command.command_type == "write_approve":
        if attachment_runtime_state_root is None:
            return _degraded(command, reason="attachment_runtime_state_root is required")
        try:
            approval = decide_attached_write_request(
                attachment_runtime_state_root=attachment_runtime_state_root,
                approval_id=_payload_required_string(command.payload, "approval_id"),
                decision=_payload_required_string(command.payload, "decision"),
                decided_by=_payload_required_string(command.payload, "decided_by"),
            )
        except ValueError as exc:
            return _degraded(command, reason=str(exc))

        return SessionBridgeResult(
            command_id=command.command_id,
            command_type=command.command_type,
            status="approval_recorded",
            payload={
                "execution_id": _execution_id(command),
                "approval_id": approval.approval_id,
                "approval_status": approval.status,
                "decided_by": approval.decided_by,
                "approval_record_ref": approval.approval_record_ref,
                "reason": approval.reason,
            },
            policy_decision_ref=command.policy_decision_ref,
        )

    if command.command_type == "write_status":
        return _write_status(command, attachment_runtime_state_root=attachment_runtime_state_root)

    if command.command_type in EXECUTION_COMMAND_TYPES:
        if requires_human_approval(command):
            return SessionBridgeResult(
                command_id=command.command_id,
                command_type=command.command_type,
                status="approval_required",
                payload={"escalation_context": command.escalation_context or {}},
                policy_decision_ref=command.policy_decision_ref,
            )
        if not is_execution_command(command):
            return _degraded(command, reason="execution command is not executable")
        if command.command_type == "write_execute":
            if attachment_root is None or attachment_runtime_state_root is None:
                return _degraded(command, reason="attachment_root and attachment_runtime_state_root are required")
            try:
                execution = execute_attached_write_request(
                    attachment_root=attachment_root,
                    attachment_runtime_state_root=attachment_runtime_state_root,
                    task_id=command.task_id,
                    tool_name=_payload_required_string(command.payload, "tool_name"),
                    target_path=_payload_required_string(command.payload, "target_path"),
                    tier=_payload_required_string(command.payload, "tier"),
                    rollback_reference=_payload_required_string(command.payload, "rollback_reference"),
                    content=_payload_required_string(command.payload, "content"),
                    approval_id=_payload_optional_string(command.payload, "approval_id"),
                )
            except ValueError as exc:
                return _degraded(command, reason=str(exc))

            status: SessionBridgeResultStatus = "write_executed"
            if execution.execution_status == "blocked":
                status = "approval_required"
            elif execution.execution_status == "denied":
                status = "denied"
            return SessionBridgeResult(
                command_id=command.command_id,
                command_type=command.command_type,
                status=status,
                payload={
                    "execution_id": _execution_id(command),
                    "repo_id": execution.repo_id,
                    "binding_id": execution.binding_id,
                    "task_id": execution.task_id,
                    "target_path": execution.target_path,
                    "write_tier": execution.write_tier,
                    "execution_status": execution.execution_status,
                    "artifact_ref": execution.artifact_ref,
                    "approval_id": execution.approval_id,
                    "approval_status": execution.approval_status,
                    "bytes_written": execution.bytes_written,
                    "reason": execution.reason,
                },
                policy_decision_ref=execution.policy_decision.evidence_ref,
            )
        mode = "quick" if command.command_type == "run_quick_gate" else "full"
        plan = _verification_plan_for_command(
            command,
            mode=mode,
            attachment_root=attachment_root,
            attachment_runtime_state_root=attachment_runtime_state_root,
        )
        return SessionBridgeResult(
            command_id=command.command_id,
            command_type=command.command_type,
            status="verification_requested",
            payload={
                "mode": plan.mode,
                "gate_order": [gate.gate_id for gate in plan.gates],
                "commands": [gate.command for gate in plan.gates],
            },
            policy_decision_ref=command.policy_decision_ref,
        )

    if command.command_type == "request_approval":
        return SessionBridgeResult(
            command_id=command.command_id,
            command_type=command.command_type,
            status="approval_required",
            payload={"escalation_context": command.escalation_context or {}},
            policy_decision_ref=command.policy_decision_ref,
        )

    return _degraded(command, reason=f"command is not implemented by the local session bridge: {command.command_type}")


def run_launch_mode(
    command: SessionBridgeCommand,
    *,
    argv: list[str],
    cwd: str | Path,
    verification_refs: list[str] | None = None,
) -> SessionBridgeResult:
    working_directory = Path(cwd)
    before = _file_snapshot(working_directory)
    completed = subprocess.run(
        argv,
        capture_output=True,
        text=True,
        cwd=working_directory,
        check=False,
    )
    after = _file_snapshot(working_directory)
    changed_files = sorted(path for path, digest in after.items() if before.get(path) != digest)
    deleted_files = sorted(path for path in before if path not in after)
    return SessionBridgeResult(
        command_id=command.command_id,
        command_type=command.command_type,
        status="launch_completed",
        payload={
            "launch_mode": "process_bridge",
            "adapter_tier": "process_bridge",
            "native_attach": False,
            "exit_code": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "changed_files": changed_files,
            "deleted_files": deleted_files,
            "verification_refs": verification_refs or [],
        },
        policy_decision_ref=command.policy_decision_ref,
    )


def manual_handoff_result(command: SessionBridgeCommand, *, reason: str) -> SessionBridgeResult:
    return SessionBridgeResult(
        command_id=command.command_id,
        command_type=command.command_type,
        status="manual_handoff",
        payload={
            "launch_mode": "manual_handoff",
            "adapter_tier": "manual_handoff",
            "native_attach": False,
        },
        policy_decision_ref=command.policy_decision_ref,
        unsupported_capability_behavior="manual_handoff",
        reason=reason,
    )


def _validate_policy_decision_matches_command(
    policy_decision: PolicyDecision,
    *,
    task_id: str,
    risk_tier: str,
) -> None:
    if policy_decision.task_id != _required_string(task_id, "task_id"):
        msg = "PolicyDecision task_id must match session bridge command task_id"
        raise ValueError(msg)
    if policy_decision.risk_tier != risk_tier:
        msg = "PolicyDecision risk_tier must match session bridge command risk_tier"
        raise ValueError(msg)


def _escalation_context_from_policy(
    policy_decision: PolicyDecision,
    *,
    policy_decision_ref: str,
    provided_context: dict | None,
) -> dict:
    context = dict(provided_context or {})
    context.setdefault("required_approval_ref", policy_decision.required_approval_ref)
    context.setdefault("policy_decision_ref", policy_decision_ref)
    context.setdefault("reason", "; ".join(policy_decision.decision_basis))
    if not context.get("required_approval_ref"):
        msg = "escalation_context requires required_approval_ref"
        raise ValueError(msg)
    return context


def _degraded(command: SessionBridgeCommand, *, reason: str) -> SessionBridgeResult:
    return SessionBridgeResult(
        command_id=command.command_id,
        command_type=command.command_type,
        status="degraded",
        payload={},
        policy_decision_ref=command.policy_decision_ref,
        unsupported_capability_behavior="manual_handoff",
        reason=reason,
    )


def _inspect_evidence(command: SessionBridgeCommand, *, task_root: Path) -> SessionBridgeResult:
    try:
        record = FileTaskStore(task_root).load(command.task_id)
    except FileNotFoundError:
        return _degraded(command, reason=f"task record not found: {command.task_id}")

    run_id = _payload_optional_string(command.payload, "run_id")
    selected_runs = [run for run in record.run_history if run_id is None or run.run_id == run_id]
    transition_evidence_refs = [
        transition.evidence_ref
        for transition in record.transition_history
        if transition.evidence_ref
    ]
    return SessionBridgeResult(
        command_id=command.command_id,
        command_type=command.command_type,
        status="ok",
        payload={
            "task_id": record.task_id,
            "current_state": record.current_state,
            "active_run_id": record.active_run_id,
            "run_id": run_id,
            "evidence_refs": _dedupe_preserve_order(
                [ref for run in selected_runs for ref in run.evidence_refs] + transition_evidence_refs
            ),
            "artifact_refs": _dedupe_preserve_order([ref for run in selected_runs for ref in run.artifact_refs]),
            "verification_refs": _dedupe_preserve_order([ref for run in selected_runs for ref in run.verification_refs]),
            "approval_ids": _dedupe_preserve_order([approval_id for run in selected_runs for approval_id in run.approval_ids]),
            "rollback_refs": _dedupe_preserve_order(
                [rollback_ref for rollback_ref in [record.rollback_ref] + [run.rollback_ref for run in selected_runs] if rollback_ref]
            ),
            "transition_evidence_refs": transition_evidence_refs,
        },
        policy_decision_ref=command.policy_decision_ref,
    )


def _inspect_handoff(command: SessionBridgeCommand, *, task_root: Path) -> SessionBridgeResult:
    try:
        record = FileTaskStore(task_root).load(command.task_id)
    except FileNotFoundError:
        return _degraded(command, reason=f"task record not found: {command.task_id}")

    run_id = _payload_optional_string(command.payload, "run_id")
    selected_runs = [run for run in record.run_history if run_id is None or run.run_id == run_id]
    payload_refs = _payload_string_list(command.payload, "handoff_refs")
    single_ref = _payload_optional_string(command.payload, "handoff_ref")
    if single_ref is not None:
        payload_refs.append(single_ref)
    discovered_refs = [
        ref
        for ref in [ref for run in selected_runs for ref in run.artifact_refs + run.evidence_refs]
        if "handoff" in ref
    ]
    return SessionBridgeResult(
        command_id=command.command_id,
        command_type=command.command_type,
        status="ok",
        payload={
            "task_id": record.task_id,
            "run_id": run_id,
            "handoff_refs": _dedupe_preserve_order(payload_refs + discovered_refs),
            "rollback_refs": _dedupe_preserve_order(
                [rollback_ref for rollback_ref in [record.rollback_ref] + [run.rollback_ref for run in selected_runs] if rollback_ref]
            ),
        },
        policy_decision_ref=command.policy_decision_ref,
    )


def _write_status(
    command: SessionBridgeCommand,
    *,
    attachment_runtime_state_root: str | Path | None,
) -> SessionBridgeResult:
    approval_id = _payload_optional_string(command.payload, "approval_id")
    approval_status = None
    approval_record_ref = None
    if attachment_runtime_state_root is not None and approval_id is not None:
        approval_path = Path(attachment_runtime_state_root) / "approvals" / f"{approval_id}.json"
        if approval_path.exists():
            approval_status = _required_string(
                json.loads(approval_path.read_text(encoding="utf-8")).get("status"),
                "status",
            )
            approval_record_ref = approval_path.as_posix()

    return SessionBridgeResult(
        command_id=command.command_id,
        command_type=command.command_type,
        status="ok",
        payload={
            "execution_id": _execution_id(command),
            "task_id": command.task_id,
            "target_path": _payload_optional_string(command.payload, "target_path"),
            "approval_id": approval_id,
            "approval_status": approval_status,
            "approval_record_ref": approval_record_ref,
            "policy_decision_ref": command.policy_decision_ref,
        },
        policy_decision_ref=command.policy_decision_ref,
    )


def _run_id_from_payload(payload: dict) -> str:
    value = payload.get("run_id")
    if isinstance(value, str) and value.strip():
        return value.strip()
    return "session-bridge-request"


def _verification_plan_for_command(
    command: SessionBridgeCommand,
    *,
    mode: str,
    attachment_root: str | Path | None,
    attachment_runtime_state_root: str | Path | None,
) -> VerificationPlan:
    if attachment_root is None or attachment_runtime_state_root is None:
        return build_verification_plan(
            mode,
            task_id=command.task_id,
            run_id=_run_id_from_payload(command.payload),
        )

    try:
        attachment = validate_light_pack(
            target_repo_root=str(attachment_root),
            light_pack_path=str(Path(attachment_root) / ".governed-ai" / "light-pack.json"),
            runtime_state_root=str(attachment_runtime_state_root),
        )
        profile = load_repo_profile(attachment.repo_profile_path)
        return build_repo_profile_verification_plan(
            mode,
            profile_raw=profile.raw,
            task_id=command.task_id,
            run_id=_run_id_from_payload(command.payload),
        )
    except (OSError, ValueError):
        pass

    return build_verification_plan(
        mode,
        task_id=command.task_id,
        run_id=_run_id_from_payload(command.payload),
    )


def _file_snapshot(root: Path) -> dict[str, str]:
    if not root.exists():
        return {}
    snapshot: dict[str, str] = {}
    for path in root.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        relative_path = path.relative_to(root).as_posix()
        snapshot[relative_path] = hashlib.sha256(path.read_bytes()).hexdigest()
    return snapshot


def _execution_id(command: SessionBridgeCommand) -> str:
    explicit = _payload_optional_string(command.payload, "execution_id")
    if explicit is not None:
        return explicit
    return f"{command.task_id}:{command.command_id}"


def _required_enum(value: str, field_name: str, valid_values: set[str]) -> str:
    normalized = _required_string(value, field_name)
    if normalized not in valid_values:
        msg = f"unsupported {field_name}: {value}"
        raise ValueError(msg)
    return normalized


def _required_string(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        msg = f"{field_name} is required"
        raise ValueError(msg)
    return value.strip()


def _optional_string(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    return _required_string(value, field_name)


def _payload_dict(value: dict | None, field_name: str) -> dict:
    if value is None:
        return {}
    if not isinstance(value, dict):
        msg = f"{field_name} must be an object"
        raise ValueError(msg)
    return dict(value)


def _optional_context(value: dict | None, field_name: str) -> dict | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        msg = f"{field_name} must be an object"
        raise ValueError(msg)
    return dict(value)


def _payload_required_string(payload: dict, field_name: str) -> str:
    return _required_string(payload.get(field_name), field_name)


def _payload_optional_string(payload: dict, field_name: str) -> str | None:
    value = payload.get(field_name)
    if value is None:
        return None
    return _required_string(value, field_name)


def _payload_string_list(payload: dict, field_name: str) -> list[str]:
    value = payload.get(field_name)
    if value is None:
        return []
    if not isinstance(value, list):
        msg = f"{field_name} must be a list"
        raise ValueError(msg)
    return [_required_string(item, field_name) for item in value]


def _dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered
