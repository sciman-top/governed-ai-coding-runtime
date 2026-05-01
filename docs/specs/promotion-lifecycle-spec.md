# Promotion Lifecycle Spec

## Status
Draft

## Purpose
Define the staged promotion and retirement lifecycle for generated skills, hooks, gates, evals, policies, and workflows.

## Required Fields
- lifecycle_id
- generated_on
- source_review
- entries
- retirement_guard
- rollback_ref

## Entry Requirements
Each lifecycle entry must include:

- asset_id
- asset_kind
- status
- materialized_path
- enabled_by_default
- review_required
- promotion_evidence_refs
- promotion_gate_refs
- effect_metric_refs
- rollback_ref

## Enumerations
### asset_kind
- skill
- hook
- gate
- eval
- policy
- workflow

### status
- disabled
- review
- test_ready
- observe
- enforce
- retired

## Invariants
- generated skills or hooks must never be enabled by default while still in `disabled`, `review`, or `test_ready`
- promotion to `observe` or `enforce` requires gate or eval evidence plus rollback instructions
- retirement may clean up stale, inactive, duplicated, replaced, or harmful candidates only when evidence history stays preserved
- reviewed assets and evidence history must remain outside direct delete scope

## Non-Goals
- automatic enablement of generated assets
- deleting reviewed assets or evidence bundles
- replacing target-repo promotion decisions with hidden heuristics
