# Continuous Execution Task Board Template

## Task Identity
- task_id:
- title:
- queue_ref: `Continuous-Execution`
- phase:
- owner_mode:
  - `autonomous`
  - `owner_directed`

## Goal
- goal:

## Scope
- in_scope:
  - 
- out_of_scope:
  - 

## Acceptance
- acceptance_criteria:
  - [ ] 
  - [ ] 
  - [ ] 

## Verification
- verification_commands:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- expected_gate_outcome:
  - 
- manual_checks:
  - 

## Evidence
- evidence_refs:
  - 
- required_evidence_alignment:
  - `goal`
  - `acceptance_criteria`
  - `verification_results`
  - `rollback_ref`
  - `open_questions`

## Rollback
- rollback_ref:
- rollback_steps:
  - 

## Interaction Controls
- signal:
  - signal_id:
  - signal_kind:
  - summary:
- policy:
  - policy_id:
  - mode:
  - posture:
- budget_snapshot:
  - budget_status:
  - total_token_budget:
  - used_explanation_tokens:
  - used_clarification_tokens:
  - used_compaction_tokens:

## Open Questions
- open_questions:
  - 
