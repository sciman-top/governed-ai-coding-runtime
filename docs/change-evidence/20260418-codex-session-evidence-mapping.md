# 20260418 Codex Session Evidence Mapping

## Goal
Implement `GAP-037 Task 8` by mapping Codex session evidence into the runtime evidence and handoff model.

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
- Added adapter evidence summary counts for:
  - file changes
  - tool calls
  - gate runs
  - approval events
  - handoff refs
- Added delivery handoff adapter references:
  - adapter id
  - adapter flow kind
  - adapter evidence refs
- Codex posture evidence records whether the flow is `direct_adapter`, `process_bridge`, or `manual_handoff`.

## TDD Evidence

### Red
- `cmd`: `python -m unittest tests.runtime.test_codex_adapter tests.runtime.test_evidence_timeline tests.runtime.test_delivery_handoff -v`
- `exit_code`: `1`
- `key_output`: missing `CodexSessionEvidence`; missing `summarize_adapter_evidence`; `build_handoff_package()` missing `adapter_id`
- `timestamp`: `2026-04-18`

### Green
- `cmd`: `python -m unittest tests.runtime.test_codex_adapter tests.runtime.test_evidence_timeline tests.runtime.test_delivery_handoff -v`
- `exit_code`: `0`
- `key_output`: `Ran 20 tests in 0.062s`; `OK`
- `timestamp`: `2026-04-18`

## Verification
- `cmd`: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `exit_code`: `0`
- `key_output`: `Ran 176 tests in 26.532s`; `OK`; `OK runtime-unittest`
- `timestamp`: `2026-04-18`

## Risks
- Codex evidence mapping records normalized runtime evidence events. It does not yet capture a real Codex structured event stream.
- Manual handoff and direct adapter flows are distinguishable by `flow_kind`, but stronger provenance can be added when a real direct adapter event source is available.
- Adapter evidence refs are optional on handoff packages to preserve compatibility with existing non-adapter handoffs.

## Rollback
- Revert:
  - `CodexSessionEvidence` and `record_codex_session_evidence`
  - `summarize_adapter_evidence`
  - adapter fields in `HandoffPackage`
  - Task 8 tests and docs
- Re-run:
  - `python -m unittest tests.runtime.test_codex_adapter tests.runtime.test_evidence_timeline tests.runtime.test_delivery_handoff -v`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
