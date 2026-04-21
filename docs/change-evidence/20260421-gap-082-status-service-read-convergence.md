# 20260421 GAP-082 Status Service-Read Convergence

## Goal
Complete another `GAP-082` convergence slice by routing CLI `status` reads through the control-plane service boundary while preserving existing CLI output fields.

## Scope
- `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
- `scripts/run-governed-task.py`
- `docs/backlog/issue-ready-backlog.md`

## Changes
1. Expanded `inspect_status` payload in `session_bridge` to include:
   - full `maintenance` object fields
   - `tasks` array with operator-facing run/artifact refs
   - existing `total_tasks`, `maintenance_stage`, and `attachments`
2. Updated `run-governed-task.py` `snapshot_payload()` to call `inspect_status` through service dispatch (`/session`) instead of direct `RuntimeStatusStore` reads.
3. Kept CLI output compatibility for:
   - `runtime_roots`
   - `maintenance`
   - `tasks`
   - `attachments`
   - `codex_capability`
4. Updated GAP-082 status note to include status-path wrapper convergence.

## Verification
### Targeted
- `python -m unittest tests.runtime.test_run_governed_task_cli`
- `python -m unittest tests.runtime.test_runtime_status`
- `python -m unittest tests.service.test_session_api tests.service.test_operator_api`

### Gate order
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

## Status Note
`GAP-082` remains in progress; this slice eliminates direct runtime-store reads from CLI status and tightens service-primary read-path consistency.

## Rollback
Revert:
- `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
- `scripts/run-governed-task.py`
- `docs/backlog/issue-ready-backlog.md`
- this evidence file
