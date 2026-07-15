# Agent Rule Governance 9.57

## Scope and basis

- `issue_id`: `agent-rule-governance-9.57-20260715`
- baseline: control repo `4fd39cd0f3bf6fe8ac0b5f96b36206ea0d6589ef`; nine target baselines are frozen in the per-repository evidence and final ledger
- content change: correct Claude Code import recursion from four hops to the current official five-hop limit
- versions: `rule_release=9.57`, `project_contract_version=2.0`, `coordination_schema=2.3`, `sync_revision=2026-07-15.1`
- target set: nine direct-child Git roots in `rules/target-project-rule-coordination.json`; Gemini and excluded directories remain outside the managed family
- official basis: [Claude Code memory imports](https://code.claude.com/docs/en/memory#import-additional-files)

## Compatibility and write boundary

- Global WHAT and common A/C/D semantics are unchanged; Codex B is unchanged; Claude B changes one stale platform fact.
- Project WHERE/HOW content is unchanged except `**全局规则复核**: 9.57`, update date, and fresh repository evidence.
- No schema shape, project contract, wrapper shape, auth, provider, secret, MCP, permission, account, VPS, hosted UI, or process state is changed.
- Existing ahead/dirty history in `k12-question-graph`, `local-ai-dev-orchestrator`, and `skills-manager` is protected through isolated worktrees or existing task PR branches.

## pre_change_review

- `control_repo_manifest_and_rule_sources`: compared root `AGENTS.md`, both managed global sources, `rules/manifest.json`, coordination allowlist/schema, verifier wiring, and the source/deployed-copy state before editing.
- `user_level_deployed_rule_files`: inspected `~/.codex/AGENTS.md` and `~/.claude/CLAUDE.md` through protected dry-run, backup, apply, exact-hash zero-drift, and fresh loading probes; no same-version overwrite was accepted.
- `repo_local_gate_scripts_and_ci`: inventoried every target `AGENTS.md`, exact `CLAUDE.md` wrapper, canonical rule-contract workflow, product gate, evidence path, and rollback entry; hosted PR checks were evaluated at frozen heads.
- `repo_local_repo_profile`: checked the control repository profile/gate contract and each target's repository-local commands and invariants; no repo profile was changed, and compliant N/A records remain target-owned.
- `repo_local_readme_and_operator_docs`: reviewed root README variants, docs index, bilingual existing-repo quickstarts, coordination spec, evidence index, and target gate/README truth before synchronizing current release text.
- `current_official_tool_loading_docs`: checked current official Codex `AGENTS.md` guidance and Claude Code memory/import, web, and permissions documentation; only the stale Claude four-hop fact required a semantic correction.
- `drift-integration decision`: integrate the confirmed five-hop fact into the managed source first, bump the shared content release to `9.57`, preserve project contract/schema versions, protect all unrelated local histories, and add a fail-closed isolated-workspace Contract input instead of moving divergent user worktrees or weakening `--require-all`.

## reference_required_review

- `changed_surface_paths`: `AGENTS.md`, `rules/global/{codex,claude}`, `rules/manifest.json`, `rules/target-project-rule-coordination.json`, `scripts/verify-repo.ps1`, `tests/runtime/test_verify_target_project_rules.py`, release/current-state docs, evidence, and protected sync backups.
- `official_sources_reviewed`: [OpenAI Codex AGENTS.md guidance](https://developers.openai.com/codex/guides/agents-md), [Claude Code memory imports](https://code.claude.com/docs/en/memory#import-additional-files), [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web), and [Claude Code permissions](https://code.claude.com/docs/en/permissions).
- `primary_references_reviewed`: provider-owned OpenAI/Anthropic documentation, the current repo-owned `verify-target-project-rules.py` implementation, canonical target CI workflow, and actual target gate scripts; no community source was promoted to authoritative status.
- `local_runtime_evidence_reviewed`: current Codex help/debug prompt-input, Claude Code version/help/doctor, exact managed-copy hashes, nine candidate worktrees, nine fresh remote refs, GitHub PR/check results, and fixed-order local gate outputs.
- `source_decision`: correct only the evidenced Claude import-depth fact, keep Codex semantics/project contract/coordination schema stable, preserve historical 9.56 records, and make the isolated audit root explicit plus fail-closed instead of weakening the configured workspace audit.

## reference_basis_review

- `changed_surface_paths`: `docs/specs/agent-rule-coordination-v2-spec.md` and `scripts/verify-repo.ps1` are the reference-basis guarded paths in this slice.
- `reference_basis_surface_ids`: `workflow-governance-and-spec-driven-delivery` and `release-gate-and-ci-boundaries`.
- `required_local_reference_ids_reviewed`: `1code`, `aider`, `anthropic-claude-code`, `anthropic-claude-code-action`, `github-copilot-cli`, `github-spec-kit`, `obra-superpowers`, `openai-codex`, `openclaw-code-agent`, and `swe-agent` were read from the repo-owned local shelf at their current frozen heads.
- `reference_adoption_decision`: retain the already-compatible worktree isolation, explicit review, CI visibility, and fail-closed gate patterns; add only the complete-workspace override needed by this release. Do not import provider/account controls, background-agent architecture, browser flows, community prompt policy, or a parallel workflow system. OpenAI/Anthropic official docs and local executable evidence remain authoritative for host semantics; community references remain structural input only.

## Frozen inventory and publication ledger

The task used isolated worktrees from the frozen baselines below. Original local `main` worktrees were never moved, reset, cleaned, staged, or pushed; this preserves the pre-existing ahead/dirty histories while remote publication is proved from fresh refs.

| repository | frozen baseline | governance commit/head | PR and fresh default-branch result |
| --- | --- | --- | --- |
| `ai-content-delivery-studio` | `374905426e7e` | `52a4a698`, final head `3929e9f8` | PR #2 merged as `fcd370fcb923`; inherited CI repair PR #3 merged as `2fc398c234fb` |
| `classroom-answer-toolkit` | `6486358e7ff5` | `7c4f6094` | PR #2 merged as `bbb9bbbc9ad8` |
| `ClassroomToolkit` | `d364d547002f` | `d9105289`, final head `054f6bc9` | PR #2 merged as `e758d2091730`; inherited CI repair PR #3 merged as `6df89621c2f1` |
| `github-toolkit` | `811afc3c04d4` | `8fbd2634` | PR #2 merged as `7b4a6b963283` |
| `k12-question-graph` | `d6239a7671bd` | `bff71e30` | PR #3 merged as `69750bc51f3b`; original local `main` remains divergent and protected |
| `local-ai-dev-orchestrator` | `a15021fb8dd7` | `465e81f4` | PR #3 merged as `7e9f993c7a13`; original local `main` remains divergent and protected |
| `qq-codex-bot` | `47c7d71a50cd` | `6af6409d` | PR #2 merged as `6b3f0a9bc997` |
| `skills-manager` | `4addb13e201e` | `c5a586215db3` | governance PR #2 open; repair PR #3 frozen at `6fd9fccc61e2`; original dirty/ahead `main` remains protected |
| `vps-ssh-launcher` | `2a575120314f` | `48c1a2b4` | PR #2 merged as `b34e3abfe3ff` |

All eight merged governance heads were re-fetched, proved as ancestors of fresh `origin/main`, and had only their merged task branches/worktrees removed. The two merged independent repair branches were likewise removed. The unmerged `skills-manager` governance and repair branches remain intact.

## Verification ledger

### Rule family, sync, and loading

- `python scripts/verify-agent-rule-family.py`: exit `0`; Codex source `10513` bytes, Claude source `11059` bytes, shared A/C/D hash `cb43a7d50fab3fefe902c2c41c80a1c2d67175564174faa2166f904f250cd92d`.
- `python scripts/sync-agent-rules.py --scope All --fail-on-change`: before apply reported exactly two managed-copy changes.
- backup confirmed at `docs/change-evidence/rule-sync-backups/20260715-154520/`; protected apply updated only `~/.codex/AGENTS.md` and `~/.claude/CLAUDE.md`.
- final post-apply dry-run: exit `0`, `changed_count=0`; source and managed-copy hashes are exactly equal (`Codex=44a9e0f2fc01d6edfeb0663783c6fe389849ff2c46d7f070ae4fe89dba342820`, `Claude=87b7a4a6afd2994e760819e62ea9f350144491c4ecf72046ddcf24b73066fd23`).
- fresh Codex `debug prompt-input` probes passed for the control repo and all nine isolated target worktrees; each contained release `9.57`, the repository marker, and the unique probe text.
- `claude doctor` passed installation checks for Claude Code `2.1.206`, but the CLI is not signed into Anthropic API or claude.ai. No auth/account change was authorized or attempted.

### Per-repository gates

- `ai-content-delivery-studio`: build `0` warnings/errors, 461 tests, reference evidence, format, normal and forced no-`rg` preflight, publish `WhatIf`, local combined-head gate, and three final governance checks passed.
- `classroom-answer-toolkit`: 57 tests, rule/vision contracts, local PDF render/review, and complete toolchain passed; existing lock-file advisories remain 1 moderate and 1 high with no dependency change in this slice.
- `ClassroomToolkit`: build `0` warnings/errors, 3544 tests, 29 contract tests, hotspot/full quality passed; repaired clean-runner state fallback and restored stable-profile resolver passed hosted `verify-lock`.
- `github-toolkit`: Python compilation and 189 tests passed; contract/hotspot `gate_na` and optional Ruff/mypy `platform_na` are fully recorded in its repository evidence.
- `k12-question-graph`: build passed with 0 errors and two existing `Microsoft.OpenApi 2.0.0` high-advisory warnings; roadmap guard passed and preserved `REAL005=not_closed`; test/hotspot process-controlled gaps are recorded as compliant `gate_na`.
- `local-ai-dev-orchestrator`: 231 tests and planning/selection contracts passed; build/hotspot `gate_na` are recorded in its repository evidence.
- `qq-codex-bot`: fast verifier passed 284 tests; same-SHA canonical full verifier passed 13/13 steps; isolated pytest passed 864 with 10 skips and three documented environment-bound observations; no secret or live VPS action occurred.
- `skills-manager`: build/generated sync, Pester 454+12, strict doctor, dependency baseline, 108-skill integrity, and full quality passed locally. Hosted CI still reproduces the inherited Windows hidden-directory failure.
- `vps-ssh-launcher`: pytest 93/1 skip, unittest 94/1 skip, pip check/audit, Bandit, vulture, Ruff/format, mypy, pyright, and full gates passed; no SSH/VPS action occurred.

### Aggregate and fixed gates

- candidate audit: all nine task heads passed the target-rule verifier; the still-open `skills-manager` head independently re-passed with `selected_target_count=1`, `failed_target_count=0`.
- fresh remote-default audit: eight repositories passed; only `skills-manager` failed with `reviewed_global_release_mismatch:9.55->9.57`, exactly matching the open governance PR boundary.
- control build: exit `0`.
- control Runtime test: 104 test files, failures `0`.
- control contract/invariant default-root observation: schema, dependency, sync, family, and preceding checks passed; the unqualified command then exited `1` because it intentionally audited untouched original `D:\CODE` worktrees whose current local branches still expose old `9.55/9.56` review markers. Those user worktrees were not moved merely to manufacture a green result.
- protected candidate Contract: added the tested `GACR_TARGET_PROJECT_RULE_WORKSPACE_ROOT` input to `scripts/verify-repo.ps1`; when set it forces `--workspace-root ... --require-all`. With eight fresh `origin/main` worktrees plus frozen `skills-manager` head `c5a58621`, the same fixed Contract command exited `0` through target rules, pre-change review, reference-required changes, reference basis, and functional effectiveness. The focused verifier suite passed 22 tests and PowerShell parsing passed.
- control hotspot: `scripts/doctor-runtime.ps1` exited `0`; all reported doctor checks passed.

### Hosted and manual boundary

- `platform_na`: ChatGPT Work, Codex cloud, Claude Chat, and Claude Code web model-visible acceptance. `reason=the task prohibits Browser, Chrome, and Computer Use after two host exits and these surfaces require a safe user-operated session`; `alternative_verification=fresh local loading probes and remote rule checks, explicitly not a substitute for hosted acceptance`; `evidence_link=this ledger`; `expires_at=next safe user-operated acceptance window`; `recovery_condition=user runs the supplied hosted acceptance prompts and records outputs`.
- `platform_na`: Claude Code local model-visible loading. `reason=Claude Code is installed but not signed in and account/auth changes are out of scope`; `alternative_verification=claude doctor plus deployed-file zero-drift, explicitly not a model-visible acceptance`; `evidence_link=this ledger`; `expires_at=next authorized signed-in Claude session`; `recovery_condition=user signs in independently and runs a fresh /context or equivalent probe`.
- Codex App/CLI processes were not stopped, restarted, killed, or auto-launched; no auth, provider, secret, MCP endpoint, live VPS, or user-account state was changed.

## Active blocker

- `skills-manager` governance PR #2 is mergeable and its rule-contract checks pass, but both CI runs inherit the same Windows hidden-directory failure.
- independent repair PR #3 passed all local full gates but repeated the same hosted failure twice and is therefore frozen at `clarify_required` under `issue_id=skills-manager-hidden-directory-ci`, `attempt_count=2`.
- owner: user/repository owner; next action: authorize either additional hosted-runner instrumentation or a Windows attribute-aware fallback contract; retest condition: PR #3 gets a new frozen head and both push/PR CI runs pass, after which PR #3 and then governance PR #2 can be merged and cleaned up.

## Completion boundary

- `repo-side completed=true`
- `published branch=true`
- `default-branch effective=false`
- `hosted/manual accepted=false`
- `fully completed=false`

Eight of nine target default branches are effective. The control repository release branch is publishable but must not be merged while the downstream `skills-manager` default-branch audit remains red.

Hosted ChatGPT Work, Codex cloud, Claude Chat, and Claude Code cloud remain user-operated acceptance surfaces. Browser, Chrome, and Computer Use integrations are prohibited for this task and local hashes/CLI probes cannot substitute for hosted model-visible acceptance.

## Rollback

- control repo: revert only the `9.57` governance commit and evidence updates
- managed global copies: use the sync backup created immediately before apply, then rerun zero-drift and fresh-process probes
- target repos: revert only each task branch/merge files (`AGENTS.md` and the new `9.57` evidence); never reset or clean unrelated local history
