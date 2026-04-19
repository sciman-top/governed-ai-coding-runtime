"""Attached target-repo write governance bridge."""

from dataclasses import dataclass
from datetime import UTC, datetime
import json
from pathlib import Path

from governed_ai_coding_runtime_contracts.approval import ApprovalLedger
from governed_ai_coding_runtime_contracts.policy_decision import PolicyDecision
from governed_ai_coding_runtime_contracts.repo_attachment import validate_light_pack
from governed_ai_coding_runtime_contracts.repo_profile import load_repo_profile
from governed_ai_coding_runtime_contracts.workspace import allocate_workspace
from governed_ai_coding_runtime_contracts.write_policy import resolve_write_policy
from governed_ai_coding_runtime_contracts.write_tool_runner import (
    WriteToolRequest,
    govern_write_request,
    policy_decision_from_write_denial,
    policy_decision_from_write_governance,
)


_APPROVALS_DIR = "approvals"


@dataclass(frozen=True, slots=True)
class AttachedWriteGovernanceResult:
    repo_id: str
    binding_id: str
    task_id: str
    target_path: str
    write_tier: str
    governance_status: str
    policy_decision: PolicyDecision
    approval_id: str | None = None
    task_state: str | None = None
    reason: str | None = None


def govern_attached_write_request(
    *,
    attachment_root: str | Path,
    attachment_runtime_state_root: str | Path,
    task_id: str,
    tool_name: str,
    target_path: str,
    tier: str,
    rollback_reference: str,
) -> AttachedWriteGovernanceResult:
    attachment_root_path = Path(attachment_root)
    runtime_state_root_path = Path(attachment_runtime_state_root)
    attachment = validate_light_pack(
        target_repo_root=str(attachment_root_path),
        light_pack_path=str(attachment_root_path / ".governed-ai" / "light-pack.json"),
        runtime_state_root=str(runtime_state_root_path),
    )
    profile = load_repo_profile(attachment.repo_profile_path)
    write_policy = resolve_write_policy(profile)
    approval_ledger = ApprovalLedger()
    allocation = allocate_workspace(task_id, profile)

    try:
        governance = govern_write_request(
            WriteToolRequest(
                task_id=task_id,
                tool_name=tool_name,
                target_path=target_path,
                tier=tier,
                rollback_reference=rollback_reference,
            ),
            allocation,
            write_policy,
            approval_ledger,
        )
    except ValueError as exc:
        denied = policy_decision_from_write_denial(
            task_id=task_id,
            tool_name=tool_name,
            target_path=target_path,
            tier=tier,
            reason=str(exc),
        )
        return AttachedWriteGovernanceResult(
            repo_id=profile.repo_id,
            binding_id=attachment.binding.binding_id,
            task_id=task_id,
            target_path=target_path,
            write_tier=tier,
            governance_status="denied",
            policy_decision=denied,
            reason=str(exc),
        )

    policy_decision = policy_decision_from_write_governance(governance)
    if governance.approval_id:
        _persist_approval_request(
            runtime_state_root=runtime_state_root_path,
            approval_id=governance.approval_id,
            task_id=task_id,
            tool_name=tool_name,
            target_path=target_path,
            tier=tier,
            reason=f"{tier} write requires approval for {target_path}",
        )
    return AttachedWriteGovernanceResult(
        repo_id=profile.repo_id,
        binding_id=attachment.binding.binding_id,
        task_id=task_id,
        target_path=target_path,
        write_tier=tier,
        governance_status=governance.status,
        policy_decision=policy_decision,
        approval_id=governance.approval_id,
        task_state=governance.task_state,
    )


def _persist_approval_request(
    *,
    runtime_state_root: Path,
    approval_id: str,
    task_id: str,
    tool_name: str,
    target_path: str,
    tier: str,
    reason: str,
) -> None:
    approvals_root = runtime_state_root / _APPROVALS_DIR
    approvals_root.mkdir(parents=True, exist_ok=True)
    record_path = approvals_root / f"{approval_id}.json"
    record = {
        "approval_id": approval_id,
        "task_id": task_id,
        "tool_name": tool_name,
        "target_path": target_path,
        "tier": tier,
        "reason": reason,
        "status": "pending",
        "decided_by": None,
        "requested_at": datetime.now(UTC).isoformat(),
        "decided_at": None,
    }
    record_path.write_text(
        json.dumps(record, indent=2, sort_keys=True),
        encoding="utf-8",
    )
