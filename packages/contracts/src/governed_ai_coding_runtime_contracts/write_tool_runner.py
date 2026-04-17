"""Write-side tool governance decisions."""

from dataclasses import dataclass
from typing import Literal

from governed_ai_coding_runtime_contracts.approval import ApprovalLedger
from governed_ai_coding_runtime_contracts.workspace import WorkspaceAllocation, validate_write_path
from governed_ai_coding_runtime_contracts.write_policy import WritePolicy


DecisionStatus = Literal["allowed", "paused"]


@dataclass(frozen=True, slots=True)
class WriteToolRequest:
    task_id: str
    tool_name: str
    target_path: str
    tier: str
    rollback_reference: str


@dataclass(frozen=True, slots=True)
class WriteGovernanceDecision:
    task_id: str
    tool_name: str
    target_path: str
    tier: str
    status: DecisionStatus
    rollback_reference: str
    approval_id: str | None = None
    task_state: str | None = None


def govern_write_request(
    request: WriteToolRequest,
    allocation: WorkspaceAllocation,
    policy: WritePolicy,
    approval_ledger: ApprovalLedger,
) -> WriteGovernanceDecision:
    _validate_request(request)
    validate_write_path(allocation, request.target_path)
    if request.tier in {"medium", "high"} and not request.rollback_reference.strip():
        msg = "medium and high tier writes require a rollback_reference"
        raise ValueError(msg)

    if policy.requires_approval(request.tier):
        approval = approval_ledger.create(
            task_id=request.task_id,
            requested_by=request.tool_name,
            tier=request.tier,
            reason=f"{request.tier} write requires approval for {request.target_path}",
        )
        interruption = approval_ledger.interruption_for(approval.approval_id)
        return WriteGovernanceDecision(
            task_id=request.task_id,
            tool_name=request.tool_name,
            target_path=request.target_path,
            tier=request.tier,
            status="paused",
            rollback_reference=request.rollback_reference,
            approval_id=approval.approval_id,
            task_state=interruption.task_state,
        )

    return WriteGovernanceDecision(
        task_id=request.task_id,
        tool_name=request.tool_name,
        target_path=request.target_path,
        tier=request.tier,
        status="allowed",
        rollback_reference=request.rollback_reference,
    )


def _validate_request(request: WriteToolRequest) -> None:
    for field_name in ("task_id", "tool_name", "target_path", "tier"):
        value = getattr(request, field_name)
        if not isinstance(value, str) or not value.strip():
            msg = f"{field_name} is required"
            raise ValueError(msg)
