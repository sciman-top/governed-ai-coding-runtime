"""Interaction-governance primitives for teaching-style collaboration and low-token control."""

from dataclasses import dataclass
from typing import Literal

from governed_ai_coding_runtime_contracts.clarification import (
    ClarificationMode,
    ClarificationPolicy,
    ClarificationScenario,
    evaluate_clarification,
)


SignalKind = Literal[
    "intent_drift",
    "goal_scope_mismatch",
    "expected_actual_missing",
    "symptom_root_cause_confusion",
    "term_confusion",
    "repeated_question_no_progress",
    "repeated_failure",
    "observation_gap",
    "budget_pressure",
    "verbosity_overrun",
    "handoff_risk",
]
Severity = Literal["low", "medium", "high"]
SignalSource = Literal[
    "user_input",
    "task_state",
    "runtime_event",
    "verification_result",
    "operator_feedback",
    "replay_analysis",
]
InteractionMode = Literal["terse", "guided", "teaching"]
TeachingLevel = Literal["none", "term_only", "concept_only", "task_scoped"]
InteractionClarificationMode = Literal["none", "light", "required"]
CompressionMode = Literal["none", "stage_summary", "aggressive_compaction", "ref_only"]
StopOrEscalate = Literal[
    "continue",
    "pause_for_user_input",
    "switch_to_checklist",
    "handoff_only",
    "stop_on_budget",
]
InteractionPosture = Literal[
    "aligned",
    "clarifying",
    "guiding",
    "teaching",
    "compressing",
    "handoff_only",
    "stopped_on_budget",
]
BudgetStatus = Literal["healthy", "warning", "near_limit", "exhausted"]

_VALID_SIGNAL_KINDS = {
    "intent_drift",
    "goal_scope_mismatch",
    "expected_actual_missing",
    "symptom_root_cause_confusion",
    "term_confusion",
    "repeated_question_no_progress",
    "repeated_failure",
    "observation_gap",
    "budget_pressure",
    "verbosity_overrun",
    "handoff_risk",
}
_VALID_SEVERITIES = {"low", "medium", "high"}
_VALID_SOURCES = {
    "user_input",
    "task_state",
    "runtime_event",
    "verification_result",
    "operator_feedback",
    "replay_analysis",
}
_VALID_MODES = {"terse", "guided", "teaching"}
_VALID_TEACHING_LEVELS = {"none", "term_only", "concept_only", "task_scoped"}
_VALID_CLARIFICATION_MODES = {"none", "light", "required"}
_VALID_COMPRESSION_MODES = {"none", "stage_summary", "aggressive_compaction", "ref_only"}
_VALID_STOP_BEHAVIORS = {
    "continue",
    "pause_for_user_input",
    "switch_to_checklist",
    "handoff_only",
    "stop_on_budget",
}
_VALID_POSTURES = {
    "aligned",
    "clarifying",
    "guiding",
    "teaching",
    "compressing",
    "handoff_only",
    "stopped_on_budget",
}
_VALID_BUDGET_STATUSES = {"healthy", "warning", "near_limit", "exhausted"}
_DEFAULT_MAX_QUESTIONS = 3
_DEFAULT_MAX_OBSERVATION_ITEMS = 4
_DEFAULT_TERM_EXPLAIN_LIMIT = 1


@dataclass(frozen=True, slots=True)
class InteractionSignal:
    signal_id: str
    task_id: str
    signal_kind: SignalKind
    severity: Severity
    confidence: float
    source: SignalSource
    summary: str
    evidence_refs: list[str]
    recorded_at: str
    run_id: str | None = None
    actor_id: str | None = None
    affected_scope: str | None = None
    related_signal_ids: list[str] | None = None
    notes: str | None = None


@dataclass(frozen=True, slots=True)
class ResponsePolicy:
    policy_id: str
    task_id: str
    mode: InteractionMode
    teaching_level: TeachingLevel
    clarification_mode: InteractionClarificationMode
    compression_mode: CompressionMode
    max_questions: int
    max_observation_items: int
    term_explain_limit: int
    restatement_required: bool
    stop_or_escalate: StopOrEscalate
    rationale_signal_ids: list[str]
    run_id: str | None = None
    posture: InteractionPosture | None = None
    checklist_kind: str | None = None
    summary_template: str | None = None
    notes: str | None = None


