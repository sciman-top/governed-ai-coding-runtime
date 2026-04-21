"""Learning-efficiency metrics derived from interaction evidence."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import json
from pathlib import Path


@dataclass(frozen=True, slots=True)
class LearningEfficiencyMetricsRecord:
    task_id: str
    restatement_count: int
    clarification_rounds: int
    term_explanation_count: int
    observation_prompt_count: int
    compression_count: int
    budget_downgrade_count: int
    token_spend_total: int
    token_spend_explanation: int
    token_spend_clarification: int
    repeated_misunderstanding_count: int
    rework_after_misalignment_count: int
    user_confirmed_alignment_count: int
    issue_resolution_without_repeated_question: int
    recorded_at: str
    run_id: str | None = None
    metrics_source_ref: str | None = None
    notes: str | None = None

    def to_dict(self) -> dict:
        payload = asdict(self)
        return {key: value for key, value in payload.items() if value is not None}


@dataclass(frozen=True, slots=True)
class LearningEfficiencyMetricsSnapshot:
    generated_at: str
    record_count: int
    baseline_metrics: dict[str, float]
    records: list[LearningEfficiencyMetricsRecord]

    def to_dict(self) -> dict:
        return {
            "generated_at": self.generated_at,
            "record_count": self.record_count,
            "baseline_metrics": dict(self.baseline_metrics),
            "records": [record.to_dict() for record in self.records],
        }


def build_learning_efficiency_metrics(
    *,
    task_id: str,
    evidence_bundle: dict,
    run_id: str | None = None,
    metrics_source_ref: str | None = None,
    notes: str | None = None,
) -> LearningEfficiencyMetricsRecord:
    if not task_id.strip():
        msg = "task_id is required"
        raise ValueError(msg)
    interaction_trace = evidence_bundle.get("interaction_trace")
    if interaction_trace is None:
        interaction_trace = {}
    if not isinstance(interaction_trace, dict):
        msg = "evidence_bundle.interaction_trace must be an object when present"
        raise ValueError(msg)

    budget_snapshots = _list(interaction_trace.get("budget_snapshots"))
    token_spend_explanation = _sum_int(budget_snapshots, "used_explanation_tokens")
    token_spend_clarification = _sum_int(budget_snapshots, "used_clarification_tokens")
    token_spend_compaction = _sum_int(budget_snapshots, "used_compaction_tokens")
    signal_kinds = [
        item.get("signal_kind")
        for item in _list(interaction_trace.get("signals"))
        if isinstance(item, dict)
    ]

    return LearningEfficiencyMetricsRecord(
        task_id=task_id,
        run_id=run_id,
        metrics_source_ref=metrics_source_ref,
        notes=notes,
        restatement_count=len(_list(interaction_trace.get("task_restatements"))),
        clarification_rounds=len(_list(interaction_trace.get("clarification_rounds"))),
        term_explanation_count=len(_list(interaction_trace.get("terms_explained"))),
        observation_prompt_count=len(_list(interaction_trace.get("observation_checklists"))),
        compression_count=len(_list(interaction_trace.get("compression_actions"))),
        budget_downgrade_count=_budget_downgrade_count(interaction_trace),
        token_spend_total=token_spend_explanation + token_spend_clarification + token_spend_compaction,
        token_spend_explanation=token_spend_explanation,
        token_spend_clarification=token_spend_clarification,
        repeated_misunderstanding_count=sum(
            1 for kind in signal_kinds if kind in {"repeated_question_no_progress", "term_confusion"}
        ),
        rework_after_misalignment_count=sum(
            1 for kind in signal_kinds if kind in {"intent_drift", "goal_scope_mismatch"}
        ),
        user_confirmed_alignment_count=1 if _alignment_confirmed(interaction_trace) else 0,
        issue_resolution_without_repeated_question=_issue_resolved_without_repeated_question(
            evidence_bundle,
            signal_kinds,
        ),
        recorded_at=datetime.now(UTC).isoformat(),
    )


def persist_learning_efficiency_metrics(
    *,
    output_root: str | Path,
    record: LearningEfficiencyMetricsRecord,
    run_id: str | None = None,
) -> Path:
    root = Path(output_root)
    run_segment = run_id or record.run_id or "latest"
    output_dir = root / record.task_id / run_segment / "metrics"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "learning-efficiency.json"
    output_path.write_text(json.dumps(record.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return output_path


def summarize_learning_efficiency_metrics(
    records: list[LearningEfficiencyMetricsRecord],
) -> LearningEfficiencyMetricsSnapshot:
    record_count = len(records)
    baseline = {
        "alignment_confirm_rate": _rate(sum(item.user_confirmed_alignment_count for item in records), record_count),
        "misalignment_detect_rate": _rate(
            sum(1 for item in records if item.rework_after_misalignment_count > 0),
            record_count,
        ),
        "repeated_failure_before_clarify": _rate(
            sum(1 for item in records if item.repeated_misunderstanding_count > 0 and item.clarification_rounds > 0),
            record_count,
        ),
        "observation_gap_prompt_rate": _rate(sum(1 for item in records if item.observation_prompt_count > 0), record_count),
        "term_explanation_trigger_rate": _rate(
            sum(1 for item in records if item.term_explanation_count > 0),
            record_count,
        ),
        "compression_trigger_rate": _rate(sum(1 for item in records if item.compression_count > 0), record_count),
        "explanation_token_share": _rate(
            sum(item.token_spend_explanation for item in records),
            sum(item.token_spend_total for item in records),
        ),
        "handoff_recovery_success_rate": _rate(
            sum(item.issue_resolution_without_repeated_question for item in records),
            record_count,
        ),
    }
    return LearningEfficiencyMetricsSnapshot(
        generated_at=datetime.now(UTC).isoformat(),
        record_count=record_count,
        baseline_metrics=baseline,
        records=list(records),
    )


def _budget_downgrade_count(interaction_trace: dict) -> int:
    count = 0
    for item in _list(interaction_trace.get("budget_snapshots")):
        if isinstance(item, dict) and item.get("budget_status") in {"warning", "near_limit", "exhausted"}:
            count += 1
    for item in _list(interaction_trace.get("applied_policies")):
        if isinstance(item, dict) and item.get("stop_or_escalate") in {"handoff_only", "stop_on_budget"}:
            count += 1
    return count


def _alignment_confirmed(interaction_trace: dict) -> bool:
    value = interaction_trace.get("alignment_outcome")
    return isinstance(value, str) and "confirm" in value.lower()


def _issue_resolved_without_repeated_question(evidence_bundle: dict, signal_kinds: list[object]) -> int:
    final_outcome = evidence_bundle.get("final_outcome")
    completed = isinstance(final_outcome, dict) and final_outcome.get("status") == "completed"
    repeated = any(kind == "repeated_question_no_progress" for kind in signal_kinds)
    return 1 if completed and not repeated else 0


def _sum_int(items: list[object], field_name: str) -> int:
    total = 0
    for item in items:
        if isinstance(item, dict):
            value = item.get(field_name, 0)
            if isinstance(value, int):
                total += value
    return total


def _list(value: object) -> list[object]:
    return value if isinstance(value, list) else []


def _rate(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 4)
