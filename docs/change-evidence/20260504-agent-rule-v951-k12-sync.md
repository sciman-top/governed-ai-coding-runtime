# Agent Rule v9.51 k12 Sync And Wrapper Boundary

- date: 2026-05-04
- rule_ids: R1, R2, R4, R6, R8, E4, E5, E6
- risk: medium
- current_landing: `rules/global/*`, `rules/projects/*`, `rules/manifest.json`, `docs/targets/target-repo-governance-baseline.json`, managed global and target rule files
- target_landing: Codex/Claude/Gemini global and project rule family v9.51, including k12-question-graph project rules and explicit import-wrapper boundaries
- rollback: restore this change set from git history, then run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -Apply`; target backups are created under `docs/change-evidence/rule-sync-backups/<timestamp>/`

## pre_change_review
- `pre_change_review`: required because this change modifies rule sources, manifest, target baseline policy, tests, and deployed global/target rule files.
- `control_repo_manifest_and_rule_sources`: reviewed `rules/manifest.json`, existing `rules/global/{codex,claude,gemini}`, existing project rule sources, and the live k12 target-local `AGENTS.md` / `CLAUDE.md` / `GEMINI.md`.
- `user_level_deployed_rule_files`: dry-run before edits showed global user files under `C:\Users\sciman\.codex`, `C:\Users\sciman\.claude`, and `C:\Users\sciman\.gemini` were same-hash with v9.50 sources.
- `target_repo_deployed_rule_files`: dry-run before edits showed all 18 then-managed entries were same-hash; k12 had local project rule files but no manifest entries.
- `target_repo_gate_scripts_and_ci`: reviewed target catalog commands for k12: `dotnet build apps/api/K12QuestionGraph.Api.csproj`, `tools/run-gates.ps1`, `tools/run-c002-dry-run-suite.ps1`, and `tools/run-roadmap-guard.ps1`.
- `target_repo_repo_profile`: k12 `.governed-ai/repo-profile.json` exists from target onboarding and carries `rule_file_coordination_policy`; baseline profile policy is updated to include import-wrapper and Trusted Folders boundaries.
- `target_repo_readme_and_operator_docs`: k12 `README.md`, prior onboarding evidence, and current project rules identify teacher-first workflow, dynamic asset contracts, full gate, quick gate, evidence, and rollback boundaries.
- `current_official_tool_loading_docs`: refreshed current sources before editing:
  - OpenAI Codex AGENTS.md guide: https://developers.openai.com/codex/guides/agents-md
  - AGENTS.md community format: https://agents.md/
  - Claude Code memory: https://code.claude.com/docs/en/memory
  - Claude Code settings: https://code.claude.com/docs/en/settings
  - Claude Code hooks: https://code.claude.com/docs/en/hooks
  - Gemini CLI GEMINI.md context: https://google-gemini.github.io/gemini-cli/docs/cli/gemini-md.html
  - Gemini CLI Trusted Folders: https://google-gemini.github.io/gemini-cli/docs/cli/trusted-folders.html
  - Gemini CLI Memory Import Processor: https://google-gemini.github.io/gemini-cli/docs/core/memport.html
- `drift-integration decision`: integrate k12 target-local rule facts into control-repo sources instead of leaving k12 unmanaged; do not blindly preserve the oversized local wording. Use `AGENTS.md` as the common project body and wrapper files for Claude/Gemini platform differences.

## Source Review Summary
- OpenAI Codex docs confirm global plus project `AGENTS.md` layering, `AGENTS.override.md`, fallback filenames, 32 KiB default `project_doc_max_bytes`, and one-file-per-directory discovery.
- AGENTS.md community guidance supports concise agent-focused content: setup/test commands, code style, security considerations, nested rules for scoped work, and a dedicated agent surface separate from README.
- Claude Code docs confirm `CLAUDE.md` is context rather than enforcement, recommend concise files, support `@AGENTS.md` import for repositories that already use AGENTS.md, support `.claude/rules/` and `paths` frontmatter, and place enforcement in settings/permissions/hooks.
- Gemini CLI docs confirm `GEMINI.md` hierarchy, `/memory show`, `/memory refresh`, `@file` imports, `.geminiignore`, configurable `context.fileName`, and Trusted Folders safe mode.
- Community/research signal remains lower authority than official docs and local code facts; it was used only to prefer concrete, minimal, verifiable rules and avoid abstract preference wallpaper.

## Changes
- Bumped manifest `default_version` to `9.51` and `sync_revision` to `2026-05-04.1`.
- Added k12-question-graph to the manifest as three project rule entries, increasing project rule entries from 15 to 18.
- Added control-repo k12 project rule sources:
  - `rules/projects/k12-question-graph/codex/AGENTS.md`: common self-contained project rule body.
  - `rules/projects/k12-question-graph/claude/CLAUDE.md`: `@AGENTS.md` wrapper plus Claude differences.
  - `rules/projects/k12-question-graph/gemini/GEMINI.md`: `@AGENTS.md` wrapper plus Gemini differences.
- Updated global Codex/Claude/Gemini rules with import-wrapper acceptance: self-contained `AGENTS.md` keeps common project facts; Claude/Gemini wrappers may stay short when the merged context still exposes `1 / A / B / C / D`, gates, evidence, rollback, and platform differences.
- Updated `rule_file_coordination_policy` baseline with AGENTS.md community guidance, Claude `@AGENTS.md` import guidance, Gemini Trusted Folders safe mode, shallow import guidance, and the `common_project_rule_import_or_full_body` required field.
- Updated tests to expect 18 project rule entries and the v9.51 manifest version.

## Verification Plan
- `codex --version`; `codex --help`
- `claude --version`; `claude --help`
- `gemini --version`; `gemini --help`
- `python -m unittest tests.runtime.test_agent_rule_sync tests.runtime.test_target_repo_governance_consistency`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -Apply`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -ApplyGovernanceBaselineOnly -Json`
- `python scripts/verify-target-repo-governance-consistency.py`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

## Verification Results
- Tool diagnostics:
  - `codex --version`: `codex-cli 0.128.0`; `codex --help` confirmed current command surface.
  - `claude --version`: `2.1.114 (Claude Code)`; `claude --help` confirmed current command surface.
  - `gemini --version`: `0.37.1`; `gemini --help` confirmed current command surface.
- Focused unit checks: `python -m unittest tests.runtime.test_agent_rule_sync tests.runtime.test_target_repo_governance_consistency` passed, `Ran 37 tests`.
- Rule sync:
  - Pre-apply dry-run: `python scripts/sync-agent-rules.py --scope All --fail-on-change` reported `entry_count=21`, `changed_count=18`, `blocked_count=0`.
  - Apply: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -Apply` reported `status=applied`, `changed_count=18`, `blocked_count=0`.
  - Backups: `docs/change-evidence/rule-sync-backups/20260504-035643/` and `docs/change-evidence/rule-sync-backups/20260504-035644/`.
  - Post-apply dry-run: `python scripts/sync-agent-rules.py --scope All --fail-on-change` reported `status=pass`, `entry_count=21`, `changed_count=0`, `blocked_count=0`.
