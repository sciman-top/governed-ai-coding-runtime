# Response Policy Spec

## Status
Draft

## Purpose
Define the bounded response policy that selects how a governed session should respond once one or more interaction signals have been observed.

## Required Fields
- policy_id
- task_id
- mode
- teaching_level
- clarification_mode
- compression_mode
- max_questions
- max_observation_items
- term_explain_limit
- restatement_required
- stop_or_escalate
- rationale_signal_ids

## Optional Fields
- run_id
- posture
- checklist_kind
- summary_template
- notes

## Enumerations

### mode
- terse
- guided
- teaching

### teaching_level
- none
- term_only
- concept_only
- task_scoped

### clarification_mode
- none
- light
- required

### compression_mode
- none
- stage_summary
- aggressive_compaction
- ref_only

### stop_or_escalate
- continue
- pause_for_user_input
- switch_to_checklist
- handoff_only
- stop_on_budget

### posture
- aligned
- clarifying
- guiding
- teaching
- compressing
- handoff_only
- stopped_on_budget

## Invariants
- response policy must remain task-scoped rather than acting as a global personality setting
- `max_questions` may not exceed the clarification cap declared by the active clarification protocol
- `mode=teaching` may not imply unlimited explanation scope; explanation must remain bounded by `term_explain_limit`, posture, and active budget
- `compression_mode=ref_only` or `stop_or_escalate=handoff_only` must preserve enough evidence references for replay or operator takeover
- response policy may reduce verbosity or switch to checklist-first guidance, but it may not weaken approval requirements, canonical gate order, or explicit degrade semantics
- `restatement_required=true` is allowed only when the task scope being restated is reviewable from task or evidence state

## Notes
- This contract governs the shape of the next response, not the full transcript history.
- It exists to make interaction behavior explicit, reviewable, and bounded.

