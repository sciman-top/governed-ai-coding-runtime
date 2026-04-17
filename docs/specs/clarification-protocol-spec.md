# Clarification Protocol Spec

## Status
Draft

## Purpose
Define when governed execution must stop direct fixing and switch into clarification mode.

## Required Fields
- issue_id
- trigger_threshold
- question_cap
- current_mode
- triggered_mode
- supported_scenarios
- reset_on_confirmation
- required_evidence_fields

## Enumerations

### current_mode / triggered_mode
- direct_fix
- clarify_required

### supported_scenarios
- plan
- requirement
- bugfix
- acceptance

## Invariants
- clarification triggers when the same `issue_id` reaches the configured failure threshold
- `question_cap` may not exceed `3`
- after clarification conclusions are confirmed, the session returns to `direct_fix` and resets the attempt counter to `0`
- clarification evidence must retain `issue_id`, `attempt_count`, `clarification_mode`, `clarification_scenario`, `clarification_questions`, and `clarification_answers`

## Notes
- This contract captures the automatic clarification behavior described in `AGENTS.md`
- it defines the protocol shape only, not the UX wording used by any specific agent frontend
