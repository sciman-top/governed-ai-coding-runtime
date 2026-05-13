# 2026-05-13 Codex App / Cockpit API connectivity root cause

## Scope
- rule_id: `codex-cockpit-api-connectivity`
- risk: `medium`
- current_landing: `D:\CODE\governed-ai-coding-runtime`
- target_landing: repo diagnostics and live host cleanup evidence only
- rollback: restore renamed files from `C:\Users\sciman\.codex\backups\disable-project-interop-20260513-091610` or revert this repo commit

## Observed Failure
- Codex App popup: `failed to load configuration: Model provider cmp_1778165666417_1 not found`
- Codex CLI after Cockpit switch to API:
  - `ChatGPT login is required, but an API key is currently being used. Logging out.`
  - The failed CLI launch removed `C:\Users\sciman\.codex\auth.json`, leaving only the prior backup.
- Codex App/CLI after Cockpit drifted back to OAuth while `~/.codex` still used API mode:
  - `Sign in with ChatGPT to use Codex as part of your paid plan or connect an API key for usage-based billing`
  - Live interop state before repair: Cockpit `current_account_id = codex_52c6816e7d3ae9a075f9f237b058b6d8` (`auth_mode = oauth`), top-level `forced_login_method = "api"`, and no live `auth.json`.
- App log evidence:
  - `C:\Users\sciman\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Local\Codex\Logs\2026\05\13\codex-desktop-80c4790e-6578-41ee-a68f-01cf9e550097-22196-t0-i1-005538-0.log`
  - `method=thread/resume`
  - `failed to load configuration: Model provider cmp_1778165666417_1 not found`

## Root Cause
The repeated failure had four coupled causes.

1. A deprecated project-managed wrapper was still first on `PATH`:
   - `C:\Users\sciman\.local\bin\codex.ps1`
   - `C:\Users\sciman\.local\bin\codex.cmd`
   - `C:\Users\sciman\.local\bin\codex-cockpit-cli-preflight-repair.py`

   That wrapper ran `codex-cockpit-cli-preflight-repair.py` before normal Codex startup. The repair script wrote live Codex/Cockpit state (`auth.json`, `config.toml`, `state_5.sqlite`) and reintroduced drift after previous repairs.

2. Cockpit/Codex account switching left a window where `auth.json` or a thread referenced `cmp_1778165666417_1`, but live `config.toml` did not contain `[model_providers.cmp_1778165666417_1]`.

   Local evidence:
   - `C:\Users\sciman\.codex\config.toml.bak` at `2026-05-13 08:56:30` had `model_provider = "codex_local_access"` and no `cmp_1778165666417_1` provider table.
   - Current `C:\Users\sciman\.codex\config.toml` at `2026-05-13 09:04:07` contains the provider table again because the old preflight repair rewrote it.
   - This explains why the failure is intermittent: the App can start in the broken window, then the CLI wrapper later masks the missing provider table.

3. The live API projection and the repo diagnostic contract disagreed about custom Cockpit API providers.

   Broken live shape:
   - Cockpit current account: `auth_mode = apikey`, `api_provider_id = cmp_1778165666417_1`, `base_url = http://35.213.82.91:8003/v1`
   - `C:\Users\sciman\.codex\config.toml`: `forced_login_method = "chatgpt"`, `model_provider = "codex_local_access"`
   - `[model_providers.codex_local_access]`: `requires_openai_auth = true`

   Codex CLI interpreted this as: the active provider requires ChatGPT login, but `auth.json` contains an API key. It therefore printed `ChatGPT login is required, but an API key is currently being used. Logging out.` and removed the live API auth projection.

   The durable contract is the opposite for Cockpit custom API providers:
   - `forced_login_method = "api"`
   - `model_provider = "<Cockpit api_provider_id>"`
   - `[model_providers.<Cockpit api_provider_id>]`
   - `wire_api = "responses"`
   - `requires_openai_auth = false`
   - `supports_websockets = false`

