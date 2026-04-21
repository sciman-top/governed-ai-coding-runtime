# Interaction Evidence Spec

## Status
Draft

## Purpose
Define the structured interaction evidence that explains why a governed session restated the task, asked clarifying questions, switched to checklist-first guidance, explained a term, compacted context, degraded behavior, or stopped on budget.

## Required Fields
- interaction_evidence_id
- task_id
- applied_policy_ref
- trigger_signal_refs
- task_restatement
- clarification_questions
- clarification_answers
- observation_checklist
- terms_explained
- compression_action
- before_after_summary
- budget_snapshot
- outcome_assessment
- created_at

## Optional Fields
- run_id
- stop_or_degrade_reason
- replay_refs
- operator_follow_up_refs
- notes

## Enumerations

### compression_action
- none
- stage_summary
- aggressive_compaction
- ref_only

### outcome_assessment
- alignment_improved
- still_blocked
- awaiting_user_input
- degraded_on_budget
- handed_off

## Invariants
- interaction evidence must reference the response policy and one or more triggering interaction signals
- missing clarification answers must remain explicit when clarification is pending rather than being silently omitted
- checklist-first guidance must be preserved as structured `observation_checklist` output instead of buried in free-form notes
- `compression_action=ref_only` must preserve sufficient summary or references for replay or operator handoff
- interaction evidence may extend an evidence bundle, but it may not replace the task-level evidence model or create a parallel system of record
- budget snapshots must be tied to reviewable budget state rather than transcript-only claims

## Notes
- This contract is designed to plug into the existing evidence bundle as a structured extension.
- It captures why the interaction posture changed, not just what the assistant happened to say.

