# Workflow Governance Spec

## Status
Draft

## Purpose
Define a governed workflow-mode contract for AI coding work so the runtime can recommend, select, degrade, project, and measure workflow modes without claiming one fixed universal best recipe.

## Required Fields
- schema_version
- workflow_governance_id
- default_workflow_mode
- allowed_workflow_modes
- workflow_mode_overrides_by_risk
- spec_artifact_requirements
- review_requirements
- worktree_policy
- subagent_policy
- automation_policy
- degrade_rules

## Workflow Modes
- direct_fix
- spec_first
- spec_plus_review
- worktree_isolated_execution
- parallel_subagent_assist
- maintenance_automation

## Selection Inputs
- task metadata
- repo profile
- adapter capability surface
- prior target-run effect evidence
- deterministic policy

## Selection Rules
- small scope and low risk default to `direct_fix`
- unclear requirements, multi-file work, or medium/high risk default to `spec_first`
- medium/high risk plus explicit review requirement default to `spec_plus_review`
- `worktree_isolated_execution` is allowed only when host capability explicitly proves worktree support
- `parallel_subagent_assist` is allowed only when host capability explicitly proves subagent support
- repeated stable tasks may use `maintenance_automation`

## Degrade Rules
- when worktree support is missing, `worktree_isolated_execution` must degrade explicitly
- when subagent support is missing, `parallel_subagent_assist` must degrade explicitly
- when automation support is missing, `maintenance_automation` must degrade explicitly
- degrade target must be `spec_plus_review` or `direct_fix`
- the runtime may not silently keep claiming the stronger workflow mode after degrade

## Output Projection
The following fields must be projectable into runtime or target-run outputs:
- workflow_mode_selected
- workflow_mode_source
- workflow_mode_reason
- workflow_degrade_reason
- workflow_required_artifacts
- workflow_metrics

## Non-Goals
- declaring one mandatory universal workflow for every repository
- replacing host-native planning, review, or worktree features
- implying advanced workflow execution without explicit host capability proof
