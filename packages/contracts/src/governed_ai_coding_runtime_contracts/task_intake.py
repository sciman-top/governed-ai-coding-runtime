"""Task intake domain model placeholders for TDD."""

from dataclasses import dataclass

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


def validate_transition(previous_state: str, next_state: str) -> bool:
    if (previous_state, next_state) not in _ALLOWED_TRANSITIONS:
        msg = f"illegal transition: {previous_state} -> {next_state}"
        raise ValueError(msg)
    return True
