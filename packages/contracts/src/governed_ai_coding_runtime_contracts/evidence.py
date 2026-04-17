"""Append-only in-memory evidence timeline primitives."""

from dataclasses import dataclass, field
from datetime import UTC, datetime

_MINIMUM_COMPLETION_FIELDS = [
    "task_id",
    "repo_id",
    "goal",
    "commands_run",
    "tool_calls",
    "files_changed",
    "approvals",
    "required_evidence",
    "verification_results",
    "rollback_ref",
    "final_outcome",
    "open_questions",
]


@dataclass(frozen=True, slots=True)
class EvidenceEvent:
    task_id: str
    event_type: str
    payload: dict
    created_at: str


@dataclass(frozen=True, slots=True)
class TaskOutput:
    task_id: str
    event_count: int
    latest_summary: str


@dataclass(frozen=True, slots=True)
class EvidenceBundleAssessment:
    ready_for_completion: bool
    missing_required_fields: list[str]
    advisory_findings: list[str]


@dataclass(slots=True)
class EvidenceTimeline:
    _events: list[EvidenceEvent] = field(default_factory=list)

    def append(self, task_id: str, event_type: str, payload: dict) -> EvidenceEvent:
        if not task_id.strip():
            msg = "task_id is required"
            raise ValueError(msg)
        if not event_type.strip():
            msg = "event_type is required"
            raise ValueError(msg)
        event = EvidenceEvent(
            task_id=task_id,
            event_type=event_type,
            payload=payload,
            created_at=datetime.now(UTC).isoformat(),
        )
        self._events.append(event)
        return event

    def for_task(self, task_id: str) -> list[EvidenceEvent]:
        return [event for event in self._events if event.task_id == task_id]


def build_task_output(task_id: str, timeline: EvidenceTimeline) -> TaskOutput:
    events = timeline.for_task(task_id)
    latest_summary = ""
    for event in reversed(events):
        summary = event.payload.get("summary")
        if isinstance(summary, str):
            latest_summary = summary
            break
    return TaskOutput(task_id=task_id, event_count=len(events), latest_summary=latest_summary)


def assess_evidence_bundle(bundle: dict) -> EvidenceBundleAssessment:
    missing_required_fields = [
        field_name
        for field_name in _MINIMUM_COMPLETION_FIELDS
        if field_name not in bundle
    ]
    advisory_findings: list[str] = []

    for result in bundle.get("verification_results", []):
        if result.get("status") == "advisory":
            advisory_findings.append(f"verification:{result.get('gate_level', 'unknown')}:advisory")

    return EvidenceBundleAssessment(
        ready_for_completion=len(missing_required_fields) == 0,
        missing_required_fields=missing_required_fields,
        advisory_findings=advisory_findings,
    )
