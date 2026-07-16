# Implementation Plan: Agent Rule Governance v2

## Overview

Reduce this repository from a general governed AI coding runtime to a static,
service-free control repository for OpenAI Codex and Anthropic Claude Code rule
governance. Target repositories keep ownership of their project rules. This
repository owns global sources, host deltas, target inventory, deterministic
validation, protected sync, native loading probes, CI coordination, and
release evidence.

## Architecture Decisions

- Keep `AGENTS.md` as the target-repository common rule and an exact one-line
  `CLAUDE.md` import wrapper unless a verified Claude-only delta is required.
- Keep target rule bodies in target repositories; the control repository may
  audit or produce a candidate diff, but never blind-sync project rules.
- Separate `default_branch_effective`, `workspace_effective`, `host_loaded`,
  and `hosted_accepted` instead of collapsing them into one completion flag.
- Use Markdown, JSON/TOML, JSON Schema, Python, PowerShell wrappers, Git, and
  GitHub Actions. Do not retain a database, HTTP API, UI, daemon, task runtime,
  model execution layer, or provider/auth management.
- Preserve the pre-migration tree at annotated tag
  `archive/runtime-v1-20260716`; every implementation slice remains
  independently revertible.

## Dependency Graph

```text
Git archive boundary
  -> explicit target-state audit semantics
    -> unified rulesctl entrypoint and minimal gates
      -> canonical rule-source assembly
        -> product-truth documentation
          -> mechanical runtime/history pruning
            -> review and fixed-order verification
```

## Task List

### Phase 1: Safety And State Semantics

- [x] Task 1: Create the archive tag and v2 feature branch.
- [x] Task 2: Add a git-ref audit mode and tests so published default branches
  can be verified without moving dirty or divergent target worktrees.
- [x] Task 3: Add a machine-readable status command that reports source,
  global projection, target default branch, and local workspace separately.

### Checkpoint: State Model

- [x] Focused unit tests pass.
- [x] Current `origin/main` refs pass independently of local workspace drift.
- [x] Current local workspace drift remains visible and non-destructive.

### Phase 2: Minimal Product Surface

- [x] Task 4: Add a single `rulesctl` entrypoint and minimal fixed-order gates.
- [x] Task 5: Introduce canonical common/platform rule fragments with a
  deterministic build/check path for the two global outputs.
- [x] Task 6: Replace broad Windows CI and operator entrypoints with rule-only
  verification and coordination workflows.

### Checkpoint: Rule Toolchain

- [x] Build, focused tests, contract/invariant, and hotspot pass in order.
- [x] Global sync dry-run reports zero drift.
- [x] Generated global outputs match committed files exactly.

### Phase 3: Product Truth And Pruning

- [x] Task 7: Rewrite root contracts, README variants, architecture, runbook,
  and release evidence for the v2 boundary.
- [x] Task 8: Remove runtime apps, packages, service infrastructure, unrelated
  schemas/scripts/tests, Gemini assets, UI media, and obsolete active docs.
- [x] Task 9: Keep only current rule-governance evidence and route historical
  recovery to the archive tag and Git history.

### Checkpoint: Minimal Active Tree

- [x] No active runtime, database, UI, Gemini, provider, auth, session, or
  orchestration surface remains.
- [x] All retained files are reachable from README, a command, a test, or CI.
- [x] `git diff --check` passes and no secrets appear in the diff.

### Phase 4: Review And Closeout

- [x] Task 10: Run independent multi-axis code review and fix findings.
- [x] Task 11: Run fresh fixed-order gates and record exact state boundaries.
- [x] Task 12: Commit the verified v2 slices with Chinese-first subjects and
  report any external actions that remain intentionally open.

## Risks And Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Historical evidence is removed from the active tree | Medium | Preserve the exact old tree in an annotated archive tag and Git history. |
| Target worktrees are stale or dirty | High | Audit `origin/main` without checkout and report workspace state separately. |
| Generated rules obscure their source | Medium | Commit both canonical fragments and deterministic outputs; fail on drift. |
| Scope expands back into host/runtime management | High | Enforce forbidden active-tree paths and product-boundary tests. |
| Large deletion hides accidental loss | High | Delete by category, inspect name-status diffs, and verify after each slice. |

## Open Questions

- Remote repository rename is intentionally deferred until the v2 tree is
  verified; it changes external URLs and should be a separate release action.
