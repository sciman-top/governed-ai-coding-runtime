"""Workflow-aware effect metrics helpers."""

from __future__ import annotations


def build_workflow_effect_metrics(
    *,
    workflow_mode_selected: str,
    workflow_mode_source: str,
    workflow_degrade_reason: str,
    recommendation_improved: bool,
    mode_level_comparison_reason: str,
    manual_intervention_count: int = 0,
    problem_run_rate: float = 0.0,
) -> dict:
    return {
        "workflow_mode_selected": workflow_mode_selected,
        "workflow_mode_source": workflow_mode_source,
        "workflow_degrade_reason": workflow_degrade_reason,
        "recommendation_improved": recommendation_improved,
        "mode_level_comparison_reason": mode_level_comparison_reason,
        "manual_intervention_count": manual_intervention_count,
        "problem_run_rate": problem_run_rate,
    }
