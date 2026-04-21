# Interaction Signal Spec

## Status
Draft

## Purpose
Define the observable interaction signals that can trigger task restatement, clarification, checklist-first guidance, teaching-mode explanation, compression, degrade behavior, or stop-on-budget behavior inside governed sessions.

## Required Fields
- signal_id
- task_id
- signal_kind
- severity
- confidence
- source
- summary
- evidence_refs
- recorded_at

## Optional Fields
- run_id
- actor_id
- affected_scope
- related_signal_ids
- notes

## Enumerations

### signal_kind
- intent_drift
- goal_scope_mismatch
- expected_actual_missing
- symptom_root_cause_confusion
- term_confusion
- repeated_question_no_progress
- repeated_failure
- observation_gap
- budget_pressure
- verbosity_overrun
- handoff_risk

### severity
- low
- medium
- high

### source
- user_input
- task_state
- runtime_event
- verification_result
- operator_feedback
- replay_analysis

## Invariants
- interaction signals must describe observable interaction friction or budget posture, not inferred user psychology
- every signal must carry at least one `evidence_ref` or other reviewable source reference
- `signal_kind=repeated_failure` must resolve to a stable task or issue scope rather than a vague session-level claim
- `signal_kind=budget_pressure` or `signal_kind=verbosity_overrun` must resolve to a budget, compaction, or context-shaping input rather than free-form intuition
- interaction signals may shape response policy but may not directly mutate approvals, verification state, or task lifecycle state

## Notes
- This contract is intentionally narrower than a memory or personalization model.
- It provides a reviewable trigger layer for interaction governance, not a hidden behavior engine.

