# Evidence Bundle Spec

## Status
Draft

## Purpose
Define the minimum evidence bundle persisted for every governed task.

## Required Fields
- task_id
- repo_id
- goal
- non_goals
- acceptance_criteria
- assumptions
- commands_run
- tool_calls
- files_changed
- approvals
- required_evidence
- verification_results
- rollback_ref
- final_outcome
- open_questions
- created_at
- completed_at

## Optional Fields
- context_snapshot_ref
- repo_profile_ref
- prompt_registry_ref
- failure_signature
- replay_case_ref
- runtime_artifact_refs
- verification_artifact_refs
- trial_feedback
- interaction_trace

## Quality Classifiers

### required_evidence
- kind
- status
- reason
- artifact_ref

`status` values:
- present
- missing_mandatory
- missing_allowed
- advisory_only

### verification_results.status
- passed
- failed
- advisory
- skipped_not_applicable

## interaction_trace Extension

`interaction_trace` is an optional structured extension of the evidence bundle. It records why the runtime chose to restate the task, clarify, guide bug observation, teach a term, compress the session, degrade verbosity, or stop on budget.

`interaction_trace` may include:
- signals
- applied_policies
- task_restatements
- clarification_rounds
- observation_checklists
- terms_explained
- compression_actions
- budget_snapshots
- alignment_outcome
- stop_or_degrade_reason

### interaction_trace.signals
- signal_id
- signal_kind
- severity
- summary
- evidence_refs

### interaction_trace.applied_policies
- policy_id
- mode
- posture
- clarification_mode
- compression_mode
- stop_or_escalate
- rationale_signal_ids

### interaction_trace.clarification_rounds
- scenario
- questions
- answers

### interaction_trace.observation_checklists
- checklist_kind
- items

### interaction_trace.terms_explained
- term
- explanation_summary
- task_role

### interaction_trace.compression_actions
- compression_mode
- summary
- retained_refs

### interaction_trace.budget_snapshots
- budget_status
- used_explanation_tokens
- used_clarification_tokens
- used_compaction_tokens
- total_token_budget

## Invariants
- evidence must be append-only at the event level
- final delivery must reference verification results
- every high-risk action must reference an approval record
- every write action must reference either a rollback path or explicit no-rollback rationale
- missing mandatory evidence must be represented explicitly and must be distinguishable from weak but present advisory evidence
- advisory verification results may coexist with successful completion, but they may not silently satisfy a missing mandatory evidence requirement
- when multi-repo onboarding or adapter feedback is relevant, `trial_feedback` should carry the structured trial reference instead of burying it in free-form notes
- `interaction_trace` is optional and must not block older evidence readers when absent
- `interaction_trace` extends the task-level evidence bundle and must not create a parallel system of record
- `interaction_trace` entries should point back to evidence refs or task facts when they claim a signal, clarification turn, compression action, or degrade reason

## Storage Note
The storage backend is implementation-specific. In the first Full Runtime stage, evidence should resolve to local artifact paths under the governed runtime artifact store rather than transcript-only output.
