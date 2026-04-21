# Adapter Conformance Parity Matrix

## Purpose
Record host-level conformance parity using one shared gate family across Codex and non-Codex adapters.

## Shared Gate Family
Both hosts are checked against the same minimum linkage gates:
- identity linkage: `session_id`, `resume_id`, `continuation_id`
- execution linkage refs: evidence and verification refs
- explicit posture semantics: `flow_kind` plus fallback/degrade posture

## Latest Snapshot (2026-04-21)
| host | adapter_id | conformance_status | parity_status | notes |
|---|---|---|---|---|
| Codex live probe | `codex-cli` | `pass` | `supported` | `flow_kind=live_attach`, `unsupported_capability_behavior=none`, runtime-owned evidence/handoff refs persisted |
| Generic process fallback | `generic.process.cli` | `pass` | `degraded` | runtime-check fallback explicit (`flow_kind=manual_handoff`, `closure_state=fallback_explicit`), identity+verification+adapter-event linkage preserved |
| Broken fixture (test-only) | `broken.adapter` | `fail` | `blocked` | missing required identity/linkage fields fails gate family |

## Evidence References
- Codex live trial:
  - `artifacts/task-gap080-live-adapter-trial-20260421/codex-trial-safe/evidence/codex-session.json`
  - `artifacts/task-gap080-live-adapter-trial-20260421/codex-trial-safe/handoff/package.json`
- Generic runtime-check trial:
  - `artifacts/task-gap081-generic-trial2-20260421/task-gap081-generic-trial2-20260421-session-bridge-request/evidence/adapter-events.json`
  - `artifacts/task-gap081-generic-trial2-20260421/session-bridge-request/verification-output/contract.txt`
  - `artifacts/task-gap081-generic-trial2-20260421/session-bridge-request/verification-output/test.txt`

## Implementation Hooks
- shared gate module: `packages/contracts/src/governed_ai_coding_runtime_contracts/adapter_conformance.py`
- parity tests: `tests/runtime/test_adapter_conformance.py`