@dataclass(frozen=True, slots=True)
class TeachingBudget:
    task_id: str
    total_token_budget: int
    execution_budget: int
    clarification_budget: int
    explanation_budget: int
    compaction_budget: int
    used_execution_tokens: int
    used_clarification_tokens: int
    used_explanation_tokens: int
    used_compaction_tokens: int
    soft_thresholds: dict[str, int]
    hard_thresholds: dict[str, int]
    budget_status: BudgetStatus
    run_id: str | None = None
    budget_source_ref: str | None = None
    last_compaction_at: str | None = None
    notes: str | None = None


def build_interaction_signal(
    *,
    signal_id: str,
    task_id: str,
    signal_kind: SignalKind,
    severity: Severity,
    confidence: float,
    source: SignalSource,
    summary: str,
    evidence_refs: list[str],
    recorded_at: str,
    run_id: str | None = None,
    actor_id: str | None = None,
    affected_scope: str | None = None,
    related_signal_ids: list[str] | None = None,
    notes: str | None = None,
) -> InteractionSignal:
    return InteractionSignal(
        signal_id=_required_string(signal_id, "signal_id"),
        task_id=_required_string(task_id, "task_id"),
        signal_kind=_required_enum(signal_kind, "signal_kind", _VALID_SIGNAL_KINDS),
        severity=_required_enum(severity, "severity", _VALID_SEVERITIES),
        confidence=_required_confidence(confidence),
        source=_required_enum(source, "source", _VALID_SOURCES),
        summary=_required_string(summary, "summary"),
        evidence_refs=_required_string_list(evidence_refs, "evidence_refs", min_items=1),
        recorded_at=_required_string(recorded_at, "recorded_at"),
        run_id=_optional_string(run_id, "run_id"),
        actor_id=_optional_string(actor_id, "actor_id"),
        affected_scope=_optional_string(affected_scope, "affected_scope"),
        related_signal_ids=_optional_string_list(related_signal_ids, "related_signal_ids"),
        notes=_optional_string(notes, "notes"),
    )


def build_response_policy(
    *,
    policy_id: str,
    task_id: str,
    mode: InteractionMode,
    teaching_level: TeachingLevel,
    clarification_mode: InteractionClarificationMode,
    compression_mode: CompressionMode,
    max_questions: int,
    max_observation_items: int,
    term_explain_limit: int,
    restatement_required: bool,
    stop_or_escalate: StopOrEscalate,
    rationale_signal_ids: list[str],
    run_id: str | None = None,
    posture: InteractionPosture | None = None,
    checklist_kind: str | None = None,
    summary_template: str | None = None,
    notes: str | None = None,
) -> ResponsePolicy:
    normalized_mode = _required_enum(mode, "mode", _VALID_MODES)
    normalized_teaching_level = _required_enum(teaching_level, "teaching_level", _VALID_TEACHING_LEVELS)
    normalized_clarification_mode = _required_enum(
        clarification_mode, "clarification_mode", _VALID_CLARIFICATION_MODES
    )
    normalized_compression_mode = _required_enum(compression_mode, "compression_mode", _VALID_COMPRESSION_MODES)
    normalized_stop = _required_enum(stop_or_escalate, "stop_or_escalate", _VALID_STOP_BEHAVIORS)
    normalized_posture = _optional_enum(posture, "posture", _VALID_POSTURES)
    normalized_rationale_signal_ids = _required_string_list(
        rationale_signal_ids, "rationale_signal_ids", min_items=1
    )

    if max_questions < 0 or max_questions > _DEFAULT_MAX_QUESTIONS:
        msg = "max_questions must stay within clarification cap"
        raise ValueError(msg)
    if max_observation_items < 0:
        msg = "max_observation_items must be zero or greater"
        raise ValueError(msg)
    if term_explain_limit < 0:
        msg = "term_explain_limit must be zero or greater"
        raise ValueError(msg)
    if normalized_mode != "teaching" and normalized_teaching_level == "task_scoped":
        msg = "task_scoped teaching requires mode=teaching"
        raise ValueError(msg)
    if normalized_stop == "stop_on_budget" and normalized_compression_mode == "none":
        msg = "stop_on_budget requires explicit compression or handoff behavior"
        raise ValueError(msg)

    return ResponsePolicy(
        policy_id=_required_string(policy_id, "policy_id"),
        task_id=_required_string(task_id, "task_id"),
        mode=normalized_mode,
        teaching_level=normalized_teaching_level,
        clarification_mode=normalized_clarification_mode,
        compression_mode=normalized_compression_mode,
        max_questions=max_questions,
        max_observation_items=max_observation_items,
        term_explain_limit=term_explain_limit,
        restatement_required=_required_bool(restatement_required, "restatement_required"),
        stop_or_escalate=normalized_stop,
        rationale_signal_ids=normalized_rationale_signal_ids,
        run_id=_optional_string(run_id, "run_id"),
        posture=normalized_posture,
        checklist_kind=_optional_string(checklist_kind, "checklist_kind"),
        summary_template=_optional_string(summary_template, "summary_template"),
        notes=_optional_string(notes, "notes"),
    )


