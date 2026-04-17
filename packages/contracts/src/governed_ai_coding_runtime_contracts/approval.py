"""Approval request state handling and audit primitives."""

from dataclasses import dataclass, replace
from typing import Literal
from uuid import uuid4


ApprovalStatus = Literal["pending", "approved", "rejected", "revoked", "timed_out"]


@dataclass(frozen=True, slots=True)
class ApprovalRequest:
    approval_id: str
    task_id: str
    requested_by: str
    tier: str
    reason: str
    status: ApprovalStatus
    decided_by: str | None = None


@dataclass(frozen=True, slots=True)
class ApprovalInterruption:
    approval_id: str
    task_id: str
    task_state: str
    reason: str


@dataclass(frozen=True, slots=True)
class ApprovalAuditEvent:
    approval_id: str
    task_id: str
    event_type: str
    actor: str
    status: ApprovalStatus


class ApprovalLedger:
    def __init__(self) -> None:
        self._requests: dict[str, ApprovalRequest] = {}
        self._events: list[ApprovalAuditEvent] = []

    def create(self, task_id: str, requested_by: str, tier: str, reason: str) -> ApprovalRequest:
        request = ApprovalRequest(
            approval_id=f"approval-{uuid4().hex}",
            task_id=_required_string(task_id, "task_id"),
            requested_by=_required_string(requested_by, "requested_by"),
            tier=_required_string(tier, "tier"),
            reason=_required_string(reason, "reason"),
            status="pending",
        )
        self._persist(request, "approval_created", request.requested_by)
        return request

    def approve(self, approval_id: str, decided_by: str) -> ApprovalRequest:
        return self._decide(approval_id, "approved", "approval_approved", decided_by)

    def reject(self, approval_id: str, decided_by: str) -> ApprovalRequest:
        return self._decide(approval_id, "rejected", "approval_rejected", decided_by)

    def revoke(self, approval_id: str, decided_by: str) -> ApprovalRequest:
        return self._decide(approval_id, "revoked", "approval_revoked", decided_by)

    def timeout(self, approval_id: str, decided_by: str = "system") -> ApprovalRequest:
        return self._decide(approval_id, "timed_out", "approval_timed_out", decided_by)

    def get(self, approval_id: str) -> ApprovalRequest:
        approval_id = _required_string(approval_id, "approval_id")
        if approval_id not in self._requests:
            msg = f"unknown approval_id: {approval_id}"
            raise ValueError(msg)
        return self._requests[approval_id]

    def interruption_for(self, approval_id: str) -> ApprovalInterruption:
        request = self.get(approval_id)
        if request.status != "pending":
            msg = f"approval is not pending: {approval_id}"
            raise ValueError(msg)
        return ApprovalInterruption(
            approval_id=request.approval_id,
            task_id=request.task_id,
            task_state="approval_pending",
            reason=request.reason,
        )

    def audit_trail(self, approval_id: str) -> list[ApprovalAuditEvent]:
        approval_id = _required_string(approval_id, "approval_id")
        return [event for event in self._events if event.approval_id == approval_id]

    def _decide(
        self,
        approval_id: str,
        status: ApprovalStatus,
        event_type: str,
        decided_by: str,
    ) -> ApprovalRequest:
        request = self.get(approval_id)
        if request.status != "pending":
            msg = f"approval is already terminal: {approval_id}"
            raise ValueError(msg)
        updated = replace(request, status=status, decided_by=_required_string(decided_by, "decided_by"))
        self._persist(updated, event_type, updated.decided_by)
        return updated

    def _persist(self, request: ApprovalRequest, event_type: str, actor: str) -> None:
        self._requests[request.approval_id] = request
        self._events.append(
            ApprovalAuditEvent(
                approval_id=request.approval_id,
                task_id=request.task_id,
                event_type=event_type,
                actor=actor,
                status=request.status,
            )
        )


def _required_string(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        msg = f"{field_name} is required"
        raise ValueError(msg)
    return value.strip()
