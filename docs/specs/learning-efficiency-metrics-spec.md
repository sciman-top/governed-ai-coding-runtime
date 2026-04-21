# Learning Efficiency Metrics Spec

## Status
Draft

## Purpose
Define the bounded metric set used to assess whether governed interaction behavior reduces repeated misunderstanding, improves task alignment, and stays inside explicit explanation and clarification budgets.

## Required Fields
- task_id
- restatement_count
- clarification_rounds
- term_explanation_count
- observation_prompt_count
- compression_count
- budget_downgrade_count
- token_spend_total
- token_spend_explanation
- token_spend_clarification
- repeated_misunderstanding_count
- rework_after_misalignment_count
- user_confirmed_alignment_count
- issue_resolution_without_repeated_question
- recorded_at

## Optional Fields
- run_id
- metrics_source_ref
- notes

## Invariants
- metrics must remain bounded and task-scoped; they may not become an unreviewable personalization score
- token-spend metrics must remain distinguishable between explanation and clarification activity
- repeated misunderstanding and rework metrics must resolve to reviewable task, evidence, or postmortem references
- efficiency metrics may inform controlled improvement proposals, but they may not autonomously mutate response policy or runtime behavior
- low token spend is not sufficient evidence of success unless alignment and outcome metrics remain reviewable
- runtime-generated metrics should be persisted as task/run artifacts that point back to their source evidence bundle

## Minimal Baseline Metrics
- alignment_confirm_rate
- misalignment_detect_rate
- repeated_failure_before_clarify
- observation_gap_prompt_rate
- term_explanation_trigger_rate
- compression_trigger_rate
- explanation_token_share
- handoff_recovery_success_rate

## Notes
- This contract is intentionally small. It exists to make trade-offs visible, not to maximize metric breadth.
- Later telemetry expansion must preserve the same evidence-backed, non-authoritative posture.