def build_teaching_budget(
    *,
    task_id: str,
    total_token_budget: int,
    execution_budget: int,
    clarification_budget: int,
    explanation_budget: int,
    compaction_budget: int,
    used_execution_tokens: int,
    used_clarification_tokens: int,
    used_explanation_tokens: int,
    used_compaction_tokens: int,
    soft_thresholds: dict[str, int],
    hard_thresholds: dict[str, int],
    budget_status: BudgetStatus,
    run_id: str | None = None,
    budget_source_ref: str | None = None,
    last_compaction_at: str | None = None,
    notes: str | None = None,
) -> TeachingBudget:
    total = _required_int(total_token_budget, "total_token_budget", minimum=1)
    execution = _required_int(execution_budget, "execution_budget", minimum=0)
    clarification = _required_int(clarification_budget, "clarification_budget", minimum=0)
    explanation = _required_int(explanation_budget, "explanation_budget", minimum=0)
    compaction = _required_int(compaction_budget, "compaction_budget", minimum=0)
    if total < execution + clarification + explanation + compaction:
        msg = "total_token_budget must cover all active sub-budgets"
        raise ValueError(msg)

    return TeachingBudget(
        task_id=_required_string(task_id, "task_id"),
        total_token_budget=total,
        execution_budget=execution,
        clarification_budget=clarification,
        explanation_budget=explanation,
        compaction_budget=compaction,
        used_execution_tokens=_required_int(used_execution_tokens, "used_execution_tokens", minimum=0),
        used_clarification_tokens=_required_int(
            used_clarification_tokens, "used_clarification_tokens", minimum=0
        ),
        used_explanation_tokens=_required_int(used_explanation_tokens, "used_explanation_tokens", minimum=0),
        used_compaction_tokens=_required_int(used_compaction_tokens, "used_compaction_tokens", minimum=0),
        soft_thresholds=_required_int_map(soft_thresholds, "soft_thresholds"),
        hard_thresholds=_required_int_map(hard_thresholds, "hard_thresholds"),
        budget_status=_required_enum(budget_status, "budget_status", _VALID_BUDGET_STATUSES),
        run_id=_optional_string(run_id, "run_id"),
        budget_source_ref=_optional_string(budget_source_ref, "budget_source_ref"),
        last_compaction_at=_optional_string(last_compaction_at, "last_compaction_at"),
        notes=_optional_string(notes, "notes"),
    )


def build_task_created_policy(*, task_id: str, summary_template: str | None = None) -> ResponsePolicy:
    return build_response_policy(
        policy_id=f"{_required_string(task_id, 'task_id')}:task-created",
        task_id=task_id,
        mode="guided",
        teaching_level="none",
        clarification_mode="none",
        compression_mode="none",
        max_questions=0,
        max_observation_items=0,
        term_explain_limit=0,
        restatement_required=True,
        stop_or_escalate="continue",
        rationale_signal_ids=["task-created"],
        posture="aligned",
        summary_template=summary_template,
    )


