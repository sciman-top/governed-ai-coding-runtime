# Workflow Effect Metrics Spec

## Status
Draft

## Purpose
Define a workflow-aware metric surface so KPI and effect reports can compare workflow modes with evidence-backed reasons instead of pass/fail only.

## Required Fields
- schema_version
- metrics_id
- workflow_mode_selected
- workflow_mode_source
- recommendation_improved
- mode_level_comparison_reason

## Optional Fields
- workflow_degrade_reason
- required_artifact_coverage
- manual_intervention_count
- time_saved_seconds
- problem_run_rate
- deny_to_success_retries
- evidence_refs

## Invariants
- metrics must remain evidence-backed
- mode comparison must include an explicit reason, not only a boolean result
- advanced-mode success may be claimed only when host capability proof exists
- degraded workflow execution must preserve `workflow_degrade_reason`

## Non-Goals
- replacing detailed target-run evidence
- forcing one universal cost model across hosts and repositories
