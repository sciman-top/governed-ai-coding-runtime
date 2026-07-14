# Agent Rule Governance 9.56 Refresh Plan

## Goal

Refresh the OpenAI and Anthropic global/project rule family from current 2026-07-14
official and host evidence, repair deterministic cross-repository audit defects, and
publish a verified `9.56 / project contract 2.0 / coordination schema 2.3` release
without overwriting repository-owned facts or unrelated dirty worktrees.

## Frozen Scope

- Control repository: `D:\CODE\governed-ai-coding-runtime`.
- Managed global copies: `~/.codex/AGENTS.md`, `~/.claude/CLAUDE.md`.
- Target repositories: `ai-content-delivery-studio`, `classroom-answer-toolkit`,
  `ClassroomToolkit`, `github-toolkit`, `k12-question-graph`,
  `local-ai-dev-orchestrator`, `qq-codex-bot`, `skills-manager`, and
  `vps-ssh-launcher`.
- Excluded direct children: `external`, `governed-ai-coding-runtime`,
  `physicist_chinese_poster_batch_tool`, and `文档`.
- Gemini remains outside the managed family.

The inventory was frozen from direct-child Git-root probes, not directory names or the
historic allowlist. The nine discovered targets currently match the allowlist.

## Baseline Findings

1. Global sources and deployed copies are byte-identical at release `9.55`.
2. All nine project rules declare contract `2.0`; all Claude wrappers are one-line,
   UTF-8 without BOM, and begin with `@AGENTS.md`.
3. `verify-target-project-rules.py --require-all` fails seven targets because it hashes
   raw CRLF working-tree bytes against an LF manifest hash. The canonical template test
   fails for the same reason. This is a control-plane hash-definition defect, not target
   workflow drift.
4. The manifest is explicit but current code does not independently compare it with
   direct-child Git-root discovery.
5. Common N/A wording lacks the requested `recovery_condition`; three project rules
   contain executable `gate_na` records that need the same field.
6. Current official evidence distinguishes ChatGPT Work hosted/project context from the
   local `~/.codex/AGENTS.md` file, and confirms newer Claude diagnostics and native
   Windows sandbox limits.

## Change Matrix

| Surface | Change | Verification | Rollback |
|---|---|---|---|
| Coordination schema/manifest | Add `workspace_inventory`, `workflow_hash_mode=utf8_lf_v1`, bump schema to `2.3` | JSON Schema + focused tests + `--require-all` | Revert schema/manifest/script/test slice |
| Target verifier | Normalize workflow line endings, self-check template, discover direct Git roots, validate N/A records | RED/GREEN unit tests and real nine-repo audit | Revert verifier and tests |
| Global Codex/Claude sources | Bump to `9.56`, add five-field N/A, refresh host/surface deltas | family verifier + official/local probes | Revert sources, then sync backup |
| Control docs | Update spec, README routing, plan, research, and evidence | docs/contract gates | Revert this task's docs only |
| Nine target rules | Review against current facts; update release marker/date; add `recovery_condition` only where N/A exists | target verifier plus each repository's ordered rule-change gates | Revert each repository's rule/evidence slice |
| Global deployment | guarded dry-run, backup, apply, zero-drift check | source/target hashes and fresh process probes | sync backup plus reverted source |

## Ordered Tasks

### Task 1: Contract-first verifier repair

- Add failing tests for CRLF/LF equivalence, semantic workflow drift, canonical template
  mismatch, direct-child discovery, exclusions, filtered-CI skip behavior, non-Git
  allowlisted paths, and incomplete N/A records.
- Implement only enough schema/verifier behavior to pass those tests.
- Run focused tests and the real nine-repository strict audit.

### Task 2: Global rule release 9.56

- Keep A/C/D byte-equivalent between Codex and Claude.
- Add `recovery_condition` to the common N/A contract.
- Clarify ChatGPT Work/project context versus local Codex global instructions.
- Update Claude `--bare`, `--safe-mode`, settings-source diagnostics, and native Windows
  sandbox boundary from current official/help evidence.
- Update manifest and project review markers without changing project contract `2.0`.

### Task 3: Target repository review

- Preserve every repository's current commands, invariants, milestones, and evidence path.
- Change only `AGENTS.md` metadata and proven N/A gaps; leave `CLAUDE.md` unchanged when
  already exact.
- Add one bounded evidence note per target. Do not include unrelated dirty changes from
  `skills-manager`.

### Task 4: Publish and verify

- Run static family/target/schema checks before global synchronization.
- Run global sync dry-run, confirm backup destination, apply, then prove zero drift.
- Use new isolated commands/sessions only; do not restart or terminate running clients.
- Run control and target gates in their declared order. Record scoped N/A where the rule
  slice or prohibited process impact makes a product gate inapplicable.
- Review diffs, scan staged content for secrets, commit only task write-sets, push, and
  verify remote commits. A pushed task branch is not default-branch acceptance.

## Acceptance Criteria

- The strict audit discovers exactly the nine intended direct-child Git roots and all pass.
- CRLF and LF workflow checkouts produce the same canonical hash; a content change fails.
- Global common sections match and deployed copies have zero drift after guarded apply.
- All target wrappers remain exact one-line imports and all project rules remain within
  configured budgets.
- Every modified repository has fresh ordered gate evidence, a scoped commit, a verified
  push, and an explicit completion boundary.

## Prohibited Actions

No force push, branch/worktree deletion, PR merge, auth/provider/credential mutation,
Gemini work, process restart/termination, or unrelated dirty-worktree cleanup.
