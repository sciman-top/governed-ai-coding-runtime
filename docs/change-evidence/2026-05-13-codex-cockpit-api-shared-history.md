# 2026-05-13 Codex Cockpit API Shared History Repair

## Rule
- `R1`: current landing is local Codex/Cockpit interop state and `scripts/codex-interop-check.py`; target landing is API-key startup that preserves the shared `openai` history bucket.
- `R6`: verification order used a focused runtime unit test, live interop diagnostic, and CLI API smoke.
- `R8`: backups were created before local config/auth projection; rollback is file restore from backup or git history for repo code.

## Risk
- Level: medium, because the live repair writes local `~/.codex/config.toml`, `~/.codex/auth.json`, Cockpit `codex_accounts.json`, and Cockpit `codex_instances.json`.
- Secret boundary: command output and this evidence omit raw API keys.

## Root Cause
- Cockpit API switching had drifted into a custom `cmp_*` model provider bucket.
- Codex history picker is bucketed by `threads.model_provider`, and the live local history distribution was `openai=1697`.
- Switching API sessions to `cmp_*` therefore made the picker look empty even though history still existed.
- A second mismatch left `forced_login_method = "api"` active while Cockpit's current account was OAuth and `auth.json` was missing, causing Codex CLI startup to report an API-key-vs-ChatGPT login conflict.

## Changes
- `scripts/codex-interop-check.py`
  - Cockpit API projection now keeps `model_provider = "openai"`.
  - API relay routing uses top-level and profile-level `openai_base_url`.
  - Saved Cockpit API provider checks now require the shared `openai` bucket instead of custom `cmp_*` provider tables.
  - Provider bucket drift is a failure for API mode instead of a warning.
- `tests/runtime/test_codex_shared_launcher.py`
  - Added/updated coverage for explicit API projection, OAuth-to-API preference, and non-shared provider bucket failures.

## Live Repair
- Command:
  - `python scripts/codex-interop-check.py --codex-home "$HOME\.codex" --cc-switch-db "$HOME\.cc-switch\cc-switch.db" --cockpit-home "$HOME\.antigravity_cockpit" --repair-current-cockpit-api-projection --prefer-cockpit-api-account --quick-launch`
- Backups:
  - `C:\Users\sciman\.codex\backups\config.toml.20260513_194648_cockpit-api-projection.bak`
  - `C:\Users\sciman\.antigravity_cockpit\backups\codex_accounts.json.20260513_194648_cockpit-api-projection.bak`
  - `C:\Users\sciman\.antigravity_cockpit\backups\codex_instances.json.20260513_194648_cockpit-api-projection.bak`
- Result:
  - live interop status: `pass`
  - active provider bucket: `openai`
  - history distribution: `openai=1697`
  - forced login method: `api`
  - active base URL: `http://35.213.82.91:8003/v1`
  - `auth.json` mode: `apikey`
  - Cockpit default instance: follows current account, no fixed bind account

## Follow-up Repair
- Trigger:
  - After Cockpit switched to API mode and Codex App could see history again, the App showed `Reconnecting`; Codex CLI could connect, but picker/history behavior still diverged between paths.
- Command:
  - `python scripts\codex-interop-check.py --codex-home "$HOME\.codex" --cc-switch-db "$HOME\.cc-switch\cc-switch.db" --cockpit-home "$HOME\.antigravity_cockpit" --quick-launch --repair-current-cockpit-api-projection --prefer-cockpit-api-account`
- Backups:
  - `C:\Users\sciman\.codex\backups\config.toml.20260513_202404_cockpit-api-projection.bak`
  - `C:\Users\sciman\.codex\backups\auth.json.20260513_202404_cockpit-api-projection.bak`
  - `C:\Users\sciman\.antigravity_cockpit\backups\codex_accounts.json.20260513_202404_cockpit-api-projection.bak`
  - `C:\Users\sciman\.antigravity_cockpit\backups\codex_instances.json.20260513_202404_cockpit-api-projection.bak`
- Result:
  - Cockpit `current_account_id`: `codex_apikey_8b8853f15e823dc53bd156163035bc78`
  - `config.toml`: `forced_login_method = "api"`, `model_provider = "openai"`, `openai_base_url = "http://35.213.82.91:8003/v1"`
  - `auth.json`: API-key shaped and aligned with Cockpit current API account.
  - `codex_instances.json`: `followLocalAccount = true`, `bindAccountId = null`
  - history distribution: dominant `openai`; one stray `codex_local_access` thread is treated as `warn`, not shared-history failure.
