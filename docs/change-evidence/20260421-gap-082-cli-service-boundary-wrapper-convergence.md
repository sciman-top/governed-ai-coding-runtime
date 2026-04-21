# 20260421 GAP-082 CLI Service-Boundary Wrapper Convergence

## Goal
Reduce `GAP-082` drift risk by routing attached execution CLI flows through the control-plane service boundary instead of direct session-bridge calls.

## Scope
- `scripts/run-governed-task.py`
- `docs/backlog/issue-ready-backlog.md`

## Changes
1. Reworked attached execution-related CLI flows to dispatch through control-plane session routes:
   - `verify-attachment`
   - `govern-attachment-write`
   - `decide-attachment-write`
   - `execute-attachment-write`
2. Added internal control-plane module-loading and dispatch helpers in `run-governed-task.py`:
   - `_load_module`
   - `_build_control_plane_app`
   - `_dispatch_session_command`
   - `_response_payload`
3. Preserved existing CLI output payload contract while moving implementation path to service boundary dispatch.
4. Updated `GAP-082` backlog status wording and marked execution-like API/CLI parity criterion complete.

## Verification
### Targeted
- `python -m unittest tests.runtime.test_run_governed_task_cli`
- `python -m unittest tests.service.test_session_api tests.service.test_operator_api`

### Gate order
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

## Status Note
`GAP-082` remains in progress. This slice converges attached execution paths to service boundaries; full closeout still requires finishing all remaining parallel CLI/runtime logic convergence and proving merge-time drift coverage across the complete wrapper surface.

## Rollback
Revert:
- `scripts/run-governed-task.py`
- `docs/backlog/issue-ready-backlog.md`
- this evidence file
