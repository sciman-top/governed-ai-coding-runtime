# 20260421 GAP-082 Closeout And GAP-083 Operator Write-Status Baseline

## Goal
Close `GAP-082` after all acceptance criteria passed, and start `GAP-083` with the first operator remediation-depth query slice for approval/write status diagnostics.

## Scope
- `packages/agent-runtime/service_facade.py`
- `apps/control-plane/routes/operator.py`
- `tests/service/test_operator_api.py`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/README.md`
- `docs/backlog/full-lifecycle-backlog-seeds.md`

## Changes
1. Added operator `write_status` service route wiring:
   - new facade method `operator_write_status(...)`
   - new operator action `write_status`
2. Extended operator parity test to cover `write_status` through control-plane route vs direct session-bridge result parity.
3. Closed `GAP-082` status in backlog and promoted `GAP-083` to in-progress.
4. Synced near-term active queue wording across backlog entry docs:
   - completed: `GAP-080` through `GAP-082`
   - active: `GAP-083` through `GAP-084`

## Verification
### Targeted
- `python -m unittest tests.service.test_operator_api`
- `python -m unittest tests.service.test_session_api`
- `python -m unittest tests.runtime.test_run_governed_task_cli tests.runtime.test_run_governed_task_service_wrapper`

### Gate order
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

## Status Note
- `GAP-082`: complete on current branch baseline.
- `GAP-083`: in progress with an initial operator remediation-depth surface (`write_status`) now queryable through service boundary routes and parity-tested.

## Rollback
Revert:
- `packages/agent-runtime/service_facade.py`
- `apps/control-plane/routes/operator.py`
- `tests/service/test_operator_api.py`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/README.md`
- `docs/backlog/full-lifecycle-backlog-seeds.md`
- this evidence file
