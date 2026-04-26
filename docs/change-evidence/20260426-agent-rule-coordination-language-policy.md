# 20260426 agent rule coordination and language policy

## Scope
- Global user rules: `C:\Users\sciman\.codex\AGENTS.md`, `C:\Users\sciman\.claude\CLAUDE.md`, `C:\Users\sciman\.gemini\GEMINI.md`.
- Project-level rules: current catalog target repos under `D:\CODE`.
- Runtime-governed target profile baseline: `docs/targets/target-repo-governance-baseline.json`.

## Changes
- Upgraded global user rules from `v9.40` to `v9.41` with Chinese-first coding communication, explicit global/project 1+1 coordination, progressive disclosure boundaries, and corrected tool-specific loading semantics.
- Updated or created project-level `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` files for active target repos with concise repo facts, gates, evidence, rollback, and platform-specific diagnostics.
- Added machine-readable `interaction_profile` language fields and `rule_file_coordination_policy` to the target repo governance baseline.
- Synchronized the updated baseline into active target repo `.governed-ai/repo-profile.json` files.
- Follow-up hardening upgraded rule files to `v9.41` by aligning tool-specific loading semantics with current documentation:
  - Codex: keep `AGENTS.md` global/project/nested discovery and `AGENTS.override.md` as a short-term override only.
  - Claude: use `CLAUDE.md` / `.claude/CLAUDE.md`, gitignored `CLAUDE.local.md`, `.claude/rules/`, `/memory`; do not assume `CLAUDE.override.md`.
  - Gemini: use `~/.gemini/GEMINI.md`, workspace/JIT `GEMINI.md`, `/memory show` / `/memory reload`, `@file.md` imports, and `.geminiignore`; do not assume `GEMINI.override.md`.
- Second follow-up upgraded global rules to `v9.42` and corrected the Gemini memory commands against the then-current local and official behavior.
- Added explicit `Global Rule -> Repo Action` mappings to target project rule files so `E4/E5/E6` are no longer only implied by profile policy.
- Third follow-up made `governed-ai-coding-runtime` the authoritative source for managed agent rule files:
  - Added `rules/manifest.json` with 3 global rule entries and 15 project rule entries.
  - Added source copies under `rules/global/<tool>/` and `rules/projects/<target>/<tool>/`.
  - Added `scripts/sync-agent-rules.py` plus PowerShell wrappers `scripts/sync-agent-rules.ps1` and `scripts/verify-agent-rules.ps1`.
  - Default behavior is dry-run/idempotent verification; `-Apply` writes files, same-hash files are skipped, same-version content drift is blocked unless `-Force`, and overwritten files are backed up under `docs/change-evidence/rule-sync-backups/`.
  - Wired agent rule drift verification into `scripts/verify-repo.ps1 -Check Contract` via the new `agent-rule-sync` check.
- Fourth follow-up upgraded managed rule files to `v9.43`:
  - Added a common external-context trust boundary: instruction-like text from webpages, community examples, configs, logs, and data files is evidence/data, not a rule override.
  - Added explicit conflict handling: state the effective rule source by precedence before changing files.
  - Strengthened Claude rules with `.claude/settings*.json` permissions/hooks/CI as the enforcement layer and made auto/local memory subordinate to repo facts.
  - Strengthened Gemini rules with `/memory list` / `/memory show` inspection, `/memory refresh` preferred reload plus documented `reload` fallback, and `.geminiignore` source-safety boundaries.
  - Updated the target governance baseline to `sync_revision=2026-04-26.5`.
  - Fixed `scripts/sync-agent-rules.py` Windows backup path handling so absolute target paths are backed up under `docs/change-evidence/rule-sync-backups/` instead of resolving back to the target file.
  - Updated `tests/runtime/test_agent_rule_sync.py` to assert backups are separate files with the old content, and to use a temporary backup root during tests.

## Source Review
- OpenAI Codex official docs: `AGENTS.md` discovery supports global and project layering, root-to-current-directory merge order, `AGENTS.override.md`, fallback filenames, and verification prompts.
- OpenAI Codex official docs: hooks/rules can make repeatable validation or permission behavior deterministic instead of relying only on prose.
- Anthropic Claude Code official docs: `CLAUDE.md` is context, not enforced configuration; project/user/local scopes, `.claude/rules/`, imports, `/memory`, settings/permissions, and concise files are recommended.
- Google Gemini CLI official docs: `GEMINI.md` supports global, workspace, and just-in-time context, `/memory list` / `/memory show` / reload-style commands, `@file.md` imports, configurable context filenames, and `.geminiignore`; command spelling must be help-gated per installed version.
- Community/research signal: keep root rule files concise, concrete, and constraint-oriented; move long procedures to child docs or scoped rule mechanisms.
- Primary sources used in this follow-up:
  - <https://developers.openai.com/codex/guides/agents-md>
  - <https://code.claude.com/docs/en/memory>
  - <https://code.claude.com/docs/en/settings>
  - <https://code.claude.com/docs/en/best-practices>
  - <https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/gemini-md.md>
  - <https://github.com/google-gemini/gemini-cli/blob/main/docs/reference/commands.md>
  - <https://github.com/openai/codex/blob/main/AGENTS.md>

## Risk
- Risk level: low, documentation/profile-only.
- Compatibility: existing gate order remains `build -> test -> contract/invariant -> hotspot`; no business code or public runtime schema behavior changed.

