# 2026-05-01 GAP-141 Historical Problem-Trace Closure Policy

## Goal
Close `GAP-141` by turning historical problem-trace handling from an implicit backlog habit into an explicit rolling-window retention and closure policy.

## Root Cause And Changes
- The effect report already distinguished current pass/fail state from historical failures, but it did not expose one explicit machine-readable policy for when a historical problem trace remains open or can stop emitting backlog pressure.
- Added `historical_problem_trace_policy` to the target-repo reuse effect report.
- Kept the rule simple and evidence-bound:
  - use the rolling KPI window
  - keep the backlog candidate while `problem_run_rate > 0`
  - close only when the active rolling window no longer contains the latest problem trace
  - never collapse historical failures into the current pass-state claim
- Added verifier coverage and test assertions for the new policy fields.

## Verification
- `python -m unittest tests.runtime.test_target_repo_reuse_effect_feedback`
  - result: `OK`
- `python scripts/build-target-repo-reuse-effect-report.py --target classroomtoolkit`
  - result: report includes `historical_problem_trace_policy.window_kind=rolling`
  - result: report includes the explicit `claim_guard`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  - result: passes with the new policy fields and evidence docs present

## Risks
- The closure rule intentionally keeps backlog pressure while the rolling KPI window still contains historical failures, even if the latest run is passing.
- If the KPI window contract changes, this policy must be updated in lockstep.

## Rollback
Revert the effect-report policy fields, verifier/test updates, and backlog/status/doc updates that mark `GAP-141` complete.
