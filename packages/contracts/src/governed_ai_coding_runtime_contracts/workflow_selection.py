"""Deterministic workflow selection helpers."""

from __future__ import annotations

from governed_ai_coding_runtime_contracts.workflow_governance import WorkflowGovernanceDecision


def select_workflow_mode(
    *,
    risk_level: str,
    multi_file: bool,
    unclear_requirements: bool,
    needs_review: bool,
    supports_worktrees: bool,
    supports_subagents: bool,
    supports_background_automation: bool,
    repeated_stable_task: bool,
) -> WorkflowGovernanceDecision:
    if repeated_stable_task:
        if supports_background_automation:
            return WorkflowGovernanceDecision(
                workflow_mode_selected="maintenance_automation",
                workflow_mode_source="deterministic_policy",
                workflow_mode_reason="repeated stable task with proven automation support",
                workflow_degrade_reason="",
                workflow_required_artifacts=[],
            )
        return WorkflowGovernanceDecision(
            workflow_mode_selected="direct_fix",
            workflow_mode_source="deterministic_policy",
            workflow_mode_reason="repeated stable task but automation capability is unavailable",
            workflow_degrade_reason="supports_background_automation missing; degraded from maintenance_automation to direct_fix",
            workflow_required_artifacts=[],
        )

    if needs_review or risk_level == "high":
        return WorkflowGovernanceDecision(
            workflow_mode_selected="spec_plus_review",
            workflow_mode_source="deterministic_policy",
            workflow_mode_reason="high-risk or reviewer-required change",
            workflow_degrade_reason="",
            workflow_required_artifacts=["spec"],
        )

    if unclear_requirements or multi_file or risk_level == "medium":
        return WorkflowGovernanceDecision(
            workflow_mode_selected="spec_first",
            workflow_mode_source="deterministic_policy",
            workflow_mode_reason="multi-file or medium-risk work benefits from explicit spec-first delivery",
            workflow_degrade_reason="",
            workflow_required_artifacts=["spec"],
        )

    return WorkflowGovernanceDecision(
        workflow_mode_selected="direct_fix",
        workflow_mode_source="deterministic_policy",
        workflow_mode_reason="small low-risk scoped change",
        workflow_degrade_reason="",
        workflow_required_artifacts=[],
    )
