# Agent Rule Coordination v2 Implementation Plan

> **For agentic workers:** Execute task-by-task with tests before production verifier changes. Preserve unrelated worktree changes in every repository.

**Goal:** Roll out a concise Codex/Claude user-plus-project rule architecture across nine explicit target repositories with deterministic audit, guarded global sync, loading evidence, and scoped rollback.

**Architecture:** Keep global rule distribution global-only. Make every target `AGENTS.md` host-neutral and every Claude wrapper a one-line import unless a real local Claude difference exists. Use a versioned coordination manifest and schema to audit target truth without storing or overwriting project rule bodies.

**Tech Stack:** Markdown, JSON Schema 2020-12, Python 3 standard library, PowerShell, unittest, Codex CLI, Claude Code CLI.

---

### Task 1: Freeze the contract and failing verifier tests

**Files:**
- Create: `docs/specs/agent-rule-coordination-v2-spec.md`
- Create: `docs/plans/agent-rule-coordination-v2-implementation-plan.md`
- Modify: `tests/runtime/test_verify_target_project_rules.py`
- Modify: `tests/runtime/test_verify_agent_rule_family.py`

- [x] Add tests for the `2.0` contract, one-line wrapper, first-line/BOM enforcement, host-neutral `AGENTS.md`, target-specific anchors, relative workspace resolution, version review drift, and global common-section equality.
- [x] Run the two test modules and confirm failures are caused by the missing v2 behavior.

Run:

```powershell
python -m unittest tests.runtime.test_verify_target_project_rules tests.runtime.test_verify_agent_rule_family
```

Expected: failures identifying unsupported v2 fields and missing validation.

### Task 2: Implement the machine-readable v2 contract

**Files:**
- Create: `schemas/jsonschema/target-project-rule-coordination.schema.json`
- Modify: `schemas/catalog/schema-catalog.yaml`
- Modify: `rules/target-project-rule-coordination.json`
- Modify: `scripts/verify-target-project-rules.py`
- Modify: `scripts/verify-agent-rule-family.py`

- [x] Add the schema and catalog pairing.
- [x] Replace the pilot-only manifest with the nine-repository explicit allowlist.
- [x] Resolve target paths from `workspace_root` plus `repo_path`.
- [x] Add enforce versus observe findings and `--require-all`.
- [x] Compare normalized global common sections, not only heading signatures.
- [x] Run the focused tests until green.

Run:

```powershell
python -m unittest tests.runtime.test_verify_target_project_rules tests.runtime.test_verify_agent_rule_family
```

Expected: all focused tests pass.

### Task 3: Revise the global rule release

**Files:**
- Modify: `rules/manifest.json`
- Modify: `rules/global/codex/AGENTS.md`
- Modify: `rules/global/claude/CLAUDE.md`
- Modify: `AGENTS.md`
- Modify: `CLAUDE.md`

- [x] Bump the managed release to `9.55`.
- [x] Make common sections equivalent and concise.
- [x] Correct instruction priority, Codex chain budget/diagnostics, Claude concatenation/import/path-rule/subagent behavior, and enforcement boundaries.
- [x] Remove machine-specific provider guidance and project-level Codex-only content from shared project rules.
- [x] Run the family verifier and sync dry-run before deployment.

Run:

```powershell
python scripts/verify-agent-rule-family.py
python scripts/sync-agent-rules.py --scope All --fail-on-change
```

Expected: family passes; sync dry-run reports the intentional release change without overwriting deployed copies.

### Task 4: Integrate nine target repositories in place

**Files:**
- Modify in each target: `AGENTS.md`
- Create or replace in each target: `CLAUDE.md`
- Create in each target: repository-owned rule rollout evidence under its existing evidence directory

- [x] Preserve each repository's current truth, gate entrypoints, domain invariants, safety boundaries, evidence path, and rollback.
- [x] Remove repeated global/platform text and all managed Gemini references.
- [x] Use a raw first-line `@AGENTS.md` wrapper.
- [x] Preserve unrelated changes in `skills-manager` and `vps-ssh-launcher`.
- [x] Record build/test/contract/hotspot applicability for this rule-only slice.

Run:

```powershell
python scripts/verify-target-project-rules.py --require-all
```

Expected: all nine targets pass; observations remain non-blocking and explicit.

### Task 5: Update operator documentation and evidence

**Files:**
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `README.en.md`
- Modify: `docs/README.md`
- Modify: `docs/quickstart/use-with-existing-repo.md`
- Modify: `docs/quickstart/use-with-existing-repo.zh-CN.md`
- Create: `docs/change-evidence/20260710-agent-rule-coordination-v2.md`

- [x] Document global-only sync, explicit target audit, one-line Claude wrapper, nine-target scope, load probes, and rollback.
- [x] Keep operator guidance bilingual.
- [x] Record source URLs, before/after versions, commands, key outputs, compatibility, N/A entries, and rollback.

### Task 6: Deploy, probe, and close the gates

**Files:**
- Deployed copies: `~/.codex/AGENTS.md`, `~/.claude/CLAUDE.md`
- Backup/evidence output under `docs/change-evidence/`

- [x] Run focused and full control-repository tests.
- [x] Apply guarded global sync and verify zero drift afterward.
- [x] Run `codex debug prompt-input` from all nine targets.
- [x] Run Claude fresh-session loading probes, recording any platform or workspace-trust limitation.
- [x] Execute control gates in the required order.
- [x] Run target rule-change verification, using scoped `gate_na` only where the product build/test gates are not applicable to Markdown-only changes.
- [x] Inspect every repository diff and confirm unrelated dirty changes remain untouched.

Run:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
```

Expected: all blocking gates pass, or the final evidence names the exact blocker without making a completion claim.
