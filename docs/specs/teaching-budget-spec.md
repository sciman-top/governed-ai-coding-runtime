# Teaching Budget Spec

## Status
Draft

## Purpose
Define the explicit interaction budget used to bound clarification, explanation, and compaction work inside a governed session.

## Required Fields
- task_id
- total_token_budget
- execution_budget
- clarification_budget
- explanation_budget
- compaction_budget
- used_execution_tokens
- used_clarification_tokens
- used_explanation_tokens
- used_compaction_tokens
- soft_thresholds
- hard_thresholds
- budget_status

## Optional Fields
- run_id
- budget_source_ref
- last_compaction_at
- notes

## Enumerations

### budget_status
- healthy
- warning
- near_limit
- exhausted

## Invariants
- `total_token_budget` must be greater than or equal to the sum of the active sub-budgets available to the session
- clarification, explanation, and compaction budgets must remain distinguishable from execution budget
- `budget_status=exhausted` must lead to explicit degrade, handoff, or stop behavior rather than silent continuation
- soft and hard thresholds must be machine-reviewable and may not rely on hidden provider-only heuristics
- compaction budget may reduce context footprint, but it may not erase required evidence, rollback references, or replay-relevant summaries
- this contract bounds interaction behavior only; it does not replace task, wall-clock, or cost budgets that may exist elsewhere

## Notes
- Precise token accounting may vary by host and provider. This contract cares about bounded, reviewable budgeting rather than perfect telemetry.
- The budget model is intentionally local to governed interaction behavior and must not become a hidden pricing system.

