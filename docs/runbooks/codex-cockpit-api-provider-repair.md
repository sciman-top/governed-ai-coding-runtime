# Codex/Cockpit API Provider Repair Runbook

## Scope
Use this runbook when Codex App can see local history but shows `Reconnecting`, or Codex CLI can connect while the picker/history appears empty after Cockpit Tools switches Codex to an API provider.

This runbook is for local Codex/Cockpit interoperability only. Do not restart, stop, kill, or auto-launch Codex App unless the operator explicitly confirms that action for the current incident.

## Root Cause Summary
- Codex App picker visibility is bucketed by `state_5.sqlite.threads.model_provider`.
- API relay connectivity needs a custom `model_providers.<id>` entry when the relay does not support the Codex Responses WebSocket route, because `supports_websockets = false` is available only on custom providers.
- The old assumption was wrong: API mode does not have to stay in the built-in `openai` history bucket.
- The durable invariant is: active `config.toml` provider, Cockpit current API account `api_provider_id`, and `threads.model_provider` must match.
- Built-in `openai` plus `openai_base_url` can preserve one historical bucket, but cannot disable WebSocket retries for relays such as `http://35.213.82.91:8003/v1`.
- Historical project guards made the problem worse by creating SQLite triggers or running generic provider-bucket repairs that could pull history back toward `openai` or race Cockpit Tools state writes.

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
- Cockpit provider metadata records the same provider id and `supports_websockets = false`.

For a ChatGPT/OAuth account:
- `model_provider = "openai"` remains valid.
- Do not define `[model_providers.openai]`.

## Allowed Actions
- Read-only diagnosis:
  ```powershell
  python scripts\codex-interop-check.py --codex-home "$HOME\.codex" --cc-switch-db "$HOME\.cc-switch\cc-switch.db" --cockpit-home "$HOME\.antigravity_cockpit" --quick-launch
  ```
- Explicit current API account projection when the operator wants to repair the current Cockpit API account:
  ```powershell
  python scripts\codex-interop-check.py --codex-home "$HOME\.codex" --cc-switch-db "$HOME\.cc-switch\cc-switch.db" --cockpit-home "$HOME\.antigravity_cockpit" --quick-launch --repair-current-cockpit-api-projection --prefer-cockpit-api-account
  ```
- Legacy shim cleanup:
  ```powershell
  pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Disable-CodexProjectInterop.ps1 -Apply -DisableProjectShortcuts
  ```

## Forbidden Actions
- Do not use generic `--apply` as a repair path.
- Do not use `--migrate-provider-bucket` as a repair path.
- Do not create SQLite triggers such as `trg_threads_shared_provider_after_insert` or `trg_threads_shared_provider_after_update`.
- Do not install or start `codex-cockpit-switch-guard`.
- Do not install no-op launchers, restart wrappers, no-restart shims, or CLI preflight wrappers to intercept Cockpit Tools.
- Do not force `codex_launch_on_switch` on or off; it is a Cockpit UI/user setting.

## Guard Audit Commands
Use these before claiming the issue is fixed:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Start-CodexCockpitSwitchGuard.ps1 -Status
```

Expected:
- `task_state = "not_installed"`
- `process_count = 0`

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

## Evidence
Record the final incident evidence in `docs/change-evidence/` with:
- live `config.toml` provider id
- current Cockpit account id and `api_provider_id`
- thread provider distribution
- guard task/process status
- SQLite trigger count
- smoke result, such as a `codex exec` final message
- backup paths for changed live files

The 2026-05-13 reference incident is recorded in:
- `docs/change-evidence/2026-05-13-codex-cockpit-api-shared-history.md`

## Rollback
- Restore the timestamped backups created by `--repair-current-cockpit-api-projection`.
- Restore `~/.codex/config.toml`, `~/.codex/auth.json`, `~/.codex/state_5.sqlite`, and Cockpit provider metadata together. Do not restore only one file unless the evidence shows only that file drifted.
- Re-run the guard audit and read-only interop check after rollback.