4. The installed Cockpit Codex switch path can reintroduce the same drift after a successful repair.

   Local evidence:
   - `C:\Users\sciman\AppData\Local\Temp\cockpit-tools-src\src-tauri\src\modules\codex_account.rs` writes custom API providers with `requires_openai_auth = true` and has no `forced_login_method` writer in the inspected snapshot.
   - `C:\Users\sciman\AppData\Local\Temp\cockpit-tools-src\src-tauri\src\commands\codex.rs` calls `update_default_settings(Some(Some(account_id.clone())), None, Some(false), None)`, which rewrites `codex_instances.json` to `followLocalAccount = false` plus a fixed `bindAccountId`.
   - Cockpit logs at `2026-05-13T10:26:27+08:00` show an OAuth Codex switch to `codex_52c6816e7d3ae9a075f9f237b058b6d8`, a write to `C:\Users\sciman\.codex\auth.json`, and `已同步更新 Codex 默认实例绑定账号`.

   This explains the new prompt: after Cockpit makes OAuth current, Codex still sees an API login mode or missing/mismatched `auth.json`, so it falls back to the sign-in/API-key screen. The durable repair must treat Cockpit current account, Codex `auth.json`, Codex `config.toml`, and default instance binding as one projection.

## Cockpit WS Probe Result
- Cockpit Tools process: `cockpit-tools.exe` version `0.23.2`, `ws://127.0.0.1:19528/`
- `request.get_current_account` and `request.get_accounts` are reachable.
- `request.switch_account` is not the Codex-specific switch path on this host; it entered the generic Antigravity switch path and returned `APP_PATH_NOT_FOUND:antigravity`.
- Cockpit binary strings show a separate native command named `switch_codex_account`, but the simple WS request used here did not expose it.

## Changes
- Deprecated `scripts/codex-cockpit-cli-preflight-repair.py` as a no-write compatibility shim.
- Extended `scripts/Disable-CodexProjectInterop.ps1` so cleanup also disables `codex-cockpit-cli-preflight-repair.py` in `C:\Users\sciman\.local\bin`.
- Added regression coverage that a saved Cockpit API provider is a hard failure when its provider bucket is missing from live `config.toml`.
- Added explicit `scripts/codex-interop-check.py --repair-current-cockpit-api-projection` for the narrow current-Cockpit-API-account projection case. General `--apply` and provider-bucket migration remain disabled.
- Added `--prefer-cockpit-api-account` so the repair can recover from a Cockpit OAuth current account by selecting the preferred API account, promoting it to `codex_accounts.json.current_account_id`, and then projecting it into Codex.
- Updated Cockpit API provider validation so custom API providers require `requires_openai_auth = false` instead of the stale `true` assertion.
- The explicit repair backs up and rewrites:
  - `C:\Users\sciman\.codex\config.toml`
  - `C:\Users\sciman\.codex\auth.json`
  - `C:\Users\sciman\.antigravity_cockpit\codex_accounts.json`
  - `C:\Users\sciman\.antigravity_cockpit\codex_instances.json`
- The repair also clears stale fixed instance binding by setting `followLocalAccount = true` and `bindAccountId = null`.
- Added/updated tests for disabling project-owned Codex shims.
- Moved the MCP stdout-pollution fix to the actual source repo, `D:\CODE\skills-manager`, so future `同步MCP` runs do not restore the broken Codex MCP set.

