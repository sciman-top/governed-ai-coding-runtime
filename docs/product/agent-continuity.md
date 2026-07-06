# Agent Continuity Guide

## Purpose
Explain how this runtime preserves portable cross-host continuity for `Codex`, `Claude Code`, and adjacent host surfaces without mutating vendor-owned history stores or copying secrets.

## Current Boundary
- Native host history stays host-owned.
- The shared layer stores classified metadata only:
  - summaries
  - evidence refs
  - handoff refs
  - next actions
  - retention and sensitivity labels
- Secret-like payloads fail closed before they can be written into the runtime-owned continuity index.
- `Claude Desktop` remains a `referenced_only` boundary, not a shared writable history store.

## Continuity Classes
| Class | Meaning | Typical use |
|---|---|---|
| `native_shared` | same host family can safely reuse its own native state | shared `~/.codex`, Claude Code transcript root |
| `portable_shared` | runtime-owned shared artifact | handoff summary, evidence-linked continuity record |
| `referenced_only` | source can be referenced but not copied into the shared layer | transcript path, Desktop boundary, external export path |
| `isolated_secret` | must never be copied into shared continuity | API keys, cookies, refresh tokens, raw auth snapshots |

## Main Surfaces

### Read-only audit
```powershell
python scripts/agent-continuity.py audit --json
```

This returns the current continuity posture for:
- `codex-shared-home`
- `claude-shared-home`
- `claude-desktop-boundary`

The audit is classification-first and does not mutate host state.

### Runtime-owned continuity index
```powershell
python scripts/agent-continuity.py search --index-root .runtime/agent-continuity --repo-id governed-ai-coding-runtime --json
```

The local continuity index is the portable surface for:
- classified shared records
- evidence-linked handoff search
- repo/host/provider scoped lookup

### Operator surface
Use the interactive operator surface to inspect the continuity panel:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action OperatorUi
```

The continuity panel is read-only and shows:
- classified continuity records
- continuity class
- redaction/secret boundary state
- runtime-owned continuity JSON

## Write Boundary
Continuity writes are allowed only for classified portable records.

Current guarantees:
- records containing blocked secret material are rejected
- secret-like text patterns are rejected
- host-native auth/provider/history state is not rewritten by this flow

## What To Expect In Practice
- `Codex` continuity is strongest inside one shared Codex home and portable across hosts only through classified records.
- `Claude Code` continuity is anchored in one Claude home and portable through shared handoff/index records.
- `Claude Desktop` is documented honestly as a boundary surface, not treated as a writable shared continuity store.

## What Not To Claim
- Do not claim that Codex and Claude native histories are merged.
- Do not claim that Claude Desktop chat history is a runtime-owned shared store.
- Do not claim that credentials, cookies, tokens, or raw transcripts are copied into the continuity layer.

## Related Files
- [Agent Continuity And Shared Context Plan](../plans/agent-continuity-and-shared-context-plan.md)
- [Host Feedback Loop](./host-feedback-loop.md)
- [Codex CLI/App Integration Guide](./codex-cli-app-integration-guide.md)
- [Change Evidence Index](../change-evidence/README.md)
