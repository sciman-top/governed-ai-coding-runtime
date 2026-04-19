"""Single-machine execution runtime and run orchestration primitives."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal, Protocol
from uuid import uuid4

from governed_ai_coding_runtime_contracts.task_store import FileTaskStore, TaskRecord, TaskRunRecord
from governed_ai_coding_runtime_contracts.workflow import fail_task, pause_task, transition_task
from governed_ai_coding_runtime_contracts.workspace import WorkspaceAllocation, allocate_workspace


WorkerOutcome = Literal["completed", "interrupted", "failed"]


@dataclass(frozen=True, slots=True)
class WorkerExecutionResult:
    outcome: WorkerOutcome
    summary: str
    evidence_refs: list[str] = field(default_factory=list)
    approval_ids: list[str] = field(default_factory=list)
    artifact_refs: list[str] = field(default_factory=list)
    verification_refs: list[str] = field(default_factory=list)
    rollback_ref: str | None = None
    failure_reason: str | None = None


@dataclass(frozen=True, slots=True)
class RunPreparation:
    record: TaskRecord
    run: TaskRunRecord
    workspace: WorkspaceAllocation


@dataclass(frozen=True, slots=True)
class GovernedRunContext:
    record: TaskRecord
    run: TaskRunRecord
    workspace: WorkspaceAllocation


class RuntimeWorker(Protocol):
    worker_id: str

    def execute(self, context: GovernedRunContext) -> WorkerExecutionResult: ...


class ExecutionRuntime:
    def __init__(
        self,
        store: FileTaskStore,
        *,
        actor_id: str = "execution-runtime",
        runtime_workspaces_root: str | None = None,
    ) -> None:
        self._store = store
        self._actor_id = actor_id
        self._runtime_workspaces_root = runtime_workspaces_root

    def prepare_run(self, task_id: str, repo_profile: object, *, worker_id: str = "local-worker") -> RunPreparation:
        record = self._store.load(task_id)
        if record.current_state != "planned":
            msg = f"task is not ready for execution: {record.current_state}"
            raise ValueError(msg)

        run_id = f"run-{uuid4().hex[:12]}"
        attempt_number = len(record.run_history) + 1
        attempt_id = f"{task_id}-attempt-{attempt_number}"
        workspace = allocate_workspace(
            task_id,
            repo_profile,
            run_id=run_id,
            attempt_id=attempt_id,
            runtime_workspaces_root=self._runtime_workspaces_root,
        )
        executing = transition_task(
            record,
            "executing",
            actor_type="system",
            actor_id=self._actor_id,
            reason="runtime execution started",
            store=self._store,
        )
        run = TaskRunRecord(
            run_id=run_id,
            attempt_id=attempt_id,
            worker_id=worker_id,
            status="executing",
            workspace_root=workspace.workspace_root,
            started_at=datetime.now(UTC).isoformat(),
        )
        executing.current_attempt_id = attempt_id
        executing.active_run_id = run_id
        executing.workspace_root = workspace.workspace_root
        executing.run_history.append(run)
        self._store.save(executing)
        return RunPreparation(record=executing, run=run, workspace=workspace)

    def finalize_run(self, task_id: str, result: WorkerExecutionResult) -> TaskRecord:
        record = self._store.load(task_id)
        run = self._active_run(record)
        updated_run = TaskRunRecord(
            run_id=run.run_id,
            attempt_id=run.attempt_id,
            worker_id=run.worker_id,
            status=_result_status(result),
            workspace_root=run.workspace_root,
            started_at=run.started_at,
            finished_at=datetime.now(UTC).isoformat(),
            summary=result.summary,
            evidence_refs=result.evidence_refs,
            approval_ids=result.approval_ids,
            artifact_refs=result.artifact_refs,
            verification_refs=result.verification_refs,
            rollback_ref=result.rollback_ref,
            failure_reason=result.failure_reason,
        )

        if result.outcome == "completed":
            next_record = transition_task(
                record,
                "verifying",
                actor_type="worker",
                actor_id=run.worker_id,
                reason=result.summary or "worker completed",
                evidence_ref=_first_ref(result.evidence_refs),
                store=self._store,
            )
            next_record.rollback_ref = result.rollback_ref
        elif result.outcome == "interrupted":
            next_record = pause_task(
                record,
                actor_type="worker",
                actor_id=run.worker_id,
                reason=result.summary or "worker interrupted",
            )
        else:
            next_record = fail_task(
                record,
                actor_type="worker",
                actor_id=run.worker_id,
                reason=result.failure_reason or result.summary or "worker failed",
            )

        next_record.current_attempt_id = updated_run.attempt_id
        next_record.active_run_id = updated_run.run_id
        next_record.workspace_root = updated_run.workspace_root
        next_record.rollback_ref = result.rollback_ref or next_record.rollback_ref
        next_record.run_history = [
            updated_run if item.run_id == updated_run.run_id else item
            for item in record.run_history
        ]
        self._store.save(next_record)
        return next_record

    def execute_task(self, task_id: str, repo_profile: object, worker: RuntimeWorker) -> TaskRecord:
        prepared = self.prepare_run(task_id, repo_profile, worker_id=worker.worker_id)
        result = worker.execute(
            GovernedRunContext(record=prepared.record, run=prepared.run, workspace=prepared.workspace)
        )
        return self.finalize_run(task_id, result)

    def _active_run(self, record: TaskRecord) -> TaskRunRecord:
        if not record.active_run_id:
            msg = "task has no active run"
            raise ValueError(msg)
        for item in record.run_history:
            if item.run_id == record.active_run_id:
                return item
        msg = f"active run missing from history: {record.active_run_id}"
        raise ValueError(msg)


def _first_ref(refs: list[str]) -> str:
    return refs[0] if refs else ""


def _result_status(result: WorkerExecutionResult) -> str:
    return {
        "completed": "completed",
        "interrupted": "interrupted",
        "failed": "failed",
    }[result.outcome]
