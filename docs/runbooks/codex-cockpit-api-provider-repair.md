# Codex/Cockpit Account Projection Repair Runbook

## Scope
Use this runbook when Codex App can see local history but shows `Reconnecting`, Codex CLI can connect while the picker/history appears empty after Cockpit Tools switches Codex to an API provider, or Codex CLI fails after switching Cockpit Tools back to OAuth/ChatGPT with:

```text
API key login is required, but ChatGPT is currently being used. Logging out.
```

This runbook is for local Codex/Cockpit interoperability only. Do not restart, stop, kill, or auto-launch Codex App unless the operator explicitly confirms that action for the current incident.

This runbook covers the old direct Cockpit projection mode. It remains supported for Codex App/CLI OAuth/API roundtrips even though the new preferred gateway lane is `Codex -> LiteLLM -> Cockpit API service`.

Use the mode switch deliberately:
- New gateway mode: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\operator.ps1 -Action CodexGatewayEnable`
- Old direct API projection mode: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\operator.ps1 -Action CodexApiProjectionRepair`
- Old direct OAuth projection mode: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\operator.ps1 -Action CodexOauthProjectionRepair`
- Gateway rollback before returning to direct projection when needed: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\operator.ps1 -Action CodexGatewayRollback`
- Cockpit-owned automatic materialization: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\operator.ps1 -Action CodexModeSync` reads `~/.antigravity_cockpit/codex_runtime_mode.json` and chooses the matching path.

This runbook does not repair the `Codex -> LiteLLM -> Cockpit API service` gateway lane. In gateway mode, Codex must stay on `model_provider = "litellm_gateway"` with `auth_mode = "apikey"` and `base_url = "http://127.0.0.1:4000/v1"`; direct Cockpit projection repairs intentionally overwrite that shape.

## Highest Priority Contract
- Treat Codex/Cockpit OAuth/API roundtrips, `state_5.sqlite.threads.model_provider` history buckets, picker visibility metadata, and repair entrypoints as the highest-priority local interoperability contract for this repository.
- Before changing any Codex/Cockpit auth, provider, API relay, launcher, history, or repair behavior, run a read-only baseline with `CodexProjectionSmoke` or `codex-interop-check.py --quick-launch` and inspect this runbook.
- Only three write entrypoints are allowed: `CodexApiProjectionRepair`, `CodexOauthProjectionRepair`, and `CodexLaunchBindingRepair`. They must create backups, must not restart/stop/kill Codex, and must keep config, auth, Cockpit account/provider metadata, `threads.model_provider`, and picker visibility metadata aligned.
- Do not run `CodexApiProjectionRepair` or `CodexOauthProjectionRepair` while the intended route is `Codex -> LiteLLM -> Cockpit API service`. Use `scripts\Manage-LiteLLMGateway.ps1 -Action PrepareCockpitUpstream` and `-Action WriteCodexProfile` instead.
- Do not treat the gateway lane as a replacement for direct projection. It is a new selectable mode; the old `CodexApiProjectionRepair` / `CodexOauthProjectionRepair` roundtrip must continue to work for Codex App/CLI.
- Do not reintroduce generic `--apply`, `--migrate-provider-bucket`, SQLite provider triggers, background guards / 后台 guard, no-op launchers, restart wrappers, CLI preflight wrappers, automatic Codex restart / 自动重启 Codex, or `[model_providers.openai]`.
- History sharing must not override API relay connectivity. If a relay needs `supports_websockets=false`, use the Cockpit API account's non-built-in provider bucket and migrate/verify history into that bucket; when returning to OAuth, migrate/verify history back to `openai`.
- Enforce this contract with `tests.runtime.test_codex_cockpit_policy_contract`, `tests.runtime.test_codex_shared_launcher`, `CodexProjectionSmoke`, and `Test-CodexGuardAbsence.ps1` before claiming the issue is fixed.

## Root Cause Summary
- Codex App/CLI picker visibility is bucketed by `state_5.sqlite.threads.model_provider` and still depends on user-visible thread metadata such as `has_user_event` and `first_user_message`.
- API relay connectivity needs a custom `model_providers.<id>` entry when the relay does not support the Codex Responses WebSocket route, because `supports_websockets = false` is available only on custom providers.
- The old assumption was wrong: API mode does not have to stay in the built-in `openai` history bucket.
- The durable invariant is: active `config.toml` provider, Cockpit current API account `api_provider_id`, `threads.model_provider`, and picker-visible `threads.has_user_event` metadata must match.
- Built-in `openai` plus `openai_base_url` can preserve one historical bucket, but cannot disable WebSocket retries for relays such as `http://35.213.82.91:8003/v1`.
- Historical project guards made the problem worse by creating SQLite triggers or running generic provider-bucket repairs that could pull history back toward `openai` or race Cockpit Tools state writes.
- OAuth/ChatGPT switching has the symmetric failure mode: Cockpit can make an OAuth account current while Codex live projection still has `forced_login_method = "api"` or a missing/stale `auth.json`. In that state Codex CLI requires API-key login even though the current account is ChatGPT/OAuth.
- API switching has the opposite symmetric failure mode: Cockpit can make an API-key account current while Codex live projection still has `forced_login_method = "chatgpt"`, a ChatGPT-only provider, or no API-key `auth.json`. In that state Codex CLI requires ChatGPT login even though the current account is API-key mode.

