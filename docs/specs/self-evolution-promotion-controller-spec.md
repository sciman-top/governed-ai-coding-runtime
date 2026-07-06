# Self-Evolution Promotion Controller Spec

## Status
Draft

## Purpose
Define the non-mutating controller report that explains how self-evolution recommendations may advance toward policy mutation, skill enablement, push, or merge.

The controller is an admission surface, not an executor. It reports the current trigger, lane state, blockers, required review, and rollback posture before any effective change is allowed.

## Required Fields
- schema_version
- artifact_type
- status
- as_of
- promotion_stage
- recommended_next_action
- selector_next_action
- selector_why
- source_recommendation_path
- effective_change_allowed
- control_lanes
- trigger_model
- guards
- rollback
- artifact_refs

## Control Lanes
Each report must cover exactly these lane identities:

- policy_mutation
- skill_enablement
- push_or_merge

Each lane records:

- lane
- status
- automatic_enabled
- guard_key
- reason
- next_action

## Trigger Model
The recommended operator action is `SelfEvolutionPromotionPlan`. It may be refreshed proactively by `SelfEvolutionRecommend` and `FeedbackReport`, but the controller must not perform effective changes by itself.

## Invariants
- `artifact_type` is `self_evolution_promotion_controller_report`.
- `effective_change_allowed` is `false` until a separate reviewed promotion path explicitly changes the governed contract.
- `trigger_model.automatic_effective_change` is `false`.
- `guards.automatic_policy_mutation`, `guards.automatic_skill_enablement`, and `guards.automatic_push_or_merge` are `false`.
- `guards.requires_human_review_before_effective_change` is `true`.
- Every lane has `automatic_enabled=false`.
- Missing recommendation or selector-blocked states remain report-only and must point to the next bounded action.
- Rollback instructions must be present and must not require reversing hidden mutations, because the controller report is non-mutating.

## Non-Goals
- Automatically modifying policies.
- Automatically enabling skills.
- Automatically pushing or merging branches.
- Replacing review, gate evidence, or rollback evidence with hidden heuristics.
