# Agent CLI Local Config Review

- date: 2026-05-02
- rule_id: local-agent-cli-config-review
- risk_level: low
- scope: user-level Codex/Claude/Gemini settings and repo-level `.claude/settings.json`

## Basis

- OpenAI Codex configuration reference: `~/.codex/config.toml`, sandbox, approvals, MCP, project document limits.
- OpenAI Codex agent-loop documentation: Codex loads global `AGENTS.md`, then project `AGENTS.md` or configured fallback files within the project document byte limit.
- Claude Code settings documentation: `~/.claude/settings.json`, `.claude/settings.json`, scope precedence, `$schema`, permission syntax, `defaultShell`, `language`, and `disableBypassPermissionsMode`.
- Claude Code hooks documentation: command hooks execute with the current user's permissions and must be treated as guardrails, not a hard security boundary.
- Gemini CLI configuration documentation and schema: user/project settings, MCP server configuration, `general.defaultApprovalMode`, `security.environmentVariableRedaction`, and `privacy.usageStatisticsEnabled`.

## Pre-change Review

- pre_change_review: completed for local agent CLI settings, managed Claude Code project settings, governance baseline managed files, and sync/verification scripts already staged in this working tree.
- control_repo_manifest_and_rule_sources: checked `rules/manifest.json`, `rules/global/*`, `rules/projects/*`, `docs/targets/target-repo-governance-baseline.json`, and `docs/targets/templates/claude-code/settings.json`; `scripts/sync-agent-rules.py --scope All --fail-on-change` reported no rule-source drift.
- user_level_deployed_rule_files: checked deployed user-level `C:\Users\sciman\.codex\AGENTS.md`, `C:\Users\sciman\.claude\CLAUDE.md`, and `C:\Users\sciman\.gemini\GEMINI.md` through the sync dry-run; all matched source hashes.
- target_repo_deployed_rule_files: checked target `AGENTS.md`/`CLAUDE.md`/`GEMINI.md` files through the sync dry-run; all managed rule files matched source hashes.
- target_repo_gate_scripts_and_ci: inspected target governance consistency and repo profile enforcement through `python scripts/verify-target-repo-governance-consistency.py`; initial drift was limited to managed `.claude/settings.json` and `ClassroomToolkit` speed profile, then resolved through `apply-target-repo-governance.py`.
- target_repo_repo_profile: checked `.governed-ai/repo-profile.json` for `D:\CODE\ClassroomToolkit`, `D:\CODE\github-toolkit`, `D:\CODE\skills-manager`, and `D:\CODE\vps-ssh-launcher` through the governance consistency verifier; final result was `drift_count=0`.
- target_repo_readme_and_operator_docs: this change does not alter target user workflows or operator commands; existing README/operator docs remain applicable because only Claude Code project settings guardrails and local CLI configuration were changed.
- current_official_tool_loading_docs: verified against current official Codex config/AGENTS loading docs, Claude Code settings/hooks docs, and Gemini CLI settings schema before editing.
- drift-integration decision: integrate the managed Claude Code settings change at the source template and apply it to target repos, rather than accepting per-target drift or manually patching individual target files.

## Changes

- `C:\Users\sciman\.codex\config.toml`
  - changed `cli_auth_credentials_store` from `file` to `auto`
  - added explicit `project_doc_max_bytes = 32768`
  - added `[sandbox_workspace_write].network_access = true`
- `C:\Users\sciman\.claude\settings.json`
  - added official JSON schema
  - enabled Claude Code PowerShell tool with `CLAUDE_CODE_USE_POWERSHELL_TOOL=1`
  - added `defaultShell = powershell` and `language = Chinese`
  - removed schema-invalid `MultiEdit` and replaced schema-invalid `Bash(*)` with `Bash`
  - added schema-valid common tools `PowerShell`, `Glob`, `Grep`, `LSP`, `Skill`, and `TodoWrite` to avoid blocking normal Claude Code workflow under `dontAsk`
  - changed stale additional directory `E:/CODE/skills-manager` to `D:/CODE/skills-manager`
- `D:\CODE\governed-ai-coding-runtime\.claude\settings.json`
  - added official JSON schema
  - expanded project deny rules for credential/token path patterns
- `D:\CODE\governed-ai-coding-runtime\docs\targets\templates\claude-code\settings.json`
  - mirrored the managed Claude Code project settings change so target governance consistency does not drift
- `C:\Users\sciman\.gemini\settings.json`
  - added official Gemini CLI settings schema
  - set `general.defaultApprovalMode = auto_edit`
  - enabled checkpointing and plan mode
  - enabled environment variable redaction for common token/key variables
  - disabled usage statistics
- `C:\Users\sciman\.gemini\antigravity\settings.json`
  - mirrored schema, auto-edit, checkpointing, plan mode, env redaction, and usage-statistics settings

## Verification

- `python` JSON/TOML parse checks passed for all edited config files.
- `jsonschema` validation passed for:
  - `C:\Users\sciman\.claude\settings.json`
  - `D:\CODE\governed-ai-coding-runtime\.claude\settings.json`
  - `C:\Users\sciman\.gemini\settings.json`
  - `C:\Users\sciman\.gemini\antigravity\settings.json`
- `codex --version` returned `codex-cli 0.125.0`.
- `codex debug prompt-input` loaded the edited Codex config and reported `sandbox_mode=workspace-write` with network enabled.
- `claude --version` returned `2.1.114 (Claude Code)`.
- `claude config list` reported Shell `PowerShell` and language `Chinese`.
- `gemini --version` returned `0.37.1`.
- `gemini mcp list` connected configured MCP servers, with a warning for unreadable `.pytest_cache` that is unrelated to settings schema.
- `python scripts/apply-target-repo-governance.py --target-repo <target>` applied the managed `.claude/settings.json` template to `D:\CODE\ClassroomToolkit`, `D:\CODE\github-toolkit`, `D:\CODE\skills-manager`, and `D:\CODE\vps-ssh-launcher` after check-only drift detection.

## Rollback

- Restore backups created before edits:
  - `C:\Users\sciman\.codex\config-backups\config-20260502-011958-before-agent-config-review.toml`
  - `C:\Users\sciman\.claude\settings-backups\settings-20260502-011958-before-agent-config-review.json`
  - `C:\Users\sciman\.gemini\settings-backups\settings-20260502-011958-before-agent-config-review.json`
  - `C:\Users\sciman\.gemini\settings-backups\antigravity-settings-20260502-011958-before-agent-config-review.json`
- Revert repo-level `.claude/settings.json` through git if needed.
