"""Attached target-repo write approval and execution bridge."""

from dataclasses import dataclass
import json
from pathlib import Path

from governed_ai_coding_runtime_contracts.artifact_store import LocalArtifactStore
from governed_ai_coding_runtime_contracts.attached_write_governance import govern_attached_write_request
from governed_ai_coding_runtime_contracts.policy_decision import PolicyDecision, build_policy_decision
from governed_ai_coding_runtime_contracts.repo_attachment import validate_light_pack
from governed_ai_coding_runtime_contracts.repo_profile import load_repo_profile
from governed_ai_coding_runtime_contracts.workspace import allocate_workspace, validate_write_path
from governed_ai_coding_runtime_contracts.write_policy import resolve_write_policy
from governed_ai_coding_runtime_contracts.write_tool_runner import policy_decision_from_write_denial


_APPROVALS_DIR = "approvals"
_SUPPORTED_WRITE_TOOLS = {"write_file", "append_file"}
_SUPPORTED_TIERS = {"low", "medium", "high"}


@dataclass(frozen=True, slots=True)
class AttachedApprovalDecisionResult:
    approval_id: str
    status: str
    decided_by: str
    reason: str
    approval_record_ref: str


@dataclass(frozen=True, slots=True)
class AttachedWriteExecutionResult:
    repo_id: str
    binding_id: str
    task_id: str
    target_path: str
    write_tier: str
    execution_status: str
    policy_decision: PolicyDecision
    artifact_ref: str | None = None
    approval_id: str | None = None
    approval_status: str | None = None
    bytes_written: int | None = None
    reason: str | None = None


def decide_attached_write_request(
    *,
    attachment_runtime_state_root: str | Path,
    approval_id: str,
    decision: str,
    decided_by: str,
) -> AttachedApprovalDecisionResult:
    normalized_decision = _required_string(decision, "decision").lower()
    if normalized_decision not in {"approve", "reject"}:
        msg = f"unsupported decision: {decision}"
        raise ValueError(msg)

    normalized_decided_by = _required_string(decided_by, "decided_by")
    approval_path = _approval_record_path(Path(attachment_runtime_state_root), approval_id)
    if not approval_path.exists():
        msg = f"approval request not found: {approval_id}"
        raise ValueError(msg)

    record = json.loads(approval_path.read_text(encoding="utf-8"))
    current_status = _required_string(record.get("status"), "status")
    if current_status != "pending":
        msg = f"approval is already terminal: {approval_id}"
        raise ValueError(msg)

    new_status = "approved" if normalized_decision == "approve" else "rejected"
    record["status"] = new_status
    record["decided_by"] = normalized_decided_by
    approval_path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")

    return AttachedApprovalDecisionResult(
        approval_id=approval_id,
        status=new_status,
        decided_by=normalized_decided_by,
        reason=_required_string(record.get("reason"), "reason"),
        approval_record_ref=approval_path.as_posix(),
    )


