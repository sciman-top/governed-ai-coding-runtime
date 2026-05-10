# Agent Continuity And Shared Context Plan

## Status
- Created: 2026-05-10.
- Queue: `GAP-159` through `GAP-164`.
- Current state: `GAP-159..164` are implemented. The queue now has a scope fence, schema-backed continuity record contract, read-only Codex/Claude continuity auditor, runtime-owned portable continuity index, operator-visible continuity surface, and a portable handoff closeout record.
- Scope boundary: plan, classify, and then implement an auditable shared continuity layer for Codex App, Codex CLI, Claude Code, and Claude Desktop where supported. Do not merge private vendor history stores or copy credentials.

## Goal
Make daily AI coding work portable across the active hosts while preserving host ownership and account boundaries.

The intended outcome is:

```text
native host history where safe
  + shared rules and provider metadata
  + portable continuity records
  + governed handoff packages
  + memory retrieval with provenance and expiry
  + operator-visible diagnostics
```

## Architecture Decisions
- Codex family continuity should keep one shared `~/.codex` root by default and use profiles, environment variables, and base URL projection for account or relay switching. Separate `CODEX_HOME` remains an explicit privacy or trust boundary.
- Claude Code continuity should keep one `~/.claude` or declared `CLAUDE_CONFIG_DIR` by default and switch provider state through settings, profile metadata, or process environment. Separate config roots are treated as isolated sessions.
- Claude Desktop and Claude Code do not get treated as one native history store. Shared behavior is limited to supported configuration, project memory, MCP surfaces, Desktop transfer flows where available, and portable handoff records.
- Cross-host continuity is a runtime contract, not a private database mutation. The shared layer stores summaries, refs, labels, evidence links, next actions, and sensitivity metadata; it does not rewrite vendor-owned SQLite, JSONL, cookies, tokens, or cloud history.
- Memory can inform later retrieval, but repository files, verified evidence, and explicit handoff packages remain stronger than memory.

## Shared Object Classes
| Class | Meaning | Examples | Default action |
|---|---|---|---|
| `native_shared` | Same host family can safely reuse native state | Codex `sqlite_home`, Codex history persistence, Claude Code session transcript root | Verify, back up before apply, keep host-owned |
| `portable_shared` | Cross-host data can be shared as a governed artifact | continuity records, handoff summaries, evidence refs, repo maps, rule refs | Store in runtime index and expose through CLI/MCP/operator |
| `referenced_only` | Sensitive or bulky source is referenced, not copied | transcript path, session id, app state file path, external export path | Store ref plus sensitivity label |
| `isolated_secret` | Must not be copied into shared memory | API keys, refresh tokens, cookies, auth snapshots, private account data | Store only redacted presence or env-var name |

## Task List

### GAP-159 Cross-Host Continuity Scope Fence
**Purpose:** Freeze what will and will not be shared before any runtime index or MCP endpoint is added.

**Acceptance criteria:**
- [x] Codex App, Codex CLI, Claude Code, and Claude Desktop surfaces are listed with native, portable, referenced-only, and isolated-secret boundaries.
- [x] Multi-account and multi-provider behavior is described without requiring secret copying.
- [x] Rollback and backup expectations are documented before any live state mutation.

**Verification:**
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`

**Dependencies:** `GAP-158`.

**Files likely touched:**
- `docs/plans/agent-continuity-and-shared-context-plan.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/issue-seeds.yaml`
- `docs/change-evidence/<date>-agent-continuity-planning.md`

**Estimated scope:** Small.

### GAP-160 Agent Continuity Record Contract
**Purpose:** Add the machine-readable record shape for cross-host continuity without storing private raw transcripts or secrets.

**Acceptance criteria:**
- [x] `agent-continuity-record` schema validates the required identity, host, account/provider alias, scope, evidence, memory, and sensitivity fields.
- [x] The schema distinguishes `native_shared`, `portable_shared`, `referenced_only`, and `isolated_secret`.
- [x] Schema catalog pairing passes.

**Verification:**
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`

**Dependencies:** `GAP-159`.

**Files likely touched:**
- `docs/specs/agent-continuity-record-spec.md`
- `schemas/jsonschema/agent-continuity-record.schema.json`
- `schemas/catalog/schema-catalog.yaml`
- `schemas/README.md`

**Estimated scope:** Medium.

### GAP-161 Read-Only Continuity Auditor
**Purpose:** Implement a no-mutation scanner that reports current continuity posture for Codex and Claude host families.

**Acceptance criteria:**
- [x] Auditor reads Codex home, config, history persistence, SQLite state presence, launcher presence, and provider/profile metadata without printing secrets.
- [x] Auditor reads Claude home, `CLAUDE_CONFIG_DIR`, projects transcript count, `history.jsonl`, provider switch policy, and Desktop boundary indicators without printing secrets.
- [x] Auditor emits an `agent-continuity-record` candidate and structured `platform_na` when a host surface is unavailable.

