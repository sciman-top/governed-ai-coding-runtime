"""Clarification policy primitives derived from AGENTS clarification rules."""

from dataclasses import dataclass
from typing import Literal


ClarificationMode = Literal["direct_fix", "clarify_required"]
ClarificationScenario = Literal["plan", "requirement", "bugfix", "acceptance"]

_EVIDENCE_FIELDS = [
    "issue_id",
    "attempt_count",
    "clarification_mode",
    "clarification_scenario",
    "clarification_questions",
    "clarification_answers",
]


@dataclass(frozen=True, slots=True)
class ClarificationPolicy:
    trigger_threshold: int = 2
    question_cap: int = 3


@dataclass(frozen=True, slots=True)
class ClarificationDecision:
    issue_id: str
    attempt_count: int
    current_mode: ClarificationMode
    next_mode: ClarificationMode
    scenario: ClarificationScenario
    clarification_required: bool
    question_cap: int
    required_evidence_fields: list[str]


@dataclass(frozen=True, slots=True)
class ClarificationState:
    issue_id: str
    attempt_count: int
    mode: ClarificationMode


def evaluate_clarification(
    policy: ClarificationPolicy,
    *,
    issue_id: str,
    attempt_count: int,
    current_mode: ClarificationMode,
    scenario: ClarificationScenario,
) -> ClarificationDecision:
    clarification_required = attempt_count >= policy.trigger_threshold
    next_mode: ClarificationMode = "clarify_required" if clarification_required else current_mode
    return ClarificationDecision(
        issue_id=issue_id,
        attempt_count=attempt_count,
        current_mode=current_mode,
        next_mode=next_mode,
        scenario=scenario,
        clarification_required=clarification_required,
        question_cap=policy.question_cap,
        required_evidence_fields=list(_EVIDENCE_FIELDS),
    )


def reset_clarification_state(*, issue_id: str, clarified: bool) -> ClarificationState:
    if clarified:
        return ClarificationState(issue_id=issue_id, attempt_count=0, mode="direct_fix")
    return ClarificationState(issue_id=issue_id, attempt_count=0, mode="clarify_required")
