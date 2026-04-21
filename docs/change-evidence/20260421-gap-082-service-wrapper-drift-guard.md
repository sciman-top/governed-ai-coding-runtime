# 20260421 GAP-082 Service Wrapper Drift Guard

## Goal
Enforce merge-time detection of service-wrapper drift so wrapper CLI paths cannot silently fall back to direct session-bridge logic.

## Scope
- `scripts/verify-repo.ps1`
- `docs/backlog/issue-ready-backlog.md`

## Changes
1. Added runtime verification sentinel in `Invoke-RuntimeChecks`:
   - scans `scripts/run-governed-task.py` for forbidden direct session-bridge tokens:
     - `build_session_bridge_command(`
     - `handle_session_bridge_command(`
2. Runtime check now fails immediately if either token reappears in wrapper CLI script.
3. Added runtime gate signal:
   - `OK runtime-service-wrapper-drift-guard`
4. Marked GAP-082 acceptance criterion "`parity drift fails verification before merge`" as complete.

## Verification
### Runtime gate
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - `OK runtime-unittest`
  - `OK runtime-service-parity`
  - `OK runtime-service-wrapper-drift-guard`

### Additional gates
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

## Status Note
`GAP-082` is still in progress; wrapper-drift blocking is active, while full service-boundary convergence of remaining CLI parallel logic is pending.

## Rollback
Revert:
- `scripts/verify-repo.ps1`
- `docs/backlog/issue-ready-backlog.md`
- this evidence file