**Verification:**
- [x] focused unit tests for the auditor
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check RuntimeQuick`

**Dependencies:** `GAP-160`.

**Files likely touched:**
- `scripts/agent-continuity.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/agent_continuity.py`
- `tests/runtime/test_agent_continuity.py`

**Estimated scope:** Medium.

### GAP-162 Portable Handoff And Memory Index
**Purpose:** Store portable continuity records and handoff summaries in a runtime-owned index that can be queried by multiple hosts.

**Acceptance criteria:**
- [x] Index stores only classified fields, refs, evidence paths, summaries, decisions, changed files, next actions, and sensitivity labels.
- [x] Search and retrieval filter by repo, host, account alias, provider alias, task, sensitivity, and expiry.
- [x] Retention and retirement follow the governed knowledge-memory lifecycle.

**Verification:**
- [x] focused unit tests for write, search, expiry, and redaction
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check RuntimeQuick`

**Dependencies:** `GAP-161`.

**Files likely touched:**
- `packages/contracts/src/governed_ai_coding_runtime_contracts/agent_continuity.py`
- `scripts/agent-continuity.py`
- `docs/product/agent-continuity.md`
- `tests/runtime/test_agent_continuity.py`

**Estimated scope:** Medium.

### GAP-163 Continuity MCP And Operator Surface
**Purpose:** Expose continuity search and handoff operations to Codex, Claude Code, Claude Desktop, and the local `8770` operator without granting secret access.

**Acceptance criteria:**
- [x] MCP or equivalent local tool surface supports `search_context`, `get_handoff`, and `write_handoff`.
- [x] Operator UI shows continuity posture, recent handoffs, redaction status, and isolated-secret warnings.
- [x] Write operations classify sensitivity and fail closed on secret-like payloads.

**Verification:**
- [x] focused service/operator tests
- [x] browser verification of `http://127.0.0.1:8770/?lang=zh-CN`
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`

**Dependencies:** `GAP-162`.

**Files likely touched:**
- `scripts/operator.ps1`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/service.py`
- `tests/service/test_operator_api.py`
- `tests/runtime/test_operator_ui.py`

**Estimated scope:** Medium.

### GAP-164 Cross-Host Continuity Closeout
**Purpose:** Prove at least one safe Codex-to-Claude-to-Codex handoff path and document the unsupported native-history boundaries.

**Acceptance criteria:**
- [x] A real repo task can be summarized from one host and resumed through another host using the portable continuity layer.
- [x] Native-history unsupported surfaces are documented as explicit `platform_na` or `referenced_only`, not as failures.
- [x] Full gate or declared N/A evidence exists, with rollback instructions.

**Verification:**
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

**Dependencies:** `GAP-163`.

**Files likely touched:**
- `docs/change-evidence/<date>-agent-continuity-closeout.md`
- `docs/product/agent-continuity.md`
- `README.md`

**Estimated scope:** Medium.

## Checkpoints

### Checkpoint: Contract Baseline
- [x] `GAP-159` and `GAP-160` are complete.
- [x] Contract gate passes.
- [x] No user-local live state was modified except documented dry-run evidence.

### Checkpoint: Read-Only Runtime
- [x] `GAP-161` is complete.
- [x] Auditor reports current host posture without secret leakage.
- [x] RuntimeQuick passes.

### Checkpoint: Shared Runtime Surface
- [x] `GAP-163` is complete.
- [x] `GAP-162` is complete.
- [ ] Operator and MCP surfaces expose classified continuity records.
- [ ] Write paths fail closed on secrets.

### Checkpoint: Closeout
- [x] `GAP-164` is complete.
- [x] Codex and Claude handoff proof is fresh and evidence-backed.
- [x] Unsupported native history claims are documented honestly.

## Risks And Mitigations
| Risk | Impact | Mitigation |
|---|---|---|
| Private vendor state is mutated or corrupted | High | Keep this queue read-only until explicit apply tasks; back up before any live state mutation |
| Cross-account memory leaks | High | Require account aliases, sensitivity labels, and default filtering before injection |
| Raw transcripts become hidden truth | High | Store transcript refs and summaries only; repository facts and evidence remain stronger |
| Claude Desktop capabilities are overstated | Medium | Record unsupported native history sharing as `platform_na` or `referenced_only` |
| Provider switchers drift from runtime assumptions | Medium | Keep Cockpit Tools and CC Switch as ownership peers, then verify their projected state through read-only audits |

## Completion Definition
This queue is complete only when a verified portable continuity path exists across at least Codex CLI/App and Claude Code, the Claude Desktop boundary is explicit, and the operator can show the current classified posture without exposing credentials.