## MCP Flicker Root Cause
- Codex App logs also showed MCP JSON parse failures caused by non-JSON `taskkill` success text on the App MCP pipe.
- `codex exec` reproduced the same issue before the MCP fix: stdout contained repeated `SUCCESS: The process with PID ... has been terminated.` lines before the model response.
- Isolation showed the noisy Windows stdio MCP path came from npx/stdio servers (`context7`, `filesystem`, `playwright`) and an unmanaged `fetch` entry.
- `skills-manager` now skips known leaky npx stdio MCPs for Codex by default and keeps clean HTTP MCPs plus `postgres` through a cached Node wrapper.
- Live Codex MCP state after `./skills.ps1 同步MCP`:
  - stdio: `postgres`
  - HTTP: `github`, `microsoft-learn`, `openaiDeveloperDocs`
  - excluded for Codex by default: `context7`, `filesystem`, `playwright`, unmanaged `fetch`

## Live Host Cleanup Evidence
- Command:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Disable-CodexProjectInterop.ps1 -Apply -DisableProjectShortcuts`
- Evidence:
  - `docs/change-evidence/disable-codex-project-interop-20260513-091610.json`
- Result:
  - Official `codex` now resolves from `C:\Users\sciman\AppData\Roaming\npm\codex.ps1`.
  - Deprecated project shims were renamed with `.disabled-20260513-091610`.

## API Projection Repair Evidence
- Command:
  - `python scripts\codex-interop-check.py --codex-home "$HOME\.codex" --cc-switch-db "$HOME\.cc-switch\cc-switch.db" --cockpit-home "$HOME\.antigravity_cockpit" --quick-launch --repair-current-cockpit-api-projection`
- Result:
  - exit_code: `0`
  - action: `repair_current_cockpit_api_projection`
  - action_status: `changed`
  - provider_id: `cmp_1778165666417_1`
  - base_url: `http://35.213.82.91:8003/v1`
  - `cockpit_instance_binding_changed = true`
- Backups:
  - `C:\Users\sciman\.codex\backups\config.toml.20260513_101432_cockpit-api-projection.bak`
  - `C:\Users\sciman\.codex\backups\auth.json.20260513_101432_cockpit-api-projection.bak`
  - `C:\Users\sciman\.antigravity_cockpit\backups\codex_instances.json.20260513_101432_cockpit-api-projection.bak`
- Post-repair live checks:
  - `codex login status`: `Logged in using an API key - sk-***`
  - `cockpit_live_login_mode_matches_current_account`: `pass`, `active_forced_login_method = api`, `requires_openai_auth = false`
  - `codex_auth_matches_cockpit_current_account`: `pass`
  - `cockpit_saved_api_provider_profiles_projectable`: `pass`
  - `cockpit_codex_instances_follow_current_account`: `pass`

## OAuth Drift Recovery Evidence
- Command:
  - `python scripts\codex-interop-check.py --codex-home "$HOME\.codex" --cc-switch-db "$HOME\.cc-switch\cc-switch.db" --cockpit-home "$HOME\.antigravity_cockpit" --quick-launch --repair-current-cockpit-api-projection --prefer-cockpit-api-account`
- Result:
  - exit_code: `0`
  - status: `attention`
  - action: `repair_current_cockpit_api_projection`
  - `account_id = codex_apikey_8b8853f15e823dc53bd156163035bc78`
  - `provider_id = cmp_1778165666417_1`
  - `cockpit_current_account_changed = true`
  - `previous_cockpit_current_account_id = codex_52c6816e7d3ae9a075f9f237b058b6d8`
  - `cockpit_instance_binding_changed = true`
- Backups:
  - `C:\Users\sciman\.codex\backups\config.toml.20260513_103810_cockpit-api-projection.bak`
  - `C:\Users\sciman\.antigravity_cockpit\backups\codex_accounts.json.20260513_103810_cockpit-api-projection.bak`
  - `C:\Users\sciman\.antigravity_cockpit\backups\codex_instances.json.20260513_103810_cockpit-api-projection.bak`
- Post-repair live checks:
  - `codex login status`: `Logged in using an API key - sk-***`
  - `codex debug models`: exit_code `0`
  - `codex exec --ephemeral --skip-git-repo-check --output-last-message <temp> "Reply exactly OK."`: exit_code `0`, last_message `OK`, provider `cmp_1778165666417_1`
  - no-arg `codex-interop-check.py --quick-launch`: exit_code `0`, status `attention`, all auth/API/provider/instance checks pass

