# 20260614 Conditional Queue Promotion Guard

## Goal
- current landing: `D:\CODE\governed-ai-coding-runtime`
- target home:
  - `scripts/verify-planning-status.py`
  - `tests/runtime/test_planning_status.py`
  - `docs/change-evidence/20260614-conditional-queue-promotion-guard.md`
- verification path: convert the conditional-queue activation boundary from prose-only guidance into a fail-closed planning-status verifier rule without promoting any new active queue

## Why This Slice Was Needed
- The repository already states that `GAP-165..168` and other conditional follow-on queues cannot become active work without promotion evidence plus a `planning-status.json` update.
- Before this change, that boundary was spread across plan and backlog prose, but `scripts/verify-planning-status.py` did not explicitly fail when those conditional-promotion guard snippets drifted or disappeared.
- The current selector still returns `defer_ltp_and_refresh_evidence`, so the safest autonomous continuation is to harden the activation guard rather than to start a conditional queue early.

## Change Summary
- Added conditional-queue promotion guard checks to `scripts/verify-planning-status.py`.
- The verifier now fail-closes when the active queue remains `GAP-159..164` but required promotion-boundary snippets disappear from:
  - `docs/plans/README.md`
  - `docs/backlog/README.md`
  - `docs/plans/host-family-capability-operationalization-plan.md`
  - `docs/plans/continuous-execution-readiness-and-rollout-plan.md`
- Added a focused regression test proving the planning-status verifier rejects an incomplete conditional-promotion guard surface.

## Verification
- `python -m unittest tests.runtime.test_planning_status`
  - result: pass
  - result: `Ran 4 tests`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  - result: pass
  - key output includes `OK planning-status`

## Queue Boundary
- This slice does **not** promote `GAP-165..168`.
- This slice does **not** activate `Continuous Execution Readiness And Rollout`.
- This slice only hardens the machine-checkable rule that later promotion must be explicit and reviewable.

## Risk
- risk_level: `low`
- reason: verifier and test hardening only; no runtime behavior, queue selection, or target-repo mutation changed

## Rollback
- revert:
  - `scripts/verify-planning-status.py`
  - `tests/runtime/test_planning_status.py`
  - `docs/change-evidence/20260614-conditional-queue-promotion-guard.md`
- re-run:
  - `python -m unittest tests.runtime.test_planning_status`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
