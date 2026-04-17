"""Deterministic workflow helpers built on the task intake state validator."""

from governed_ai_coding_runtime_contracts.task_intake import validate_transition
from governed_ai_coding_runtime_contracts.task_store import FileTaskStore, TaskRecord


def transition_task(
    record: TaskRecord,
    next_state: str,
    *,
    actor_type: str,
    actor_id: str,
    reason: str,
    evidence_ref: str = "",
    store: FileTaskStore | None = None,
) -> TaskRecord:
    validate_transition(record.current_state, next_state)
    updated = _clone_record(record)
    updated.current_state = next_state
    if next_state != "paused":
        updated.resume_state = None
    transition = (store.append_transition if store else _append_transition_without_store)
    return transition(
        updated,
        previous_state=record.current_state,
        next_state=next_state,
        actor_type=actor_type,
        actor_id=actor_id,
        reason=reason,
        evidence_ref=evidence_ref,
    )


def pause_task(record: TaskRecord, *, actor_type: str, actor_id: str, reason: str) -> TaskRecord:
    updated = _clone_record(record)
    updated.resume_state = record.current_state
    return transition_task(
        updated,
        "paused",
        actor_type=actor_type,
        actor_id=actor_id,
        reason=reason,
    )


def resume_task(record: TaskRecord, *, actor_type: str, actor_id: str, reason: str) -> TaskRecord:
    if record.current_state != "paused" or not record.resume_state:
        msg = "task is not paused"
        raise ValueError(msg)
    return transition_task(
        record,
        record.resume_state,
        actor_type=actor_type,
        actor_id=actor_id,
        reason=reason,
    )


def fail_task(
    record: TaskRecord,
    *,
    actor_type: str,
    actor_id: str,
    reason: str,
    timeout_at: str | None = None,
) -> TaskRecord:
    updated = transition_task(
        record,
        "failed",
        actor_type=actor_type,
        actor_id=actor_id,
        reason=reason,
    )
    updated.last_failure_reason = reason
    updated.timeout_at = timeout_at
    return updated


def retry_task(record: TaskRecord, *, actor_type: str, actor_id: str, reason: str) -> TaskRecord:
    updated = transition_task(
        record,
        "planned",
        actor_type=actor_type,
        actor_id=actor_id,
        reason=reason,
    )
    updated.retry_count += 1
    return updated


def _clone_record(record: TaskRecord) -> TaskRecord:
    return TaskRecord.from_dict(record.to_dict())


def _append_transition_without_store(
    record: TaskRecord,
    *,
    previous_state: str,
    next_state: str,
    actor_type: str,
    actor_id: str,
    reason: str,
    evidence_ref: str = "",
) -> TaskRecord:
    store = FileTaskStore.__new__(FileTaskStore)
    return FileTaskStore.append_transition(
        store,
        record,
        previous_state=previous_state,
        next_state=next_state,
        actor_type=actor_type,
        actor_id=actor_id,
        reason=reason,
        evidence_ref=evidence_ref,
    )
