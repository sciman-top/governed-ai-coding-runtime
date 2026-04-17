"""Control registry health evaluation helpers."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ControlHealthResult:
    control_id: str
    healthy_for_enforced_mode: bool
    gaps: list[str]


def evaluate_control_health(control: dict) -> ControlHealthResult:
    gaps: list[str] = []

    observability_signals = control.get("observability_signals", [])
    if control.get("class") == "hard" and not observability_signals:
        gaps.append("missing_observability_signals")

    rollback_ref = str(control.get("rollback_ref", "")).strip()
    if not rollback_ref and not control.get("rollback_not_applicable", False):
        gaps.append("missing_rollback_visibility")

    if control.get("class") == "progressive":
        last_reviewed_at = str(control.get("last_reviewed_at", "")).strip()
        next_review_at = str(control.get("next_review_at", "")).strip()
        if not last_reviewed_at or not next_review_at:
            gaps.append("missing_review_schedule")

    healthy = len(gaps) == 0 and control.get("status") == "active"
    return ControlHealthResult(
        control_id=str(control.get("control_id", "")),
        healthy_for_enforced_mode=healthy,
        gaps=gaps,
    )
