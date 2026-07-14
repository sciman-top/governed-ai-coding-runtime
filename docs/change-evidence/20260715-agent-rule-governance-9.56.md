# 20260715 Agent Rule Governance 9.56

## Scope

- control_repo: `D:\CODE\governed-ai-coding-runtime`
- managed_global_copies: `C:\Users\sciman\.codex\AGENTS.md`, `C:\Users\sciman\.claude\CLAUDE.md`
- discovered_targets: `ai-content-delivery-studio`, `classroom-answer-toolkit`, `ClassroomToolkit`, `github-toolkit`, `k12-question-graph`, `local-ai-dev-orchestrator`, `qq-codex-bot`, `skills-manager`, `vps-ssh-launcher`
- excluded_direct_children: `external`, `governed-ai-coding-runtime`, `physicist_chinese_poster_batch_tool`, `文档`
- platform_scope: OpenAI ChatGPT Work / Codex App / Codex CLI and Anthropic Claude / Claude Code; Gemini is outside the managed family.
- frozen_at: `2026-07-14`; verified_through: `2026-07-15T01:05:58+08:00`

Direct-child Git-root discovery found exactly the nine targets above. Exclusions were not recursively searched or project-rule modified. The control repository remains a global-rule and audit control plane; it does not own target project-rule bodies.

## Research

The primary record is [OpenAI / Anthropic Agent 规则治理事实刷新](../research/2026-07-14-agent-rule-governance-refresh.md). It records source URL, access date, applicable host/version, local probes, and `adopt / reject / defer` decisions.

- Local versions: Codex CLI `0.144.1`, Codex App `26.707.9981.0`, Claude Code `2.1.206`.
- OpenAI facts adopted: root-to-cwd `AGENTS.md` discovery, 32 KiB total project-rule budget, trusted project configuration, local sandbox/approval separation, stable hooks, experimental exec rules, and hosted/local surface separation.
- Anthropic facts adopted: `CLAUDE.md` concatenation, explicit `@AGENTS.md` import, settings/permissions precedence, hook blocking semantics, `/context` loading diagnostics, and native Windows sandbox limitations.
- Rejected: treating a local global-rule hash as proof that ChatGPT Work web, Codex cloud, Claude Chat, or Claude Code cloud loaded the same bytes; treating prose or import wrappers as deterministic enforcement; treating community examples as normative host semantics.
- Deferred: host configuration repairs unrelated to this task, including the eight observed Codex schema findings for `mcp_servers.*.transport`; no auth/provider/MCP/credential/config mutation was performed.
- Community and official repositories were used only at fixed commits for structure and implementation cross-checks. The research report verified 50 cited URLs with HTTP 2xx and kept official/local evidence above community guidance.

## Architecture

- Global WHAT: release `9.56` carries cross-repository obligations, risk/evidence semantics, five-field N/A records, and the shared A/C/D contract.
- Project WHERE/HOW: target `AGENTS.md` files remain host-neutral and own repository facts, real gates, invariants, evidence, and rollback. Claude wrappers remain one-line `@AGENTS.md` imports.
- Platform DELTA: Codex and Claude B sections contain only verified loading, diagnostics, permissions, enforcement, and fallback differences.
- Deterministic enforcement: manifest/schema/verifier/tests/workflows/sync scripts and repository gates enforce repeatable checks. Prose does not grant permissions or prove a gate ran.
- Discovery is reconciliation, not auto-enrollment. A new direct-child Git root blocks until a reviewed allowlist decision is made.

## Pre-Change Review

### pre_change_review

- Reviewed the global sources, deployed copies, manifest, nine target roots, existing rules/wrappers, CI workflows, repository gates, evidence paths, Git topology, and official loading model before changing sensitive files.
- Distinguished repository-owned differences from drift; target facts and commands were preserved, while only release markers and proven N/A recovery fields changed.

### control_repo_manifest_and_rule_sources

- Compared `rules/manifest.json`, `rules/global/codex/AGENTS.md`, `rules/global/claude/CLAUDE.md`, `rules/target-project-rule-coordination.json`, the coordination schema/spec, and the canonical target workflow.
- The manifest still distributes exactly two user-level copies. Coordination schema `2.3` audits nine explicit targets without storing or overwriting target bodies.

### user_level_deployed_rule_files

