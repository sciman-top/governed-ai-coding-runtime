# Capability Portfolio Classifier Spec

## Status
Draft

## Purpose
Define the machine-checkable portfolio classifier used by `GAP-131` to evaluate both external mechanism sources and existing repository capabilities before later control-pack, inheritance, and target-repo reuse work begins.

## Required Fields
- schema_version
- portfolio_id
- status
- reviewed_on
- review_expires_at
- required_doc_refs
- evidence_refs
- entries

## Entry Fields
Each entry must include:
- id
- title
- source_type
- product_layer
- lifecycle_outcome
- summary
- source_refs
- review_refs
- effect_hypothesis
- rollback

## Enumerations
### source_type
- external_source
- existing_capability
- candidate_cleanup

### lifecycle_outcome
- add
- keep
- improve
- merge
- deprecate
- retire
- delete_candidate

## Effect Hypothesis Fields
Each entry must declare:
- expected_benefit
- expected_cost
- expected_risk
- effect_metric
- verification_command

## Invariants
- every absorbed, retained, improved, merged, deprecated, retired, or deleted capability must have an explicit effect hypothesis
- every external source and existing capability must map to a product layer and lifecycle outcome
- `deprecate`, `retire`, and `delete_candidate` entries must include both `retention_rule` and `future_trigger`
- local `source_refs`, `review_refs`, `required_doc_refs`, and `evidence_refs` must resolve to real repository files
- the classifier records adoption and retirement intent only; it does not directly mutate active policy, enable skills, sync target repos, push, or merge

## Non-Goals
- automatic host replacement
- automatic policy mutation
- automatic skill installation
- target-repo synchronization
- remote push or merge
