"""Runtime read model for CLI-first operator visibility."""

from dataclasses import dataclass
from pathlib import Path

from governed_ai_coding_runtime_contracts.maintenance_policy import (
    MaintenancePolicyStatus,
    load_maintenance_policy_status,
)
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
class RuntimeSnapshot:
    total_tasks: int
    maintenance: MaintenancePolicyStatus
    tasks: list[RuntimeTaskStatus]


class RuntimeStatusStore:
    def __init__(self, task_root: Path, repo_root: Path | None = None) -> None:
        self._task_root = task_root
        self._repo_root = repo_root or task_root.parent.parent

    def snapshot(self) -> RuntimeSnapshot:
        maintenance = load_maintenance_policy_status(self._repo_root)
        if not self._task_root.exists():
            return RuntimeSnapshot(total_tasks=0, maintenance=maintenance, tasks=[])

        store = FileTaskStore(self._task_root)
        tasks = [
            self._to_status(store.load(path.stem))
            for path in sorted(self._task_root.glob("*.json"))
        ]
        return RuntimeSnapshot(total_tasks=len(tasks), maintenance=maintenance, tasks=tasks)

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
