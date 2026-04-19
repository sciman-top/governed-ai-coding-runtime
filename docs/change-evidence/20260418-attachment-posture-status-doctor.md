# 20260418 Attachment Posture Status Doctor

## Goal
Implement `GAP-035 Task 3` so runtime status and doctor can report target-repo attachment posture while preserving the existing local-baseline status path.

## Landing
- Source plan: `docs/plans/interactive-session-productization-implementation-plan.md`
- Target destination:
  - posture inspector: `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_attachment.py`
  - status read model: `packages/contracts/src/governed_ai_coding_runtime_contracts/runtime_status.py`
  - status CLI: `scripts/run-governed-task.py`
  - doctor CLI: `scripts/doctor-runtime.ps1`
  - tests: `tests/runtime/test_runtime_status.py`, `tests/runtime/test_runtime_doctor.py`
  - docs: `docs/product/target-repo-attachment-flow.md`

## Changes
- Added `RepoAttachmentPosture` and `inspect_attachment_posture`.
- Added status read-model support for attached repo id, binding id, binding state, light-pack path, adapter preference, gate profile, and reason.
- Added optional `status --attachment-root --attachment-runtime-state-root` inputs.
- Added optional doctor `-AttachmentRoot -RuntimeStateRoot` posture check.
- Doctor now distinguishes:
  - missing light pack
  - invalid light pack
  - stale binding
  - healthy binding
- Kept default `status --json` and default `doctor-runtime.ps1` behavior working without attachment arguments.

## 2026-04-20 Remediation And Fail-Closed Update (Task 14)
- `RepoAttachmentPosture` now carries:
  - `remediation`
  - `fail_closed`
- `inspect_attachment_posture` now returns explicit remediation guidance for:
  - `missing_light_pack`
  - `invalid_light_pack`
  - `stale_binding`
- `scripts/doctor-runtime.ps1` now enforces fail-closed behavior when attachment posture is unhealthy:
  - prints `FAIL attachment-posture-<state>`
  - prints `REMEDIATE <command>`
  - exits non-zero
- `RuntimeStatusStore` and session/operator query surfaces now expose attachment `remediation` and `fail_closed`.

## TDD Evidence

### Red
- `cmd`: `python -m unittest tests.runtime.test_runtime_status tests.runtime.test_runtime_doctor -v`
- `exit_code`: `1`
- `key_output`: `RuntimeStatusStore.__init__() got an unexpected keyword argument 'attachment_roots'`; missing `OK attachment-posture-missing-light-pack`
- `timestamp`: `2026-04-18`

### Green
- `cmd`: `python -m unittest tests.runtime.test_runtime_status tests.runtime.test_runtime_doctor -v`
- `exit_code`: `0`
- `key_output`: `Ran 12 tests in 11.416s`; `OK`
- `timestamp`: `2026-04-18`

## Verification
- `cmd`: `python scripts/run-governed-task.py status --json`
- `exit_code`: `0`
- `key_output`: JSON includes `attachments: []`, `maintenance.stage: completed`, and `total_tasks: 0`
- `timestamp`: `2026-04-18`

- `cmd`: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
- `exit_code`: `0`
- `key_output`: `OK runtime-status-surface`; `OK maintenance-policy-visible`; `OK adapter-posture-visible`
- `timestamp`: `2026-04-18`

- `cmd`: `python -m unittest tests.runtime.test_runtime_doctor tests.runtime.test_repo_attachment tests.runtime.test_runtime_status tests.runtime.test_operator_queries tests.runtime.test_session_bridge -v`
- `exit_code`: `0`
- `key_output`: `Ran 60 tests`; `OK`
- `timestamp`: `2026-04-20`

## Risks
- Stale binding detection currently checks light-pack binding id against the repo profile repo id. Later attachment metadata may add a stronger binding version or content hash.
- Attachment inspection remains opt-in for status and doctor. Automatic discovery across many repositories remains later multi-repo work.
- Fail-closed enforcement is posture-level and attachment-scoped; richer per-control remediation workflows are still future work.

## Rollback
- Revert:
  - posture inspector additions in `repo_attachment.py`
  - attachment read-model additions in `runtime_status.py`
  - attachment CLI parameters in `scripts/run-governed-task.py`
  - attachment doctor parameters in `scripts/doctor-runtime.ps1`
  - Task 3 tests and docs
- Re-run:
  - `python -m unittest tests.runtime.test_runtime_status tests.runtime.test_runtime_doctor -v`
  - `python scripts/run-governed-task.py status --json`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