- Compared both deployed files with their sources before sync, ran dry-run, captured backup `docs/change-evidence/rule-sync-backups/20260715-003426/`, applied the two intended `9.55 -> 9.56` updates, and reran zero-drift.
- Raw source/deployed SHA-256: Codex `D3C873F73A378136B43588EBB2DB2291077A16A5FB8CFA9264AF22B17232786B`; Claude `4A24410AFA9F39911C05E745397858C44EA90216DCF989C4D817A16775F30A7C`.
- Sync semantic SHA-256: Codex `92883d03e51f45637e3290955660fcedf6139bf8823501a2e691fde780b4d284`; Claude `1a3e7c394443b9b06cfd71ccbf10616d83601f564dde389616a339d661b3927f`.

### repo_local_gate_scripts_and_ci

- Reviewed `scripts/build-runtime.ps1`, `scripts/verify-repo.ps1`, `scripts/doctor-runtime.ps1`, target gate declarations, the canonical `.github/workflows/agent-rule-contract.yml`, and the nine-repository aggregate matrix.
- Added direct-root inventory reconciliation, `utf8_lf_v1` workflow hashing, exact N/A field-token checks, and regression tests. No parallel bypass gate was added.

### repo_local_repo_profile

- Reviewed `.governed-ai/repo-profile.json` as the control repository's own policy surface. It neither distributes target rules nor carries target-private commands.
- No repo profile, host permission, provider, auth, MCP, or credential setting changed.

### repo_local_readme_and_operator_docs

- Updated the root README family, `docs/README.md`, bilingual existing-repository quickstarts, claim catalog, coordination spec, plan, and research routing.
- Documentation consistently states that discovery only reconciles the allowlist and that branch push, local loading, and default-branch effectiveness are separate facts.

### current_official_tool_loading_docs

- OpenAI conclusions use current Codex manual pages plus local `--help`, schema, version, and fresh `codex debug prompt-input` output.
- Anthropic conclusions use current Claude Code memory/settings/permissions/hooks/sandbox/debug documentation plus local `--help`, version, and fresh interactive `/context` output.

### drift-integration decision

- Adopted normalized workflow hashing because CRLF/LF differences were checkout artifacts; semantic workflow changes still block.
- Preserved repository-specific facts and unrelated dirty worktrees. Rejected blind target sync, template overwrite, hosted-surface inference, Gemini restoration, and pushing existing local ahead commits with this task.

## Reference Basis

### reference_basis_review

- The guarded coordination spec was checked against first-party host documentation, fixed official source commits, the current target-rule workflow, and the local nine-repository audit.

### changed_surface_paths

- `docs/specs/agent-rule-coordination-v2-spec.md`
- `rules/global/codex/AGENTS.md`
- `rules/global/claude/CLAUDE.md`
- `rules/manifest.json`
- `rules/target-project-rule-coordination.json`
- `schemas/jsonschema/target-project-rule-coordination.schema.json`
- `scripts/verify-target-project-rules.py`
- `tests/runtime/test_target_rule_ci.py`
- `tests/runtime/test_verify_target_project_rules.py`

### reference_basis_surface_ids

- `workflow-governance-and-spec-driven-delivery`

### required_local_reference_ids_reviewed

- `1code`
- `aider`
- `anthropic-claude-code`
- `github-spec-kit`
- `obra-superpowers`
- `openai-codex`
- `openclaw-code-agent`
- `swe-agent`

### reference_adoption_decision

- Adopted host-neutral project contracts, thin Claude imports, bounded root rules, deterministic schema/verifier/CI, fresh-process diagnostics, and explicit rollback/evidence.
- Rejected copying target bodies into the control repository, auto-enrollment, line-ending-sensitive hashes, prose-only enforcement, and community-derived host claims without official/local confirmation.

## Changes And Integration

- Global rules: bumped `9.55 -> 9.56`, kept A/C/D common text identical, refreshed platform B facts, and added `recovery_condition` to the N/A contract.
- Coordination contract: bumped `2.2 -> 2.3`; added direct-child Git-root inventory and `workflow_hash_mode=utf8_lf_v1`.
- Verifier: checks actual Git roots, reconciles dynamic inventory with the allowlist, reports raw/normalized workflow hashes and line endings, and validates N/A field identifiers without substring bypass.
- Tests: cover CRLF/LF equivalence, semantic drift, excluded/unlisted/missing roots, filtered CI layouts, Git-root identity, canonical workflow hashing, and complete N/A records.
- Targets: preserved commands/invariants and changed only `AGENTS.md` review metadata, required N/A recovery fields, and one bounded evidence file per repository. `CLAUDE.md` wrappers were already exact and were not rewritten.
- Validation artifact cleanup: removed the 20260715 `skills-manager` scan/report generated by this task after verification; preserved the user's 20260714 evidence and later unrelated dirty files.