## Fixed Shape
For a Cockpit API account:
- `~/.codex/config.toml` top-level `forced_login_method = "api"`.
- `~/.codex/config.toml` top-level `model_provider = "<Cockpit api_provider_id>"`.
- No top-level `openai_base_url` for the custom API provider path.
- `[model_providers.<Cockpit api_provider_id>]` contains:
  - `base_url = "<Cockpit API base URL>"`
  - `wire_api = "responses"`
  - `requires_openai_auth = false`
  - `supports_websockets = false`
- `~/.codex/auth.json` matches the current Cockpit API account key and base URL.
- `~/.codex/state_5.sqlite.threads.model_provider` uses the same provider id for active local history.
- Active local history rows with a non-empty `first_user_message` have `has_user_event = 1`; otherwise App/CLI pickers can show an empty list even when the provider bucket has rows.
- Cockpit provider metadata records the same provider id and `supports_websockets = false`.

For a ChatGPT/OAuth account:
- `~/.codex/config.toml` top-level `forced_login_method = "chatgpt"`.
- `model_provider = "openai"` remains valid.
- Do not define `[model_providers.openai]`.
- `~/.codex/auth.json` has `auth_mode = "chatgpt"` and current Cockpit OAuth tokens.
- `~/.codex/state_5.sqlite.threads.model_provider` uses `openai` for active OAuth/ChatGPT history.
- Active local history rows with a non-empty `first_user_message` have `has_user_event = 1`.
- Saved Cockpit API provider profiles should remain present as non-built-in custom providers with `supports_websockets = false`, so switching back to API does not lose relay compatibility.

## Cockpit Local API Service Boundary
- Cockpit Tools' Codex API service is a separate local-access gateway, not the same thing as projecting the current Cockpit account into Codex `auth.json`/`config.toml`.
- Do not assume the service is loopback-only just because the UI shows `127.0.0.1`. Verify the running Cockpit build with `netstat`/PowerShell before pointing Codex CLI/App at `http://127.0.0.1:2876/v1`.
- The custom local Cockpit build changes `codex_local_access.rs` to bind `CODEX_LOCAL_ACCESS_BIND_HOST = "127.0.0.1"`. If an official build is used and it binds `0.0.0.0`, keep `codex_local_access.json.enabled = false` until a host firewall rule or default inbound block is verified.
- If the operator explicitly enables the API service, first run `CodexProjectionSmoke`, then verify listener scope with `netstat`/PowerShell and a local `/v1/models` probe. Do not enable Cockpit automatic account switching at the same time.
- Editing `codex_local_access.json` alone may not start the listener in the already-running Cockpit process; the UI command `codex_local_access_set_enabled`/`codex_local_access_activate` starts the in-process gateway. Do not restart Cockpit or Codex to force this unless the operator confirms that action for the current incident.
- In the custom local Cockpit build, API-service activation must not clear Cockpit's current Codex account or bind the default instance to `__api_service__`. The governed gateway lane keeps Codex pointed at LiteLLM and lets Cockpit local access follow the current account as the upstream.

## Allowed Actions
- Read-only diagnosis:
  ```powershell
  python scripts\codex-interop-check.py --codex-home "$HOME\.codex" --cc-switch-db "$HOME\.cc-switch\cc-switch.db" --cockpit-home "$HOME\.antigravity_cockpit" --quick-launch
  ```
- Explicit current API account projection when the operator wants to repair the current Cockpit API account:
  ```powershell
  python scripts\codex-interop-check.py --codex-home "$HOME\.codex" --cc-switch-db "$HOME\.cc-switch\cc-switch.db" --cockpit-home "$HOME\.antigravity_cockpit" --quick-launch --repair-current-cockpit-api-projection --prefer-cockpit-api-account
  ```
