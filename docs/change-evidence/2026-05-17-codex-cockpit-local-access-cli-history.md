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

## Cockpit-Only Switching Closeout

### Additional Actions

- Removed deprecated duplicate build directory `D:\CODE\external\Cockpit-Tools-Local\target-release-build`.
- Rebuilt Cockpit from the canonical repo using `npm run tauri -- build --no-bundle`.
- Restarted only `cockpit-tools.exe`; Codex App and Codex CLI processes were not stopped or restarted.
- Standardized the running executable on `D:\CODE\external\Cockpit-Tools-Local\target\release\cockpit-tools.exe`.
- Added Cockpit WebSocket message `request.codex_account_switch` in `src-tauri/src/modules/websocket.rs`, delegating to the existing Cockpit command `switch_codex_account`.
- Used `request.codex_runtime_mode_set` for mode changes and `request.codex_account_switch` for Codex account changes, so Direct API, Direct OAuth, and Cockpit API Service switching can be driven by Cockpit instead of governed repair scripts.

### Additional Evidence

- Pre-restart continuity:
  - `C:\Users\sciman\.codex\config.toml`: `model_provider = "openai"`, `forced_login_method = "chatgpt"`.
  - `C:\Users\sciman\.codex\auth.json`: OAuth tokens present, no API key.
  - `codex exec --json --output-last-message "%TEMP%\codex-maintenance-direct-oauth-pre-restart.txt" "Reply exactly: PRE_RESTART_DIRECT_OAUTH_OK"` returned `PRE_RESTART_DIRECT_OAUTH_OK`.
- Cockpit rebuild and restart:
  - `npm run typecheck`: pass.
  - `cargo fmt --check`: pass.
  - `cargo test --release -q runtime_account_uses_dedicated_local_access_provider_bucket --lib`: pass, `1 passed`.
  - `cargo test --release -q stable_local_access_port --lib`: pass, `2 passed`.
  - `cargo test --release -q runtime_mode_renames_gateway_litellm_to_cockpit_api_service --lib`: pass, `1 passed`.
  - `npm run tauri -- build --no-bundle`: pass, built `D:\CODE\external\Cockpit-Tools-Local\target\release\cockpit-tools.exe`.
  - Built exe readback: LastWriteTime `2026-05-17T18:27:14.5419103+08:00`, size `61029376`.
  - Running process readback: PID `25092`, path `D:\CODE\external\Cockpit-Tools-Local\target\release\cockpit-tools.exe`, StartTime `2026-05-17T18:27:24.6024773+08:00`.
  - Listener readback after final mode: `0.0.0.0:19528` and `127.0.0.1:45335`, both owned by PID `25092`.
  - `Test-Path D:\CODE\external\Cockpit-Tools-Local\target-release-build`: `False`.
- Direct API real run through Cockpit:
  - WS `request.codex_account_switch` to `codex_apikey_8b8853f15e823dc53bd156163035bc78` followed by `request.codex_runtime_mode_set` to `direct_projection`.
  - Config readback: `model_provider = "cmp_1778165666417_1"`, `forced_login_method = "api"`.
  - Provider readback: `[model_providers.cmp_1778165666417_1].base_url = "http://35.213.82.91:8003/v1"`, `supports_websockets = false`.
  - SQLite history bucket readback: `[["cmp_1778165666417_1", 1765]]`.
  - `codex exec --json --output-last-message "%TEMP%\codex-live-direct-api.txt" "Reply exactly: LIVE_DIRECT_API_OK"` returned `LIVE_DIRECT_API_OK`.
- Direct OAuth real run through Cockpit:
  - WS `request.codex_account_switch` to `codex_effcdc2e7c378bf040521d4bd7848c8e` followed by `request.codex_runtime_mode_set` to `direct_projection`.
  - Runtime response: `mode = "direct_projection"`, `accountKind = "oauth"`, `currentAccountId = "codex_effcdc2e7c378bf040521d4bd7848c8e"`.
  - Config readback: `model_provider = "openai"`, `forced_login_method = "chatgpt"`.
  - Auth readback: OAuth tokens present, no API key.
  - SQLite history bucket readback: `[["openai", 1766]]`.
  - `codex exec --json --output-last-message "%TEMP%\codex-live-direct-oauth-roundtrip.txt" "Reply exactly: LIVE_DIRECT_OAUTH_ROUNDTRIP_OK"` returned `LIVE_DIRECT_OAUTH_ROUNDTRIP_OK`.
