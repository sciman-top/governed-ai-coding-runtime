# Eval And Trace Grading Spec

## Status
Draft

## Purpose
Define the minimum evaluation, trace grading, and postmortem-input policy that turns runtime traces into replay-safe and proposal-safe governance signals.

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
- evidence_refs
- policy_decision_refs
- outcome_summary
- replay_artifact_ref
- review_feedback_refs when a human review exists
- trial_id when the run is part of a multi-repo onboarding trial

## Trace Grading Dimensions
Trace grading must score the run across four dimensions instead of collapsing everything into one pass or fail bit:

### evidence_completeness
- `pass`: execution, approvals, checkpoints, and rollback evidence can all be resolved.
- `warn`: evidence exists but one or more non-critical references are incomplete.
- `fail_missing_evidence`: required evidence needed for replay, audit, or rollback is absent.

### workflow_correctness
- `pass`: the recorded workflow stayed inside the declared risk, approval, and control boundaries.
- `warn`: the workflow completed but required a manual fallback or explicit degrade path.
- `fail_policy_miss`: the run crossed a policy, approval, or control boundary without a valid recorded decision.

### replay_readiness
- `pass`: the run can be reconstructed from commands, checkpoints, artifacts, and refs.
- `warn`: replay is possible but requires operator-side reconstruction steps.
- `fail_replay_gap`: the trace is not replayable from the recorded refs.

### outcome_quality
- `pass`: the run met the declared acceptance target.
- `warn`: the run is usable but carries unresolved gaps or degraded quality.
- `fail_poor_outcome`: the run finished with poor or incorrect outcome quality even if evidence exists.

## Failure Classifications
The grading policy must distinguish at least these failure classes:
- `missing_evidence`
- `policy_miss`
- `replay_gap`
- `poor_outcome_quality`
- `reviewer_disagreement`
- `repeated_failure_signature`
- `misalignment_not_caught`
- `over_explained_under_budget_pressure`
- `under_explained_with_high_user_confusion`
- `repeated_question_without_signal_upgrade`
- `observation_gap_ignored`
- `compression_without_recoverable_summary`

The first four classes come directly from trace grading. The remaining classes are postmortem input classes that can enrich later improvement proposals without being treated as runtime execution success.

## Postmortem Input Model
Failed runs and reviewer feedback must be normalized into explicit postmortem inputs rather than ad hoc notes.

### Required Postmortem Sources
- `failed_run`
- `review_feedback`
- `repeated_failure_signature`

### Required Postmortem Fields
- `input_id`
- `source_kind`
- `summary`
- `evidence_refs`
- `affected_dimensions`
- `failure_classifications`
- `follow_up_scope`
- `recorded_at`

### Interaction Failure Inputs
Interaction-quality failures must remain postmortem-ready inputs instead of a fifth primary grading dimension.

When an interaction failure classification is recorded, the input should also capture:
- the triggering evidence refs
- the affected trace-grading dimensions
- the affected interaction signal or policy refs when available
- whether the failure came from over-explaining, under-explaining, missed alignment, or unrecoverable compression

### follow_up_scope
- `kernel`
- `adapter`
- `repo`
- `docs`
- `control`

## Invariants
- Trace grading must evaluate `evidence_completeness`, `workflow_correctness`, `replay_readiness`, and `outcome_quality` for every governed run.
- `missing_evidence` and `replay_gap` are fail-closed grades and cannot be downgraded into warnings.
- `policy_miss` must point to at least one missing or incompatible `policy_decision_ref` or approval reference.
- Postmortem inputs must link back to one or more evidence references and at least one affected trace-grading dimension.
- Interaction-oriented postmortem inputs may enrich the postmortem record, but they must not autonomously mutate policy or overwrite the original four trace grades.
- Reviewer feedback may generate a postmortem input even when runtime gates passed, but it must not rewrite the original trace grades.
- Repeated-failure signatures may aggregate multiple runs, but they must retain the member run refs instead of replacing them with one anecdotal summary.

## Governance Loop Integration
The minimum governance loop must keep this order:
1. governed execution records evidence
2. evidence persistence closes the runtime-owned trace
3. trace grading evaluates the four dimensions
4. postmortem inputs are created from failed runs, reviewer feedback, or repeated failure signatures
5. later governance tasks may generate controlled improvement proposals from those inputs

Trace grading and postmortem capture therefore sit after evidence persistence and before any future proposal-generation surface.

## Phase Guidance
- Phase 1: emit the required fields, the four grading dimensions, and explicit failure classifications.
- Phase 2: require postmortem-ready inputs for failed runs and reviewer disagreement.
- Phase 3: connect trace grading and postmortem inputs to later rollout and controlled-improvement tasks.

## Non-Goals
- automatically mutating policy or kernel behavior from trace output
- replacing approval, evidence, or replay records with summary grades
- treating reviewer comments as authoritative without linked evidence
