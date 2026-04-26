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
  - Gemini: use `~/.gemini/GEMINI.md`, workspace/JIT `GEMINI.md`, `/memory list/show/refresh`, and `@file.md` imports; do not assume `GEMINI.override.md`.
- Added explicit `Global Rule -> Repo Action` mappings to target project rule files so `E4/E5/E6` are no longer only implied by profile policy.

## Source Review
- OpenAI Codex official docs: `AGENTS.md` discovery supports global and project layering, root-to-current-directory merge order, `AGENTS.override.md`, fallback filenames, and verification prompts.
- OpenAI Codex official docs: hooks/rules can make repeatable validation or permission behavior deterministic instead of relying only on prose.
- Anthropic Claude Code official docs: `CLAUDE.md` is context, not enforced configuration; project/user/local scopes, `.claude/rules/`, imports, `/memory`, and concise files are recommended.
- Google Gemini CLI official docs: `GEMINI.md` supports global, workspace, and just-in-time context, `/memory` commands, and `@file.md` imports.
- Community/research signal: keep root rule files concise, concrete, and constraint-oriented; move long procedures to child docs or scoped rule mechanisms.

## Risk
- Risk level: low, documentation/profile-only.
- Compatibility: existing gate order remains `build -> test -> contract/invariant -> hotspot`; no business code or public runtime schema behavior changed.

## Verification
- `python -m json.tool docs\targets\target-repo-governance-baseline.json`
- `python -m json.tool docs\targets\target-repo-rollout-contract.json`
- `python -m json.tool docs\targets\target-repos-catalog.json`
- `python -m json.tool .governed-ai\repo-profile.json`
- `rg -n "GlobalUser/(AGENTS|CLAUDE|GEMINI)\.md v9\.40|CLAUDE\.override|GEMINI\.override" ...` -> only expected "do not assume ..." lines remain.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -ApplyGovernanceBaselineOnly -Json` -> `failure_count=0`, `target_count=5`.
- `python scripts\verify-target-repo-governance-consistency.py` -> `status=pass`, `target_count=5`, `drift_count=0`, `sync_revision=2026-04-26.3`.
- `python -m unittest tests.runtime.test_target_repo_governance_consistency` -> 6 tests passed.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1` -> passed.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` -> passed after rerun with longer timeout; 389 tests passed, 2 skipped, plus 10 tests passed.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` -> passed.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1` -> passed.

## Rollback
- Restore the global rule backups created at `*.bak-20260426`.
- Revert changed repo files through git history or file diffs.
- Re-run target governance consistency after rollback.