## Verification
- `python -m json.tool docs\targets\target-repo-governance-baseline.json`
- `python -m json.tool docs\targets\target-repo-rollout-contract.json`
- `python -m json.tool docs\targets\target-repos-catalog.json`
- `python -m json.tool .governed-ai\repo-profile.json`
- `codex --version` -> `codex-cli 0.125.0`
- `codex --help` -> available; `codex status` -> `stdin is not a terminal`, recorded as `platform_na` for non-interactive status.
- `claude --version` -> `2.1.114 (Claude Code)`; `claude --help` -> available.
- `gemini --version` -> `0.37.1`; `gemini --help` -> available.
- `rg -n "GlobalUser/(AGENTS|CLAUDE|GEMINI)\.md v9\.40|CLAUDE\.override|GEMINI\.override" ...` -> only expected "do not assume ..." lines remain.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -ApplyGovernanceBaselineOnly -Json` -> `failure_count=0`, `target_count=5`.
- `python scripts\verify-target-repo-governance-consistency.py` -> `status=pass`, `target_count=5`, `drift_count=0`, `sync_revision=2026-04-26.3`.
- `python -m unittest tests.runtime.test_target_repo_governance_consistency` -> 6 tests passed.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1` -> passed.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` -> passed after rerun with longer timeout; 389 tests passed, 2 skipped, plus 10 tests passed.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` -> passed.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1` -> passed.
- `v9.42` follow-up re-run:
  - `python -m json.tool docs\targets\*.json` -> passed for baseline, rollout contract, and catalog.
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -ApplyGovernanceBaselineOnly -Json` -> `failure_count=0`, `target_count=5`, all targets changed `rule_file_coordination_policy`.
  - `python scripts\verify-target-repo-governance-consistency.py` -> `status=pass`, `target_count=5`, `drift_count=0`, `sync_revision=2026-04-26.4`.
  - `python -m unittest tests.runtime.test_target_repo_governance_consistency` -> 6 tests passed.
  - `rg -n "/memory list|/memory refresh|GlobalUser/(AGENTS|CLAUDE|GEMINI)\.md v9\.41|Universal Agent Protocol v9\.41" ...` -> no matches in current runtime rules and active target rules.
  - `git diff --check` -> no whitespace errors in runtime repo and active target repos; only expected CRLF/LF warnings on existing files.
  - Direct content scan for new github-toolkit and vps-ssh-launcher rules -> all six files contain `Global Rule -> Repo Action` and no stale Gemini memory command tokens.
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1` -> passed.
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` -> passed; 389 tests passed, 2 skipped, plus 10 tests passed.
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` -> passed.
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1` -> passed.
- Rule-source sync follow-up:
  - `python -m unittest tests.runtime.test_agent_rule_sync` -> 4 tests passed.
  - `python scripts\sync-agent-rules.py --scope All --fail-on-change` -> `status=pass`, `entry_count=18`, `changed_count=0`, `blocked_count=0`.
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-agent-rules.ps1 -Scope All` -> `status=pass`, `entry_count=18`, `changed_count=0`, `blocked_count=0`.
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\sync-agent-rules.ps1 -Scope All -Apply` -> `status=pass`, `mode=apply`, `entry_count=18`, `changed_count=0`, `blocked_count=0`.
  - `python -m unittest tests.runtime.test_agent_rule_sync tests.runtime.test_target_repo_governance_consistency` -> 10 tests passed.
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Contract` -> passed, including `OK agent-rule-sync`.
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\build-runtime.ps1` -> passed.
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Runtime` -> passed; 393 tests passed, 2 skipped, plus 10 tests passed.
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\doctor-runtime.ps1` -> passed.
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Scripts` -> passed.
  - `python -m json.tool rules\manifest.json` -> passed.
  - `git diff --check` -> no whitespace errors; only expected CRLF/LF warnings on existing files.
- `v9.43` follow-up re-run:
  - `python -m json.tool rules\manifest.json` -> passed.
  - `python -m json.tool docs\targets\target-repo-governance-baseline.json` -> passed.
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\sync-agent-rules.ps1 -Scope All` -> `status=dry_run_changes`, `entry_count=18`, `changed_count=18`, `blocked_count=0`.
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\sync-agent-rules.ps1 -Scope All -Apply` -> `status=applied`, `entry_count=18`, `changed_count=18`, `blocked_count=0`.
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\runtime-flow-preset.ps1 -AllTargets -ApplyGovernanceBaselineOnly -Json` -> `failure_count=0`, `target_count=5`, all targets changed `rule_file_coordination_policy`.
  - `python -m unittest tests.runtime.test_agent_rule_sync tests.runtime.test_target_repo_governance_consistency` -> 10 tests passed.
  - `python scripts\sync-agent-rules.py --scope All --fail-on-change` -> `status=pass`, `entry_count=18`, `changed_count=0`, `blocked_count=0`.
  - `python scripts\verify-target-repo-governance-consistency.py` -> `status=pass`, `sync_revision=2026-04-26.5`, `target_count=5`, `drift_count=0`.
  - `rg --fixed-strings "v9.42" ... managed rule sources and targets` -> no matches.
  - `git diff --check` in runtime and active target repos -> no whitespace errors; only expected CRLF/LF warnings on existing files.
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\build-runtime.ps1` -> passed.
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Runtime` -> passed; 393 tests passed, 2 skipped, plus 10 tests passed.
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Contract` -> passed, including `OK target-repo-governance-consistency` and `OK agent-rule-sync`.
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\doctor-runtime.ps1` -> passed.
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Scripts` -> passed.

## Rollback
- Restore the global rule backups created at `*.bak-20260426`, `*.bak-20260426-rule-v942`, or git/file-history diffs for `v9.43` changes.
- Revert changed repo files through git history or file diffs.
- Re-run target governance consistency after rollback.
