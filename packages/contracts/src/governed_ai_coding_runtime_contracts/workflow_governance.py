"""Workflow governance contract helpers."""

from __future__ import annotations

from dataclasses import dataclass


WORKFLOW_MODES = {
    "direct_fix",
    "spec_first",
    "spec_plus_review",
    "worktree_isolated_execution",
    "parallel_subagent_assist",
    "maintenance_automation",
}


@dataclass(frozen=True, slots=True)
class WorkflowGovernanceDecision:
    workflow_mode_selected: str
    workflow_mode_source: str
    workflow_mode_reason: str
    workflow_degrade_reason: str
    workflow_required_artifacts: list[str]


def ensure_supported_workflow_mode(mode: str) -> str:
    if mode not in WORKFLOW_MODES:
        msg = f"unsupported workflow mode: {mode}"
        raise ValueError(msg)
    return mode