- Connectivity:
  - `codex login status`: API-key login.
  - relay `/v1/models`: `200`.
  - official `https://api.openai.com/v1/models` with the same key: `401`, confirming the key is relay-scoped.
  - `codex debug models`: succeeded.
  - `codex exec --ephemeral --skip-git-repo-check ... "Reply exactly: CODEX_API_OK"`: returned `CODEX_API_OK`.
- Fresh verification:
  - `python scripts\codex-interop-check.py --codex-home "$HOME\.codex" --cc-switch-db "$HOME\.cc-switch\cc-switch.db" --cockpit-home "$HOME\.antigravity_cockpit" --quick-launch`: `status=attention` only because `codex_thread_provider_distribution=warn`; `distribution={"openai":1698,"codex_local_access":1}`, `tolerated_unexpected_count=16`.
  - `codex login status`: `Logged in using an API key`.
  - relay `/v1/models` with the current `auth.json` key: `200`.
  - official `https://api.openai.com/v1/models` with the same key: `401`.
  - `codex debug models`: succeeded.
  - `codex exec --ephemeral --skip-git-repo-check --output-last-message .runtime\codex-api-smoke-last-message-followup.txt "Reply exactly: CODEX_API_OK"`: exit code `0`, final message `CODEX_API_OK`.
- Residual:
  - The same `codex exec` stderr reproduced the App symptom: `failed to connect to websocket: HTTP error: 404 Not Found, url: ws://35.213.82.91:8003/v1/responses`, followed by `ERROR: Reconnecting...`.
  - Fresh stderr repeated `ERROR: Reconnecting... 2/5` through `ERROR: Reconnecting... 5/5` while still completing over the non-WebSocket path.
  - This is not an HTTP Responses outage: direct `POST /v1/responses` and `POST /responses` both returned `200`.
  - The narrower failure is WebSocket handshake routing: an Upgrade probe to `/v1/responses` returned `404`, and an Upgrade probe to `/responses` returned `200` instead of `101 Switching Protocols`.
  - A custom non-built-in probe provider with `supports_websockets=false` avoids the retry noise, but would use a separate history bucket. It was not made live because shared App picker/history continuity is the higher-priority invariant.

## Final Repair
- Correction:
  - Treating built-in `openai` as mandatory for API mode was too narrow. The actual invariant is that the active provider bucket and `state_5.sqlite.threads.model_provider` must match.
  - Because Codex 0.130 exposes `supports_websockets=false` only on custom `model_providers.<id>`, the durable API relay shape is provider-first: use Cockpit API provider `cmp_1778165666417_1`, disable WebSocket on that provider, and migrate current local history into that same bucket.
- Live changes:
  - `C:\Users\sciman\.codex\config.toml`: top-level `model_provider = "cmp_1778165666417_1"` and `[model_providers.cmp_1778165666417_1]` with `base_url = "http://35.213.82.91:8003/v1"`, `wire_api = "responses"`, `requires_openai_auth = false`, `supports_websockets = false`.
  - `C:\Users\sciman\.antigravity_cockpit\codex_model_providers.json`: provider `cmp_1778165666417_1` now records `wire_api = "responses"`, `requires_openai_auth = false`, and `supports_websockets = false`.
  - `C:\Users\sciman\.codex\state_5.sqlite`: `threads.model_provider` migrated from `openai/codex_local_access` to `cmp_1778165666417_1`.
- Backups:
  - `C:\Users\sciman\.codex\backups\config.toml.20260513_205630_api-custom-provider-no-ws.bak`
  - `C:\Users\sciman\.antigravity_cockpit\backups\codex_model_providers.json.20260513_205630_api-custom-provider-no-ws.bak`
  - `C:\Users\sciman\.codex\backups\state_5.sqlite.20260513_205630_api-custom-provider-no-ws.bak`