def derive_response_policy(
    *,
    task_id: str,
    signals: list[InteractionSignal],
    budget: TeachingBudget | None = None,
    clarification_policy: ClarificationPolicy | None = None,
    attempt_count: int = 0,
    clarification_current_mode: ClarificationMode = "direct_fix",
    clarification_scenario: ClarificationScenario = "bugfix",
) -> ResponsePolicy:
    normalized_task_id = _required_string(task_id, "task_id")
    normalized_signals = _required_signal_list(signals)

    if budget is not None and budget.budget_status == "exhausted":
        return build_response_policy(
            policy_id=f"{normalized_task_id}:budget-stop",
            task_id=normalized_task_id,
            mode="terse",
            teaching_level="none",
            clarification_mode="none",
            compression_mode="ref_only",
            max_questions=0,
            max_observation_items=0,
            term_explain_limit=0,
            restatement_required=False,
            stop_or_escalate="stop_on_budget",
            rationale_signal_ids=[signal.signal_id for signal in normalized_signals],
            posture="stopped_on_budget",
        )

    signal_map = {signal.signal_kind: signal for signal in normalized_signals}

    if "goal_scope_mismatch" in signal_map or "intent_drift" in signal_map:
        prioritized = signal_map.get("goal_scope_mismatch") or signal_map["intent_drift"]
        return build_response_policy(
            policy_id=f"{normalized_task_id}:{prioritized.signal_kind}",
            task_id=normalized_task_id,
            mode="guided",
            teaching_level="none",
            clarification_mode="light",
            compression_mode="none",
            max_questions=1,
            max_observation_items=0,
            term_explain_limit=0,
            restatement_required=True,
            stop_or_escalate="pause_for_user_input",
            rationale_signal_ids=[prioritized.signal_id],
            posture="aligned",
        )

    if "repeated_failure" in signal_map:
        active_policy = clarification_policy or ClarificationPolicy(trigger_threshold=2, question_cap=3)
        clarification = evaluate_clarification(
            active_policy,
            issue_id=normalized_task_id,
            attempt_count=attempt_count,
            current_mode=clarification_current_mode,
            scenario=clarification_scenario,
        )
        return build_response_policy(
            policy_id=f"{normalized_task_id}:repeated-failure",
            task_id=normalized_task_id,
            mode="guided",
            teaching_level="none",
            clarification_mode="required" if clarification.clarification_required else "light",
            compression_mode="none",
            max_questions=clarification.question_cap if clarification.clarification_required else 1,
            max_observation_items=0,
            term_explain_limit=0,
            restatement_required=True,
            stop_or_escalate="pause_for_user_input",
            rationale_signal_ids=[signal_map["repeated_failure"].signal_id],
            posture="clarifying",
        )

    if "observation_gap" in signal_map or "expected_actual_missing" in signal_map:
        prioritized = signal_map.get("observation_gap") or signal_map["expected_actual_missing"]
        return build_response_policy(
            policy_id=f"{normalized_task_id}:{prioritized.signal_kind}",
            task_id=normalized_task_id,
            mode="guided",
            teaching_level="none",
            clarification_mode="light",
            compression_mode="none",
            max_questions=1,
            max_observation_items=_DEFAULT_MAX_OBSERVATION_ITEMS,
            term_explain_limit=0,
            restatement_required=False,
            stop_or_escalate="switch_to_checklist",
            rationale_signal_ids=[prioritized.signal_id],
            posture="guiding",
            checklist_kind="bugfix-observation",
        )

    if "term_confusion" in signal_map or "symptom_root_cause_confusion" in signal_map:
        prioritized = signal_map.get("term_confusion") or signal_map["symptom_root_cause_confusion"]
        teaching_level: TeachingLevel = "term_only" if prioritized.signal_kind == "term_confusion" else "concept_only"
        return build_response_policy(
            policy_id=f"{normalized_task_id}:{prioritized.signal_kind}",
            task_id=normalized_task_id,
            mode="teaching",
            teaching_level=teaching_level,
            clarification_mode="light",
            compression_mode="none",
            max_questions=1,
            max_observation_items=0,
            term_explain_limit=_DEFAULT_TERM_EXPLAIN_LIMIT,
            restatement_required=False,
            stop_or_escalate="continue",
            rationale_signal_ids=[prioritized.signal_id],
            posture="teaching",
        )

    if "budget_pressure" in signal_map or "verbosity_overrun" in signal_map:
        prioritized = signal_map.get("budget_pressure") or signal_map["verbosity_overrun"]
        compression_mode: CompressionMode = "aggressive_compaction" if budget and budget.budget_status == "near_limit" else "stage_summary"
        stop_behavior: StopOrEscalate = "handoff_only" if budget and budget.budget_status == "near_limit" else "continue"
        posture: InteractionPosture = "handoff_only" if stop_behavior == "handoff_only" else "compressing"
        return build_response_policy(
            policy_id=f"{normalized_task_id}:{prioritized.signal_kind}",
            task_id=normalized_task_id,
            mode="terse",
            teaching_level="none",
            clarification_mode="none",
            compression_mode=compression_mode,
            max_questions=0,
            max_observation_items=0,
            term_explain_limit=0,
            restatement_required=False,
            stop_or_escalate=stop_behavior,
            rationale_signal_ids=[prioritized.signal_id],
            posture=posture,
        )

    first_signal = normalized_signals[0]
    return build_response_policy(
        policy_id=f"{normalized_task_id}:{first_signal.signal_kind}",
        task_id=normalized_task_id,
        mode="guided",
        teaching_level="none",
        clarification_mode="none",
        compression_mode="none",
        max_questions=0,
        max_observation_items=0,
        term_explain_limit=0,
        restatement_required=False,
        stop_or_escalate="continue",
        rationale_signal_ids=[first_signal.signal_id],
        posture="aligned",
    )


