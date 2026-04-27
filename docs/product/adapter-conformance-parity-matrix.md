# Adapter Conformance Parity Matrix

## Purpose
Record host-level conformance parity using one shared gate family across Codex and non-Codex adapters.

## Shared Gate Family
Both hosts are checked against the same minimum linkage gates:
- identity linkage: `session_id`, `resume_id`, `continuation_id`
- execution linkage refs: evidence and verification refs
- explicit posture semantics: `flow_kind` plus fallback/degrade posture

## Latest Snapshot (2026-04-27)
| host | adapter_id | conformance_status | parity_status | notes |
|---|---|---|---|---|
| Codex canonical runtime-flow | `codex-cli` | `pass` | `supported` | `flow_kind=live_attach`, `closure_state=live_closure_ready`, runtime-owned evidence/handoff/replay refs persisted |
| Claude Code live native attach | `claude-code` | `pass` | `supported` | `flow_kind=live_attach`, session/resume/continuation ids and hook/evidence/replay refs satisfy the same conformance gate family |
| Generic process fallback | `generic.process.cli` | `pass` | `degraded` | canonical runtime-flow fallback explicit (`flow_kind=manual_handoff`, `closure_state=fallback_explicit`), approval+verification+adapter-event+handoff+replay linkage preserved |
| Broken fixture (test-only) | `broken.adapter` | `fail` | `blocked` | missing required identity/linkage fields fails gate family |

## Evidence References
- Codex canonical runtime-flow trial:
  - `artifacts/gap-106-live-loop/gap-106-live-loop-session-bridge-request/evidence/adapter-events.json`
  - `artifacts/gap-106-live-loop/gap-106-live-loop-approval-approval-5b12c33dca3e4df3bd021647871addf2/handoff/write-flow.json`
  - `artifacts/gap-106-live-loop/gap-106-live-loop-approval-approval-5b12c33dca3e4df3bd021647871addf2/replay/write-flow.json`
- Generic non-Codex canonical runtime-flow trial:
  - `artifacts/gap-107-non-codex-loop/gap-107-non-codex-loop-session-bridge-request/evidence/adapter-events.json`
  - `artifacts/gap-107-non-codex-loop/session-bridge-request/verification-output/contract.txt`
  - `artifacts/gap-107-non-codex-loop/gap-107-non-codex-loop-approval-approval-e8f2e06c784948aabaacae0dec2a7821/handoff/write-flow.json`
  - `artifacts/gap-107-non-codex-loop/gap-107-non-codex-loop-approval-approval-e8f2e06c784948aabaacae0dec2a7821/replay/write-flow.json`
- Claude Code native attach trial:
  - `docs/change-evidence/20260427-claude-code-native-attach-tier-parity.md`
  - `artifacts/task-gap-native-claude/claude-code-trial-safe/evidence/claude-code-probe.json`
  - `artifacts/task-gap-native-claude/claude-code-trial-safe/evidence/claude-code-hooks.json`
  - `artifacts/task-gap-native-claude/claude-code-trial-safe/replay/adapter-flow.json`

## Implementation Hooks
- shared gate module: `packages/contracts/src/governed_ai_coding_runtime_contracts/adapter_conformance.py`
- parity tests: `tests/runtime/test_adapter_conformance.py`
