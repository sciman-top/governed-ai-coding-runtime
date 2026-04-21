# 20260421 GAP-082 Service-Primary Convergence Runtime-Gate Baseline

## Goal
Implement the first executable slice of `GAP-082 NTP-03` by enforcing API/CLI parity checks in runtime verification gates.

## Scope
- `scripts/verify-repo.ps1`
- `docs/backlog/issue-ready-backlog.md`

## Changes
1. Extended `Invoke-RuntimeChecks` to run service API parity tests after runtime unit tests:
   - `python -m unittest tests.service.test_session_api`
2. Added explicit runtime gate signal:
   - `OK runtime-service-parity`
3. Promoted backlog status for `GAP-082` from planned to in progress.

## Verification
### Targeted
- `python -m unittest tests.service.test_session_api -v`

### Gate check
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - includes both:
    - runtime unit suite (`tests/runtime`)
    - service parity suite (`tests.service.test_session_api`)

## Status Note
This is a baseline convergence slice for `GAP-082`; full closeout still requires proving wrapper-only CLI behavior and broader parity drift coverage across execution-like commands and operator reads.

## Rollback
Revert:
- `scripts/verify-repo.ps1`
- `docs/backlog/issue-ready-backlog.md`
- this evidence file
