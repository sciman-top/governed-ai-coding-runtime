"""Runtime read model for CLI-first operator visibility."""

from dataclasses import dataclass, field
from pathlib import Path

from governed_ai_coding_runtime_contracts.maintenance_policy import (
    MaintenancePolicyStatus,
    load_maintenance_policy_status,
)
from governed_ai_coding_runtime_contracts.repo_attachment import inspect_attachment_posture
from governed_ai_coding_runtime_contracts.task_store import FileTaskStore, TaskRecord


@dataclass(frozen=True, slots=True)
class RuntimeTaskStatus:
    task_id: str
    current_state: str
    goal: str
    rollback_ref: str | None
    active_run_id: str | None
    workspace_root: str | None
    approval_ids: list[str]
    artifact_refs: list[str]
    evidence_refs: list[str]
    verification_refs: list[str]


@dataclass(frozen=True, slots=True)
class RuntimeAttachmentStatus:
    repo_id: str | None
    binding_id: str | None
    binding_state: str
    light_pack_path: str
    adapter_preference: str | None
    gate_profile: str | None
    reason: str | None


@dataclass(frozen=True, slots=True)
class RuntimeSnapshot:
    total_tasks: int
    maintenance: MaintenancePolicyStatus
    tasks: list[RuntimeTaskStatus]
    attachments: list[RuntimeAttachmentStatus] = field(default_factory=list)


class RuntimeStatusStore:
    def __init__(
        self,
        task_root: Path,
        repo_root: Path | None = None,
        attachment_roots: list[Path] | None = None,
        attachment_runtime_state_root: Path | None = None,
    ) -> None:
        self._task_root = task_root
        self._repo_root = repo_root or task_root.parent.parent
        self._attachment_roots = attachment_roots or []
        self._attachment_runtime_state_root = attachment_runtime_state_root

    def snapshot(self) -> RuntimeSnapshot:
        maintenance = load_maintenance_policy_status(self._repo_root)
        attachments = self._attachment_statuses()
        if not self._task_root.exists():
            return RuntimeSnapshot(total_tasks=0, maintenance=maintenance, tasks=[], attachments=attachments)

        store = FileTaskStore(self._task_root)
        tasks = [
            self._to_status(store.load(path.stem))
            for path in sorted(self._task_root.glob("*.json"))
        ]
        return RuntimeSnapshot(total_tasks=len(tasks), maintenance=maintenance, tasks=tasks, attachments=attachments)

    def _to_status(self, record: TaskRecord) -> RuntimeTaskStatus:
        active_run = None
        if record.active_run_id:
            for item in record.run_history:
                if item.run_id == record.active_run_id:
                    active_run = item
                    break
        return RuntimeTaskStatus(
            task_id=record.task_id,
            current_state=record.current_state,
            goal=record.task.goal,
            rollback_ref=record.rollback_ref,
            active_run_id=record.active_run_id,
            workspace_root=record.workspace_root,
            approval_ids=active_run.approval_ids if active_run else [],
            artifact_refs=active_run.artifact_refs if active_run else [],
            evidence_refs=active_run.evidence_refs if active_run else [],
            verification_refs=active_run.verification_refs if active_run else [],
        )

    def _attachment_statuses(self) -> list[RuntimeAttachmentStatus]:
        statuses: list[RuntimeAttachmentStatus] = []
        for attachment_root in self._attachment_roots:
            runtime_state_root = self._attachment_runtime_state_root or self._task_root.parent / "attachments" / attachment_root.name
            posture = inspect_attachment_posture(
                target_repo_root=str(attachment_root),
                runtime_state_root=str(runtime_state_root),
            )
            statuses.append(
                RuntimeAttachmentStatus(
                    repo_id=posture.repo_id,
                    binding_id=posture.binding_id,
                    binding_state=posture.binding_state,
                    light_pack_path=posture.light_pack_path,
                    adapter_preference=posture.adapter_preference,
                    gate_profile=posture.gate_profile,
                    reason=posture.reason,
                )
            )
        return statuses
