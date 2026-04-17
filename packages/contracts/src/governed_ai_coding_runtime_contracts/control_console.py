"""Minimal control-plane console facade."""

from dataclasses import dataclass

from governed_ai_coding_runtime_contracts.approval import ApprovalLedger, ApprovalRequest
from governed_ai_coding_runtime_contracts.evidence import EvidenceEvent, EvidenceTimeline


@dataclass(slots=True)
class ControlPlaneConsole:
    approval_ledger: ApprovalLedger
    evidence_timeline: EvidenceTimeline
    scope: str = "control_plane"

    def approve(self, approval_id: str, operator: str) -> ApprovalRequest:
        return self.approval_ledger.approve(approval_id, decided_by=operator)

    def reject(self, approval_id: str, operator: str) -> ApprovalRequest:
        return self.approval_ledger.reject(approval_id, decided_by=operator)

    def evidence_for_task(self, task_id: str) -> list[EvidenceEvent]:
        return self.evidence_timeline.for_task(task_id)
