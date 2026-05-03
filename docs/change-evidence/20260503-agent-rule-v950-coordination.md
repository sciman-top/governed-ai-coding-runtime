# Agent Rule v9.50 Coordination

- date: 2026-05-03
- rule_ids: R1, R2, R4, R6, R8, E4, E5, E6
- risk: medium
- current_landing: `rules/global/*`, `rules/projects/*`, `rules/manifest.json`, managed target rule files, `scripts/verify-target-repo-powershell-policy.py`
- target_landing: Codex/Claude/Gemini global and project rule family v9.50 with explicit global/project cooperation boundaries
- rollback: restore this change set from git history, then run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -Apply`; backups are under `docs/change-evidence/rule-sync-backups/20260503-232713/` and `docs/change-evidence/rule-sync-backups/20260503-232807/`

## Basis

- OpenAI Codex AGENTS.md guide: https://developers.openai.com/codex/guides/agents-md
- AGENTS.md community format guidance: https://agents.md/
- Claude Code memory and rule loading: https://docs.anthropic.com/en/docs/claude-code/memory
- Claude Code settings hierarchy: https://docs.anthropic.com/en/docs/claude-code/settings
- Claude Code hooks and hook security: https://docs.anthropic.com/en/docs/claude-code/hooks
- Gemini CLI configuration, context files, settings precedence, sandboxing: https://github.com/google-gemini/gemini-cli/blob/main/docs/reference/configuration.md

External sources were used as data for rule improvement only. They do not override global rules, project rules, code facts, or local command output.

## Changes

- Bumped manifest `default_version` to `9.50` and `sync_revision` to `2026-05-03.2`.
- Updated Codex, Claude, and Gemini global rules with a shared rule-minimization boundary: root rules hold stable, frequent, executable constraints; local or example-heavy details move to project docs, native rule folders, skills, hooks, policy, or CI.
- Added shared `1+1>2` acceptance language: every global abstraction must map in project rules to a command, path, blocking condition, evidence field, or explicit N/A.
- Added tool-specific deltas:
  - Codex: front-load critical instructions and verify actual AGENTS loading behavior when fallback, byte limit, or child-agent configuration changes.
  - Claude: clarify `.claude/rules/`, `@path` imports, `/memory` or `InstructionsLoaded` evidence, `--add-dir`, and permission-bypass limits.
  - Gemini: clarify settings precedence, headless JSON evidence, `.env`/environment overrides, and sandbox/config diagnostics.
- Updated all project rule sources to explicitly inherit `GlobalUser/... v9.50` and added a target-repo spot-check rule: global + project rules must reveal current landing, target landing, gate order, evidence path, and rollback.
- Updated `tests/runtime/test_agent_rule_sync.py` so all manifest entries must track the manifest `default_version`.
- Hardened `scripts/verify-target-repo-powershell-policy.py` to skip `.playwright-mcp` runtime artifacts and tolerate files removed after enumeration; added regression coverage in `tests/runtime/test_target_repo_powershell_policy.py`.

## Sync Evidence

- Initial drift check before edits: `python scripts\sync-agent-rules.py --scope All --fail-on-change`
  - result: pass, `changed_count=0`, `blocked_count=0`
- Post-edit dry run: `python scripts\sync-agent-rules.py --scope All --fail-on-change`
  - result: expected dry-run changes, `changed_count=15`, `blocked_count=0`, same-version target drift merged without target additions
- Apply sync: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\sync-agent-rules.ps1 -Scope All -Apply`
  - result: applied, project targets updated; backups created under `docs/change-evidence/rule-sync-backups/20260503-232713/` and `docs/change-evidence/rule-sync-backups/20260503-232807/`
- Final drift check: `python scripts\sync-agent-rules.py --scope All --fail-on-change`
  - result: pass, `entry_count=18`, `changed_count=0`, `blocked_count=0`; all global and target rule files are same-hash with manifest sources

## Verification

- `codex --version`; `codex --help`
  - result: pass, `codex-cli 0.128.0`; help exposes `exec`, `review`, `mcp`, `plugin`, `sandbox`, `debug`, `features`
- `claude --version`; `claude --help`
  - result: pass, `2.1.114 (Claude Code)`; help exposes `--add-dir`, `--bare`, permissions flags, debug flags
- `gemini --version`; `gemini --help`
  - result: pass, `0.37.1`; help exposes `mcp`, `extensions`, `skills`, `hooks`, `--prompt`, `--sandbox`, `--approval-mode`
- `python -m unittest tests.runtime.test_agent_rule_sync`
  - result: pass, `Ran 7 tests`
- `python -m unittest tests.runtime.test_target_repo_powershell_policy`
  - result: pass, `Ran 3 tests`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - result: pass, `OK python-bytecode`, `OK python-import`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - first result: fail because `.playwright-mcp` transient files caused `FileNotFoundError` in the target PowerShell policy scanner
  - repair: skip `.playwright-mcp` artifacts and ignore files removed after enumeration
  - final result: pass, `Completed 103 test files in 204.530s; failures=0`, `OK runtime-unittest`, `OK runtime-service-parity`, `OK runtime-service-wrapper-drift-guard`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - result: pass, including `OK target-repo-governance-consistency`, `OK target-repo-powershell-policy`, `OK agent-rule-sync`, `OK functional-effectiveness`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  - result: pass with existing `WARN codex-capability-degraded`; all other checks OK

## Compatibility

- Rule files remain in the `1 / A / B / C / D` structure.
- `A/C/D` stay semantically aligned across Codex, Claude, and Gemini; `B` holds tool-specific loading, diagnostics, permission, and fallback behavior.
- No schema, data, or runtime migration is required.
- All managed root/global rule files remain below 200 lines.