def _required_signal_list(signals: list[InteractionSignal]) -> list[InteractionSignal]:
    if not isinstance(signals, list) or not signals:
        msg = "signals are required"
        raise ValueError(msg)
    for signal in signals:
        if not isinstance(signal, InteractionSignal):
            msg = "signals must contain InteractionSignal entries"
            raise ValueError(msg)
    return signals


def _required_string(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        msg = f"{field_name} is required"
        raise ValueError(msg)
    return value.strip()


def _optional_string(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    return _required_string(value, field_name)


def _required_enum(value: str, field_name: str, valid_values: set[str]) -> str:
    normalized = _required_string(value, field_name).lower()
    if normalized not in valid_values:
        msg = f"unsupported {field_name}: {value}"
        raise ValueError(msg)
    return normalized


def _optional_enum(value: str | None, field_name: str, valid_values: set[str]) -> str | None:
    if value is None:
        return None
    return _required_enum(value, field_name, valid_values)


def _required_string_list(value: list[str], field_name: str, *, min_items: int = 0) -> list[str]:
    if not isinstance(value, list):
        msg = f"{field_name} is required"
        raise ValueError(msg)
    normalized = [_required_string(item, f"{field_name} entry") for item in value]
    if len(normalized) < min_items:
        msg = f"{field_name} requires at least {min_items} item(s)"
        raise ValueError(msg)
    return normalized


def _optional_string_list(value: list[str] | None, field_name: str) -> list[str] | None:
    if value is None:
        return None
    return _required_string_list(value, field_name)


def _required_int(value: int, field_name: str, *, minimum: int) -> int:
    if not isinstance(value, int) or value < minimum:
        msg = f"{field_name} must be an integer >= {minimum}"
        raise ValueError(msg)
    return value


def _required_int_map(value: dict[str, int], field_name: str) -> dict[str, int]:
    if not isinstance(value, dict) or not value:
        msg = f"{field_name} is required"
        raise ValueError(msg)
    normalized: dict[str, int] = {}
    for key, raw in value.items():
        normalized[_required_string(key, f"{field_name} key")] = _required_int(raw, f"{field_name} value", minimum=0)
    return normalized


def _required_confidence(value: float) -> float:
    if not isinstance(value, (int, float)):
        msg = "confidence must be a number between 0 and 1"
        raise ValueError(msg)
    normalized = float(value)
    if normalized < 0 or normalized > 1:
        msg = "confidence must be a number between 0 and 1"
        raise ValueError(msg)
    return normalized


def _required_bool(value: bool, field_name: str) -> bool:
    if not isinstance(value, bool):
        msg = f"{field_name} must be a boolean"
        raise ValueError(msg)
    return value

