# Agent Rule v9.45 Coordination Evidence

## Goal
- 优化 Codex / Claude / Gemini 全局用户级规则与目标仓项目级规则，强化 `1+1>2` 协同：全局只定义 WHAT，项目级只定义 WHERE/HOW，平台差异只落在各自 `B` 节。
- 修改前先比对控制仓源文件、用户目录、目标仓分发副本与当前官方加载模型，避免盲目覆盖。

## Source Review
- OpenAI Codex `AGENTS.md`: https://developers.openai.com/codex/guides/agents-md
- Claude Code memory and best practices: https://docs.anthropic.com/en/docs/claude-code/memory, https://code.claude.com/docs/en/best-practices
- Gemini CLI memory and configuration: https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/gemini-md.md, https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/configuration.md
- Community / practice signal reviewed: concise operational files, exact build/test commands, quick or file-scoped validation, examples by reference, and treating rule files as code that must be tested after edits.

## Changes
- Bumped managed rule family from `9.44` to `9.45`; `rules/manifest.json` `sync_revision` is `2026-04-28.1`.
- Added source/target drift review before rule edits across global and project rules.
- Added common rule quality boundary: long-term rules must map to behavior, command, field, evidence, or explicit prohibition.
- Kept `A/C/D` common and `B` platform-specific across Codex / Claude / Gemini.
- Updated platform differences:
  - Codex: `project_doc_fallback_filenames` and `.codex/rules/*.rules` boundary.
  - Claude: `paths` frontmatter, `/memory`, Plan Mode for uncertain multi-file work, and hooks/CI/gates for repeated prose failures.
  - Gemini: context file names must follow current schema/help; `/memory show` and `.geminiignore` remain the verification boundary.
- Updated `docs/targets/target-repo-governance-baseline.json` and target profile projections with `quick_feedback_boundary` and `source_target_drift_review`.
- Normalized managed rule source files to one trailing newline after sync exposed same-version hash drift from extra EOF blank lines.

## Verification
- Initial drift check before edits: `python scripts/sync-agent-rules.py --scope All --fail-on-change` -> `status=pass`, `entry_count=18`, `changed_count=0`, `blocked_count=0`.
- Post-edit dry run: `python scripts/sync-agent-rules.py --scope All --fail-on-change` -> expected `status=dry_run_changes`, `changed_count=18`, `blocked_count=0`.
- First apply: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -Apply` -> `status=applied`, `changed_count=18`, `blocked_count=0`; backup root `docs/change-evidence/rule-sync-backups/20260428-001402/`.
- Target governance baseline apply: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -ApplyGovernanceBaselineOnly -Json` -> `target_count=5`, `failure_count=0`.
- EOF normalization apply: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -Apply -Force` -> `status=applied`, `changed_count=10`, `blocked_count=0`; backup root `docs/change-evidence/rule-sync-backups/20260428-001951/`.
- Final sync check: `python scripts/sync-agent-rules.py --scope All --fail-on-change` -> `status=pass`, `entry_count=18`, `changed_count=0`, `blocked_count=0`.
- Target governance consistency: `python scripts/verify-target-repo-governance-consistency.py` -> `status=pass`, `sync_revision=2026-04-28.1`, `drift_count=0`.
- Build: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1` -> `OK python-bytecode`, `OK python-import`.
- Runtime test: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` -> `Completed 74 test files`, `failures=0`.
- Contract: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` -> `OK agent-rule-sync`, `OK functional-effectiveness`.
- Hotspot: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1` -> all checks `OK`, including `codex-capability-ready` and `adapter-posture-visible`.

## Rollback
- Preferred rollback: git restore/revert the managed source changes in this control repo, then rerun `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -Apply`.
- Backup rollback: restore specific distributed rule files from `docs/change-evidence/rule-sync-backups/20260428-001402/` or `docs/change-evidence/rule-sync-backups/20260428-001951/`.
