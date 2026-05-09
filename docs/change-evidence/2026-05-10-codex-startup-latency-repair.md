# 2026-05-10 Codex startup latency repair

- landing: `scripts/Optimize-CodexLocal.ps1`, `scripts/lib/codex_local.py`, `tests/runtime/test_codex_local.py`, and live `C:\Users\sciman\.codex\config.toml`
- target: reduce Codex App and Codex CLI startup stalls caused by startup-time remote plugin sync failures, invalid local plugin metadata, repeated stdio MCP cold starts, and leaked postgres MCP connection strings in long-lived process arguments
- risk: low for config hardening and diagnostics; medium for live process cleanup because it terminates stale MCP subprocesses while preserving the Codex App main process

## Root cause evidence

- command: `where.exe codex`
- evidence: multiple launch paths exist: npm shims, app-local `C:\Users\sciman\AppData\Local\OpenAI\Codex\bin\codex.exe`, and WindowsApps entries. Direct CLI timing was not the dominant bottleneck.
- command: measured `codex --version`, direct app `codex.exe --version`, `codex --help`, and `codex mcp list`
- evidence: CLI/help startup was sub-second to low-second; `codex mcp list` showed enabled MCP surface and took about 2 seconds.
- command: inspect `C:\Users\sciman\.codex\log\codex-tui.log`
- evidence: repeated startup warnings included remote plugin sync failures, Cloudflare 403 responses, `missing or invalid plugin.json plugin="chrome@openai-bundled"`, and apps-list fallback.
- command: inspect process tree for MCP and node subprocesses
- evidence: before cleanup there were 51 matching MCP-related subprocesses using about 2433.7 MB working set.
- command: inspect `C:\Users\sciman\.codex\logs_2.sqlite`
- evidence: SQLite quick check was OK, but file size was 1355087872 bytes, above the 1 GiB startup-health threshold.

## Changes

- `scripts/Optimize-CodexLocal.ps1` now writes `check_for_update_on_startup = false`.
- `scripts/Optimize-CodexLocal.ps1` now disables `[plugins."chrome@openai-bundled"].enabled` when the cached plugin metadata is invalid.
- `scripts/Optimize-CodexLocal.ps1` now routes postgres MCP through `C:\Users\sciman\.codex\scripts\mcp-postgres-env-wrapper.mjs` instead of expanding the connection string in the process command line.
- `scripts/lib/codex_local.py` now includes `startup_health` checks for startup update sync, invalid chrome plugin metadata, stdio MCP count, postgres MCP process-argument exposure, oversized logs DB, and recent startup log failures.
- `tests/runtime/test_codex_local.py` covers the new startup-health diagnostics.

## Live remediation evidence

- command: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/Optimize-CodexLocal.ps1 -Apply`
- evidence: status `ok`; config backup `C:\Users\sciman\.codex\config-backups\config-20260510-020310.toml`; wrapper installed at `C:\Users\sciman\.codex\scripts\mcp-postgres-env-wrapper.mjs`; interop status `pass`.
- command: inspect live `C:\Users\sciman\.codex\config.toml`
- evidence: no `$true` or `$false` TOML literals; `check_for_update_on_startup = false`; `[plugins."chrome@openai-bundled"].enabled = false`; `[mcp_servers.postgres].command = "node"` with wrapper args; postgres block contains no connection string.
- command: `codex_startup_health(C:\Users\sciman\.codex)`
- evidence: `startup_update_check_disabled=pass`; `invalid_chrome_plugin_disabled=pass`; `stdio_mcp_startup_surface=pass` with `stdio_server_count=4`; `postgres_mcp_connection_string_not_in_process_args=pass`; remaining attention items are `logs_sqlite_size_under_1gb` and `recent_startup_log_failures`.
- command: live MCP process cleanup
- evidence: targeted 51 MCP-related subprocesses using 2433.7 MB working set; after cleanup, remaining matching subprocess count was 0. Some processes exited before termination and returned transient "not found".
- command: post-change CLI timing
- evidence: `codex --version` exit 0 in 808.1 ms; `codex --help` exit 0 in 575.2 ms; `codex mcp list` exit 0 in 2286.4 ms and showed postgres using `node C:\Users\sciman\.codex\scripts\mcp-postgres-env-wrapper.mjs`.

## Residual risks

- `C:\Users\sciman\.codex\logs_2.sqlite` remains 1355087872 bytes. Archive or compact it only after stopping Codex App and CLI processes.
- `recent_startup_log_failures` remains attention until a fresh App restart or log rotation removes the old tail entries.
- This run did not restart Codex App because doing so would interrupt the active investigation session. The startup-critical config changes apply on next App or CLI start.

## Rollback

- Restore live config from `C:\Users\sciman\.codex\config-backups\config-20260510-020310.toml` if startup behavior regresses.
- Remove `C:\Users\sciman\.codex\scripts\mcp-postgres-env-wrapper.mjs` only after restoring the old postgres MCP command.
- Revert the changed repo files with git if the startup-health diagnostics need to be removed.
- A prior interop repair backup also exists at `C:\Users\sciman\.codex\backups\config.toml.20260510_020321_cockpit_provider.bak`.
