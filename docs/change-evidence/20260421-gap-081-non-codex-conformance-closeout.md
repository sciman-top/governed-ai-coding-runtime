# 20260421 GAP-081 Non-Codex Conformance Closeout

## Goal
Close `GAP-081 NTP-02` with executable proof that Codex and at least one non-Codex adapter pass one shared conformance gate family and emit comparable runtime linkage fields.

## Scope
- `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/adapter_conformance.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/__init__.py`
- `tests/runtime/test_session_bridge.py`
- `tests/runtime/test_adapter_conformance.py`
- `docs/product/adapter-conformance-parity-matrix.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/README.md`
- `docs/backlog/README.md`
- `docs/backlog/full-lifecycle-backlog-seeds.md`

## What Changed
1. Removed Codex-only adapter-event persistence behavior in session bridge.
   - non-Codex adapters now emit `adapter_event_ref` and `adapter_event_summary` on gate/write paths via the same evidence timeline model.
2. Added default non-Codex session posture fields:
   - `adapter_tier=manual_handoff`
   - `flow_kind=manual_handoff`
   - explicit `posture_reason`
3. Added/expanded shared conformance gates in code and tests.
4. Updated parity matrix documentation with supported/degraded/blocked host statuses and linkage refs.
5. Promoted backlog posture to `GAP-081 complete` and advanced active near-term queue to `GAP-082..084`.

## Executable Evidence
### Codex path (supported)
- command: `python scripts/run-codex-adapter-trial.py --repo-id "governed-ai-coding-runtime" --task-id "task-gap080-live-adapter-trial-20260421" --binding-id "binding-governed-ai-coding-runtime" --probe-live`
- result: `adapter_tier=native_attach`, `flow_kind=live_attach`, linkage refs persisted.

### Non-Codex path (degraded, explicit)
- command: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-check.ps1 -AttachmentRoot "D:\CODE\governed-ai-coding-runtime" -AttachmentRuntimeStateRoot "D:\CODE\governed-ai-runtime-state\self-runtime" -Mode quick -PolicyStatus allow -TaskId "task-gap081-generic-trial2-20260421" -RunId "run-gap081-generic-trial2-20260421" -CommandId "cmd-gap081-generic-trial2-20260421" -AdapterId "generic.process.cli" -Json`
- result:
  - `summary.overall_status=pass`
  - `request_gate.payload.adapter_event_ref` present
  - `request_gate.payload.adapter_event_summary` present (`gate_run_count=2`)
  - `session_identity.flow_kind=manual_handoff`
  - `live_loop.closure_state=fallback_explicit`

### Shared conformance tests
- `python -m unittest tests.runtime.test_adapter_conformance -v`
- `python -m unittest tests.runtime.test_session_bridge -v`

Both pass with Codex-supported and non-Codex-degraded assertions under one gate family.

## Acceptance Mapping (`GAP-081`)
- [x] at least one non-Codex adapter passes the same conformance gate family used by Codex
- [x] non-Codex trials emit equivalent runtime evidence linkage fields
- [x] parity matrix records supported, degraded, and blocked capabilities per host

## Rollback
Revert:
- `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/adapter_conformance.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/__init__.py`
- `tests/runtime/test_session_bridge.py`
- `tests/runtime/test_adapter_conformance.py`
- `docs/product/adapter-conformance-parity-matrix.md`
- backlog/docs posture updates touched in this closeout
- this evidence file
