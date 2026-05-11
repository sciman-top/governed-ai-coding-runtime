# 2026-05-12 Codex CLI startup skill config dedupe

- landing: `scripts/Optimize-CodexLocal.ps1`, `tests/runtime/test_codex_shared_launcher.py`, and live `C:\Users\sciman\.codex\config.toml`
- target: reduce Codex CLI startup config parsing overhead after repeated `[[skills.config]]` duplicate disable overrides accumulated in user config
- risk: low; the live change only removes duplicate `[[skills.config]]` blocks with the same `path` and preserves the first block for each path

## Root cause evidence

- command: count live `C:\Users\sciman\.codex\config.toml` skill config blocks
- evidence: before remediation the config had 4010 lines, 111352 bytes, 936 `[[skills.config]]` blocks, 78 unique paths, and 858 duplicate entries.
- command: inspect recent `C:\Users\sciman\.codex\log\codex-tui.log`
- evidence: the remaining startup hot path still includes remote plugin sync failures and stdio MCP cold starts; duplicate skill config blocks were an additional local parsing/load contributor.

## Changes

- live `C:\Users\sciman\.codex\config.toml` was backed up to `C:\Users\sciman\.codex\config-backups\config-20260512-015352-before-skill-config-dedupe.toml`.
- live `C:\Users\sciman\.codex\config.toml` now keeps only the first `[[skills.config]]` block per normalized `path`.
- `scripts/Optimize-CodexLocal.ps1` now removes duplicate `[[skills.config]]` blocks before adding duplicate-skill disable overrides.
- `tests/runtime/test_codex_shared_launcher.py` verifies repeated optimizer runs collapse duplicate `skills.config` paths.

## Verification

- command: post-remediation count of live `C:\Users\sciman\.codex\config.toml`
- evidence: 578 lines, 16054 bytes, 78 `[[skills.config]]` blocks, 78 unique paths, and 0 duplicate entries.
- command: `python -m unittest tests.runtime.test_codex_shared_launcher.CodexSharedLauncherTests.test_optimizer_apply_writes_shared_history_config_without_fixed_relay_id`
- evidence: pass.
- command: `Measure-Command { codex --version | Out-Null }`
- evidence: `codex-cli 0.130.0`; elapsed about 72.9 ms.
- command: `Measure-Command { codex mcp list | Out-Null }`
- evidence: elapsed about 1739.8 ms; enabled MCP inventory still lists context7, fetch, filesystem, playwright, postgres, github, microsoft-learn, and openaiDeveloperDocs.
- command: `codex features list`
- evidence: `plugins` remains stable and enabled; `remote_plugin` remains under development and disabled. No documented precise startup-only remote plugin sync disable key was found in the current config reference.

## Residual risks

- Interactive startup can still be delayed by startup remote plugin sync attempts that fail with ChatGPT auth / Cloudflare 403 when using API-key provider state.
- Interactive startup can still wait on stdio MCP cold starts, especially `npx`-backed context7/filesystem/playwright and postgres when `POSTGRES_CONNECTION_STRING` is absent.
- Disabling all plugins would likely remove useful local plugin capabilities, so this change deliberately avoids that broader tradeoff.

## Rollback

- Restore `C:\Users\sciman\.codex\config.toml` from `C:\Users\sciman\.codex\config-backups\config-20260512-015352-before-skill-config-dedupe.toml`.
- Revert `scripts/Optimize-CodexLocal.ps1`, `tests/runtime/test_codex_shared_launcher.py`, and this evidence file from git history if the durable dedupe behavior needs to be removed.
