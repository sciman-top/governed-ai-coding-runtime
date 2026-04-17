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

## Invariants
- evidence must be append-only at the event level
- final delivery must reference verification results
- every high-risk action must reference an approval record
- every write action must reference either a rollback path or explicit no-rollback rationale
- missing mandatory evidence must be represented explicitly and must be distinguishable from weak but present advisory evidence
- advisory verification results may coexist with successful completion, but they may not silently satisfy a missing mandatory evidence requirement

## Storage Note
The storage backend is implementation-specific. This spec defines the logical shape only.