## Verification
- `python -m py_compile scripts\codex-cockpit-cli-preflight-repair.py`
- `python -m py_compile scripts\codex-interop-check.py scripts\codex-cockpit-cli-preflight-repair.py`
- `python -m unittest tests.runtime.test_codex_shared_launcher.CodexSharedLauncherTests.test_interop_checker_repairs_current_cockpit_api_projection_explicitly tests.runtime.test_codex_shared_launcher.CodexSharedLauncherTests.test_interop_checker_prefers_api_account_after_cockpit_oauth_switch`
  - `Ran 2 tests`
  - `OK`
- `python -m unittest tests.runtime.test_codex_cockpit_cli_preflight_repair tests.runtime.test_codex_shared_launcher.CodexSharedLauncherTests.test_disable_project_interop_disables_top_level_codex_shims`
- `python -m unittest tests.runtime.test_codex_shared_launcher tests.runtime.test_codex_cockpit_switch_trace`
  - `Ran 21 tests`
  - `OK`
- `python scripts\codex-interop-check.py --codex-home "$HOME\.codex" --cc-switch-db "$HOME\.cc-switch\cc-switch.db" --cockpit-home "$HOME\.antigravity_cockpit" --quick-launch`
  - exit_code: `0`
  - status: `attention`
  - pass: auth/API/provider projection checks
  - warn: existing active thread history is still bucketed under `codex_local_access`; API connectivity is primary and history sharing is secondary unless explicitly requested.
- `git diff --check`
  - exit_code: `0`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\build-runtime.ps1`
  - `OK python-bytecode`
  - `OK python-import`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Runtime`
  - `Completed 113 test files`
  - `failures=0`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Contract`
  - `OK functional-effectiveness`
  - `OK agent-rule-sync`
  - `OK target-repo-governance-consistency`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\doctor-runtime.ps1`
  - `OK runtime-status-surface`
  - `OK adapter-posture-visible`
  - residual existing warning: `WARN codex-capability-degraded`
- `codex debug models`
  - exit_code: `0`
  - result: model catalog returned through provider `cmp_1778165666417_1`
- `codex mcp list`
  - stdio: `postgres`
  - HTTP: `github`, `microsoft-learn`, `openaiDeveloperDocs`
  - no noisy npx stdio MCP entries in the live Codex list
- `codex exec --ephemeral --skip-git-repo-check --output-last-message <temp> "Reply exactly OK."`
  - exit_code: `0`
  - stdout: `OK`
  - last_message: `OK`
  - provider: `cmp_1778165666417_1`
  - note: stderr still contains native stale-PID cleanup noise like `ERROR: The process "<pid>" not found.`; this is separate from API auth/connectivity and did not corrupt stdout or the last message.
- `D:\CODE\skills-manager`:
  - `./build.ps1`
  - `./skills.ps1 发现`
  - `Invoke-Pester -Script tests\Unit\Core.Tests.ps1`
  - `./skills.ps1 同步MCP`
  - `./skills.ps1 doctor --strict --threshold-ms 8000`
  - `./skills.ps1 构建生效`

## Residual Risk
- Live API connectivity is fixed and verified through `codex login status`, `codex debug models`, and real `codex exec`.
- Current residual warning is history bucket mismatch only:
  - `state_5.sqlite` active thread distribution after the OAuth-drift repair: `openai = 1692`, `codex_local_access = 2`
  - current expected API provider bucket: `cmp_1778165666417_1`
  - Do not run provider-bucket migration unless the user explicitly prioritizes shared history over keeping API connectivity stable.
- The native Codex CLI may still emit stale-PID cleanup noise on stderr. Treat that as a separate startup-noise issue unless it correlates with auth failure, non-zero exit, or corrupted stdout.
