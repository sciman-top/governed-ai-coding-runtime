# Runtime Operator Surface Spec

## Status
Draft

## Purpose
Define the CLI-first runtime status and task query surface that operators can use before a richer UI shell exists.

## Required Fields
- total_tasks
- maintenance.stage
- maintenance.compatibility_policy_ref
- maintenance.upgrade_policy_ref
- maintenance.triage_policy_ref
- maintenance.deprecation_policy_ref
- maintenance.retirement_policy_ref
- tasks[].task_id
- tasks[].current_state
- tasks[].goal
- tasks[].active_run_id
- tasks[].workspace_root
- tasks[].rollback_ref
- tasks[].approval_ids
- tasks[].artifact_refs
- tasks[].evidence_refs
- tasks[].verification_refs

## Optional Interaction Projection Fields
- tasks[].interaction_posture
- tasks[].latest_task_restatement
- tasks[].interaction_budget_status
- tasks[].clarification_active
- tasks[].latest_compression_action
- tasks[].outstanding_observation_items_count

When an active run has an evidence bundle with `interaction_trace`, the operator surface may project the latest interaction posture, restatement, budget status, clarification activity, compression action, and outstanding observation checklist count.

## Invariants
- the operator surface is read-model only and may not mutate runtime state directly
- task and run identifiers must remain stable across repeated status queries
- maintenance policy references must point to repository-local product docs when the maintenance stage is complete
- evidence, artifact, and verification links must refer to persisted local runtime data rather than transcript-only output
- interaction projection is optional and must not require a separate interaction-only store
- interaction projection should be derived from persisted runtime evidence when available rather than free-form transcript state
- the first operator surface stays CLI-first and local-first
- a later UI may project the same runtime read model without redefining task or artifact semantics

## Non-Goals
- replacing the upstream coding interface
- embedding an IDE or editor in the operator surface
- introducing a network service boundary in this stage
