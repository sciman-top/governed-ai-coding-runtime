# Codex/Cockpit Account Projection Repair Runbook

## Scope
Use this runbook when Codex App can see local history but shows `Reconnecting`, Codex CLI can connect while the picker/history appears empty after Cockpit Tools switches Codex to an API provider, or Codex CLI fails after switching Cockpit Tools back to OAuth/ChatGPT with:

```text
API key login is required, but ChatGPT is currently being used. Logging out.
```

This runbook is for local Codex/Cockpit interoperability only. Do not restart, stop, kill, or auto-launch Codex App unless the operator explicitly confirms that action for the current incident.

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
- Explicit current account projection for the currently selected Cockpit account, including OAuth/ChatGPT:
  ```powershell
  python scripts\codex-interop-check.py --codex-home "$HOME\.codex" --cc-switch-db "$HOME\.cc-switch\cc-switch.db" --cockpit-home "$HOME\.antigravity_cockpit" --quick-launch --repair-current-cockpit-account-projection
  ```
- Install and start the narrow current-account projection guard. This guard only runs the explicit projection command above after Cockpit/Codex state files change; it must not launch, stop, or kill Codex:
  ```powershell
  pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Start-CodexCockpitSwitchGuard.ps1 -InstallTask
  pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Start-CodexCockpitSwitchGuard.ps1 -Start
  ```
  If Windows denies scheduled-task registration, `-InstallTask` writes a hidden current-user Startup-folder VBS fallback instead. The fallback must contain exactly two lines, with the full `shell.Run "... -RunWorker ...", 0, False` command on the second line; embedded newlines inside the command break logon startup.
- Operator entrypoint for the same explicit projection:
  ```powershell
  pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\operator.ps1 -Action CodexApiProjectionRepair
  ```
- Legacy shim cleanup:
  ```powershell
  pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Disable-CodexProjectInterop.ps1 -Apply -DisableProjectShortcuts
  ```

## Forbidden Actions
- Do not use generic `--apply` as a repair path.
- Do not use `--migrate-provider-bucket` as a repair path.
- Do not create SQLite triggers such as `trg_threads_shared_provider_after_insert` or `trg_threads_shared_provider_after_update`.
- Do not install or start any guard that calls generic `--apply`, calls `--migrate-provider-bucket`, creates SQLite triggers, edits launcher paths, or starts/stops Codex.
- Do not install no-op launchers, restart wrappers, no-restart shims, or CLI preflight wrappers to intercept Cockpit Tools.
- Do not force `codex_launch_on_switch` on or off; it is a Cockpit UI/user setting.

## Guard Audit Commands
Use these before claiming the issue is fixed:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Start-CodexCockpitSwitchGuard.ps1 -Status
```

Expected:
- if the current-account projection guard is installed: `task_state = "Running"` or `process_count > 0`
- if intentionally disabled: `task_state = "not_installed"` and `process_count = 0`
- no other guard/checker process should run with `--apply`, `--migrate-provider-bucket`, or trigger-writing code

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
- Restore the timestamped backups created by `--repair-current-cockpit-api-projection` or `--repair-current-cockpit-account-projection`.
- Restore `~/.codex/config.toml`, `~/.codex/auth.json`, `~/.codex/state_5.sqlite`, and Cockpit provider metadata together. Do not restore only one file unless the evidence shows only that file drifted.
- Re-run the guard audit and read-only interop check after rollback.
