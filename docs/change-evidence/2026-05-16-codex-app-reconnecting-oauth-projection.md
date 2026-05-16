# 2026-05-16 Codex App Reconnecting OAuth Projection

- status: `superseded`
- superseded_by: `2026-05-16-codex-app-reconnecting-litellm-gateway-restore.md`
- correction: The intended local mode for this incident was the LiteLLM gateway lane, not old direct OAuth projection. This note records the mistaken direct-OAuth repair and its backups for rollback traceability only.

- rule_id: `LocalCodexCockpit`
- risk_level: `medium`
- timestamp: `2026-05-16T21:49:00+08:00`
- landing: live Codex/Cockpit projection under `C:\Users\sciman\.codex`
- target_outcome: align current Cockpit OAuth account with Codex App/CLI auth, provider bucket, and picker-visible history

## Cause

`CodexProjectionSmoke` showed Cockpit's current Codex account was OAuth/ChatGPT while the live Codex projection still used API/gateway shape:

- before `forced_login_method`: `api`
- before `model_provider`: `litellm_gateway`
- before `auth_mode`: `apikey`
- expected provider bucket: `openai`

This mismatch can leave Codex App at `Reconnecting...` and can split picker-visible history.

## Commands

```powershell
python scripts\codex-interop-check.py --codex-home "$HOME\.codex" --cc-switch-db "$HOME\.cc-switch\cc-switch.db" --cockpit-home "$HOME\.antigravity_cockpit" --quick-launch
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Test-CodexGuardAbsence.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\operator.ps1 -Action CodexOauthProjectionRepair
python scripts\codex-interop-check.py --codex-home "$HOME\.codex" --cc-switch-db "$HOME\.cc-switch\cc-switch.db" --cockpit-home "$HOME\.antigravity_cockpit" --quick-launch
codex exec --skip-git-repo-check "Respond with exactly: codex-cli-ok"
```

## Evidence

- repair result: `status=pass`
- final smoke result: `status=pass`
- final config: `forced_login_method="chatgpt"`, `model_provider="openai"`, `openai_base_url=<absent>`
- final auth: `auth_mode=chatgpt`, `has_tokens=True`, `has_openai_api_key=False`
- history provider distribution: `openai=1753`
- history visibility: `user_message_threads=1707`, `visible_user_event_threads=1707`
- guard audit: `status=pass`, `scheduled_task_present=false`, `process_count=0`, `retired_installed_files_present=[]`
- CLI live probe: `codex-cli 0.130.0`; `codex exec` returned `codex-cli-ok` with `provider: openai`
- no Codex App/Codex process was stopped, killed, restarted, or auto-launched by this repair

## Backups

- `C:\Users\sciman\.codex\backups\config.toml.20260516_214820_cockpit-oauth-projection.bak`
- `C:\Users\sciman\.codex\backups\auth.json.20260516_214820_cockpit-oauth-projection.bak`
- `C:\Users\sciman\.codex\backups\state_5.sqlite.20260516_214820_cockpit-oauth-projection.bak`

## Rollback

Restore the three timestamped backups together, then rerun:

```powershell
python scripts\codex-interop-check.py --codex-home "$HOME\.codex" --cc-switch-db "$HOME\.cc-switch\cc-switch.db" --cockpit-home "$HOME\.antigravity_cockpit" --quick-launch
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Test-CodexGuardAbsence.ps1
```