## Verification

### Control And Coordination

| command | exit | result |
|---|---:|---|
| `python -m unittest tests.runtime.test_verify_target_project_rules tests.runtime.test_target_rule_ci` | 0 | 28 tests passed after the N/A token-boundary regression fix |
| focused governance suite | 0 | 36 tests passed in the earlier implementation slice |
| `python scripts/verify-agent-rule-family.py` | 0 | release 9.56; A/C/D common hash match; no failures |
| `python scripts/verify-target-project-rules.py --require-all` | 0 | 9 discovered, 9 passed, 0 missing/unlisted/failed |
| `python scripts/export-target-rule-ci-matrix.py` | 0 | nine entries with public/private aggregate routing preserved |
| `pwsh ... scripts/build-runtime.ps1` | 0 | `OK python-bytecode`, `OK python-import` |
| `pwsh ... scripts/verify-repo.ps1 -Check Runtime` | 0 | 101 test files, 8 workers, failures=0, 329.234s |
| first `pwsh ... scripts/verify-repo.ps1 -Check Contract` | 1 | correctly blocked on missing current-diff pre-change evidence; this file is the root-cause fix |
| second `pwsh ... scripts/verify-repo.ps1 -Check Contract` | 0 | schema/catalog, dependency, rules, pre-change, reference, and functional-effectiveness checks all passed |
| `pwsh ... scripts/doctor-runtime.ps1` | 0 | 29 runtime/path/gate/hook/status/capability checks passed |

### Repair Trace

- `issue_id=contract-pre-change-evidence-9.56`; `attempt_count=1`; `clarification_mode=direct_fix`.
- Root cause: the verifier intentionally accepts only current-diff `docs/change-evidence/*.md` files, while the 9.56 research and plan live under `docs/research/` and `docs/plans/`; old 9.55 evidence cannot authorize a new sensitive diff.
- Fix: this task ledger now carries the eight pre-change tokens plus the guarded coordination-spec reference-basis paths, surface ID, and all eight required local reference IDs.
- Direct verification: `verify-pre-change-review.py` and `verify-reference-basis.py` passed before the full Contract rerun; the full Contract then passed without changing or weakening either verifier.

### Fresh-Process Loading

- Codex: new `codex debug prompt-input` processes in the control repository and all nine targets each returned `items=5`, `global_956=true`, `project_rule=true`, and `project_review_956=true`.
- Claude: new interactive CLI sessions in the control repository and all nine targets ran local `/context` followed by `/exit`; all returned `user_claude=true`, `project_claude=true`, and `imported_agents=true`.
- These probes prove local loading only. They do not prove ChatGPT Work web, Codex cloud, Claude Chat, or Claude Code cloud workspace state.
- No existing Codex/Claude process was restarted, terminated, or taken over.

### Target Gates

Each repository evidence file records the ordered commands, exit code, key output, N/A, and rollback. Summary:

- `ai-content-delivery-studio`: build; 461 tests; reference/format; release preflight passed.
- `classroom-answer-toolkit`: build; 57 tests; 43 assets/3 packs/3 snapshots; toolchain passed.
- `ClassroomToolkit`: build, 3544 tests, 29 contract tests, and hotspot passed; canonical full gate failed at dependency governance.
- `github-toolkit`: compile, 189 tests, Ruff, and Mypy passed; independent contract command is five-field `gate_na`.
- `k12-question-graph`: build, roadmap guard, C002 dry-run, and structured data parsing passed; process-impacting full gate and independent hotspot are five-field `gate_na`.
- `local-ai-dev-orchestrator`: 307 tests, planning verifier, selector, and release preflight passed; build/hotspot N/A remain tied to the first executable slice.
- `qq-codex-bot`: 867 tests/10 skipped and full verifier passed; local health probe completed with `all_checks_ok=false`; no VPS projection occurred.
- `skills-manager`: Unit 484 + E2E 12, doctor, dependency baseline, and full local gate passed.
- `vps-ssh-launcher`: 93 pytest/1 skipped/20 subtests, 94 unittest/1 skipped, and offline full gate passed.

## Git Ledger

