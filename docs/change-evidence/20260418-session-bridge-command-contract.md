# 20260418 Session Bridge Command Contract

## Goal
Implement `GAP-036 Task 4` by defining the first stable session bridge command contract for governed actions callable from an active AI coding session.

## Landing
- Source plan: `docs/plans/interactive-session-productization-implementation-plan.md`
- Target destination:
  - spec: `docs/specs/session-bridge-command-spec.md`
  - schema: `schemas/jsonschema/session-bridge-command.schema.json`
  - Python contract: `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
  - tests: `tests/runtime/test_session_bridge.py`
  - product doc: `docs/product/session-bridge-commands.md`

## Changes
- Added `SessionBridgeCommand`.
- Added `build_session_bridge_command`.
- Added command types:
  - `bind_task`
  - `show_repo_posture`
  - `request_approval`
  - `run_quick_gate`
  - `run_full_gate`
  - `inspect_evidence`
  - `inspect_status`
- Added execution modes:
  - `read_only`
  - `execute`
  - `requires_approval`
- Required every command to carry task id, repo binding id, adapter id, and risk tier.
- Required execution-like quick/full gate commands to consume PolicyDecision.
- Made `deny` fail closed for execution-like commands.
- Converted `escalate` into approval-required command posture with escalation context.
- Added schema/spec/catalog/package-root wiring and product documentation.

## TDD Evidence

### Red
- `cmd`: `python -m unittest tests.runtime.test_session_bridge -v`
- `exit_code`: `1`
- `key_output`: `No module named 'governed_ai_coding_runtime_contracts.session_bridge'`; `SessionBridgeCommand is not exported from package root`
- `timestamp`: `2026-04-18`

### Green
- `cmd`: `python -m unittest tests.runtime.test_session_bridge -v`
- `exit_code`: `0`
- `key_output`: `Ran 9 tests in 1.114s`; `OK`
- `timestamp`: `2026-04-18`

## Verification
- `cmd`: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `exit_code`: `0`
- `key_output`: `OK schema-json-parse`; `OK schema-example-validation`; `OK schema-catalog-pairing`
- `timestamp`: `2026-04-18`

- `cmd`: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `exit_code`: `0`
- `key_output`: `Ran 153 tests in 24.078s`; `OK`; `OK runtime-unittest`
- `timestamp`: `2026-04-18`

## Risks
- This slice defines the contract only; it does not implement the local session bridge CLI entrypoint.
- JSON Schema can require fields and enum shape but cannot prove that a referenced PolicyDecision exists or has status `allow`; Python contract tests cover that invariant.
- Adapter capability checks remain later work and are not inferred by this contract.

## Rollback
- Revert:
  - `docs/specs/session-bridge-command-spec.md`
  - `schemas/jsonschema/session-bridge-command.schema.json`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
  - `tests/runtime/test_session_bridge.py`
  - `docs/product/session-bridge-commands.md`
  - session bridge catalog/index/export additions
- Re-run:
  - `python -m unittest tests.runtime.test_session_bridge -v`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
