# Agent Rule v9.52 Wrapper Convergence

## Scope
- rule_id: `agent-rule-v9.52-wrapper-convergence`
- risk_level: `medium`
- current_landing: control-repo rule sources, global user deployed rules, and target-repo project rule files
- target_landing: Codex/Claude/Gemini rule family v9.52 with `AGENTS.md` as the common project body and thin Claude/Gemini import wrappers
- rollback_ref: `docs/change-evidence/rule-sync-backups/20260504-102715/` plus git history

## Basis
- OpenAI Codex official guidance confirms `AGENTS.md` discovery, user/project layering, override behavior, fallback filename configuration, and size-bound project-doc loading.
- Claude Code official memory guidance favors concise `CLAUDE.md`, supports project/user/local memory surfaces, and documents that large memory files reduce adherence.
- Gemini CLI official docs currently show `GEMINI.md` hierarchy, `/memory show`, `/memory reload`, `@file` imports, configurable `context.fileName`, JIT context discovery, and ignore/trust boundaries; older rendered docs still mention `/memory refresh`, so rules now require help-gated fallback rather than one hard-coded command.
- AGENTS.md community guidance supports a predictable README-for-agents surface with setup, test, style, security, and scoped nested rules.
- Pre-change local evidence: `python scripts/sync-agent-rules.py --scope All --fail-on-change` returned `pass`, 21 entries, `skipped_same_hash` before the source rewrite.

## pre_change_review
- `pre_change_review`: required because this change modifies rule sources, deployed rule files, `rules/manifest.json`, `docs/targets/target-repo-governance-baseline.json`, target `.governed-ai/repo-profile.json` files, sync backups, and rule-sync tests.
- `control_repo_manifest_and_rule_sources`: reviewed and changed `rules/manifest.json`, `rules/global/*`, and `rules/projects/*` as the source-of-truth rule family.
- `user_level_deployed_rule_files`: compared and synchronized `C:\Users\sciman\.codex\AGENTS.md`, `C:\Users\sciman\.claude\CLAUDE.md`, and `C:\Users\sciman\.gemini\GEMINI.md`.
- `target_repo_deployed_rule_files`: compared and synchronized target `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` files for `classroomtoolkit`, `github-toolkit`, `k12-question-graph`, `self-runtime`, `skills-manager`, and `vps-ssh-launcher`.
- `target_repo_gate_scripts_and_ci`: target project rules retain each repo's existing build/test/contract/hotspot commands; this slice changed rule-loading shape, not target gate scripts or CI.
- `target_repo_repo_profile`: refreshed all six target `.governed-ai/repo-profile.json` files with `runtime-flow-preset.ps1 -AllTargets -ApplyGovernanceBaselineOnly -ApplyCodingSpeedProfile -Json`; consistency verifier returned `drift_count=0`.
- `target_repo_readme_and_operator_docs`: target README/operator docs were treated as inputs for boundary review; this slice did not rewrite their project usage text.
- `current_official_tool_loading_docs`: checked current Codex, Claude Code, Gemini CLI, and AGENTS.md guidance before changing loading semantics.
- `drift-integration decision`: source/deployed drift was first classified by `sync-agent-rules.py`; target-local rule files were aligned through the managed manifest path, and generated backups were retained under `docs/change-evidence/rule-sync-backups/20260504-102715/`.

## Changes
- Bumped `rules/manifest.json` and all managed rule entries from `9.51` to `9.52`.
- Kept global files in the shared `1 / A / B / C / D` structure while adding official/community evidence layering, wrapper-import boundaries, concise-root constraints, and deterministic-enforcement escalation rules.
- Converted all target-repo `CLAUDE.md` and `GEMINI.md` project rules into thin wrappers with an independent `@AGENTS.md` import line and only `1 / B / D` platform-specific sections.
- Kept target-repo `AGENTS.md` files as the shared project-rule body, with explicit wrapper structure and "do not duplicate common body" maintenance constraints.
- Updated `docs/targets/target-repo-governance-baseline.json` and all target `.governed-ai/repo-profile.json` files to prefer `/memory reload` with `/memory refresh` fallback when installed help still exposes the older spelling.
- Added `tests.runtime.test_agent_rule_sync.AgentRuleSyncTests.test_project_claude_and_gemini_rules_are_import_wrappers` to prevent future rule-copy bloat.

