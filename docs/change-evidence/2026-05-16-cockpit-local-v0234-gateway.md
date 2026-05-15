# 2026-05-16 Cockpit local v0.23.4 gateway

## Scope
- Current landing: `D:\CODE\external\cockpit-tools` branch `codex/follow-current-local-v0.23.4`; governed orchestration in this repository.
- Destination: self-built Cockpit local gateway for `Codex -> LiteLLM -> Cockpit API service`, with loopback-only listener, follow-current single-account mode, API-key/free accounts allowed by default, and official auto-update disabled for the self build.
- Risk: medium. Cockpit Tools process was restarted; Codex App/CLI processes were not restarted.

## Changes
- Merged upstream Cockpit Tools `v0.23.4`.
- Self-build identity: product/window title changed to `Cockpit Tools Local`, bundle identifier changed to `com.sciman.cockpit-tools-local`.
- Update safety: frontend updater checks return early; backend update settings force `auto_check=false`, `auto_install=false`, and `remind_on_update=false`; updater artifacts disabled.
- Network safety: Codex local API service bind host changed from `0.0.0.0` to `127.0.0.1`.
- Account policy: default `restrictFreeAccounts=false`; local access no longer excludes API-key accounts.
- API-key support: API-key accounts now send upstream requests to their configured `api_base_url` with `openai_api_key`; OAuth accounts still use ChatGPT Codex upstream with OAuth access tokens.
- API-service activation no longer clears Cockpit's current Codex account or binds the default instance to `__api_service__`; this prevents the custom gateway lane from being overwritten back into direct Cockpit projection.
- Governed script/runbook updated so `PrepareCockpitUpstream` writes current account single-account mode with `followCurrentAccount=true` and `restrictFreeAccounts=false`, and clears Cockpit default-instance fixed account binding.
- Governed `WriteCodexProfile` now activates `model_provider = "litellm_gateway"` and writes `auth.json` for `http://127.0.0.1:4000/v1` instead of only adding an opt-in profile.
- Governed LiteLLM default upstream model changed from stale `gpt-5.4` to current repository baseline `gpt-5.5`.
- Official Cockpit Tools `0.23.4` was uninstalled from `C:\Users\sciman\AppData\Local\Cockpit Tools`.
- Self-built Cockpit Tools Local was installed to `C:\Users\sciman\AppData\Local\Cockpit Tools Local\cockpit-tools-local.exe`, and a desktop shortcut was created at `D:\Desktop\Cockpit Tools Local.lnk`.
- Risk reduction for large imported free pools: Codex quota auto-refresh defaults to disabled, Codex import/token-add no longer auto-refreshes quota, and manual refresh remains an operator action.

## Verification
- `npm run typecheck` in `D:\CODE\external\cockpit-tools`: pass.
- `npm run build` in `D:\CODE\external\cockpit-tools`: pass.
- `cargo check --lib` in `D:\CODE\external\cockpit-tools\src-tauri`: pass with pre-existing warnings.
- `cargo test update_checker --lib` in `D:\CODE\external\cockpit-tools\src-tauri`: 6 passed.
- `npm run tauri -- build --no-bundle`: parent command timed out, but release build completed afterward; final exe `D:\CODE\external\cockpit-tools\target\release\cockpit-tools.exe`, last write `2026-05-16 01:51:52`.
- Custom Cockpit live process: `D:\CODE\external\cockpit-tools\target\release\cockpit-tools.exe`, PID `18572`.
- Installed custom Cockpit live process after replacement: `C:\Users\sciman\AppData\Local\Cockpit Tools Local\cockpit-tools-local.exe`, PID `24848`.
- Cockpit listener: `127.0.0.1:2876`, `non_loopback_listener_count=0`, `safe_for_upstream=true`.
- Official Cockpit uninstall verification: registry query for `Cockpit Tools` returned no installed entry, and `C:\Users\sciman\AppData\Local\Cockpit Tools` no longer exists.
- Production local access state after restore: `enabled=true`, `account_count=1`, `follow_current_account=true`, `restrict_free_accounts=false`.
- LiteLLM smoke: `GET http://127.0.0.1:4000/v1/models` returned `cockpit-current`.
- LiteLLM config after refresh maps `cockpit-current` to upstream `openai/gpt-5.5`.
- Real completion direct Cockpit API-key probe: `POST http://127.0.0.1:2876/v1/chat/completions`, model `gpt-5.4-mini`, returned content `OK`.
- Real completion through LiteLLM API-key probe: `POST http://127.0.0.1:4000/v1/chat/completions`, model `cockpit-current`, returned content `OK`, usage total tokens `31`.
- New Codex CLI process after fixing config/auth returned `OK` through `model=cockpit-current`, proving new CLI sessions use `127.0.0.1:4000`.
- Current follow-current OAuth/free production account remains upstream-cooled for real completion; LiteLLM log showed `429` with `模型 gpt-5.4 的可用账号均在冷却中`.
- After switching the default upstream to `gpt-5.5`, the current follow-current account later returned `429` with `模型 gpt-5.5 的可用账号均在冷却中，请 603466 秒 后重试`; this proves the request reached LiteLLM/Cockpit and was blocked by the selected account's cooldown, not by OAuth fallback.
- After Codex default activation, `codex exec --skip-git-repo-check` reached LiteLLM and Cockpit local access; the observed `429` was confirmed in `.runtime/litellm/litellm.log` and `codex-api.log.2026-05-15` as current-account cooldown for `codex_518a4c08eb865933ff9e3bd58103ccbb`, not a bypass of `127.0.0.1:4000`.
- Retired guard evidence: `C:\Users\sciman\.codex\log\codex-cockpit-switch-guard.jsonl` last showed writes on `2026-05-14`; no fresh background guard write was observed for the `2026-05-16` drift. The live drift source was Cockpit/Codex direct projection state and fixed default-instance binding.

## Rollback
- Stop the custom Cockpit process and restart the installed official Cockpit Tools if needed.
- Restore Cockpit local access from:
  - `C:\Users\sciman\.antigravity_cockpit\backups\codex_local_access.json.20260516-015216.api-key-probe.bak`
  - `C:\Users\sciman\.antigravity_cockpit\backups\codex_local_access.json.20260516-015339.restore-follow-current.bak`
- Revert the Cockpit branch `codex/follow-current-local-v0.23.4` or reset it to upstream tag `v0.23.4`.
- Revert this repository's LiteLLM runbook/script/test changes if the gateway lane is retired.
- Restore Codex config/auth from `C:\Users\sciman\.codex\config-backups\` and `C:\Users\sciman\.codex\backups\` if reverting from LiteLLM gateway back to direct OAuth/API projection.
