# 20260418 Local Session Bridge Entrypoint

## Goal
Implement `GAP-036 Task 5` by adding the first local session bridge entrypoint and runtime helper surface.

## Landing
- Source plan: `docs/plans/interactive-session-productization-implementation-plan.md`
- Target destination:
  - runtime helper: `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
  - CLI: `scripts/session-bridge.py`
  - write governance normalization: `packages/contracts/src/governed_ai_coding_runtime_contracts/write_tool_runner.py`
  - tests: `tests/runtime/test_session_bridge.py`
  - docs: `docs/product/session-bridge-commands.md`

## Changes
- Added `SessionBridgeResult`.
- Added `handle_session_bridge_command`.
- Added local bridge support for:
  - binding an existing task to a repo binding id
  - reading attached repo posture
  - reading runtime status without mutating task state
  - requesting quick/full verification plans through the existing verification runner plan path
  - returning approval-required results for escalation
  - returning explicit degrade results for unsupported local bridge capabilities
- Added `scripts/session-bridge.py` with subcommands:
  - `bind-task`
  - `repo-posture`
  - `status`
  - `request-gate`
- Added write governance normalization into PolicyDecision:
  - allowed -> `allow`
  - paused -> `escalate`
  - denial helper -> `deny`

## TDD Evidence

### Red
- `cmd`: `python -m unittest tests.runtime.test_session_bridge -v`
- `exit_code`: `1`
- `key_output`: missing `handle_session_bridge_command`; missing `scripts/session-bridge.py`; missing `policy_decision_from_write_governance`
- `timestamp`: `2026-04-18`

### Green
- `cmd`: `python -m unittest tests.runtime.test_session_bridge tests.runtime.test_write_tool_runner -v`
- `exit_code`: `0`
- `key_output`: `Ran 20 tests in 1.414s`; `OK`
- `timestamp`: `2026-04-18`

## Verification
- `cmd`: `python -m unittest tests.runtime.test_session_bridge -v`
- `exit_code`: `0`
- `key_output`: `Ran 15 tests in 1.413s`; `OK`
- `timestamp`: `2026-04-18`

- `cmd`: `python scripts/session-bridge.py --help`
- `exit_code`: `0`
- `key_output`: `Local governed session bridge.`
- `timestamp`: `2026-04-18`

- `cmd`: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `exit_code`: `0`
- `key_output`: `Ran 159 tests in 26.369s`; `OK`; `OK runtime-unittest`
- `timestamp`: `2026-04-18`

## Risks
- `request-gate` currently requests a verification plan and does not execute long-running gate commands directly.
- Evidence inspection is explicitly degraded to manual handoff until the evidence query surface is implemented.
- Adapter capability detection remains future adapter registry work.

## Rollback
- Revert:
  - `scripts/session-bridge.py`
  - Task 5 additions in `session_bridge.py`
  - PolicyDecision normalization helpers in `write_tool_runner.py`
  - Task 5 tests in `tests/runtime/test_session_bridge.py`
  - Task 5 docs in `docs/product/session-bridge-commands.md`
- Re-run:
  - `python -m unittest tests.runtime.test_session_bridge tests.runtime.test_write_tool_runner -v`
  - `python scripts/session-bridge.py --help`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
