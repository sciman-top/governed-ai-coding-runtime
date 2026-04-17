# Control Registry Spec

## Status
Draft

## Purpose
Define the machine-readable registry of platform controls.

## Scope
Controls covered by this registry:
- policy controls
- risk and approval controls
- evidence controls
- verification controls
- eval controls
- rollback and recovery controls

## Required Fields
- control_id
- plane
- owner
- class
- mode
- status
- lifecycle_status
- last_reviewed_at
- next_review_at
- source_of_truth
- artifacts
- rollback_ref
- observability_signals
- applies_to

## Enumerations
### plane
- task_intake
- runtime_policy
- approval
- tool_contract
- evidence
- verification
- eval
- rollback

### class
- hard
- progressive
- advisory

### mode
- observe
- enforce
- advisory

## Invariants
- each control must have a stable `control_id`
- each control must name a rollback reference or explicit `rollback_not_applicable`
- progressive controls must define an observe-to-enforce condition
- hard controls cannot be enabled without at least one observability signal
- controls intended for enforced use must carry review cadence metadata
- missing rollback visibility or missing observability must keep a control unhealthy for enforced mode

## Open Questions
- should controls support repo-specific status overrides in the registry itself or only via repo profiles?
- should retirement candidates live in the same file or separate metadata?
