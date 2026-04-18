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
- trial_id when the run is part of a multi-repo onboarding trial

## Trace Grading Goals
- evidence should be sufficient for replay
- key policy decisions should be observable
- grading should report coverage, not just presence of logs
- multi-repo trial traces should separate repo-specific fixes from onboarding-generic, adapter-generic, and contract-generic follow-ups

## Phase Guidance
- Phase 1: emit required fields and basic eval results
- Phase 2: add coverage thresholds and replay-readiness checks
- Phase 3: add trace grading gates tied to promotion or rollout