- Verification:
  - `codex exec --ephemeral --skip-git-repo-check --output-last-message .runtime\codex-final-api-provider-no-ws.txt "Reply exactly: FINAL_NO_WS_OK"`: exit code `0`, final message `FINAL_NO_WS_OK`, no `websocket`, `Reconnecting`, or `404` output.
  - `python scripts\codex-interop-check.py --codex-home "$HOME\.codex" --cc-switch-db "$HOME\.cc-switch\cc-switch.db" --cockpit-home "$HOME\.antigravity_cockpit" --quick-launch`: `status=pass`, `distribution={"cmp_1778165666417_1":1699}`, active provider and expected provider both `cmp_1778165666417_1`.
  - `python -m unittest tests.runtime.test_codex_shared_launcher`: `OK`, 20 tests.
  - Syntax check via `compile(Path('scripts/codex-interop-check.py').read_text(...), ..., 'exec')`: `syntax_ok`; direct `py_compile` was blocked by a transient Windows `__pycache__` access-denied lock.
  - `git diff --check`: no whitespace errors; CRLF normalization warnings only.

## Verification
- `python -m unittest tests.runtime.test_codex_shared_launcher`
  - result: `OK`, 20 tests
- `python scripts/codex-interop-check.py --codex-home "$HOME\.codex" --cc-switch-db "$HOME\.cc-switch\cc-switch.db" --cockpit-home "$HOME\.antigravity_cockpit" --quick-launch`
  - result: `pass`
- `codex exec --json -C "D:\CODE\governed-ai-coding-runtime" --output-last-message .runtime\codex-api-smoke-last-message.txt "Reply exactly: CODEX_API_OK"`
  - exit code: `0`
  - final message: `CODEX_API_OK`
  - observed residual: relay WebSocket `GET /v1/responses` returned `404`, then Codex fell back and completed successfully.
- `python -m unittest tests.runtime.test_codex_shared_launcher.CodexSharedLauncherTests.test_interop_checker_warns_for_single_stray_provider_thread tests.runtime.test_codex_shared_launcher.CodexSharedLauncherTests.test_interop_checker_fails_when_any_active_thread_uses_non_shared_provider`
  - result: `OK`, 2 tests
  - purpose: single stray provider thread is a warning when the dominant expected bucket remains `openai`; real non-shared provider drift still fails.
- `python -m py_compile scripts\codex-interop-check.py`
  - result: `OK`
- `git diff --check`
  - result: no whitespace errors; PowerShell reported CRLF normalization warnings only.

## Residual Risk
- Official Codex config supports `openai_base_url` for the built-in `openai` provider.
- Official Codex config exposes `supports_websockets` only under custom `model_providers.<id>`, and built-in provider IDs such as `openai` are reserved.
- Therefore, using built-in `openai` plus `openai_base_url` can still produce WebSocket retry noise when a relay serves HTTP Responses but does not complete the Codex Responses WebSocket handshake at the URL Codex derives from `openai_base_url`.
- The current working repair keeps App/picker visibility by moving the local history bucket to the active custom API provider instead of keeping API sessions in the built-in `openai` bucket.
- If the user switches back to an OAuth/ChatGPT account, the same projection logic must move the active history bucket back to `openai` or the picker will again appear split by provider.

## Guard Audit
- Question: could an existing guard overwrite or break the final API custom-provider repair?
- Runtime status:
  - `Get-CimInstance Win32_Process ... codex-cockpit|interop-check|switch-guard`: only `serve-operator-ui.py` matched under this repo; no guard/checker worker was running.
  - `Get-ScheduledTask ... codex|cockpit|governed|interop|guard`: only `GovernedRuntimeOperatorUi-8770` matched; `codex-cockpit-switch-guard` was absent.
  - `pwsh -File scripts\Start-CodexCockpitSwitchGuard.ps1 -Status`: `task_state=not_installed`, `process_count=0`.
  - `state_5.sqlite` trigger query: `trigger_count=0`.
  - `C:\Users\sciman\.codex\log\codex-cockpit-switch-guard.jsonl` last write remained `2026-05-12 00:13:24`, so the old guard log was historical.
