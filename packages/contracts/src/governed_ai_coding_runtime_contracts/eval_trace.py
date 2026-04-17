"""Evaluation baseline and trace grading primitives."""

from dataclasses import dataclass
from typing import Any, Literal


OutcomeQuality = Literal["pass", "fail"]
TraceGrade = Literal["pass", "missing_evidence", "poor_outcome_quality"]


@dataclass(frozen=True, slots=True)
class EvalBaseline:
    repo_id: str
    required_suites: list[str]


@dataclass(frozen=True, slots=True)
class TraceRecord:
    task_id: str
    evidence_link: str
    validation_status: str
    outcome_quality: OutcomeQuality


@dataclass(frozen=True, slots=True)
class TraceGradeResult:
    task_id: str
    grade: TraceGrade
    reason: str


def record_eval_baseline(repo_profile: Any) -> EvalBaseline:
    raw = getattr(repo_profile, "raw", None)
    if not isinstance(raw, dict):
        msg = "repo_profile.raw is required"
        raise ValueError(msg)
    suites = raw.get("extra_eval_suites", [])
    if not isinstance(suites, list):
        msg = "extra_eval_suites must be a list"
        raise ValueError(msg)
    return EvalBaseline(repo_id=getattr(repo_profile, "repo_id"), required_suites=suites)


def emit_trace_record(
    task_id: str,
    evidence_link: str,
    validation_status: str,
    outcome_quality: OutcomeQuality,
) -> TraceRecord:
    task_id = _required_string(task_id, "task_id")
    validation_status = _required_string(validation_status, "validation_status")
    if outcome_quality not in {"pass", "fail"}:
        msg = f"unsupported outcome_quality: {outcome_quality}"
        raise ValueError(msg)
    return TraceRecord(
        task_id=task_id,
        evidence_link=evidence_link.strip() if isinstance(evidence_link, str) else "",
        validation_status=validation_status,
        outcome_quality=outcome_quality,
    )


def grade_trace(trace: TraceRecord) -> TraceGradeResult:
    if not trace.evidence_link:
        return TraceGradeResult(
            task_id=trace.task_id,
            grade="missing_evidence",
            reason="trace record has no evidence_link",
        )
    if trace.outcome_quality == "fail":
        return TraceGradeResult(
            task_id=trace.task_id,
            grade="poor_outcome_quality",
            reason="trace outcome quality failed despite evidence",
        )
    return TraceGradeResult(task_id=trace.task_id, grade="pass", reason="trace is complete and passing")


def _required_string(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        msg = f"{field_name} is required"
        raise ValueError(msg)
    return value.strip()
