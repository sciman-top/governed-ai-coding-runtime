# 20260421 GAP-080 Live Loop Closure Runtime-Check Hardening

## Goal
Implement the second executable slice of `GAP-080` so one runtime-check write loop can:
- keep one explicit session/resume/continuation identity across gate + write steps
- produce runtime-owned closure diagnostics that explicitly distinguish live vs fallback posture
- expose attachment-scoped inspect evidence and handoff surfaces in the same run output

## Scope
- `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
- `scripts/run-governed-task.py`
- `scripts/session-bridge.py`
- `scripts/runtime-check.ps1`
- `scripts/runtime-flow.ps1`
- `tests/runtime/test_session_bridge.py`
- `tests/runtime/test_attached_repo_e2e.py`
- `docs/quickstart/use-with-existing-repo.md`
- `docs/quickstart/use-with-existing-repo.zh-CN.md`

## Changes
1. Session bridge adapter-event persistence now reuses the already-resolved `session_identity` of each command path and writes it into adapter-event artifacts.
2. Runtime task CLI write surfaces now accept explicit identity fields:
   - `--session-id`
   - `--resume-id`
   - `--continuation-id`
3. `decide-attachment-write` now accepts `--task-id` so approval continuation can stay on the same governed task lineage instead of drifting to a fixed placeholder id.
4. `execute-attachment-write` now propagates request identity into execute identity when explicit identity is not re-supplied.
5. `runtime-check.ps1` now:
   - derives stable default `session_id` / `resume_id` / `continuation_id`
   - threads those identities through request-gate + write-governance + approval + execute + write-status
   - runs `inspect-evidence` and `inspect-handoff` in write-flow mode
   - emits `live_loop` diagnostics with `flow_kind`, continuity booleans, closure state, fallback explicitness, and linked runtime refs
6. `session-bridge.py` inspect commands now accept attachment-root arguments so runtime-check can query attachment-scoped evidence/handoff directly.
7. E2E + contract tests were extended to assert closure-summary and adapter-event identity linkage.

## Verification
### Targeted tests
- `python -m unittest tests.runtime.test_session_bridge -v`
- `python -m unittest tests.runtime.test_attached_repo_e2e -v`
- `python -m unittest tests.runtime.test_run_governed_task_cli -v`

### Mandatory gate order
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

### Additional checks
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`

All commands passed on the current branch.

## Risks
- This slice strengthens executable closure diagnostics and identity continuity, but complete `GAP-080` still depends on sustained real-host evidence freshness, not only local runtime tests.

## Rollback
Revert these files to pre-change state:
- `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
- `scripts/run-governed-task.py`
- `scripts/session-bridge.py`
- `scripts/runtime-check.ps1`
- `scripts/runtime-flow.ps1`
- `tests/runtime/test_session_bridge.py`
- `tests/runtime/test_attached_repo_e2e.py`
- `docs/quickstart/use-with-existing-repo.md`
- `docs/quickstart/use-with-existing-repo.zh-CN.md`
- `docs/change-evidence/20260421-gap-080-live-loop-closure-runtime-check.md`
