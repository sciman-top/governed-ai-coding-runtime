# 20260418 Codex Direct Adapter Contract

## Goal
Implement `GAP-037 Task 7` by adding a Codex-first adapter contract that remains capability-tiered and does not make the runtime Codex-only.

## Landing
- Source plan: `docs/plans/interactive-session-productization-implementation-plan.md`
- Target destination:
  - Codex adapter contract: `packages/contracts/src/governed_ai_coding_runtime_contracts/codex_adapter.py`
  - adapter fallback helper: `packages/contracts/src/governed_ai_coding_runtime_contracts/adapter_registry.py`
  - tests: `tests/runtime/test_codex_adapter.py`, `tests/runtime/test_adapter_registry.py`
  - docs: `docs/product/codex-direct-adapter.md`, `docs/product/codex-cli-app-integration-guide.md`, `docs/product/codex-cli-app-integration-guide.zh-CN.md`

## Changes
- Added `CodexAdapterProfile`.
- Added `build_codex_adapter_profile`.
- Added `classify_codex_adapter`.
- Declared Codex adapter capability fields:
  - auth ownership
  - workspace control
  - tool visibility
  - mutation model
  - resume behavior
  - evidence export capability
  - adapter tier
  - unsupported capabilities
  - unsupported capability behavior
- Codex adapter classification supports:
  - `native_attach`
  - `process_bridge`
  - `manual_handoff`
- Updated Codex integration docs to distinguish adapter contract from live managed Codex execution.

## TDD Evidence

### Red
- `cmd`: `python -m unittest tests.runtime.test_codex_adapter -v`
- `exit_code`: `1`
- `key_output`: `No module named 'governed_ai_coding_runtime_contracts.codex_adapter'`; `CodexAdapterProfile is not exported from package root`
- `timestamp`: `2026-04-18`

### Green
- `cmd`: `python -m unittest tests.runtime.test_codex_adapter tests.runtime.test_adapter_registry -v`
- `exit_code`: `0`
- `key_output`: `Ran 9 tests in 0.044s`; `OK`
- `timestamp`: `2026-04-18`

## Verification
- `cmd`: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `exit_code`: `0`
- `key_output`: `Ran 172 tests in 24.005s`; `OK`; `OK runtime-unittest`
- `timestamp`: `2026-04-18`

- `cmd`: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- `exit_code`: `0`
- `key_output`: `OK active-markdown-links`; `OK backlog-yaml-ids`; `OK old-project-name-historical-only`
- `timestamp`: `2026-04-18`

## Risks
- This contract classifies Codex capability posture; it does not prove live native attach capability in every host environment.
- Evidence export and resume behavior are capability declarations, not yet structured Codex event capture.
- The runtime still treats Codex authentication as user-owned upstream authentication.

## Rollback
- Revert:
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/codex_adapter.py`
  - `tests/runtime/test_codex_adapter.py`
  - Codex adapter exports
  - Codex adapter docs and integration-guide additions
- Re-run:
  - `python -m unittest tests.runtime.test_codex_adapter tests.runtime.test_adapter_registry -v`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