## Commands And Evidence
- `python -m unittest tests.runtime.test_agent_rule_sync tests.runtime.test_target_repo_governance_consistency`
  - result: `OK`, 38 tests.
- `python scripts/sync-agent-rules.py --scope All --fail-on-change`
  - before apply result: `dry_run_changes`, `changed_count=21`, `blocked_count=0`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -Apply`
  - result: `applied`, `entry_count=21`, `changed_count=21`, `blocked_count=0`.
  - backup root: `docs/change-evidence/rule-sync-backups/20260504-102715/`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -ApplyGovernanceBaselineOnly -ApplyCodingSpeedProfile -Json`
  - result: `failure_count=0`, `target_count=6`.
  - changed field across targets: `rule_file_coordination_policy`.
- `python scripts/sync-agent-rules.py --scope All --fail-on-change`
  - after apply result: `pass`, `changed_count=0`, all 21 entries `skipped_same_hash`.
- `python scripts/verify-target-repo-governance-consistency.py`
  - result: `pass`, `sync_revision=2026-05-04.2`, `target_count=6`, `drift_count=0`.
- `rg -n "v9\\.51|三文件同构" ...`
  - result: no active rule/test/target-rule matches outside historical evidence archives.
- First `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - result: fail-closed on `pre-change-review`; the evidence file existed but did not yet contain all required machine-readable `pre_change_review` tokens.
- `python scripts\verify-pre-change-review.py --repo-root .`
  - result: `pass`; matched evidence `docs/change-evidence/20260504-agent-rule-v952-wrapper-convergence.md`.
- `python -m unittest tests.runtime.test_transition_stack_convergence tests.runtime.test_functional_effectiveness tests.runtime.test_dependency_baseline tests.runtime.test_run_governed_task_cli`
  - result: `OK`, 25 tests after closing the evidence-token gap.
- Final `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - result: `OK runtime-unittest`, `OK runtime-service-parity`, `OK runtime-service-wrapper-drift-guard`; 104 test files, `failures=0`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - result: pass; includes `OK target-repo-governance-consistency`, `OK agent-rule-sync`, `OK pre-change-review`, and `OK functional-effectiveness`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  - result: pass with existing `WARN codex-capability-degraded`; all doctor checks returned `OK` except the known native-attach posture warning.
- `git diff --check`
  - result: exit code `0`; only Windows CRLF conversion warnings were emitted.
- Generated evidence artifacts refreshed by gates:
  - `docs/change-evidence/runtime-test-speed-latest.json` now records the final Runtime gate timing.
  - `docs/change-evidence/repo-map-context-artifact.json` updated `excluded_archive_candidate_count` from 140 to 161 because the rule-sync backup set added 21 rollback files.

## Compatibility
- Codex keeps direct `AGENTS.md` loading semantics.
- Claude/Gemini project wrappers now rely on a real import line, not metadata-only declarations.
- Wrapper files no longer duplicate project facts, reducing drift while preserving tool-specific diagnostics, permission hooks, settings boundaries, and memory reload instructions.
- Gemini reload wording is version-tolerant: current upstream source uses `/memory reload`; older installed or rendered help can still be followed as `/memory refresh` when verified.
- Target repo dirty worktrees were not reverted; managed sync touched only manifest-owned rule files and governance baseline/profile fields.

## Rollback
- Revert the v9.52 source changes through git history, or restore deployed files from `docs/change-evidence/rule-sync-backups/20260504-102715/`.
- Rerun `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -Apply`.
- Rerun `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -ApplyGovernanceBaselineOnly -ApplyCodingSpeedProfile -Json` if the governance baseline revision is rolled back.
- Close with `python scripts/sync-agent-rules.py --scope All --fail-on-change` and `python scripts/verify-target-repo-governance-consistency.py`.
