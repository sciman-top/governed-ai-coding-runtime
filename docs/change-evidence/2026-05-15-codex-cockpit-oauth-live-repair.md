# 2026-05-15 Codex Cockpit OAuth Live Repair

- rule_id: `local-codex-cockpit-auth-interop`
- risk: medium local host state mutation
- landing: live `C:\Users\sciman\.codex`, live `C:\Users\sciman\.antigravity_cockpit`
- destination: repair current Cockpit OAuth projection, saved API provider projectability, launch follow-current binding, and picker visibility metadata without restarting Codex
- rollback: restore the timestamped backups listed below, then rerun `CodexProjectionSmoke`

## Commands

- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\operator.ps1 -Action CodexOauthProjectionRepair`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\operator.ps1 -Action CodexProjectionSmoke`

## Result

- `CodexOauthProjectionRepair`: `status=pass`
- Current Cockpit Codex account: `codex_3797bc603c01b0dd72e9181fe9aad25d`
- Current auth mode: `oauth`
- Expected provider bucket: `openai`
- `codex_thread_provider_distribution`: `openai=1726`, `status=pass`
- `codex_history_visibility_metadata`: `active_threads=1726`, `user_message_threads=1680`, `visible_user_event_threads=1680`, `status=pass`
- `cockpit_saved_api_provider_profiles_projectable`: changed from `fail` to `pass`
- `cockpit_codex_instances_follow_current_account`: changed from `fail` to `pass`
- `history_rows_changed`: `0`
- `history_visibility_rows_changed`: `12`
- `CodexProjectionSmoke`: `status=pass`
- `Test-CodexGuardAbsence.ps1`: `status=pass`, no scheduled task, no startup fallback, no worker process, no retired installed wrapper

## Backups

- `C:\Users\sciman\.codex\backups\config.toml.20260515_030555_cockpit-oauth-projection.bak`
- `C:\Users\sciman\.codex\backups\auth.json.20260515_030555_cockpit-oauth-projection.bak`
- `C:\Users\sciman\.codex\backups\state_5.sqlite.20260515_030555_cockpit-oauth-projection.bak`
- `C:\Users\sciman\.antigravity_cockpit\backups\codex_instances.json.20260515_030555_cockpit-oauth-projection.bak`

## Notes

- No Codex App, Codex CLI, or Cockpit process was restarted, stopped, killed, or auto-launched by this repair.
- `CodexLaunchBindingRepair` was not run separately because `CodexOauthProjectionRepair` also repaired `cockpit_codex_instances_follow_current_account`, and the follow-up smoke passed.
