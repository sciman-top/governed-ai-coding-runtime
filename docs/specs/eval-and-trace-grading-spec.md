# Eval And Trace Grading Spec

## Status
Draft

## Purpose
Define the minimum evaluation and trace-quality expectations for governed AI coding.

## Required Eval Suites
- smoke
- regression
- adversarial
- cost

## Required Trace Fields
- run_id
- task_id
- repo_id
- issue_or_goal_ref
- decision_score
- reason_codes
- hard_guard_hits
- checkpoint_refs
- rollback_ref

## Trace Grading Goals
- evidence should be sufficient for replay
- key policy decisions should be observable
- grading should report coverage, not just presence of logs

## Phase Guidance
- Phase 1: emit required fields and basic eval results
- Phase 2: add coverage thresholds and replay-readiness checks
- Phase 3: add trace grading gates tied to promotion or rollout
