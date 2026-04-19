# 20260418 Codex Session Evidence Mapping

## Goal
Implement `GAP-037 Task 8` and `direct-to-hybrid Task 6` by mapping Codex session evidence into the runtime evidence and handoff model with explicit unsupported-event handling.

## Landing
- Source plan: `docs/plans/interactive-session-productization-implementation-plan.md`
- Target destination:
  - Codex evidence mapper: `packages/contracts/src/governed_ai_coding_runtime_contracts/codex_adapter.py`
  - evidence summary: `packages/contracts/src/governed_ai_coding_runtime_contracts/evidence.py`
  - delivery handoff adapter refs: `packages/contracts/src/governed_ai_coding_runtime_contracts/delivery_handoff.py`
  - tests: `tests/runtime/test_codex_adapter.py`, `tests/runtime/test_evidence_timeline.py`, `tests/runtime/test_delivery_handoff.py`
  - docs: `docs/product/codex-direct-adapter.md`

## Changes
- Added `CodexSessionEvidence`.
- Added `record_codex_session_evidence`.
- Added explicit `adapter_unsupported_event` recording for:
  - unsupported capabilities
  - partially supported or dropped raw adapter events
- Added adapter evidence summary counts for:
  - file changes
  - tool calls
  - gate runs
  - approval events
  - handoff refs
  - unsupported events
  - live/manual event source counts
- Added delivery handoff adapter references:
  - adapter id
  - adapter flow kind
  - adapter evidence refs
- Added `adapter_event_summary` to delivery handoff payloads.
- Session bridge execution paths now persist `adapter-events` evidence artifacts for:
  - gate execution
  - governed tool execution
  - attached write execution
- Codex posture evidence records whether the flow is `live_attach`, `process_bridge`, or `manual_handoff`.

## TDD Evidence

### Red
- `cmd`: `python -m unittest tests.runtime.test_codex_adapter tests.runtime.test_evidence_timeline tests.runtime.test_delivery_handoff -v`
- `exit_code`: `1`
- `key_output`: missing `CodexSessionEvidence`; missing `summarize_adapter_evidence`; `build_handoff_package()` missing `adapter_id`
- `timestamp`: `2026-04-18`

### Green
- `cmd`: `python -m unittest tests.runtime.test_codex_adapter tests.runtime.test_evidence_timeline tests.runtime.test_delivery_handoff tests.runtime.test_session_bridge -v`
- `exit_code`: `0`
- `key_output`: `Ran 53 tests in 3.856s`; `OK`
- `timestamp`: `2026-04-19`

## Verification
- `cmd`: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `exit_code`: `0`
- `key_output`: `Ran 221 tests in 40.617s`; `OK`; `OK runtime-unittest`
- `timestamp`: `2026-04-19`
- `cmd`: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `exit_code`: `0`
- `key_output`: `OK schema-json-parse`; `OK schema-example-validation`; `OK schema-catalog-pairing`
- `timestamp`: `2026-04-19`

## Risks
- Codex evidence mapping currently uses runtime-captured event projection, not upstream-native full structured trace export.
- `live_attach` posture depends on host-side `codex status` capability and may degrade to `process_bridge` in non-interactive contexts.
- Adapter evidence refs remain optional on handoff packages to preserve compatibility with existing non-adapter handoffs.

## Rollback
- Revert:
  - `CodexSessionEvidence` and `record_codex_session_evidence`
  - `summarize_adapter_evidence` extended counters
  - adapter fields in `HandoffPackage`
  - session bridge `adapter-events` evidence emission
  - Task 8/Task 6 tests and docs
- Re-run:
  - `python -m unittest tests.runtime.test_codex_adapter tests.runtime.test_evidence_timeline tests.runtime.test_delivery_handoff tests.runtime.test_session_bridge -v`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