- Governance baseline:
  - Apply: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -ApplyGovernanceBaselineOnly -Json` reported `target_count=6`, `failure_count=0`; each target changed only `rule_file_coordination_policy`.
  - Consistency: `python scripts/verify-target-repo-governance-consistency.py` reported `status=pass`, `target_count=6`, `drift_count=0`.
- Hard gates:
  - build: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1` passed with `OK python-bytecode` and `OK python-import`.
  - test: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` passed `103 test files`, `failures=0`, plus `OK runtime-unittest`, `OK runtime-service-parity`, and `OK runtime-service-wrapper-drift-guard`.
  - contract/invariant: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` passed schema, dependency baseline, target repo consistency, `agent-rule-sync`, `pre-change-review`, and `functional-effectiveness`.
  - hotspot: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1` exited `0`; non-blocking existing warning remains `WARN codex-capability-degraded`.
- Format check: `git diff --check` exited `0`; Git only emitted existing CRLF normalization warnings.
- Target worktree note: rule sync intentionally modified managed rule files in target repos. `k12-question-graph` also had unrelated pre-existing non-rule changes on branch `codex/c002-quality-review-overlay`; they were not reverted or folded into this rule change.

## Compatibility
- This change does not modify application source code, schemas, migrations, or data.
- Claude/Gemini wrapper mode is allowed only when official import support is available and the effective merged context remains complete.
- k12 source facts are integrated into the control repo first, then synchronized to the target repo through the manifest path.
