"""Task intake domain model placeholders for TDD."""

from dataclasses import dataclass

_ALLOWED_INTERACTION_DEFAULT_MODES = {"terse", "guided", "teaching"}

_ALLOWED_TRANSITIONS = {
    ("created", "scoped"),
    ("scoped", "planned"),
    ("planned", "executing"),
    ("planned", "awaiting_approval"),
    ("planned", "cancelled"),
    ("awaiting_approval", "executing"),
    ("awaiting_approval", "cancelled"),
    ("executing", "verifying"),
    ("executing", "paused"),
    ("verifying", "delivered"),
    ("verifying", "paused"),
    ("executing", "failed"),
    ("verifying", "failed"),
    ("paused", "executing"),
    ("paused", "verifying"),
    ("paused", "cancelled"),
    ("failed", "planned"),
    ("failed", "rolled_back"),
}


@dataclass(slots=True)
class TaskIntake:
    goal: str
    scope: str
    acceptance: list[str]
    repo: str
    budgets: dict[str, int]
    interaction_defaults: dict[str, object] | None = None
    interaction_budget_overrides: dict[str, int] | None = None

    def __post_init__(self) -> None:
        if not self.goal.strip():
            msg = "goal is required"
            raise ValueError(msg)
        if not self.scope.strip():
            msg = "scope is required"
            raise ValueError(msg)
        if not self.acceptance:
            msg = "acceptance is required"
            raise ValueError(msg)
        if not self.repo.strip():
            msg = "repo is required"
            raise ValueError(msg)
        if not self.budgets:
            msg = "budgets are required"
            raise ValueError(msg)
        if self.interaction_defaults is not None:
            self.interaction_defaults = _normalize_interaction_defaults(self.interaction_defaults)
        if self.interaction_budget_overrides is not None:
            self.interaction_budget_overrides = _normalize_interaction_budget_overrides(
                self.interaction_budget_overrides
            )


def validate_transition(previous_state: str, next_state: str) -> bool:
    if (previous_state, next_state) not in _ALLOWED_TRANSITIONS:
        msg = f"illegal transition: {previous_state} -> {next_state}"
        raise ValueError(msg)
    return True


def apply_interaction_profile_defaults(
    task: TaskIntake,
    interaction_profile: dict[str, object] | None,
) -> TaskIntake:
    if not interaction_profile:
        return task
    if task.interaction_defaults is not None:
        return task

    defaults: dict[str, object] = {}
    if "default_mode" in interaction_profile:
        defaults["default_mode"] = interaction_profile["default_mode"]
    if "default_checklist_kind" in interaction_profile:
        defaults["default_checklist_kind"] = interaction_profile["default_checklist_kind"]
    if "summary_template" in interaction_profile:
        defaults["summary_template"] = interaction_profile["summary_template"]
    if "handoff_teaching_notes" in interaction_profile:
        defaults["handoff_teaching_notes"] = interaction_profile["handoff_teaching_notes"]
    if "term_explain_style" in interaction_profile:
        defaults["term_explain_style"] = interaction_profile["term_explain_style"]

    return TaskIntake(
        goal=task.goal,
        scope=task.scope,
        acceptance=list(task.acceptance),
        repo=task.repo,
        budgets=dict(task.budgets),
        interaction_defaults=defaults or None,
        interaction_budget_overrides=task.interaction_budget_overrides,
    )


def _normalize_interaction_defaults(interaction_defaults: dict[str, object]) -> dict[str, object]:
    if not isinstance(interaction_defaults, dict):
        msg = "interaction_defaults must be a dict"
        raise ValueError(msg)

    normalized = dict(interaction_defaults)
    default_mode = normalized.get("default_mode")
    if default_mode is not None and default_mode not in _ALLOWED_INTERACTION_DEFAULT_MODES:
        msg = f"unsupported interaction default_mode: {default_mode}"
        raise ValueError(msg)

    max_questions = normalized.get("max_questions")
    if max_questions is not None:
        if not isinstance(max_questions, int):
            msg = "interaction_defaults.max_questions must be an int"
            raise ValueError(msg)
        if max_questions < 0 or max_questions > 3:
            msg = "interaction_defaults.max_questions must stay within clarification cap 0..3"
            raise ValueError(msg)

    return normalized


def _normalize_interaction_budget_overrides(
    interaction_budget_overrides: dict[str, int],
) -> dict[str, int]:
    if not isinstance(interaction_budget_overrides, dict):
        msg = "interaction_budget_overrides must be a dict"
        raise ValueError(msg)

    normalized = dict(interaction_budget_overrides)
    for budget_name, budget_value in normalized.items():
        if not isinstance(budget_value, int):
            msg = f"interaction_budget_overrides.{budget_name} must be an int"
            raise ValueError(msg)
        if budget_value < 0:
            msg = f"interaction_budget_overrides.{budget_name} must be non-negative"
            raise ValueError(msg)
    return normalized
