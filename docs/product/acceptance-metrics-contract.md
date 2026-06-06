# Acceptance Metrics Contract

## Purpose
Turn the PRD acceptance metrics into executable operating definitions so claims, reviews, and rollout decisions use the same metric vocabulary.

## Scope
- Applies to user-facing product claims, backlog closeout, change evidence, and runtime/operator reporting.
- Complements the PRD metric list; it does not replace repository gates or claim-evidence freshness checks.

## Metric Rules
- Every metric must define: `formula`, `source events`, `window`, `owner`, `display surface`, and `follow-up action`.
- A metric name alone is not proof.
- If a metric cannot yet be computed automatically, it must be marked `manual_review_required` instead of being treated as pass-by-default.

## Core Metrics

### task_completion_rate
- Formula: `completed_tasks / started_tasks`
- Source events: task lifecycle records with `started` and `completed`
- Window: rolling 30 days
- Owner: runtime operator
- Display surface: operator status summary and change evidence closeout
- Follow-up action: if below target, inspect `task_timeout_rate` and `tool_execution_failure_rate`

### validated_completion_rate
- Formula: `tasks_completed_with_full_gate_pass / completed_tasks`
- Source events: task closeout plus `build -> test -> contract/invariant -> hotspot` verification refs
- Window: rolling 30 days
- Owner: runtime operator
- Display surface: claim review and closeout evidence
- Follow-up action: downgrade delivery claims when partial validation dominates

### approval_interruption_rate
- Formula: `tasks_with_escalation / started_tasks`
- Source events: approval records and `PolicyDecision.escalate`
- Window: rolling 30 days
- Owner: governance maintainer
- Display surface: risk posture review
- Follow-up action: tune risk rules only with evidence, not anecdote

### replay_success_rate
- Formula: `successful_replay_attempts / replay_attempts`
- Source events: replay records linked to task ids
- Window: rolling 30 days
- Owner: runtime operator
- Display surface: evidence recovery review
- Follow-up action: block stronger recovery claims if replay coverage degrades

### rollback_success_rate
- Formula: `successful_rollbacks / rollback_attempts`
- Source events: rollback execution refs and operator review
- Window: rolling 30 days
- Owner: runtime operator
- Display surface: risky-write closeout evidence
- Follow-up action: treat low rollback reliability as a release-risk signal

### evidence_completeness_rate
- Formula: `tasks_with_required_evidence_fields / completed_tasks`
- Required fields: `freshness_status`, `target_run_id`, `gate_result`, `verification_command`, `rollback_ref`
- Window: rolling 30 days
- Owner: governance maintainer
- Display surface: claim review and docs gate support
- Follow-up action: downgrade claims and open repair work when completeness drops

### verification_pass_rate
- Formula: `tasks_with_full_gate_pass / tasks_that_ran_verification`
- Source events: verification artifacts
- Window: rolling 30 days
- Owner: runtime operator
- Display surface: operator summary
- Follow-up action: inspect gate bottlenecks before widening rollout

### human_handoff_quality_rate
- Formula: `handoffs_marked_reviewable / handoffs_generated`
- Source events: handoff package review checklist
- Window: rolling 30 days
- Owner: reviewer/operator
- Display surface: delivery closeout evidence
- Follow-up action: improve handoff format if reviewers repeatedly need reconstruction

## Failure Metrics

### unauthorized_action_block_rate
- Formula: `denied_unauthorized_actions / detected_unauthorized_actions`
- Source events: `PolicyDecision.deny`
- Window: rolling 30 days
- Owner: governance maintainer
- Display surface: security/governance review

### false_positive_approval_rate
- Formula: `approvals_marked_unnecessary / approval_interruptions`
- Source events: post-run review tags
- Window: manual review until auto-labeling exists
- Owner: governance maintainer
- Display surface: periodic review
- Status: `manual_review_required`

### task_timeout_rate
- Formula: `timed_out_tasks / started_tasks`
- Source events: task lifecycle and timeout records
- Window: rolling 30 days
- Owner: runtime operator
- Display surface: operator summary

### tool_execution_failure_rate
- Formula: `failed_tool_runs / tool_runs`
- Source events: tool execution records
- Window: rolling 30 days
- Owner: runtime operator
- Display surface: runtime diagnostics

### partial_validation_completion_rate
- Formula: `completed_tasks_with_partial_validation / completed_tasks`
- Source events: task closeout plus verification refs
- Window: rolling 30 days
- Owner: runtime operator
- Display surface: claim review

## Quality Metrics

### full_evidence_bundle_rate
- Formula: `tasks_with_full_evidence_bundle / completed_tasks`
- Source events: evidence bundle artifacts
- Window: rolling 30 days
- Owner: governance maintainer

### repo_specific_gate_execution_rate
- Formula: `tasks_with_repo_specific_gate_refs / completed_tasks`
- Source events: repo-profile verification refs
- Window: rolling 30 days
- Owner: runtime operator

### high_risk_action_intercept_rate
- Formula: `intercepted_high_risk_actions / detected_high_risk_actions`
- Source events: risk classification and approval/deny records
- Window: rolling 30 days
- Owner: governance maintainer

### regression_pass_rate
- Formula: `passing_regression_runs / regression_runs`
- Source events: runtime and service test runs
- Window: rolling 30 days
- Owner: repository maintainer

### safety_eval_pass_rate
- Formula: `passing_safety_eval_runs / safety_eval_runs`
- Source events: safety or governance evaluation artifacts
- Window: rolling 30 days
- Owner: governance maintainer

## Current Reporting Posture
- The repository already enforces freshness and claim-evidence linkage through docs/contract gates.
- It does not yet expose one machine-generated dashboard for every metric above.
- Until that surface exists, rollout and product claims should explicitly state which metrics are machine-checked, which are evidence-backed but sampled, and which remain manual review.

## Verification
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`

## Rollback
- Revert this document and any matching PRD/docs gate updates if the terminology or field contract proves misleading.
