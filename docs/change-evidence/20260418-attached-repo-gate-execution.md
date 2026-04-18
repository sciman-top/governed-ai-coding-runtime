# 20260418 Attached Repo Gate Execution

## Purpose
Close the most practical external-repo gap after attachment: once a target repo is attached and its light pack is healthy, the runtime should be able to execute the declared verification gates inside that target repo instead of only planning them.

## Basis
- `packages/contracts/src/governed_ai_coding_runtime_contracts/verification_runner.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
- `scripts/run-governed-task.py`
- `scripts/session-bridge.py`
- `tests/runtime/test_verification_runner.py`
- `tests/runtime/test_session_bridge.py`
- `tests/runtime/test_run_governed_task_cli.py`

## Problem
- `session-bridge request-gate` originally returned local repo defaults unless additional attachment-aware resolution was added.
- Even after attachment-aware planning, operators still lacked a direct runtime entrypoint to execute those attached target-repo gates in the target repo working directory.
- That left external-repo usage at posture plus plan only, not posture plus declared verification execution.

## Changes
- extracted repo-profile gate resolution into `build_repo_profile_verification_plan(...)`
- updated the session bridge to use the shared repo-profile gate-plan builder when attachment inputs are present
- added `run-governed-task.py verify-attachment`
  - validates the attached repo light pack
  - loads the attached repo profile
  - builds quick/full verification plans from attached repo declarations
  - executes those gate commands in the attached repo working directory
  - persists verification-output artifacts through the existing local artifact store
- hardened gate execution output decoding to `utf-8` with replacement so external repo commands such as `dotnet test` do not break the local runner on Windows locale mismatches
- updated the existing-repo quickstart to show:
  - attachment-aware `request-gate`
  - attached repo gate execution through `verify-attachment`

## Verification
1. `python -m unittest tests.runtime.test_verification_runner tests.runtime.test_session_bridge tests.runtime.test_run_governed_task_cli -v`
   - exit `0`
2. `python scripts/run-governed-task.py verify-attachment --help`
   - exit `0`
3. `python scripts/session-bridge.py request-gate --help`
   - exit `0`
4. `python scripts/run-governed-task.py verify-attachment --attachment-root "D:\OneDrive\CODE\ClassroomToolkit" --attachment-runtime-state-root "D:\OneDrive\CODE\governed-ai-coding-runtime\.runtime\attachments\classroomtoolkit" --mode quick --task-id "task-classroom-verify-001" --run-id "run-classroom-verify-001" --json`
   - exit `0`
   - `gate_order`: `["test", "contract"]`
   - `results.test = pass`
   - `results.contract = pass`

## Outcome
The external-repo flow now covers:
- attach
- posture inspection
- attachment-aware gate planning
- execution of declared verification gates inside the target repo

It still does not mean full runtime-owned direct Codex write execution inside the target repo.

## Rollback
- revert `build_repo_profile_verification_plan(...)`
- revert `run-governed-task.py verify-attachment`
- revert the updated quickstart and session bridge docs