| repository | committed/pushed SHA | remote ref | default_branch_effective | status |
|---|---|---|---|---|
| `ai-content-delivery-studio` | `374905426e7e959fd00851a5d3d9eed7901c007e` | `main` | yes | repo-side and default branch complete |
| `classroom-answer-toolkit` | `6486358e7ff5081a59b3d6168967ab0d9169a2fd` | `main` | yes | repo-side and default branch complete |
| `ClassroomToolkit` | `cd49d47a34e67a383fb1017a9f53ced5b15e038a` | `codex/agent-rule-governance-9.56` | no | pushed; dependency governance blocked |
| `github-toolkit` | `811afc3c04d47c3c829a5f6b19d99a1b0b2ceeab` | `main` | yes | repo-side and default branch complete |
| `k12-question-graph` | `5c987cefe0f0ee0fd8d35af8679aed3cd895d789` | `codex/agent-rule-governance-9.56` | no | pushed; existing local main ahead 2 preserved |
| `local-ai-dev-orchestrator` | `c9f70f5709e20916c7b11b0fb1cbc24e781b4065` | `codex/agent-rule-governance-9.56` | no | pushed; existing local main ahead 8 preserved |
| `qq-codex-bot` | `47c7d71a50cd50c921e1362d4a98c8fc2161b768` | `main` | yes | repo-side and default branch complete; live deployment pending |
| `skills-manager` | `4addb13e201efb29e404b1c086f7cd4b48293911` | `codex/agent-rule-governance-9.56` | no | pushed; existing local main ahead and user dirty files preserved |
| `vps-ssh-launcher` | `2a575120314fb578651f3ddb619ebd63d427636b` | `main` | yes | repo-side and default branch complete |

Every push was preceded by `git fetch origin main` and a parent-SHA equality check. Every remote object was then checked with `git ls-remote`. No force push, PR merge, branch deletion, or worktree deletion occurred.

The control-repository commit cannot self-record its own SHA without a follow-up commit. Its final local/remote object equality is therefore verified after this evidence is committed and reported in the task closeout.

## Risks And N/A

- `ClassroomToolkit` blocker: `scripts/quality/dependency-outdated-waivers.json` expired on `2026-06-30`, and stable dependency drift remains. This task did not renew risk acceptance or perform dependency upgrades.
- Hosted surfaces: ChatGPT Work web/mobile, Codex cloud, Claude Chat, and Claude Code cloud are `platform_na` for local-file loading proof. Alternative evidence is official surface documentation plus local source/deployed hashes; recovery requires an authorized fresh hosted workspace session.
- K12 process-impacting full gate: not run because PostgreSQL/API pause-resume impact was not authorized. Recovery requires explicit process-impact authorization and `tools/run-gates.ps1`.
- QQ live deployment: repository verification passed, but VPS projection/health acceptance remains manual and no remote process was touched.
- Codex config schema: eight `mcp_servers.*.transport` findings remain outside this task; no config repair or provider/auth change was attempted.
- Protected dirty state: control `docs/change-evidence/governance-hub-certification-report.json`; skills-manager `skills.ps1`, `src/Commands/AuditTargets.Snapshot.ps1`, `tests/Unit/AuditTargets.Tests.ps1`, and `docs/change-evidence/20260714-audit-runtime-scan-20260714-235154-812-235330.md`.

## Completion Boundary

- fully_completed: global source optimization, protected sync/apply/zero-drift, local Codex/Claude fresh-process loading, control contract implementation, five targets effective on remote `main`.
- repo_side_completed: all nine targets were discovered, audited, changed, and have task commits with repository evidence.
- pushed_but_not_default_branch_effective: `ClassroomToolkit`, `k12-question-graph`, `local-ai-dev-orchestrator`, `skills-manager`.
- onsite_manual_acceptance_pending: hosted OpenAI/Anthropic surfaces, K12 process-impacting full gate, QQ VPS deployment/health.
- blocked: `ClassroomToolkit` dependency governance; resolution requires waiver owner action or a dedicated dependency compatibility slice.

Overall completion must not be claimed while the blocker, four non-default branches, and onsite/manual acceptance items remain open.

## Rollback

- Global copies: restore from `docs/change-evidence/rule-sync-backups/20260715-003426/`, or revert the 9.56 sources and rerun guarded sync plus zero-drift.
- Control repository: revert only this task's rules/manifest/schema/verifier/tests/docs/evidence commit; preserve the user certification report.
- Target repositories: revert the listed task SHA on its published ref; do not reset the repository or touch preserved ahead/dirty work.
- After rollback, rerun family, strict target audit, sync dry-run, fresh-process loading, and the applicable fixed-order gates.
