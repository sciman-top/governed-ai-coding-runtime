# 2026-05-15 Cockpit Refresh API Service Risk

- rule_id: `local-codex-cockpit-auth-interop`
- risk: medium live Cockpit configuration mutation
- landing: live `C:\Users\sciman\.antigravity_cockpit`, `docs/runbooks/codex-cockpit-api-provider-repair.md`
- destination: lower Cockpit refresh/switching risk without breaking Codex OAuth/API projection, and record the local API service boundary before using `127.0.0.1:2876/v1`
- rollback: restore the timestamped Cockpit config backups listed below, then rerun `CodexProjectionSmoke`

## Changes

- Set `config.json.auto_refresh_minutes = 15`.
- Preserved `config.json.codex_auto_refresh_minutes = -1`, so Codex batch quota refresh remains disabled.
- Preserved `config.json.auto_switch_enabled = false` and `config.json.codex_auto_switch_enabled = false`.
- Preserved `config.json.codex_launch_on_switch = false` and `config.json.codex_restart_specified_app_on_switch = false`.
- Temporarily enabled `codex_local_access.json.enabled = true` for a local probe, then disabled it again after source review showed the checked Cockpit Tools gateway binds to `0.0.0.0` while displaying `127.0.0.1`.
- Updated the repair runbook to require listener-scope verification before using the Cockpit Codex API service.

## Evidence

- `CodexProjectionSmoke` initially failed after live Cockpit state drifted outside this repo: `cockpit_saved_api_provider_profiles_projectable` and `cockpit_codex_instances_follow_current_account` failed.
- Ran `CodexOauthProjectionRepair`; result `status=pass`, action `status=changed`, `cockpit_instance_binding_changed=true`, `history_visibility_rows_changed=1`.
- Final `CodexProjectionSmoke`: `status=pass`.
- Final `Test-CodexGuardAbsence.ps1`: `status=pass`, no scheduled task, no startup fallback, no worker process.
- Final `codex_thread_provider_distribution`: `openai=1728`, `status=pass`.
- Final `codex_history_visibility_metadata`: `active_threads=1728`, `user_message_threads=1682`, `visible_user_event_threads=1682`, `status=pass`.
- Local API probe to `http://127.0.0.1:2876/v1/models`: connection refused; editing `codex_local_access.json` did not hot-start the already-running Cockpit in-process gateway.
- Cockpit Tools source snapshot inspected: `D:\CODE\external\cockpit-tools\src-tauri\src\modules\codex_local_access.rs` defines `CODEX_LOCAL_ACCESS_BIND_HOST = "0.0.0.0"` and `CODEX_LOCAL_ACCESS_URL_HOST = "127.0.0.1"`.

## Backups

- `C:\Users\sciman\.antigravity_cockpit\backups\config.json.20260515_034147.safe-refresh-api.bak`
- `C:\Users\sciman\.antigravity_cockpit\backups\codex_local_access.json.20260515_034147.safe-refresh-api.bak`
- `C:\Users\sciman\.antigravity_cockpit\backups\codex_local_access.json.20260515_034400.disable-unverified-bind.bak`
- `C:\Users\sciman\.codex\backups\config.toml.20260515_034233_cockpit-oauth-projection.bak`
- `C:\Users\sciman\.codex\backups\auth.json.20260515_034233_cockpit-oauth-projection.bak`
- `C:\Users\sciman\.codex\backups\state_5.sqlite.20260515_034233_cockpit-oauth-projection.bak`
- `C:\Users\sciman\.antigravity_cockpit\backups\codex_instances.json.20260515_034233_cockpit-oauth-projection.bak`

## Decision

- Do not update the project roadmap for this incident. This is an operational runbook/evidence hardening item, not a new product milestone.
- Do not keep Cockpit Codex API service enabled until the running build is verified to bind only to loopback or a host firewall rule blocks LAN access to the selected port.
- If a reverse proxy/API gateway is needed for normal API keys, prefer a dedicated OpenAI-compatible gateway such as LiteLLM Proxy. Cockpit Tools' local-access gateway is useful for Codex account convenience, but its account-token gateway and switch semantics make it a higher-risk choice for unattended coding.
