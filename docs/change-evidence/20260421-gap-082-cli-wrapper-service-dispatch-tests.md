# 20260421 GAP-082 CLI Wrapper Service-Dispatch Tests

## Goal
Provide executable proof that wrapper CLI execution/read paths dispatch through control-plane service boundaries rather than parallel direct runtime flows.

## Scope
- `tests/runtime/test_run_governed_task_service_wrapper.py`
- `docs/backlog/issue-ready-backlog.md`

## Changes
1. Added wrapper-focused unit tests that patch control-plane app construction and assert `/session` dispatch command types for:
   - `snapshot_payload -> inspect_status`
   - `govern_attachment_write -> write_request`
   - `decide_attachment_write -> write_approve`
   - `execute_attachment_write -> write_request + write_execute`
   - `run_attachment_verification -> run_quick_gate`
2. Kept existing payload contracts while asserting service-boundary call semantics.
3. Marked GAP-082 acceptance criterion "`CLI behavior is implemented through service boundaries rather than parallel runtime logic`" as complete.

## Verification
### Targeted
- `python -m unittest tests.runtime.test_run_governed_task_service_wrapper`
- `python -m unittest tests.runtime.test_run_governed_task_cli tests.service.test_session_api tests.service.test_operator_api`

### Runtime gate
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - includes wrapper drift guard and full runtime/service parity suites

## Status Note
This evidence closes the remaining GAP-082 acceptance criterion by adding direct test proof of wrapper-to-service dispatch for CLI execution/read surfaces.

## Rollback
Revert:
- `tests/runtime/test_run_governed_task_service_wrapper.py`
- `docs/backlog/issue-ready-backlog.md`
- this evidence file