- Source status at the time of the guard audit:
  - Repo `scripts\codex-cockpit-switch-guard.py` was deprecated and performed no repair.
  - Repo `scripts\Start-CodexCockpitSwitchGuard.ps1` blocked `-InstallTask`, `-Start`, and `-RunWorker`.
  - Repo `scripts\codex-interop-check.py --apply` is blocked/deprecated; `--migrate-provider-bucket` is blocked/deprecated; `ensure_codex_provider_bucket_triggers` returns `codex_provider_bucket_triggers_deprecated`.
  - The only allowed write path is explicit `--repair-current-cockpit-api-projection`, which projects the selected Cockpit API account and migrates `threads.model_provider` to that account's `api_provider_id`.
- Dormant installed-copy risk found and neutralized:
  - Before this audit, `C:\Users\sciman\.codex\scripts\codex-cockpit-switch-guard.py` and `C:\Users\sciman\.codex\scripts\codex-interop-check.py` were stale installed copies that still contained the historical `codex_provider_bucket_triggers_ensured` path.
  - Synced current safe repo copies to:
    - `C:\Users\sciman\.codex\scripts\codex-cockpit-switch-guard.py`
    - `C:\Users\sciman\.codex\scripts\codex-interop-check.py`
    - `C:\Users\sciman\.codex\scripts\Start-CodexCockpitSwitchGuard.ps1`
  - Backups:
    - `C:\Users\sciman\.codex\scripts\codex-cockpit-switch-guard.py.bak-20260513_211225-guard-neutralize`
    - `C:\Users\sciman\.codex\scripts\codex-interop-check.py.bak-20260513_211225-guard-neutralize`
    - `C:\Users\sciman\.codex\scripts\Start-CodexCockpitSwitchGuard.ps1.bak-20260513_211225-guard-neutralize`
- Post-sync verification:
  - Installed scripts search now shows only `codex_provider_bucket_triggers_deprecated`, `guard is deprecated`, and `Project-managed Codex/Cockpit interop repair is disabled`; no installed live script contains `codex_provider_bucket_triggers_ensured`.
  - Installed guard status: `task_state=not_installed`, `process_count=0`.
  - SQLite trigger query: `trigger_count=0`.
  - Installed checker read-only quick launch: `status=pass`, `distribution={"cmp_1778165666417_1":1699}`, active provider and expected provider both `cmp_1778165666417_1`.

## Project Hardening
- Root-cause summary:
  - App history visibility is provider-bucketed by `state_5.sqlite.threads.model_provider`.
  - API relay connectivity on this host needs a custom provider because `supports_websockets=false` cannot be applied to the built-in `openai` provider.
  - The correct invariant is not "API must stay in the built-in `openai` bucket"; it is "active provider, Cockpit `api_provider_id`, custom provider metadata, and `threads.model_provider` must match."
  - Existing historical guards were unsafe because they could create SQLite provider triggers or run generic bucket repair outside the current account projection.
- Fixed policy now documented in:
  - `docs/runbooks/codex-cockpit-api-provider-repair.md`
  - `README.md`
  - `README.zh-CN.md`
  - `docs/quickstart/ai-coding-usage-guide.md`
  - `docs/quickstart/ai-coding-usage-guide.zh-CN.md`
  - `docs/product/codex-cli-app-integration-guide.md`
  - `docs/product/codex-cli-app-integration-guide.zh-CN.md`
- Source hardening:
  - `scripts/codex-interop-check.py` stale reasons no longer say API mode must preserve the built-in `openai` bucket.
  - `tests/runtime/test_codex_cockpit_switch_guard.py` asserted the old guard was deprecated and unreachable instead of expecting old watch-loop behavior.
- 2026-05-13 follow-up hardening after API/OAuth symmetric switch failures:
  - Reintroduced `scripts/codex-cockpit-switch-guard.py` as a narrow current-account projection guard.
  - The new guard only invokes `codex-interop-check.py --quick-launch --repair-current-cockpit-account-projection`.
  - It does not call generic `--apply`, does not call `--migrate-provider-bucket`, does not create SQLite triggers, and does not launch/stop/kill Codex.
  - `scripts\Start-CodexCockpitSwitchGuard.ps1` can now install/start the guard as a hidden user scheduled task or process fallback.
  - `scripts\operator.ps1 -Action CodexInteropRepair` now exposes the same explicit current-account projection as an operator action.

## Rollback
- Repo code: revert the changes to `scripts/codex-interop-check.py` and `tests/runtime/test_codex_shared_launcher.py`.
- Live local state: restore the backup files listed above.