- Cockpit API Service final real run through Cockpit:
  - WS `request.codex_account_switch` to `codex_apikey_8b8853f15e823dc53bd156163035bc78` followed by `request.codex_runtime_mode_set` to `cockpit_api_service`.
  - Runtime response: `mode = "cockpit_api_service"`, `accountKind = "api"`, `currentAccountId = "codex_apikey_8b8853f15e823dc53bd156163035bc78"`.
  - Config readback: `model_provider = "codex_local_access"`, `forced_login_method = "api"`.
  - Auth readback: `auth_mode = "apikey"`, `base_url = "http://127.0.0.1:45335/v1"`, API key present, no OAuth tokens.
  - SQLite history bucket readback: `[["codex_local_access", 1767]]`.
  - HTTP smoke against `http://127.0.0.1:45335/v1/chat/completions` returned `FINAL_API_SERVICE_OK`.
  - `codex exec --json --output-last-message "%TEMP%\codex-final-api-service.txt" "Reply exactly: FINAL_CODEX_API_SERVICE_OK"` returned `FINAL_CODEX_API_SERVICE_OK`.

### Updated Boundary

Direct API, Direct OAuth, and Cockpit API Service switching are now Cockpit-driven and do not require governed repair participation for normal operation. The remaining architectural boundary is unchanged: `cockpit_api_service` is embedded in the Cockpit App process, so stopping Cockpit still stops `127.0.0.1:45335`; durable offline continuity requires splitting the API service into a separate helper or Windows service.

## 2026-05-17 Late Retest Correction

### Actions

- Rechecked the final live state after restarting Cockpit and deleting `target-release-build`.
- Kept Codex App and Codex CLI processes untouched.
- Used Cockpit WebSocket only to move the live projection from `cockpit_api_service` back to Direct OAuth after the API key account started returning upstream quota failures for Codex CLI requests.

### Evidence

- Cockpit latest release process remained alive:
  - PID `25092`
  - path `D:\CODE\external\Cockpit-Tools-Local\target\release\cockpit-tools.exe`
  - StartTime `2026-05-17T18:27:24.6024773+08:00`
- Canonical release exe readback:
  - path `D:\CODE\external\Cockpit-Tools-Local\target\release\cockpit-tools.exe`
  - LastWriteTime `2026-05-17T18:27:14.5419103+08:00`
  - size `61029376`
- Deprecated duplicate output directory was removed:
  - `Test-Path D:\CODE\external\Cockpit-Tools-Local\target-release-build`: `False`
- Cockpit API service mode was reachable at the protocol layer:
  - runtime file: `mode = "cockpit_api_service"`, `accountKind = "api"`, `currentAccountId = "codex_apikey_8b8853f15e823dc53bd156163035bc78"`
  - `auth.json`: `auth_mode = "apikey"`, `base_url = "http://127.0.0.1:45335/v1"`
  - `config.toml`: `model_provider = "codex_local_access"`, `forced_login_method = "api"`
  - listener readback: `127.0.0.1:45335` and `0.0.0.0:19528`, both owned by PID `25092`
  - HTTP `/v1/chat/completions` returned `FINAL_API_SERVICE_HTTP_OK`
  - direct HTTP `/v1/responses` returned `FINAL_RESPONSES_HTTP_OK`
- Cockpit API service mode was not left as the final live mode because `codex exec` requests through the current API key account failed with upstream quota:
  - `codex exec --json --output-last-message "%TEMP%\codex-final-api-service.txt" "Reply exactly: FINAL_COCKPIT_API_SERVICE_OK"` failed after five retries.
  - Cockpit log `C:\Users\sciman\.antigravity_cockpit\logs\codex-api.log.2026-05-17` recorded repeated `POST target=/v1/responses status=403` failures for account `codex_apikey_8b8853f15e823dc53bd156163035bc78`.
  - Error detail: `403: 用户额度不足, 剩余额度: ＄0.000000`.
- Final live fallback was Direct OAuth, switched by Cockpit WebSocket:
  - runtime file: `mode = "direct_projection"`, `accountKind = "oauth"`, `currentAccountId = "codex_d5918a432f646d7a4f7070307400cc61"`
  - `auth.json`: OAuth tokens present, no API key/base URL.
  - `config.toml`: `model_provider = "openai"`, `forced_login_method = "chatgpt"`.
  - listener readback after Direct OAuth: `0.0.0.0:19528` owned by PID `25092`; `127.0.0.1:45335` not listening, as expected outside API service mode.
  - `codex exec --json --output-last-message "%TEMP%\codex-final-direct-oauth.txt" "Reply exactly: FINAL_DIRECT_OAUTH_CODEX_OK"` returned `FINAL_DIRECT_OAUTH_CODEX_OK`.
- SQLite history bucket after final Direct OAuth fallback:
  - `threads.model_provider = "openai"`, count `1772`.
  - Latest thread `019e3592-3d02-7810-a7e8-c12e7da4e76e` used provider `openai`.

### Current Conclusion

Cockpit-only switching is live and verified for Direct OAuth, Direct API, and Cockpit API Service projection. The current API key account is not suitable as the final live mode until its upstream quota is restored or the API service pool selects a non-empty account for Codex CLI `/v1/responses` requests. To preserve Codex connectivity, the machine was left in Direct OAuth mode.
