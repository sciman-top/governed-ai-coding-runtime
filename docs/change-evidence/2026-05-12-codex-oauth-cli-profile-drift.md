# 2026-05-12 Codex OAuth CLI profile drift

## Scope
- Rule ID: R1/R3/R8, local Codex OAuth login projection and shared profile consistency.
- Risk: medium. Live `config.toml`, `auth.json`, and `state_5.sqlite` were inspected; no Codex App or long-running Codex process was restarted or killed.
- Current landing: `C:\Users\sciman\.codex\config.toml`, `C:\Users\sciman\.codex\auth.json`, `C:\Users\sciman\.codex\state_5.sqlite`.
- Target home: keep the current Cockpit OAuth account projected as Codex `chatgpt` auth under the built-in `openai` provider bucket.

## Root cause
- The current Cockpit Codex account was OAuth, which maps to Codex `auth_mode = "chatgpt"` and `forced_login_method = "chatgpt"`.
- Live `config.toml` had recovered its top-level login mode to `forced_login_method = "chatgpt"`, but shared profiles were still stale:
  - `profiles.shared-current-provider` pointed at `model_provider = "cmp_1778165666417_1"`.
  - `profiles.shared-cockpit-auth` had `forced_login_method = "api"` even though it is the OAuth profile.
- Running `codex --profile shared-current-provider exec ...` reproduced the profile drift: Codex started with `provider: cmp_1778165666417_1` and failed refreshing a ChatGPT access token.

## Changes
- Re-applied the control-repo optimizer:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/Optimize-CodexLocal.ps1 -Apply -InstallAccountSwitcher:$false -SkipInteropCheck -CodexHome C:\Users\sciman\.codex -TrustedRepoRoot D:\CODE\governed-ai-coding-runtime`
- The optimizer backed up live config to `C:\Users\sciman\.codex\config-backups\config-20260512-212153.toml`.
- Live profile state after repair:
  - top-level `forced_login_method = "chatgpt"`, `model_provider = "openai"`
  - `profiles.shared-chatgpt`: `forced_login_method = "chatgpt"`, `model_provider = "openai"`
  - `profiles.shared-current-provider`: `forced_login_method = "chatgpt"`, `model_provider = "openai"`
  - `profiles.shared-cockpit-auth`: `forced_login_method = "chatgpt"`, `model_provider = "openai"`
- The failed profile probe created one active `cmp_1778165666417_1` thread. A backup was created at `C:\Users\sciman\.codex\state-backups\state_5.sqlite.20260512_2124_before_provider_probe_cleanup.bak`, then that probe thread was restored to the expected `openai` bucket.

## Verification
- `codex exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox "请只输出 OK"`
  - Result: `provider: openai`, final output `OK`.
- `codex --profile shared-chatgpt exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox "请只输出 OK"`
  - Result: `provider: openai`, final output `OK`.
- `codex --profile shared-cockpit-auth exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox "请只输出 OK"`
  - Result: `provider: openai`, final output `OK`.
- `codex --profile shared-current-provider exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox "请只输出 OK"`
  - Result after repair: `provider: openai`, final output `OK`.
- `python scripts/codex-interop-check.py --codex-home C:\Users\sciman\.codex --cc-switch-db C:\Users\sciman\.cc-switch\cc-switch.db --cockpit-home C:\Users\sciman\.antigravity_cockpit --quick-launch`
  - Result: `status = pass`; `cockpit_current_account_projectable.auth_mode = "oauth"`, `active_forced_login_method = "chatgpt"`, `codex_auth_matches_cockpit_current_account.actual_auth_mode = "chatgpt"`, thread distribution `{ "openai": 1673 }`.
  - Residual warning: `profiles.shared-cockpit-api` currently uses `model_provider = "openai"` while saved API provider metadata expects `cmp_1778165666417_1`; this is an API-profile warning and did not affect OAuth CLI execution.

## Rollback
- Restore `C:\Users\sciman\.codex\config.toml` from `C:\Users\sciman\.codex\config-backups\config-20260512-212153.toml` if this OAuth profile repair must be undone.
- Restore `C:\Users\sciman\.codex\state_5.sqlite` from `C:\Users\sciman\.codex\state-backups\state_5.sqlite.20260512_2124_before_provider_probe_cleanup.bak` if the probe-thread provider-bucket cleanup must be undone.