- Operator UI entrypoint for the same explicit API projection: open `http://127.0.0.1:8770/?lang=zh-CN`, go to the `Codex` tab, expand `Cockpit compatibility diagnostics`, then click `Repair API projection`. The button must run only the explicit API projection command above, create backups, and must not restart, stop, kill, or auto-launch Codex.
- Operator entrypoint for the same explicit projection:
  ```powershell
  pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\operator.ps1 -Action CodexApiProjectionRepair
  ```
- When switching back to a Cockpit OAuth account, use the explicit OAuth projection. It creates backups, restores ChatGPT auth/config to the built-in `openai` provider bucket, migrates local history metadata back to `openai`, and must not restart, stop, kill, or auto-launch Codex:
  ```powershell
  pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\operator.ps1 -Action CodexOauthProjectionRepair
  ```
- If `cockpit_codex_instances_follow_current_account` fails, repair only Cockpit launch binding. This writes a `codex_instances.json` backup, sets `defaultSettings.followLocalAccount = true`, clears `defaultSettings.bindAccountId`, and must not touch Codex auth/config/history:
  ```powershell
  pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\operator.ps1 -Action CodexLaunchBindingRepair
  ```
  The same action is available in the 8770 `Codex` tab as `Repair launch follow`.
- Verify that no retired background guard, startup fallback, worker, or installed wrapper remains:
  ```powershell
  pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Test-CodexGuardAbsence.ps1
  ```
- Legacy shim cleanup:
  ```powershell
  pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Disable-CodexProjectInterop.ps1 -Apply -DisableProjectShortcuts
  ```

## Forbidden Actions
- Do not use generic `--apply` as a repair path.
- Do not use `--migrate-provider-bucket` as a repair path.
- Do not create SQLite triggers such as `trg_threads_shared_provider_after_insert` or `trg_threads_shared_provider_after_update`.
- Do not install or start any background guard, including the former current-account projection guard.
- Do not call `--repair-current-cockpit-account-projection`; generic OAuth/API account projection is deprecated because a background guard can rewrite the live state behind Cockpit Tools.
- Do not install no-op launchers, restart wrappers, no-restart shims, or CLI preflight wrappers to intercept Cockpit Tools.
- Do not force `codex_launch_on_switch` on or off; it is a Cockpit UI/user setting.

## Guard Audit Commands
Use these before claiming the issue is fixed:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Test-CodexGuardAbsence.ps1
```

Expected:
- `status = "pass"`
- `scheduled_task_present = false`, `startup_launcher_present = false`, and `process_count = 0`
- `retired_installed_files_present = []`
- no other guard/checker process should run with `--apply`, `--migrate-provider-bucket`, `--repair-current-cockpit-account-projection`, or trigger-writing code

```powershell
@'
import sqlite3, pathlib
p = pathlib.Path.home() / ".codex" / "state_5.sqlite"
con = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
try:
    rows = con.execute(
        "select name from sqlite_master where type='trigger' and (name like '%provider%' or sql like '%model_provider%')"
    ).fetchall()
    print("trigger_count=", len(rows))
finally:
    con.close()
'@ | python -
```

Expected:
- `trigger_count= 0`

```powershell
python scripts\codex-interop-check.py --codex-home "$HOME\.codex" --cc-switch-db "$HOME\.cc-switch\cc-switch.db" --cockpit-home "$HOME\.antigravity_cockpit" --quick-launch
```

Expected:
- `status = "pass"`
- `codex_live_provider_bucket.active_provider` matches the current Cockpit account provider bucket.
- `codex_thread_provider_distribution.expected_provider` matches the active provider.
- `codex_history_visibility_metadata.visible_user_event_threads` is non-zero when user-message threads exist.

## Evidence
Record the final incident evidence in `docs/change-evidence/` with:
- live `config.toml` provider id
- current Cockpit account id and `api_provider_id`
- thread provider distribution
- history visibility metadata: `user_message_threads`, `visible_user_event_threads`, and `thread_source_distribution`
- guard task/process status
- SQLite trigger count
- smoke result, such as a `codex exec` final message
- backup paths for changed live files

The 2026-05-13 reference incident is recorded in:
- `docs/change-evidence/2026-05-13-codex-cockpit-api-shared-history.md`

## Rollback
- Restore the timestamped backups created by `--repair-current-cockpit-api-projection` or `--repair-current-cockpit-oauth-projection`.
- Restore `~/.codex/config.toml`, `~/.codex/auth.json`, `~/.codex/state_5.sqlite`, and Cockpit provider metadata together. Do not restore only one file unless the evidence shows only that file drifted.
- Re-run the guard audit and read-only interop check after rollback.
