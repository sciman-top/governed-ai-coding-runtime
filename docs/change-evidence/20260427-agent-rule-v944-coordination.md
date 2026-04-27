# Agent Rule v9.44 Coordination Evidence

Date: 2026-04-27

## Goal

Improve the managed global and project-level rule files for Codex, Claude, and Gemini so they keep a shared governance core while preserving tool-specific loading, memory, approval, and safety behavior.

## Source Review

- OpenAI Codex: `AGENTS.md` project instructions, project/user layering, `.codex/rules/*.rules`, and `prefix_rule()` examples from <https://developers.openai.com/codex/agents>.
- Claude Code: `CLAUDE.md` memory scopes, imports, `/memory`, project/local/user memory, and settings/permissions from <https://docs.claude.com/en/docs/claude-code/memory> and <https://docs.claude.com/en/docs/claude-code/settings>.
- Gemini CLI: `GEMINI.md`, `contextFileName`, `.geminiignore`, Trusted Folders, and memory command behavior from <https://google-gemini.github.io/gemini-cli/docs/cli/gemini-md.html>, <https://google-gemini.github.io/gemini-cli/docs/cli/configuration.html>, <https://google-gemini.github.io/gemini-cli/docs/cli/commands.html>, <https://google-gemini.github.io/gemini-cli/docs/cli/trusted-folders.html>, and <https://google-gemini.github.io/gemini-cli/docs/cli/gemini-ignore.html>.
- Community convention: the shared `AGENTS.md` instruction-file convention from <https://github.com/openai/agents.md>.
- Research signal: context engineering evidence from <https://arxiv.org/abs/2505.23229> supports keeping rules minimal and constraint-oriented instead of overloading context with broad preference text.

## Changes

- Bumped managed rule sources and projections to `v9.44` with `sync_revision=2026-04-27.1`.
- Added a shared "minimal root rule" constraint: root rule files should keep only facts that change behavior, block risk, or cannot be cheaply inferred from code, CI, README, or local config.
- Strengthened global/project coordination:
  - global layer = shared WHAT, risk, N/A fields, gate order, and traceability semantics.
  - project layer = repo WHERE/HOW, module boundaries, exact commands, evidence paths, rollback entrypoints, and invariants.
- Added explicit project mappings for:
  - `R6`: gate commands are hard gates; quick/fast slices do not replace full delivery gates.
  - `R8`: evidence and rollback fields are required traceability.
- Added tool-specific differences:
  - Codex: use `.codex/rules/*.rules` for deterministic command approval and keep `prefix_rule()` precise with `match/not_match` examples.
  - Claude: use `.claude/settings*.json` `permissions.deny` / `sandbox` for enforceable safety boundaries, not prose-only reminders.
  - Gemini: account for Trusted Folders, `.geminiignore`, `context.fileName`, and help-gated `/memory` command differences; use `/memory show` plus `/memory list`/`refresh` when supported, otherwise record version and use `/memory reload`.
- Updated target governance baseline checks so target repo profiles must carry the same coordination policy.
- Fixed `scripts/run-governed-task.py` replay references for external `--runtime-root` values exposed by the runtime gate; replay case refs now remain repo-relative for compatibility mode and become runtime-root-relative when runtime state lives outside the repo.

## Commands And Evidence

| Step | Command | Result |
|---|---|---|
| Dry-run rule sync | `python scripts/sync-agent-rules.py --scope All --fail-on-change` | `status=dry_run_changes`, 18 projections would update from `9.43` to `9.44` |
| Apply rule sync | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -Apply` | `status=applied`, `changed_count=18`, `blocked_count=0` |
| Apply target governance baseline | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -ApplyGovernanceBaselineOnly -Json` | `target_count=5`, `failure_count=0` |
| Fix target profile drift | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target skills-manager -ApplyGovernanceBaselineOnly -Json` | `changed=["rule_file_coordination_policy"]` |
| Fix rule projection drift | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -Apply` | `changed_count=3` for `skills-manager` project rule projections |
| Force global whitespace resync | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -Apply -Force` | `changed_count=3` for same-version global whitespace cleanup |
| Verify rule projections | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-agent-rules.ps1 -Scope All` | `status=pass`, `changed_count=0`, `blocked_count=0` |
| Verify target governance | `python scripts/verify-target-repo-governance-consistency.py` | `status=pass`, `target_count=5`, `drift_count=0` |
| Unit tests | `python -m unittest tests.runtime.test_agent_rule_sync tests.runtime.test_target_repo_governance_consistency` | `Ran 21 tests`, `OK` |
| Replay regression | `python -m unittest tests.runtime.test_run_governed_task_service_wrapper.RunGovernedTaskServiceWrapperTests.test_write_replay_case_returns_runtime_relative_ref_for_external_runtime_root tests.runtime.test_run_governed_task_service_wrapper.RunGovernedTaskServiceWrapperTests.test_write_replay_case_rejects_unsafe_task_id tests.runtime.test_run_governed_task_cli.RunGovernedTaskCliTests.test_run_default_profile_executes_repo_local_quick_gate` | `Ran 3 tests`, `OK` |
| Whitespace check | `git diff --check` | pass; only line-ending conversion warnings from current Git settings |

## Rollback

- Use git history or `git diff` to revert source changes in this repo.
- Projection backups were written under:
  - `docs/change-evidence/rule-sync-backups/20260427-190348/`
  - `docs/change-evidence/rule-sync-backups/20260427-191107/`
  - `docs/change-evidence/rule-sync-backups/20260427-194113/`
- Target governance profile rollback can be done by restoring the previous `.governed-ai/repo-profile.json` from git in each target repo or by applying the previous baseline.

## Final Gate

- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1` -> pass (`OK python-bytecode`, `OK python-import`).
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` -> pass (`Ran 451 tests`, `OK`; service parity/wrapper `Ran 12 tests`, `OK`).
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` -> pass (`OK target-repo-governance-consistency`, `OK agent-rule-sync`, `OK functional-effectiveness`).
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1` -> pass (`OK codex-capability-ready`, `OK adapter-posture-visible`).
