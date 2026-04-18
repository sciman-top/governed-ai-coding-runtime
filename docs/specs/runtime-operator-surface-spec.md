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

## Invariants
- the operator surface is read-model only and may not mutate runtime state directly
- task and run identifiers must remain stable across repeated status queries
- maintenance policy references must point to repository-local product docs when the maintenance stage is complete
- evidence, artifact, and verification links must refer to persisted local runtime data rather than transcript-only output
- the first operator surface stays CLI-first and local-first
- a later UI may project the same runtime read model without redefining task or artifact semantics

## Non-Goals
- replacing the upstream coding interface
- embedding an IDE or editor in the operator surface
- introducing a network service boundary in this stage