def execute_attached_write_request(
    *,
    attachment_root: str | Path,
    attachment_runtime_state_root: str | Path,
    task_id: str,
    tool_name: str,
    target_path: str,
    tier: str,
    rollback_reference: str,
    content: str,
    approval_id: str | None = None,
) -> AttachedWriteExecutionResult:
    attachment_root_path = Path(attachment_root)
    runtime_state_root_path = Path(attachment_runtime_state_root)
    attachment = validate_light_pack(
        target_repo_root=str(attachment_root_path),
        light_pack_path=str(attachment_root_path / ".governed-ai" / "light-pack.json"),
        runtime_state_root=str(runtime_state_root_path),
    )
    profile = load_repo_profile(attachment.repo_profile_path)

    try:
        normalized_tool_name = _required_string(tool_name, "tool_name")
        if normalized_tool_name not in _SUPPORTED_WRITE_TOOLS:
            msg = f"unsupported write execution tool_name: {normalized_tool_name}"
            raise ValueError(msg)
        normalized_target_path = _required_string(target_path, "target_path")
        normalized_task_id = _required_string(task_id, "task_id")
        normalized_tier = _required_string(tier, "tier")
        if normalized_tier not in _SUPPORTED_TIERS:
            msg = f"unsupported tier: {normalized_tier}"
            raise ValueError(msg)
        normalized_rollback_reference = _required_string(rollback_reference, "rollback_reference")
    except ValueError as exc:
        denied = policy_decision_from_write_denial(
            task_id=task_id,
            tool_name=tool_name,
            target_path=target_path,
            tier=tier,
            reason=str(exc),
        )
        return AttachedWriteExecutionResult(
            repo_id=profile.repo_id,
            binding_id=attachment.binding.binding_id,
            task_id=task_id,
            target_path=target_path,
            write_tier=tier,
            execution_status="denied",
            policy_decision=denied,
            reason=str(exc),
        )

    allocation = allocate_workspace(normalized_task_id, profile)
    try:
        validate_write_path(allocation, normalized_target_path)
    except ValueError as exc:
        denied = policy_decision_from_write_denial(
            task_id=normalized_task_id,
            tool_name=normalized_tool_name,
            target_path=normalized_target_path,
            tier=normalized_tier,
            reason=str(exc),
        )
        return AttachedWriteExecutionResult(
            repo_id=profile.repo_id,
            binding_id=attachment.binding.binding_id,
            task_id=normalized_task_id,
            target_path=normalized_target_path,
            write_tier=normalized_tier,
            execution_status="denied",
            policy_decision=denied,
            reason=str(exc),
        )

    write_policy = resolve_write_policy(profile)
    if write_policy.requires_approval(normalized_tier):
        try:
            approval_check = _require_approved_request(
                runtime_state_root=runtime_state_root_path,
                approval_id=approval_id,
                task_id=normalized_task_id,
                tool_name=normalized_tool_name,
                target_path=normalized_target_path,
                tier=normalized_tier,
            )
        except ValueError as exc:
            denied = policy_decision_from_write_denial(
                task_id=normalized_task_id,
                tool_name=normalized_tool_name,
                target_path=normalized_target_path,
                tier=normalized_tier,
                reason=str(exc),
            )
            return AttachedWriteExecutionResult(
                repo_id=profile.repo_id,
                binding_id=attachment.binding.binding_id,
                task_id=normalized_task_id,
                target_path=normalized_target_path,
                write_tier=normalized_tier,
                execution_status="denied",
                policy_decision=denied,
                approval_id=approval_id,
                reason=str(exc),
            )
        if approval_check["status"] == "rejected":
            denied = policy_decision_from_write_denial(
                task_id=normalized_task_id,
                tool_name=normalized_tool_name,
                target_path=normalized_target_path,
                tier=normalized_tier,
                reason="approval request was rejected",
            )
            return AttachedWriteExecutionResult(
                repo_id=profile.repo_id,
                binding_id=attachment.binding.binding_id,
                task_id=normalized_task_id,
                target_path=normalized_target_path,
                write_tier=normalized_tier,
                execution_status="denied",
                policy_decision=denied,
                approval_id=approval_id,
                approval_status="rejected",
                reason="approval_rejected",
            )
        if approval_check["status"] != "approved":
            governance = govern_attached_write_request(
                attachment_root=attachment_root_path,
                attachment_runtime_state_root=runtime_state_root_path,
                task_id=normalized_task_id,
                tool_name=normalized_tool_name,
                target_path=normalized_target_path,
                tier=normalized_tier,
                rollback_reference=normalized_rollback_reference,
            )
            return AttachedWriteExecutionResult(
                repo_id=profile.repo_id,
                binding_id=attachment.binding.binding_id,
                task_id=normalized_task_id,
                target_path=normalized_target_path,
                write_tier=normalized_tier,
                execution_status="blocked",
                policy_decision=governance.policy_decision,
                approval_id=governance.approval_id,
                approval_status="pending",
                reason="approval_required",
            )

    target_abs_path = attachment_root_path / normalized_target_path
    target_abs_path.parent.mkdir(parents=True, exist_ok=True)
    if normalized_tool_name == "write_file":
        target_abs_path.write_text(content, encoding="utf-8")
    else:
        with target_abs_path.open("a", encoding="utf-8") as stream:
            stream.write(content)

    artifact_store = LocalArtifactStore(runtime_state_root_path)
    artifact = artifact_store.write_json(
        task_id=normalized_task_id,
        run_id="write-execution",
        kind="execution-write",
        label=normalized_target_path,
        payload={
            "tool_name": normalized_tool_name,
            "target_path": normalized_target_path,
            "tier": normalized_tier,
            "rollback_reference": normalized_rollback_reference,
            "bytes_written": len(content.encode("utf-8")),
        },
    )
    decision = build_policy_decision(
        task_id=normalized_task_id,
        action_id=f"write:{normalized_tool_name}:{normalized_target_path}",
        risk_tier=normalized_tier,
        subject=f"write_execution:{normalized_target_path}",
        status="allow",
        decision_basis=["write request executed after policy checks"],
        evidence_ref=artifact.relative_path,
    )
    approved_status = "approved" if approval_id else None
    return AttachedWriteExecutionResult(
        repo_id=profile.repo_id,
        binding_id=attachment.binding.binding_id,
        task_id=normalized_task_id,
        target_path=normalized_target_path,
        write_tier=normalized_tier,
        execution_status="executed",
        policy_decision=decision,
        artifact_ref=artifact.relative_path,
        approval_id=approval_id,
        approval_status=approved_status,
        bytes_written=len(content.encode("utf-8")),
    )


def _require_approved_request(
    *,
    runtime_state_root: Path,
    approval_id: str | None,
    task_id: str,
    tool_name: str,
    target_path: str,
    tier: str,
) -> dict:
    if not approval_id:
        return {"status": "pending"}
    approval_path = _approval_record_path(runtime_state_root, approval_id)
    if not approval_path.exists():
        return {"status": "pending"}
    record = json.loads(approval_path.read_text(encoding="utf-8"))
    expected = {
        "task_id": task_id,
        "tool_name": tool_name,
        "target_path": target_path,
        "tier": tier,
    }
    for field_name, expected_value in expected.items():
        if _required_string(record.get(field_name), field_name) != expected_value:
            msg = f"approval request mismatch on {field_name}"
            raise ValueError(msg)
    return {"status": _required_string(record.get("status"), "status")}


def _approval_record_path(runtime_state_root: Path, approval_id: str) -> Path:
    normalized_approval_id = _required_string(approval_id, "approval_id")
    return runtime_state_root / _APPROVALS_DIR / f"{normalized_approval_id}.json"


def _required_string(value: str | None, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        msg = f"{field_name} is required"
        raise ValueError(msg)
    return value.strip()
