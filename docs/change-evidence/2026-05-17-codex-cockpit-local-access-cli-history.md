# 2026-05-17 Codex/Cockpit Local Access CLI History Repair

## Scope

- issue_id: `codex-cockpit-local-access-cli-history`
- risk_level: `local_interop_medium`
- current_landing: local Codex projection files plus Cockpit source validation
- target_home: Cockpit-managed Codex runtime mode/projection, no governed write-repair dependency

## Root Cause

`C:\Users\sciman\.codex\auth.json` already pointed at Cockpit API Service on `127.0.0.1:45335`, but `C:\Users\sciman\.codex\config.toml` still selected the stale provider `cmp_1778165666417_1` with `base_url = "http://127.0.0.1:5335/v1"`. Meanwhile `state_5.sqlite` stored all visible threads under `model_provider = "codex_local_access"`, so picker/history looked empty while the history rows still existed.

## Actions

- Backed up `C:\Users\sciman\.codex\config.toml` to `config.toml.bak-codex-local-access-20260517-174552`.
- Updated active provider and shared API profiles to `codex_local_access`.
- Updated `[model_providers.codex_local_access]` to `base_url = "http://127.0.0.1:45335/v1"`, `wire_api = "responses"`, `requires_openai_auth = false`, `supports_websockets = false`.
- Corrected the inactive Direct API provider `cmp_1778165666417_1` away from stale `127.0.0.1:5335` to Cockpit's recorded upstream base URL.
- Preserved `state_5.sqlite`; no history migration was needed because the stored bucket was already `codex_local_access`.

## Evidence

- Cockpit API Service HTTP smoke returned `CLI_API_OK` from `http://127.0.0.1:45335/v1/chat/completions`.
- `codex exec --json --output-last-message "%TEMP%\codex-local-access-smoke.txt" "Reply exactly: CODEX_CLI_LOCAL_ACCESS_OK"` returned `CODEX_CLI_LOCAL_ACCESS_OK`.
- Isolated Direct API `codex exec` with temporary `CODEX_HOME` returned `CODEX_DIRECT_API_OK`; the temporary credential home was deleted after the probe.
- Isolated Direct OAuth `codex exec` with temporary `CODEX_HOME` returned `CODEX_DIRECT_OAUTH_OK`; the temporary credential home was deleted after the probe.
- SQLite readback after the CLI smoke: `threads.model_provider = codex_local_access`, count `1760`.
- Running Cockpit process remained alive: `D:\CODE\external\Cockpit-Tools-Local\target\release\cockpit-tools.exe`, listening on `127.0.0.1:45335` and `0.0.0.0:19528`.
- Cockpit source checks:
  - `npm run typecheck`
  - `cargo fmt --check`
  - `cargo test --release -q runtime_account_uses_dedicated_local_access_provider_bucket --lib`
  - `cargo test --release -q stable_local_access_port --lib`
  - `cargo test --release -q runtime_mode_renames_gateway_litellm_to_cockpit_api_service --lib`

## Rollback

Restore `C:\Users\sciman\.codex\config.toml.bak-codex-local-access-20260517-174552` over `C:\Users\sciman\.codex\config.toml`.

## Remaining Boundary

The running Cockpit release process embeds the API service, so stopping Cockpit App stops `cockpit_api_service`. Replacing the locked release exe must wait until Codex is not relying on API service mode, or the API service must be split into a helper/service process.
