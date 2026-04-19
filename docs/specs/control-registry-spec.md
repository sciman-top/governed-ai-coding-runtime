# Control Registry Spec

## Status
Draft

## Purpose
Define the machine-readable registry of platform controls, including rollout state, promotion health, rollback posture, and review cadence.

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
- observability_signals
- applies_to
- rollout_state
- health_signals

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
- canary
- enforce
- advisory

### rollout_state.current_mode / target_mode
- observe
- canary
- enforce
- advisory
- rollback

### lifecycle_status
- draft
- trial
- active
- deprecated
- retired

## Rollout Semantics
- `observe`: collect evidence and health signals but do not enforce the control path yet.
- `canary`: enforce the control for a bounded slice with explicit promotion and rollback criteria.
- `enforce`: enforce by default after promotion evidence is present.
- `rollback`: temporarily revert enforcement posture while preserving evidence and recovery visibility.
- `advisory`: keep the control informative only.

## Invariants
- each control must have a stable `control_id`
- each control must name a rollback reference or explicit `rollback_not_applicable`
- progressive controls must define rollout metadata with promotion and rollback criteria
- controls in `canary` or `enforce` mode must carry health signals and review cadence metadata
- missing rollback visibility or missing health signals must keep a control unhealthy for promotion
- `target_mode=enforce` is invalid unless promotion criteria and rollback criteria are both declared

## Review Cadence And Health
Every promoted or promotable control must record:
- review cadence via `last_reviewed_at` and `next_review_at`
- `health_signals`
- rollout gating thresholds through `rollout_state`

Health signals should make it visible whether promotion is ready, blocked, or rolled back instead of leaving the state to operator memory.

## Non-Goals
- embedding repo-specific business rules directly into the registry
- auto-promoting controls without evidence-backed review
- using waivers to redefine the kernel control contract
