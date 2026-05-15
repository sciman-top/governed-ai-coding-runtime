# LiteLLM / Cockpit Gateway Runbook

## Scope
This runbook covers the preferred gateway lane for Codex CLI:

```text
Codex -> LiteLLM -> Cockpit API service
```

Cockpit Tools remains the owner of ChatGPT/OAuth subscription accounts, quota facts, refresh, and manual account switching. LiteLLM is the client-facing gateway for normal API-key providers and can register Cockpit API service as one opt-in upstream named `cockpit-current`.

This new gateway lane is a selectable mode, not a replacement for the old direct Codex App/CLI OAuth/API projection behavior. Keep the old mode available through `CodexApiProjectionRepair` and `CodexOauthProjectionRepair` when the operator wants Cockpit Tools to project the current API or OAuth account directly into Codex.

## Safety Boundary
- LiteLLM is installed under `.runtime/litellm/venv`; it is not installed into global Python.
- Runtime config, logs, PID, and local secrets live under `.runtime/litellm/`, which is gitignored.
- LiteLLM binds to `127.0.0.1:4000` by default.
- Cockpit API service at `127.0.0.1:2876/v1` must not be used as an upstream until listener scope is verified as loopback-only or constrained by firewall.
- The custom local Cockpit build binds the Codex local API service to `127.0.0.1` and disables the official auto-update lane. If a future official build is used and binds `0.0.0.0`, the minimum acceptable constraint is Windows Firewall profile policy `BlockInbound,AllowOutbound` or an explicit inbound block rule for the Cockpit port.
- The managed setup uses Cockpit local access in follow-current single-account mode: `accountIds=[current_account_id]`, `followCurrentAccount=true`, and `restrictFreeAccounts=false` by default. API-key-shaped and free Cockpit accounts are allowed by default in the custom local build.
- This lane intentionally avoids the 409-account free pool. Routing strategy becomes a non-factor because the upstream pool contains exactly one OAuth account.
- Codex App is not restarted by this lane. New Codex CLI/App sessions use the local gateway after operator-controlled start.
- An already-running Codex App process may keep showing its previous OAuth session until it is restarted by the operator. The file-level truth for new Codex processes is `~/.codex/config.toml` plus `~/.codex/auth.json`.
- The Codex config change is reversible but active: it activates `model_provider = "litellm_gateway"`, `forced_login_method = "api"`, and `model = "cockpit-current"` at top level, writes a local API-key `auth.json`, and keeps a managed `profiles.litellm-gateway` / `model_providers.litellm_gateway` block for traceability.
- The setup clears Cockpit default-instance fixed account binding by setting `codex_instances.json.defaultSettings.followLocalAccount=true`, `bindAccountId=null`, and `lastPid=null`. A fixed `bindAccountId` can make a later Cockpit launch re-project an old OAuth account and bypass `127.0.0.1:4000`.
- LiteLLM proxy `master_key` is intentionally synchronized to the Cockpit local access key for this local-only lane. This avoids a second virtual-key database and keeps Codex's `Authorization` header valid if LiteLLM forwards it to the Cockpit upstream.
- The current self-build uses `gpt-5.5` as the LiteLLM upstream default. Override `-UpstreamModel` only for a documented compatibility probe.
- The current self-build disables Codex quota auto-refresh by default and skips automatic quota refresh after Codex account import/token add. Manual refresh remains available, but the gateway lane should not sweep large imported free-account pools.

## Commands

Mode switch overview:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\operator.ps1 -Action CodexGatewayEnable
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\operator.ps1 -Action CodexGatewayRollback
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\operator.ps1 -Action CodexApiProjectionRepair
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\operator.ps1 -Action CodexOauthProjectionRepair
```

When Cockpit self-use builds are the mode owner, the canonical state file is `~/.antigravity_cockpit/codex_runtime_mode.json`. Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\operator.ps1 -Action CodexModeSync` to materialize that state into either gateway mode or the old direct API/OAuth projection mode.

