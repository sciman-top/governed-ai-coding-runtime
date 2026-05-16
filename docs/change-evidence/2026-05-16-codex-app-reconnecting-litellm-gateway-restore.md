# 2026-05-16 Codex App Reconnecting LiteLLM Gateway Restore

- rule_id: `LocalCodexCockpit`
- risk_level: `medium`
- landing: `.runtime/litellm/`, `C:\Users\sciman\.codex\config.toml`, `C:\Users\sciman\.codex\auth.json`
- target_outcome: restore the intended `Codex -> LiteLLM -> Cockpit API service` lane after a LiteLLM uninstall attempt and an accidental direct-OAuth projection repair

## Cause

The intended route was gateway mode, but live Codex had been changed to old direct OAuth shape:

- `forced_login_method="chatgpt"`
- `model_provider="openai"`
- `auth_mode=chatgpt`

LiteLLM runtime files were still present under `.runtime/litellm/`, but the gateway was not running:

- `litellm_installed=true`
- `litellm_running=false`
- `litellm_listener_count=0`
- Cockpit local access listener was present and safe for upstream on `127.0.0.1:2876`.

## Commands

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Manage-LiteLLMGateway.ps1 -Action Status
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Manage-LiteLLMGateway.ps1 -Action CockpitStatus
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Manage-LiteLLMGateway.ps1 -Action Start
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Manage-LiteLLMGateway.ps1 -Action PrepareCockpitUpstream
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Manage-LiteLLMGateway.ps1 -Action WriteCodexProfile
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Manage-LiteLLMGateway.ps1 -Action Smoke
codex exec --skip-git-repo-check "Respond with exactly: codex-gateway-ok"
```

## Evidence

- LiteLLM start: `status=ok`, `listener=present`, wrapper PID `9900`, server process PID `25816`
- LiteLLM listener: `127.0.0.1:4000`
- Cockpit local access listener: `127.0.0.1:2876`
- Cockpit upstream safety: `safe_for_upstream=true`, `follow_current_account=true`, `account_count=1`, `non_loopback_listener_count=0`
- LiteLLM smoke: `/v1/models` returned `cockpit-current` and `gpt-5.5`
- restored Codex profile: `forced_login_method="api"`, `model_provider="litellm_gateway"`, `model="cockpit-current"`
- restored Codex auth: `auth_mode=apikey`, local gateway key present
- live Codex probe: `codex exec` returned `codex-gateway-ok` with `provider: litellm_gateway` and `model: cockpit-current`
- LiteLLM log confirmed `POST /v1/responses HTTP/1.1" 200 OK`
- no Codex App/Codex process was stopped, killed, restarted, or auto-launched

## Backups

- accidental direct OAuth backups retained for rollback traceability:
  - `C:\Users\sciman\.codex\backups\config.toml.20260516_214820_cockpit-oauth-projection.bak`
  - `C:\Users\sciman\.codex\backups\auth.json.20260516_214820_cockpit-oauth-projection.bak`
  - `C:\Users\sciman\.codex\backups\state_5.sqlite.20260516_214820_cockpit-oauth-projection.bak`
- gateway restore backups:
  - `C:\Users\sciman\.codex\config-backups\config.toml.20260516-215259.litellm-gateway.bak`
  - `C:\Users\sciman\.codex\backups\auth.json.20260516-215259.litellm-gateway.bak`

## Rollback

To leave gateway mode, use the governed rollback first:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Manage-LiteLLMGateway.ps1 -Action Rollback
```

If reverting to the pre-correction direct OAuth state is explicitly desired, restore the timestamped direct-OAuth backups together, then rerun gateway/direct projection smoke according to the intended mode.
