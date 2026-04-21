"""Stable session bridge command contract for interactive governed actions."""

from dataclasses import asdict
import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from governed_ai_coding_runtime_contracts.artifact_store import LocalArtifactStore
from governed_ai_coding_runtime_contracts.attached_write_execution import (
    decide_attached_write_request,
    execute_attached_write_request,
)
from governed_ai_coding_runtime_contracts.attached_write_governance import govern_attached_write_request
from governed_ai_coding_runtime_contracts.codex_adapter import (
    CodexSessionEvidence,
    handshake_codex_session,
    record_codex_session_evidence,
)
from governed_ai_coding_runtime_contracts.evidence import EvidenceTimeline, summarize_adapter_evidence
from governed_ai_coding_runtime_contracts.operator_queries import query_operator_attachment_surface
from governed_ai_coding_runtime_contracts.policy_decision import PolicyDecision
from governed_ai_coding_runtime_contracts.repo_attachment import inspect_attachment_posture, validate_light_pack
from governed_ai_coding_runtime_contracts.repo_profile import load_repo_profile
from governed_ai_coding_runtime_contracts.runtime_status import RuntimeStatusStore
from governed_ai_coding_runtime_contracts.task_store import FileTaskStore
from governed_ai_coding_runtime_contracts.tool_runner import execute_governed_command, govern_execution_request
from governed_ai_coding_runtime_contracts.verification_runner import (
    VerificationPlan,
    build_repo_profile_verification_plan,
    build_verification_plan,
    run_verification_plan,
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
    "verification_completed",
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
GOVERNED_TOOL_TYPES = {"shell", "git", "package"}


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


def session_bridge_result_to_dict(result: SessionBridgeResult) -> dict:
    return asdict(result)


def session_bridge_result_from_dict(raw: dict) -> SessionBridgeResult:
    if not isinstance(raw, dict):
        msg = "session bridge result payload must be an object"
        raise ValueError(msg)
    payload = raw.get("payload")
    if not isinstance(payload, dict):
        msg = "payload must be an object"
        raise ValueError(msg)
    return SessionBridgeResult(
        command_id=_required_string(raw.get("command_id"), "command_id"),
        command_type=_required_enum(raw.get("command_type"), "command_type", COMMAND_TYPES),
        status=_required_enum(raw.get("status"), "status", set(SessionBridgeResultStatus.__args__)),
        payload=dict(payload),
        policy_decision_ref=_optional_string(raw.get("policy_decision_ref"), "policy_decision_ref"),
        unsupported_capability_behavior=_optional_string(
            raw.get("unsupported_capability_behavior"),
            "unsupported_capability_behavior",
        ),
        reason=_optional_string(raw.get("reason"), "reason"),
    )


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
                "maintenance": {
                    "stage": snapshot.maintenance.stage,
                    "compatibility_policy_ref": snapshot.maintenance.compatibility_policy_ref,
                    "upgrade_policy_ref": snapshot.maintenance.upgrade_policy_ref,
                    "triage_policy_ref": snapshot.maintenance.triage_policy_ref,
                    "deprecation_policy_ref": snapshot.maintenance.deprecation_policy_ref,
                    "retirement_policy_ref": snapshot.maintenance.retirement_policy_ref,
                },
                "tasks": [
                    {
                        "task_id": task.task_id,
                        "state": task.current_state,
                        "goal": task.goal,
                        "active_run_id": task.active_run_id,
                        "workspace_root": task.workspace_root,
                        "rollback_ref": task.rollback_ref,
                        "approval_ids": task.approval_ids,
                        "artifact_refs": task.artifact_refs,
                        "evidence_refs": task.evidence_refs,
                        "verification_refs": task.verification_refs,
                    }
                    for task in snapshot.tasks
                ],
                "attachments": [
                    {
                        "repo_id": attachment.repo_id,
                        "binding_id": attachment.binding_id,
                        "binding_state": attachment.binding_state,
                        "light_pack_path": attachment.light_pack_path,
                        "adapter_preference": attachment.adapter_preference,
                        "gate_profile": attachment.gate_profile,
                        "reason": attachment.reason,
                        "remediation": attachment.remediation,
                        "fail_closed": attachment.fail_closed,
                    }
                    for attachment in snapshot.attachments
                ],
            },
        )

    if command.command_type == "inspect_evidence":
        return _inspect_evidence(
            command,
            task_root=Path(task_root),
            attachment_root=attachment_root,
            attachment_runtime_state_root=attachment_runtime_state_root,
        )

    if command.command_type == "inspect_handoff":
        return _inspect_handoff(
            command,
            task_root=Path(task_root),
            attachment_root=attachment_root,
            attachment_runtime_state_root=attachment_runtime_state_root,
        )

    if command.command_type == "write_request":
        tool_name = _payload_required_string(command.payload, "tool_name")
        if tool_name in GOVERNED_TOOL_TYPES:
            command_text = _payload_required_string(command.payload, "command")
            rollback_reference = _payload_required_string(command.payload, "rollback_reference")
            governance = govern_execution_request(
                tool_name=tool_name,
                command=command_text,
                tier=command.risk_tier,
                rollback_reference=rollback_reference,
            )
            execution_id = _execution_id(command)
            continuation_id = _continuation_id(command, execution_id=execution_id)
            session_identity = _session_identity(command, continuation_id=continuation_id)
            approval_id = None
            approval_ref = None
            if governance.requires_approval:
                if attachment_runtime_state_root is None:
                    return _degraded(
                        command,
                        reason="attachment_runtime_state_root is required for approval-tracked tool execution",
                )
                approval_id = _tool_approval_id(command)
                execution_id = _execution_id(command, approval_id=approval_id)
                continuation_id = _continuation_id(command, approval_id=approval_id, execution_id=execution_id)
                session_identity = _session_identity(
                    command,
                    continuation_id=continuation_id,
                    approval_id=approval_id,
                    attachment_runtime_state_root=attachment_runtime_state_root,
                )
                approval_ref = _persist_tool_approval_request(
                    runtime_state_root=Path(attachment_runtime_state_root),
                    approval_id=approval_id,
                    task_id=command.task_id,
                    tool_name=tool_name,
                    command_text=command_text,
                    tier=command.risk_tier,
                    rollback_reference=rollback_reference,
                    session_identity=session_identity,
                )
            policy_ref = f"artifacts/{command.task_id}/policy/tool-{governance.status}.json"
            status: SessionBridgeResultStatus
            if governance.status == "deny":
                status = "denied"
            elif governance.status == "escalate":
                status = "approval_required"
            else:
                status = "write_requested"
            return SessionBridgeResult(
                command_id=command.command_id,
                command_type=command.command_type,
                status=status,
                payload={
                    "execution_id": execution_id,
                    "continuation_id": continuation_id,
                    "adapter_id": command.adapter_id,
                    "session_identity": session_identity,
                    "task_id": command.task_id,
                    "tool_name": tool_name,
                    "command": command_text,
                    "write_tier": command.risk_tier,
                    "governance_status": governance.status,
                    "approval_id": approval_id,
                    "approval_ref": approval_ref,
                    "task_state": "approval_pending" if governance.requires_approval else "ready",
                    "policy_status": governance.status,
                    "policy_decision_ref": policy_ref,
                    "artifact_refs": [],
                    "handoff_ref": None,
                    "replay_ref": None,
                    "reason": governance.reason,
                    "rollback_reference": rollback_reference,
                },
                policy_decision_ref=policy_ref,
            )
        if attachment_root is None or attachment_runtime_state_root is None:
            return _degraded(command, reason="attachment_root and attachment_runtime_state_root are required")
        try:
            governance = govern_attached_write_request(
                attachment_root=attachment_root,
                attachment_runtime_state_root=attachment_runtime_state_root,
                task_id=command.task_id,
                tool_name=tool_name,
                target_path=_payload_required_string(command.payload, "target_path"),
                tier=_payload_required_string(command.payload, "tier"),
                rollback_reference=_payload_required_string(command.payload, "rollback_reference"),
                session_identity=_session_identity(command),
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
        execution_id = _execution_id(command, approval_id=governance.approval_id)
        continuation_id = _continuation_id(command, approval_id=governance.approval_id, execution_id=execution_id)
        session_identity = _session_identity(
            command,
            continuation_id=continuation_id,
            approval_id=governance.approval_id,
            attachment_runtime_state_root=attachment_runtime_state_root,
        )
        _persist_approval_session_identity(
            attachment_runtime_state_root=attachment_runtime_state_root,
            approval_id=governance.approval_id,
            session_identity=session_identity,
        )
        approval_ref = _approval_record_ref(
            attachment_runtime_state_root=attachment_runtime_state_root,
            approval_id=governance.approval_id,
        )

        return SessionBridgeResult(
            command_id=command.command_id,
            command_type=command.command_type,
            status=result_status,
            payload={
                "execution_id": execution_id,
                "continuation_id": continuation_id,
                "adapter_id": command.adapter_id,
                "session_identity": session_identity,
                "repo_id": governance.repo_id,
                "binding_id": governance.binding_id,
                "task_id": governance.task_id,
                "target_path": governance.target_path,
                "write_tier": governance.write_tier,
                "governance_status": governance.governance_status,
                "approval_id": governance.approval_id,
                "approval_ref": approval_ref,
                "task_state": governance.task_state,
                "policy_status": governance.policy_decision.status,
                "policy_decision_ref": governance.policy_decision.evidence_ref,
                "artifact_refs": [],
                "handoff_ref": None,
                "replay_ref": None,
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

        execution_id = _execution_id(command, approval_id=approval.approval_id)
        continuation_id = _continuation_id(command, approval_id=approval.approval_id, execution_id=execution_id)
        session_identity = _session_identity(
            command,
            continuation_id=continuation_id,
            approval_id=approval.approval_id,
            attachment_runtime_state_root=attachment_runtime_state_root,
        )
        _persist_approval_session_identity(
            attachment_runtime_state_root=attachment_runtime_state_root,
            approval_id=approval.approval_id,
            session_identity=session_identity,
        )

        return SessionBridgeResult(
            command_id=command.command_id,
            command_type=command.command_type,
            status="approval_recorded",
            payload={
                "execution_id": execution_id,
                "continuation_id": continuation_id,
                "adapter_id": command.adapter_id,
                "session_identity": session_identity,
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
                payload={
                    "execution_id": _execution_id(command),
                    "continuation_id": _continuation_id(command),
                    "escalation_context": command.escalation_context or {},
                },
                policy_decision_ref=command.policy_decision_ref,
            )
        if not is_execution_command(command):
            return _degraded(command, reason="execution command is not executable")
        if command.command_type == "write_execute":
            tool_name = _payload_required_string(command.payload, "tool_name")
            if tool_name in GOVERNED_TOOL_TYPES:
                command_text = _payload_required_string(command.payload, "command")
                rollback_reference = _payload_required_string(command.payload, "rollback_reference")
                approval_id = _payload_optional_string(command.payload, "approval_id")
                execution_id = _execution_id(command, approval_id=approval_id)
                continuation_id = _continuation_id(command, approval_id=approval_id, execution_id=execution_id)
                session_identity = _session_identity(
                    command,
                    continuation_id=continuation_id,
                    approval_id=approval_id,
                    attachment_runtime_state_root=attachment_runtime_state_root,
                )
                _persist_approval_session_identity(
                    attachment_runtime_state_root=attachment_runtime_state_root,
                    approval_id=approval_id,
                    session_identity=session_identity,
                )
                approval_status = _tool_approval_status(
                    attachment_runtime_state_root=attachment_runtime_state_root,
                    approval_id=approval_id,
                )
                if approval_status == "rejected":
                    return SessionBridgeResult(
                        command_id=command.command_id,
                        command_type=command.command_type,
                        status="denied",
                        payload={
                            "execution_id": execution_id,
                            "continuation_id": continuation_id,
                            "adapter_id": command.adapter_id,
                            "session_identity": session_identity,
                            "task_id": command.task_id,
                            "tool_name": tool_name,
                            "command": command_text,
                            "execution_status": "denied",
                            "approval_id": approval_id,
                            "approval_status": approval_status,
                            "artifact_ref": None,
                            "artifact_refs": [],
                            "approval_ref": _approval_record_ref(
                                attachment_runtime_state_root=attachment_runtime_state_root,
                                approval_id=approval_id,
                            ),
                            "handoff_ref": None,
                            "replay_ref": None,
                            "rollback_reference": rollback_reference,
                            "reason": "approval_rejected",
                        },
                        policy_decision_ref=command.policy_decision_ref,
                    )
                if command.risk_tier == "high" and approval_status in {"missing", "pending", "stale"}:
                    return SessionBridgeResult(
                        command_id=command.command_id,
                        command_type=command.command_type,
                        status="denied",
                        payload={
                            "execution_id": execution_id,
                            "continuation_id": continuation_id,
                            "adapter_id": command.adapter_id,
                            "session_identity": session_identity,
                            "task_id": command.task_id,
                            "tool_name": tool_name,
                            "command": command_text,
                            "execution_status": "denied",
                            "approval_id": approval_id,
                            "approval_status": approval_status,
                            "artifact_ref": None,
                            "artifact_refs": [],
                            "approval_ref": _approval_record_ref(
                                attachment_runtime_state_root=attachment_runtime_state_root,
                                approval_id=approval_id,
                            ),
                            "handoff_ref": None,
                            "replay_ref": None,
                            "rollback_reference": rollback_reference,
                            "reason": "high risk tool execution requires fresh approval",
                        },
                        policy_decision_ref=command.policy_decision_ref,
                    )
                if command.risk_tier in {"medium", "high"} and approval_status in {"missing", "pending"}:
                    return SessionBridgeResult(
                        command_id=command.command_id,
                        command_type=command.command_type,
                        status="approval_required",
                        payload={
                            "execution_id": execution_id,
                            "continuation_id": continuation_id,
                            "adapter_id": command.adapter_id,
                            "session_identity": session_identity,
                            "task_id": command.task_id,
                            "tool_name": tool_name,
                            "command": command_text,
                            "execution_status": "blocked",
                            "approval_id": approval_id,
                            "approval_status": approval_status,
                            "artifact_ref": None,
                            "artifact_refs": [],
                            "approval_ref": _approval_record_ref(
                                attachment_runtime_state_root=attachment_runtime_state_root,
                                approval_id=approval_id,
                            ),
                            "handoff_ref": None,
                            "replay_ref": None,
                            "rollback_reference": rollback_reference,
                            "reason": "approval_required",
                        },
                        policy_decision_ref=command.policy_decision_ref,
                    )

                execution = execute_governed_command(
                    command=command_text,
                    cwd=str(_verification_cwd(repo_root=Path(repo_root), attachment_root=attachment_root)),
                )
                execution_status = "executed" if execution.exit_code == 0 else "denied"
                artifact_store = LocalArtifactStore(
                    _verification_artifact_root(
                        task_root=Path(task_root),
                        attachment_runtime_state_root=attachment_runtime_state_root,
                    )
                )
                tool_artifact = artifact_store.write_json(
                    task_id=command.task_id,
                    run_id=_execution_id(command, approval_id=approval_id),
                    kind="execution-tool",
                    label=tool_name,
                    payload={
                        "command": command_text,
                        "exit_code": execution.exit_code,
                        "output": execution.output,
                        "tier": command.risk_tier,
                        "rollback_reference": rollback_reference,
                    },
                )
                handoff_ref, replay_ref = _write_write_flow_refs(
                    task_id=command.task_id,
                    execution_id=execution_id,
                    runtime_state_root=_verification_artifact_root(
                        task_root=Path(task_root),
                        attachment_runtime_state_root=attachment_runtime_state_root,
                    ),
                    payload={
                        "adapter_id": command.adapter_id,
                        "task_id": command.task_id,
                        "tool_name": tool_name,
                        "command": command_text,
                        "execution_status": execution_status,
                        "approval_id": approval_id,
                        "artifact_ref": tool_artifact.relative_path,
                        "policy_decision_ref": command.policy_decision_ref,
                    },
                )
                adapter_event_ref, adapter_event_summary = _record_adapter_events(
                    command=command,
                    artifact_store=artifact_store,
                    task_id=command.task_id,
                    run_id=execution_id,
                    execution_id=execution_id,
                    continuation_id=continuation_id,
                    session_identity=session_identity,
                    file_changes=[],
                    tool_calls=[
                        {
                            "tool": tool_name,
                            "command": command_text,
                            "exit_code": execution.exit_code,
                        }
                    ],
                    gate_runs=[],
                    approvals=[approval_id] if approval_id else [],
                    handoff_refs=[handoff_ref] if handoff_ref else [],
                    unsupported_events=(
                        [{"event_type": "tool_command_failure", "reason": execution.output}]
                        if execution.exit_code != 0
                        else []
                    ),
                )
                artifact_refs = _dedupe_preserve_order(
                    [
                        ref
                        for ref in [tool_artifact.relative_path, handoff_ref, replay_ref, adapter_event_ref]
                        if ref
                    ]
                )
                return SessionBridgeResult(
                    command_id=command.command_id,
                    command_type=command.command_type,
                    status="write_executed" if execution_status == "executed" else "denied",
                    payload={
                        "execution_id": execution_id,
                        "continuation_id": continuation_id,
                        "adapter_id": command.adapter_id,
                        "session_identity": session_identity,
                        "task_id": command.task_id,
                        "tool_name": tool_name,
                        "command": command_text,
                        "execution_status": execution_status,
                        "artifact_ref": tool_artifact.relative_path,
                        "artifact_refs": artifact_refs,
                        "adapter_event_ref": adapter_event_ref,
                        "adapter_event_summary": adapter_event_summary,
                        "approval_id": approval_id,
                        "approval_ref": _approval_record_ref(
                            attachment_runtime_state_root=attachment_runtime_state_root,
                            approval_id=approval_id,
                        ),
                        "approval_status": "approved" if approval_id else None,
                        "handoff_ref": handoff_ref,
                        "replay_ref": replay_ref,
                        "bytes_written": None,
                        "reason": execution.output if execution.exit_code != 0 else None,
                        "rollback_reference": rollback_reference,
                    },
                    policy_decision_ref=command.policy_decision_ref,
                )
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
            execution_id = _execution_id(command, approval_id=execution.approval_id)
            continuation_id = _continuation_id(command, approval_id=execution.approval_id, execution_id=execution_id)
            session_identity = _session_identity(
                command,
                continuation_id=continuation_id,
                approval_id=execution.approval_id,
                attachment_runtime_state_root=attachment_runtime_state_root,
            )
            _persist_approval_session_identity(
                attachment_runtime_state_root=attachment_runtime_state_root,
                approval_id=execution.approval_id,
                session_identity=session_identity,
            )
            approval_ref = _approval_record_ref(
                attachment_runtime_state_root=attachment_runtime_state_root,
                approval_id=execution.approval_id,
            )
            handoff_ref, replay_ref = _write_write_flow_refs(
                task_id=execution.task_id,
                execution_id=execution_id,
                runtime_state_root=Path(attachment_runtime_state_root),
                payload={
                    "adapter_id": command.adapter_id,
                    "task_id": execution.task_id,
                    "execution_status": execution.execution_status,
                    "target_path": execution.target_path,
                    "approval_id": execution.approval_id,
                    "artifact_ref": execution.artifact_ref,
                    "policy_decision_ref": execution.policy_decision.evidence_ref,
                },
            )
            adapter_event_ref, adapter_event_summary = _record_adapter_events(
                command=command,
                artifact_store=LocalArtifactStore(Path(attachment_runtime_state_root)),
                task_id=execution.task_id,
                run_id=execution_id,
                execution_id=execution_id,
                continuation_id=continuation_id,
                session_identity=session_identity,
                file_changes=[execution.target_path] if execution.execution_status == "executed" else [],
                tool_calls=[
                    {
                        "tool": _payload_required_string(command.payload, "tool_name"),
                        "target_path": execution.target_path,
                        "status": execution.execution_status,
                    }
                ],
                gate_runs=[],
                approvals=[execution.approval_id] if execution.approval_id else [],
                handoff_refs=[handoff_ref] if handoff_ref else [],
                unsupported_events=(
                    [{"event_type": "write_execution_denied", "reason": execution.reason}]
                    if execution.execution_status == "denied"
                    else []
                ),
            )
            artifact_refs = _dedupe_preserve_order(
                [
                    ref
                    for ref in [execution.artifact_ref, handoff_ref, replay_ref, adapter_event_ref]
                    if ref
                ]
            )
            return SessionBridgeResult(
                command_id=command.command_id,
                command_type=command.command_type,
                status=status,
                payload={
                    "execution_id": execution_id,
                    "continuation_id": continuation_id,
                    "adapter_id": command.adapter_id,
                    "session_identity": session_identity,
                    "repo_id": execution.repo_id,
                    "binding_id": execution.binding_id,
                    "task_id": execution.task_id,
                    "target_path": execution.target_path,
                    "write_tier": execution.write_tier,
                    "execution_status": execution.execution_status,
                    "artifact_ref": execution.artifact_ref,
                    "artifact_refs": artifact_refs,
                    "adapter_event_ref": adapter_event_ref,
                    "adapter_event_summary": adapter_event_summary,
                    "approval_id": execution.approval_id,
                    "approval_ref": approval_ref,
                    "approval_status": execution.approval_status,
                    "handoff_ref": handoff_ref,
                    "replay_ref": replay_ref,
                    "bytes_written": execution.bytes_written,
                    "reason": execution.reason,
                },
                policy_decision_ref=execution.policy_decision.evidence_ref,
            )
        mode = "quick" if command.command_type == "run_quick_gate" else "full"
        try:
            plan = _verification_plan_for_command(
                command,
                mode=mode,
                attachment_root=attachment_root,
                attachment_runtime_state_root=attachment_runtime_state_root,
            )
        except ValueError as exc:
            return _degraded(command, reason=f"contract_reader_error: {exc}")
        run_id = _run_id_from_payload(command.payload)
        execution_id = _execution_id(command, run_id=run_id)
        continuation_id = _continuation_id(command, run_id=run_id, execution_id=execution_id)
        try:
            plan_only = _payload_optional_bool(command.payload, "plan_only")
        except ValueError as exc:
            return _degraded(command, reason=str(exc))
        if plan_only:
            session_identity = _session_identity(command, continuation_id=continuation_id)
            return SessionBridgeResult(
                command_id=command.command_id,
                command_type=command.command_type,
                status="verification_requested",
                payload={
                    "execution_id": execution_id,
                    "continuation_id": continuation_id,
                    "adapter_id": command.adapter_id,
                    "session_identity": session_identity,
                    "run_id": run_id,
                    "mode": plan.mode,
                    "plan_only": True,
                    "gate_order": [gate.gate_id for gate in plan.gates],
                    "commands": [gate.command for gate in plan.gates],
                },
                policy_decision_ref=command.policy_decision_ref,
            )
        artifact_store = LocalArtifactStore(
            _verification_artifact_root(
                task_root=Path(task_root),
                attachment_runtime_state_root=attachment_runtime_state_root,
            )
        )
        verification_artifact = run_verification_plan(
            plan,
            artifact_store=artifact_store,
            execute_gate=lambda gate: _execute_gate_at_root(
                gate.command,
                cwd=_verification_cwd(repo_root=Path(repo_root), attachment_root=attachment_root),
            ),
        )
        session_identity = _session_identity(command, continuation_id=continuation_id)
        adapter_event_ref, adapter_event_summary = _record_adapter_events(
            command=command,
            artifact_store=artifact_store,
            task_id=command.task_id,
            run_id=execution_id,
            execution_id=execution_id,
            continuation_id=continuation_id,
            session_identity=session_identity,
            file_changes=[],
            tool_calls=[],
            gate_runs=list(verification_artifact.result_artifact_refs.values()),
            approvals=[],
            handoff_refs=[],
            unsupported_events=(
                [
                    {
                        "event_type": "gate_failed",
                        "reason": gate_id,
                    }
                    for gate_id, result in verification_artifact.results.items()
                    if result != "pass"
                ]
            ),
        )
        return SessionBridgeResult(
            command_id=command.command_id,
            command_type=command.command_type,
            status="verification_completed",
            payload={
                "execution_id": execution_id,
                "continuation_id": continuation_id,
                "adapter_id": command.adapter_id,
                "session_identity": session_identity,
                "run_id": run_id,
                "mode": plan.mode,
                "plan_only": False,
                "gate_order": [gate.gate_id for gate in plan.gates],
                "commands": [gate.command for gate in plan.gates],
                "results": verification_artifact.results,
                "result_artifact_refs": verification_artifact.result_artifact_refs,
                "risky_artifact_refs": verification_artifact.risky_artifact_refs,
                "evidence_link": verification_artifact.evidence_link,
                "adapter_event_ref": adapter_event_ref,
                "adapter_event_summary": adapter_event_summary,
                "outcome": "pass"
                if all(result == "pass" for result in verification_artifact.results.values())
                else "fail",
            },
            policy_decision_ref=command.policy_decision_ref,
        )

    if command.command_type == "request_approval":
        return SessionBridgeResult(
            command_id=command.command_id,
            command_type=command.command_type,
            status="approval_required",
            payload={
                "execution_id": _execution_id(command),
                "continuation_id": _continuation_id(command),
                "adapter_id": command.adapter_id,
                "session_identity": _session_identity(command),
                "escalation_context": command.escalation_context or {},
            },
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


def _inspect_evidence(
    command: SessionBridgeCommand,
    *,
    task_root: Path,
    attachment_root: str | Path | None,
    attachment_runtime_state_root: str | Path | None,
) -> SessionBridgeResult:
    run_id = _payload_optional_string(command.payload, "run_id")
    query = query_operator_attachment_surface(
        task_root=task_root,
        task_id=command.task_id,
        repo_binding_id=command.repo_binding_id,
        run_id=run_id,
        attachment_root=attachment_root,
        attachment_runtime_state_root=attachment_runtime_state_root,
    )

    transition_evidence_refs: list[str] = []
    rollback_refs: list[str] = []
    if query.task_found:
        record = FileTaskStore(task_root).load(command.task_id)
        selected_runs = [run for run in record.run_history if run_id is None or run.run_id == run_id]
        transition_evidence_refs = [
            transition.evidence_ref
            for transition in record.transition_history
            if transition.evidence_ref
        ]
        rollback_refs = _dedupe_preserve_order(
            [
                rollback_ref
                for rollback_ref in [record.rollback_ref] + [run.rollback_ref for run in selected_runs]
                if rollback_ref
            ]
        )

    return SessionBridgeResult(
        command_id=command.command_id,
        command_type=command.command_type,
        status="ok",
        payload={
            "execution_id": _execution_id(command),
            "continuation_id": _continuation_id(command),
            "adapter_id": command.adapter_id,
            "session_identity": _session_identity(command),
            "task_id": query.task_id,
            "task_found": query.task_found,
            "current_state": query.current_state,
            "active_run_id": query.active_run_id,
            "run_id": query.run_id,
            "evidence_refs": _dedupe_preserve_order(query.evidence_refs + transition_evidence_refs),
            "artifact_refs": query.artifact_refs,
            "verification_refs": query.verification_refs,
            "approval_ids": query.approval_ids,
            "approval_refs": query.approval_refs,
            "handoff_refs": query.handoff_refs,
            "replay_refs": query.replay_refs,
            "rollback_refs": rollback_refs,
            "transition_evidence_refs": transition_evidence_refs,
            "posture_summary": asdict(query.posture_summary) if query.posture_summary else None,
            "read_only": query.read_only,
        },
        policy_decision_ref=command.policy_decision_ref,
    )


def _inspect_handoff(
    command: SessionBridgeCommand,
    *,
    task_root: Path,
    attachment_root: str | Path | None,
    attachment_runtime_state_root: str | Path | None,
) -> SessionBridgeResult:
    run_id = _payload_optional_string(command.payload, "run_id")
    query = query_operator_attachment_surface(
        task_root=task_root,
        task_id=command.task_id,
        repo_binding_id=command.repo_binding_id,
        run_id=run_id,
        attachment_root=attachment_root,
        attachment_runtime_state_root=attachment_runtime_state_root,
    )

    rollback_refs: list[str] = []
    discovered_refs = list(query.handoff_refs)
    if query.task_found:
        record = FileTaskStore(task_root).load(command.task_id)
        selected_runs = [run for run in record.run_history if run_id is None or run.run_id == run_id]
        rollback_refs = _dedupe_preserve_order(
            [
                rollback_ref
                for rollback_ref in [record.rollback_ref] + [run.rollback_ref for run in selected_runs]
                if rollback_ref
            ]
        )
        discovered_refs = _dedupe_preserve_order(
            discovered_refs
            + [
                ref
                for ref in [ref for run in selected_runs for ref in run.artifact_refs + run.evidence_refs]
                if "handoff" in ref
            ]
        )

    payload_refs = _payload_string_list(command.payload, "handoff_refs")
    single_ref = _payload_optional_string(command.payload, "handoff_ref")
    if single_ref is not None:
        payload_refs.append(single_ref)

    return SessionBridgeResult(
        command_id=command.command_id,
        command_type=command.command_type,
        status="ok",
        payload={
            "execution_id": _execution_id(command),
            "continuation_id": _continuation_id(command),
            "adapter_id": command.adapter_id,
            "session_identity": _session_identity(command),
            "task_id": query.task_id,
            "task_found": query.task_found,
            "run_id": query.run_id,
            "handoff_refs": _dedupe_preserve_order(payload_refs + discovered_refs),
            "replay_refs": query.replay_refs,
            "rollback_refs": rollback_refs,
            "posture_summary": asdict(query.posture_summary) if query.posture_summary else None,
            "read_only": query.read_only,
        },
        policy_decision_ref=command.policy_decision_ref,
    )


def _write_status(
    command: SessionBridgeCommand,
    *,
    attachment_runtime_state_root: str | Path | None,
) -> SessionBridgeResult:
    approval_id = _payload_optional_string(command.payload, "approval_id")
    execution_id = _execution_id(command, approval_id=approval_id)
    continuation_id = _continuation_id(command, approval_id=approval_id, execution_id=execution_id)
    session_identity = _session_identity(
        command,
        continuation_id=continuation_id,
        approval_id=approval_id,
        attachment_runtime_state_root=attachment_runtime_state_root,
    )
    _persist_approval_session_identity(
        attachment_runtime_state_root=attachment_runtime_state_root,
        approval_id=approval_id,
        session_identity=session_identity,
    )
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
            "execution_id": execution_id,
            "continuation_id": continuation_id,
            "adapter_id": command.adapter_id,
            "session_identity": session_identity,
            "task_id": command.task_id,
            "target_path": _payload_optional_string(command.payload, "target_path"),
            "approval_id": approval_id,
            "approval_ref": approval_record_ref,
            "approval_status": approval_status,
            "approval_record_ref": approval_record_ref,
            "policy_decision_ref": command.policy_decision_ref,
        },
        policy_decision_ref=command.policy_decision_ref,
    )


def _record_adapter_events(
    *,
    command: SessionBridgeCommand,
    artifact_store: LocalArtifactStore,
    task_id: str,
    run_id: str,
    execution_id: str,
    continuation_id: str,
    session_identity: dict | None = None,
    file_changes: list[str],
    tool_calls: list[dict],
    gate_runs: list[str],
    approvals: list[str],
    handoff_refs: list[str],
    unsupported_events: list[dict],
) -> tuple[str | None, dict | None]:
    identity = dict(session_identity) if isinstance(session_identity, dict) else _session_identity(
        command,
        continuation_id=continuation_id,
    )
    flow_kind = (
        identity.get("flow_kind")
        if isinstance(identity.get("flow_kind"), str)
        else "manual_handoff"
    )
    event_source = "live_adapter" if flow_kind == "live_attach" else flow_kind
    unsupported_capabilities = identity.get("unsupported_capabilities")
    if not isinstance(unsupported_capabilities, list):
        unsupported_capabilities = []
    timeline = EvidenceTimeline()
    if command.adapter_id == "codex-cli":
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
        record_codex_session_evidence(timeline, session)
    else:
        base_payload = {
            "adapter_id": command.adapter_id,
            "adapter_tier": str(identity.get("adapter_tier", "manual_handoff")),
            "flow_kind": flow_kind,
            "execution_id": execution_id,
            "continuation_id": continuation_id,
            "event_source": event_source,
        }
        timeline.append(
            task_id,
            "adapter_posture",
            {
                **base_payload,
                "unsupported_capabilities": [str(item) for item in unsupported_capabilities if isinstance(item, str)],
            },
        )
        for path in file_changes:
            timeline.append(task_id, "adapter_file_change", {**base_payload, "path": path})
        for tool_call in tool_calls:
            timeline.append(task_id, "adapter_tool_call", {**base_payload, **tool_call})
        for artifact_ref in gate_runs:
            timeline.append(task_id, "adapter_gate_run", {**base_payload, "artifact_ref": artifact_ref})
        for approval_id in approvals:
            if approval_id:
                timeline.append(task_id, "adapter_approval_event", {**base_payload, "approval_id": approval_id})
        for handoff_ref in handoff_refs:
            timeline.append(task_id, "adapter_handoff", {**base_payload, "handoff_ref": handoff_ref})
        for capability in unsupported_capabilities:
            timeline.append(
                task_id,
                "adapter_unsupported_event",
                {
                    **base_payload,
                    "capability": capability,
                    "reason": "unsupported capability recorded by adapter posture",
                },
            )
        for raw_event in unsupported_events:
            if not isinstance(raw_event, dict):
                continue
            timeline.append(
                task_id,
                "adapter_unsupported_event",
                {
                    **base_payload,
                    "capability": raw_event.get("capability"),
                    "event_type": raw_event.get("event_type"),
                    "reason": raw_event.get("reason") or "unsupported adapter event",
                    "raw_event": raw_event,
                },
            )
    summary = summarize_adapter_evidence(task_id, timeline)
    events = [
        {
            "task_id": event.task_id,
            "event_type": event.event_type,
            "payload": event.payload,
            "created_at": event.created_at,
        }
        for event in timeline.for_task(task_id)
    ]
    artifact = artifact_store.write_json(
        task_id=task_id,
        run_id=run_id,
        kind="evidence",
        label="adapter-events",
        payload={
            "task_id": task_id,
            "run_id": run_id,
            "execution_id": execution_id,
            "continuation_id": continuation_id,
            "session_identity": identity,
            "flow_kind": flow_kind,
            "event_source": event_source,
            "events": events,
            "summary": asdict(summary),
        },
    )
    return artifact.relative_path, asdict(summary)


def _run_id_from_payload(payload: dict) -> str:
    value = payload.get("run_id")
    if isinstance(value, str) and value.strip():
        return value.strip()
    return "session-bridge-request"


def _verification_cwd(*, repo_root: Path, attachment_root: str | Path | None) -> Path:
    if attachment_root is None:
        return repo_root
    return Path(attachment_root)


def _verification_artifact_root(
    *,
    task_root: Path,
    attachment_runtime_state_root: str | Path | None,
) -> Path:
    if attachment_runtime_state_root is not None:
        return Path(attachment_runtime_state_root)
    return task_root.parent / "artifacts"


def _approval_record_ref(
    *,
    attachment_runtime_state_root: str | Path | None,
    approval_id: str | None,
) -> str | None:
    if attachment_runtime_state_root is None or approval_id is None:
        return None
    approval_path = Path(attachment_runtime_state_root) / "approvals" / f"{approval_id}.json"
    return approval_path.as_posix()


def _tool_approval_id(command: SessionBridgeCommand) -> str:
    explicit = _payload_optional_string(command.payload, "approval_id")
    if explicit is not None:
        return explicit
    digest = hashlib.sha1(
        f"{command.task_id}:{_payload_required_string(command.payload, 'tool_name')}:{_payload_required_string(command.payload, 'command')}".encode(
            "utf-8"
        )
    ).hexdigest()[:12]
    return f"approval-tool-{digest}"


def _persist_tool_approval_request(
    *,
    runtime_state_root: Path,
    approval_id: str,
    task_id: str,
    tool_name: str,
    command_text: str,
    tier: str,
    rollback_reference: str,
    session_identity: dict | None = None,
) -> str:
    approvals_root = runtime_state_root / "approvals"
    approvals_root.mkdir(parents=True, exist_ok=True)
    record_path = approvals_root / f"{approval_id}.json"
    payload = {
        "approval_id": approval_id,
        "task_id": task_id,
        "tool_name": tool_name,
        "target_path": command_text,
        "tier": tier,
        "reason": f"{tier} governed tool execution requires approval",
        "status": "pending",
        "decided_by": None,
        "requested_at": "now",
        "rollback_reference": rollback_reference,
    }
    if session_identity is not None:
        payload["session_identity"] = dict(session_identity)
        for field_name in ("session_id", "resume_id", "continuation_id"):
            value = session_identity.get(field_name)
            if isinstance(value, str) and value.strip():
                payload[field_name] = value.strip()
    record_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return record_path.as_posix()


def _tool_approval_status(
    *,
    attachment_runtime_state_root: str | Path | None,
    approval_id: str | None,
) -> str:
    if approval_id is None or attachment_runtime_state_root is None:
        return "missing"
    approval_path = Path(attachment_runtime_state_root) / "approvals" / f"{approval_id}.json"
    if not approval_path.exists():
        return "missing"
    status = json.loads(approval_path.read_text(encoding="utf-8")).get("status")
    if not isinstance(status, str) or not status.strip():
        return "missing"
    normalized = status.strip().lower()
    if normalized == "approved":
        return "approved"
    if normalized == "rejected":
        return "rejected"
    return "pending"


def _load_approval_record(
    *,
    attachment_runtime_state_root: str | Path | None,
    approval_id: str | None,
) -> dict | None:
    if attachment_runtime_state_root is None or approval_id is None:
        return None
    approval_path = Path(attachment_runtime_state_root) / "approvals" / f"{approval_id}.json"
    if not approval_path.exists():
        return None
    try:
        payload = json.loads(approval_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def _approval_session_identity(
    *,
    attachment_runtime_state_root: str | Path | None,
    approval_id: str | None,
) -> dict | None:
    record = _load_approval_record(
        attachment_runtime_state_root=attachment_runtime_state_root,
        approval_id=approval_id,
    )
    if record is None:
        return None
    payload = record.get("session_identity")
    if isinstance(payload, dict):
        return dict(payload)
    return None


def _persist_approval_session_identity(
    *,
    attachment_runtime_state_root: str | Path | None,
    approval_id: str | None,
    session_identity: dict,
) -> None:
    if attachment_runtime_state_root is None or approval_id is None:
        return
    record = _load_approval_record(
        attachment_runtime_state_root=attachment_runtime_state_root,
        approval_id=approval_id,
    )
    if record is None:
        return
    record["session_identity"] = dict(session_identity)
    for field_name in ("session_id", "resume_id", "continuation_id"):
        value = session_identity.get(field_name)
        if isinstance(value, str) and value.strip():
            record[field_name] = value.strip()
    approval_path = Path(attachment_runtime_state_root) / "approvals" / f"{approval_id}.json"
    approval_path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")


def _session_identity(
    command: SessionBridgeCommand,
    *,
    continuation_id: str | None = None,
    approval_id: str | None = None,
    attachment_runtime_state_root: str | Path | None = None,
) -> dict:
    identity: dict[str, object] = {"adapter_id": command.adapter_id}
    session_id = _payload_optional_string(command.payload, "session_id")
    resume_id = _payload_optional_string(command.payload, "resume_id")
    approval_identity = _approval_session_identity(
        attachment_runtime_state_root=attachment_runtime_state_root,
        approval_id=approval_id,
    )
    approval_continuation = None
    if approval_identity is not None:
        if session_id is None:
            session_id = _payload_optional_string(approval_identity, "session_id")
        if resume_id is None:
            resume_id = _payload_optional_string(approval_identity, "resume_id")
        approval_continuation = _payload_optional_string(approval_identity, "continuation_id")

    if command.adapter_id == "codex-cli":
        handshake_payload = dict(command.payload)
        if session_id is not None and "session_id" not in handshake_payload:
            handshake_payload["session_id"] = session_id
        if resume_id is not None and "resume_id" not in handshake_payload:
            handshake_payload["resume_id"] = resume_id
        if approval_continuation is not None and continuation_id is None and "continuation_id" not in handshake_payload:
            handshake_payload["continuation_id"] = approval_continuation
        handshake = handshake_codex_session(
            task_id=command.task_id,
            command_id=command.command_id,
            payload=handshake_payload,
            continuation_id=continuation_id or approval_continuation,
        )
        session_id = session_id or handshake.session_id
        resume_id = resume_id or handshake.resume_id
        identity["adapter_tier"] = handshake.adapter_tier
        identity["flow_kind"] = handshake.flow_kind
        identity["live_attach_available"] = handshake.live_attach_available
        identity["unsupported_capabilities"] = handshake.unsupported_capabilities
        identity["posture_reason"] = handshake.posture_reason
        identity["continuation_id"] = handshake.continuation_id
    else:
        identity.setdefault("adapter_tier", "manual_handoff")
        identity.setdefault("flow_kind", "manual_handoff")
        identity.setdefault(
            "posture_reason",
            "non-codex adapter uses generic fallback posture until live host conformance is promoted",
        )
        identity.setdefault("unsupported_capabilities", [])

    if session_id is not None:
        identity["session_id"] = session_id
    if resume_id is not None:
        identity["resume_id"] = resume_id
    if continuation_id is None and approval_continuation is not None:
        continuation_id = approval_continuation
    if continuation_id is not None:
        identity["continuation_id"] = continuation_id
    return identity


def _write_write_flow_refs(
    *,
    task_id: str,
    execution_id: str,
    runtime_state_root: Path,
    payload: dict,
) -> tuple[str, str]:
    artifact_store = LocalArtifactStore(runtime_state_root)
    handoff_artifact = artifact_store.write_json(
        task_id=task_id,
        run_id=execution_id,
        kind="handoff",
        label="write-flow",
        payload=payload,
    )
    replay_artifact = artifact_store.write_json(
        task_id=task_id,
        run_id=execution_id,
        kind="replay",
        label="write-flow",
        payload=payload,
    )
    return handoff_artifact.relative_path, replay_artifact.relative_path


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
    except OSError:
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


def _execution_id(
    command: SessionBridgeCommand,
    *,
    run_id: str | None = None,
    approval_id: str | None = None,
) -> str:
    explicit = _payload_optional_string(command.payload, "execution_id")
    if explicit is not None:
        return explicit
    if run_id is not None:
        return f"{command.task_id}:{run_id}"
    if approval_id is not None:
        return f"{command.task_id}:approval:{approval_id}"

    payload_run_id = _payload_optional_string(command.payload, "run_id")
    if payload_run_id is not None:
        return f"{command.task_id}:{payload_run_id}"
    payload_approval_id = _payload_optional_string(command.payload, "approval_id")
    if payload_approval_id is not None:
        return f"{command.task_id}:approval:{payload_approval_id}"

    tool_name = _payload_optional_string(command.payload, "tool_name")
    target_path = _payload_optional_string(command.payload, "target_path")
    if tool_name is not None and target_path is not None:
        digest = hashlib.sha1(f"{tool_name}:{target_path}".encode("utf-8")).hexdigest()[:12]
        return f"{command.task_id}:write:{digest}"

    return f"{command.task_id}:{command.command_id}"


def _continuation_id(
    command: SessionBridgeCommand,
    *,
    run_id: str | None = None,
    approval_id: str | None = None,
    execution_id: str | None = None,
) -> str:
    explicit = _payload_optional_string(command.payload, "continuation_id")
    if explicit is not None:
        return explicit
    if run_id is not None:
        return f"{command.task_id}:{run_id}"
    if approval_id is not None:
        return f"{command.task_id}:approval:{approval_id}"
    if execution_id is not None:
        return execution_id
    return _execution_id(command)


def _payload_optional_bool(payload: dict, field_name: str) -> bool:
    value = payload.get(field_name)
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    msg = f"{field_name} must be a boolean"
    raise ValueError(msg)


def _execute_gate_at_root(command: str, *, cwd: Path) -> tuple[int, str]:
    completed = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=cwd,
        check=False,
    )
    output = "\n".join(part for part in [completed.stdout, completed.stderr] if part).strip()
    return completed.returncode, output


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