The same choices are exposed through root shortcuts: `.\run.ps1 codex-mode-new`, `.\run.ps1 codex-mode-rollback`, `.\run.ps1 codex-mode-old-api`, and `.\run.ps1 codex-mode-old-oauth`.

Install or refresh LiteLLM:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Manage-LiteLLMGateway.ps1 -Action Install
```

Render local config and secrets:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Manage-LiteLLMGateway.ps1 -Action RenderConfig
```

Start the local gateway:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Manage-LiteLLMGateway.ps1 -Action Start
```

Prepare Cockpit local access as a safe LiteLLM upstream. This writes the current manual Codex account as the only API service account and enables follow-current mode for Cockpit builds that support it:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Manage-LiteLLMGateway.ps1 -Action PrepareCockpitUpstream
```

If `restart_required=true`, restart Cockpit Tools only. Do not restart Codex App or `codex` processes as part of this lane.

Inspect state:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Manage-LiteLLMGateway.ps1 -Action Status
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Manage-LiteLLMGateway.ps1 -Action CockpitStatus
```

Smoke the LiteLLM front door without printing secrets:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Manage-LiteLLMGateway.ps1 -Action Smoke
```

Write the reversible Codex profile:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Manage-LiteLLMGateway.ps1 -Action WriteCodexProfile
```

Run all local setup steps:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Manage-LiteLLMGateway.ps1 -Action All
```

Verify a new Codex CLI run uses the gateway:

```powershell
$env:LITELLM_MASTER_KEY = (Get-Content .runtime\litellm\secrets.env | Where-Object { $_ -like 'LITELLM_MASTER_KEY=*' }).Split('=', 2)[1]
codex exec --skip-git-repo-check "Reply exactly: ok"
```

Rollback:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Manage-LiteLLMGateway.ps1 -Action Rollback
```

Rollback stops only the PID recorded by `.runtime/litellm/litellm.pid` and removes the managed Codex config block after creating a backup under `~/.codex/config-backups/`.

## Verification
- `litellm --version` from `.runtime/litellm/venv`.
- `/v1/models` through `http://127.0.0.1:4000` with the local master key.
- `/v1/chat/completions` through `http://127.0.0.1:4000` returns a real completion from `cockpit-current`.
- `codex exec --skip-git-repo-check` reaches LiteLLM. A `429` with `模型 ... 可用账号均在冷却中` is an upstream Cockpit account cooldown, not a failure to use `127.0.0.1:4000`.
- `CockpitStatus.safe_for_upstream = true` before treating `cockpit-current` as live.
- `CockpitStatus.account_count = 1` and `CockpitStatus.follow_current_account = true` for the preferred production lane.
- `CodexProjectionSmoke` remains the direct Cockpit/Codex projection check; gateway mode may still report direct Cockpit projection issues until the Cockpit upstream is enabled and hardened.

## Failure Handling
- If LiteLLM starts but `/v1/models` fails, inspect `.runtime/litellm/litellm.log` and stop the gateway before retrying.
- If Cockpit API service has no listener, keep LiteLLM running for config/profile validation but mark Cockpit upstream live smoke as `gate_na` with reason `cockpit_api_service_not_enabled`.
- If Cockpit API service binds to a non-loopback address and neither Windows Firewall default inbound block nor an explicit block rule is present, do not connect Codex to it.
- If Codex cannot read `LITELLM_MASTER_KEY`, rerun `WriteCodexProfile` and start a new Codex process so the user-scope environment variable is visible.
- If Codex returns to direct Cockpit OAuth after a Cockpit switch or API-service activation, inspect `~/.codex/config.toml`, `~/.codex/auth.json`, and `~/.antigravity_cockpit/codex_instances.json`; rerun `PrepareCockpitUpstream` and `WriteCodexProfile`, not `CodexApiProjectionRepair` or `CodexOauthProjectionRepair`.
