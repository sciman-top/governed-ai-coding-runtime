# 20260418 Launch-Second Fallback

## Goal
Implement `GAP-036 Task 6` by making launch-second fallback explicit and preserving manual handoff when process bridge capability is unavailable.

## Landing
- Source plan: `docs/plans/interactive-session-productization-implementation-plan.md`
- Target destination:
  - launch helper: `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
  - minimal adapter fallback helper: `packages/contracts/src/governed_ai_coding_runtime_contracts/adapter_registry.py`
  - CLI: `scripts/session-bridge.py`
  - tests: `tests/runtime/test_session_bridge.py`, `tests/runtime/test_adapter_registry.py`
  - docs: `docs/product/session-bridge-commands.md`, `docs/product/adapter-degrade-policy.md`

## Changes
- Added explicit `run_launch_mode`.
- Added process bridge capture for:
  - launch mode
  - adapter tier
  - exit code
  - stdout
  - stderr
  - changed files
  - deleted files
  - verification references
- Added `manual_handoff_result`.
- Added minimal `resolve_launch_fallback` helper for native attach, process bridge, and manual handoff fallback.
- Added `session-bridge.py launch`.
- Documented that process bridge launch is not native attach.

## TDD Evidence

### Red
- `cmd`: `python -m unittest tests.runtime.test_session_bridge -v`
- `exit_code`: `1`
- `key_output`: missing `run_launch_mode`; missing `adapter_registry`; invalid CLI choice `launch`
- `timestamp`: `2026-04-18`

### Green
- `cmd`: `python -m unittest tests.runtime.test_session_bridge tests.runtime.test_adapter_registry -v`
- `exit_code`: `0`
- `key_output`: `Ran 22 tests in 1.738s`; `OK`
- `timestamp`: `2026-04-18`

## Verification
- `cmd`: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- `exit_code`: `0`
- `key_output`: `OK active-markdown-links`; `OK backlog-yaml-ids`; `OK old-project-name-historical-only`
- `timestamp`: `2026-04-18`

- `cmd`: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `exit_code`: `0`
- `key_output`: `Ran 166 tests in 28.307s`; `OK`; `OK runtime-unittest`
- `timestamp`: `2026-04-18`

## Risks
- This is a minimal launch-second helper, not the full adapter registry planned for `GAP-038`.
- Changed-file discovery is filesystem based for process bridge capture. Git-aware diff recovery can be added when adapter evidence mapping is implemented.
- Process bridge capture does not imply native attach guarantees.

## Rollback
- Revert:
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/adapter_registry.py`
  - launch additions in `session_bridge.py`
  - launch additions in `scripts/session-bridge.py`
  - Task 6 tests and docs
- Re-run:
  - `python -m unittest tests.runtime.test_session_bridge tests.runtime.test_adapter_registry -v`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
