"""Append-only in-memory evidence timeline primitives."""

from dataclasses import dataclass, field
from datetime import UTC, datetime

from governed_ai_coding_runtime_contracts.verification_runner import VerificationArtifact

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


@dataclass(frozen=True, slots=True)
class AdapterEvidenceSummary:
    task_id: str
    file_change_count: int
    tool_call_count: int
    gate_run_count: int
    approval_event_count: int
    handoff_ref_count: int


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


def summarize_adapter_evidence(task_id: str, timeline: EvidenceTimeline) -> AdapterEvidenceSummary:
    events = timeline.for_task(task_id)
    return AdapterEvidenceSummary(
        task_id=task_id,
        file_change_count=_count_events(events, "adapter_file_change"),
        tool_call_count=_count_events(events, "adapter_tool_call"),
        gate_run_count=_count_events(events, "adapter_gate_run"),
        approval_event_count=_count_events(events, "adapter_approval_event"),
        handoff_ref_count=_count_events(events, "adapter_handoff"),
    )


def build_evidence_bundle(
    *,
    task_id: str,
    repo_id: str,
    goal: str,
    acceptance_criteria: list[str],
    verification_artifact: VerificationArtifact,
    rollback_ref: str,
    final_status: str,
    final_summary: str,
    artifact_refs: list[str],
    replay_case_ref: str | None = None,
    failure_signature: str | None = None,
    trial_feedback: dict | None = None,
) -> dict:
    created_at = datetime.now(UTC).isoformat()
    verification_results = [
        {
            "gate_level": verification_artifact.mode,
            "status": _verification_status(result),
            "artifact_ref": verification_artifact.result_artifact_refs.get(gate_id, ""),
        }
        for gate_id, result in verification_artifact.results.items()
    ]
    return {
        "task_id": task_id,
        "repo_id": repo_id,
        "goal": goal,
        "non_goals": [],
        "acceptance_criteria": acceptance_criteria,
        "assumptions": [],
        "commands_run": [],
        "tool_calls": [],
        "files_changed": [],
        "approvals": [],
        "required_evidence": [
            {
                "kind": "runtime_artifacts",
                "status": "present" if artifact_refs else "missing_mandatory",
                "artifact_ref": artifact_refs[0] if artifact_refs else "",
            }
        ],
        "verification_results": verification_results,
        "rollback_ref": rollback_ref,
        "final_outcome": {
            "status": final_status,
            "summary": final_summary,
        },
        "open_questions": [],
        "created_at": created_at,
        "completed_at": created_at,
        "failure_signature": failure_signature,
        "replay_case_ref": replay_case_ref,
        "trial_feedback": trial_feedback,
    }


def _verification_status(result: str) -> str:
    return {
        "pass": "passed",
        "fail": "failed",
        "advisory": "advisory",
        "not_run": "skipped_not_applicable",
    }.get(result, "skipped_not_applicable")


def _count_events(events: list[EvidenceEvent], event_type: str) -> int:
    return sum(1 for event in events if event.event_type == event_type)
