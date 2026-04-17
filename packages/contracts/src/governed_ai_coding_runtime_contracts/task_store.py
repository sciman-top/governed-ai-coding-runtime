"""File-backed task persistence primitives for Foundation."""

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
import json
from pathlib import Path

from governed_ai_coding_runtime_contracts.task_intake import TaskIntake


@dataclass(frozen=True, slots=True)
class TaskTransitionRecord:
    previous_state: str
    next_state: str
    actor_type: str
    actor_id: str
    reason: str
    evidence_ref: str
    timestamp: str


@dataclass(slots=True)
class TaskRecord:
    task_id: str
    task: TaskIntake
    current_state: str
    transition_history: list[TaskTransitionRecord] = field(default_factory=list)
    retry_count: int = 0
    timeout_at: str | None = None
    last_failure_reason: str | None = None
    resume_state: str | None = None

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "task": asdict(self.task),
            "current_state": self.current_state,
            "transition_history": [asdict(item) for item in self.transition_history],
            "retry_count": self.retry_count,
            "timeout_at": self.timeout_at,
            "last_failure_reason": self.last_failure_reason,
            "resume_state": self.resume_state,
        }

    @classmethod
    def from_dict(cls, raw: dict) -> "TaskRecord":
        return cls(
            task_id=raw["task_id"],
            task=TaskIntake(**raw["task"]),
            current_state=raw["current_state"],
            transition_history=[TaskTransitionRecord(**item) for item in raw.get("transition_history", [])],
            retry_count=raw.get("retry_count", 0),
            timeout_at=raw.get("timeout_at"),
            last_failure_reason=raw.get("last_failure_reason"),
            resume_state=raw.get("resume_state"),
        )


class FileTaskStore:
    def __init__(self, root: Path) -> None:
        self._root = root
        self._root.mkdir(parents=True, exist_ok=True)

    def save(self, record: TaskRecord) -> Path:
        path = self._path_for(record.task_id)
        path.write_text(json.dumps(record.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        return path

    def load(self, task_id: str) -> TaskRecord:
        raw = json.loads(self._path_for(task_id).read_text(encoding="utf-8"))
        return TaskRecord.from_dict(raw)

    def append_transition(
        self,
        record: TaskRecord,
        *,
        previous_state: str,
        next_state: str,
        actor_type: str,
        actor_id: str,
        reason: str,
        evidence_ref: str = "",
    ) -> TaskRecord:
        updated = TaskRecord.from_dict(record.to_dict())
        updated.current_state = next_state
        updated.transition_history.append(
            TaskTransitionRecord(
                previous_state=previous_state,
                next_state=next_state,
                actor_type=actor_type,
                actor_id=actor_id,
                reason=reason,
                evidence_ref=evidence_ref,
                timestamp=datetime.now(UTC).isoformat(),
            )
        )
        return updated

    def _path_for(self, task_id: str) -> Path:
        return self._root / f"{task_id}.json"
