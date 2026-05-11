# Codex API Provider-First Interop Repair

- landing: `scripts/codex-interop-check.py`, `scripts/Start-CodexShared.ps1`, `scripts/Optimize-CodexLocal.ps1`, `scripts/lib/codex_local.py`, `scripts/operator.ps1`, `scripts/codex-cockpit-switch-guard.py`, `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui_text.py`
- destination: API accounts keep explicit custom `model_provider` buckets for connectivity; shared history is secondary and history bucket migration is explicit only.
- risk: medium; this changes local Codex/Cockpit projection policy. Live host repair was limited to file-level projection/guard state and installed-script refresh, with backups and without restarting Codex App.

## Root Cause

- The previous shared-history strategy normalized Cockpit API providers into the built-in `openai` provider bucket and routed relay endpoints through `openai_base_url`.
- That made the Codex App provider chip show `openai` instead of the custom provider name such as `35.213.82.91` or `RightCode`.
- The strategy also prevented `supports_websockets = false` from being applied to API relays because built-in provider IDs must not be overridden.
- Mixed `openai` bucket, API key auth, Cockpit account metadata, and custom relay base URLs can leave Codex App/CLI in an inconsistent startup state.
- A second live root cause was found in `codex-cockpit-switch-guard`: the installed guard previously called repair with `--migrate-provider-bucket` and logged `change_skipped_min_interval` for the same files Cockpit Tools rewrites during API switching. That made a rapid switch capable of leaving `auth.json` / `config.toml` only partially projected.
- A third live root cause was found in `C:\Users\sciman\.codex\config.toml`: custom API provider tables for `35.213.82.91` and `RightCode` still had `requires_openai_auth = true`, and `profiles.shared-cockpit-api` still pointed to the official `openai` provider/base URL. That explains "provider chip is 35.213.82.91 but connectivity still fails."

## Changes

- `codex-interop-check.py` now derives API account provider buckets from `api_provider_id` or API base URL and writes custom provider tables with:
  - `wire_api = "responses"`
  - `requires_openai_auth = false`
  - `supports_websockets = false`
- Existing history in another bucket is a warning for API accounts unless explicit migration is requested.
- `Start-CodexShared.ps1` no longer ignores custom API providers for history continuity and no longer runs pre-launch repair with `--migrate-provider-bucket`.
- `Optimize-CodexLocal.ps1 -Apply` defaults `MigrateProviderBucket` to `false`, and the installed `codex-interop-repair.cmd` no longer includes `--migrate-provider-bucket`.
- `scripts/lib/codex_local.py` now projects saved API profiles to a custom provider bucket instead of `model_provider = "openai"` plus `openai_base_url`.
- `scripts/operator.ps1` and `scripts/codex-cockpit-switch-guard.py` no longer call repair with `--migrate-provider-bucket`.
- `scripts/codex-cockpit-switch-guard.py` now delays short-interval changes and still repairs them; it no longer drops switch events via `change_skipped_min_interval`.
- `codex-interop-check.py` now normalizes all Cockpit API provider tables it can discover, even while the current account is OAuth, so saved API providers remain launchable after switching back from OAuth.
- `Save-CodexCockpitSwitchRecord.ps1` / `codex-cockpit-switch-trace.py` now include provider-first diagnostic fields in switch snapshots: Cockpit current account auth/provider/base URL, active provider `requires_openai_auth`, active provider `supports_websockets`, and `profiles.shared-cockpit-api` provider/base URL. Installed snapshot scripts were refreshed so both repo and installed entrypoints capture the same fields.
- `Optimize-CodexLocal.ps1 -Apply` preserves an active custom top-level `model_provider` and writes `profiles.shared-cockpit-api` to the custom provider when active.
- The 8770 operator UI text now says `检查 provider 互操作` / `应用 provider 优先优化`; the API save confirmation no longer says it will project into an `openai` shared-history bucket.
- Live installed scripts were refreshed from this repo:
  - `C:\Users\sciman\.codex\scripts\Start-CodexShared.ps1`
  - `C:\Users\sciman\.codex\scripts\codex-interop-check.py`
  - `C:\Users\sciman\.codex\scripts\codex-cockpit-switch-guard.py`
  - `C:\Users\sciman\.local\bin\codex-interop-repair.cmd`
- Installed-script backup: `C:\Users\sciman\.codex\backups\provider-first-install-20260511-222406`.
- Follow-up installed-script backup after fixing the guard skip/API profile normalization gap: `C:\Users\sciman\.codex\backups\provider-first-guard-fix-20260511-224409`.
- Snapshot command installed-script backups:
  - `C:\Users\sciman\.codex\backups\switch-record-snapshot-schema-20260511-231115`
  - `C:\Users\sciman\.codex\backups\switch-record-output-root-20260511-231317`
- Live Cockpit fixed-account binding was repaired from `followLocalAccount=false` and `bindAccountId=<oauth account>` to `followLocalAccount=true` and `bindAccountId=null`; backup: `C:\Users\sciman\.antigravity_cockpit\backups\codex_instances.json.20260511_222406_cockpit_follow_current_account.bak`.
- Live Codex `config.toml` and `auth.json` were re-projected for the currently selected OAuth account only; backups:
  - `C:\Users\sciman\.codex\backups\config.toml.20260511_222406_cockpit_provider.bak`
  - `C:\Users\sciman\.codex\backups\auth.json.20260511_222406_cockpit_auth.bak`
- Follow-up live projection normalized both saved API providers while keeping the active OAuth account intact:
  - `model_providers.cmp_1778165666417_1`: `base_url = "http://35.213.82.91:8003/v1"`, `requires_openai_auth = false`, `supports_websockets = false`
  - `model_providers.cmp_1778246510288_1`: `base_url = "https://right.codes/codex/v1"`, `requires_openai_auth = false`, `supports_websockets = false`
  - `profiles.shared-cockpit-api`: `model_provider = "cmp_1778165666417_1"`
  - backups:
    - `C:\Users\sciman\.codex\backups\config.toml.20260511_224409_cockpit_provider.bak`
    - `C:\Users\sciman\.codex\backups\auth.json.20260511_224409_cockpit_auth.bak`

## Verification

- `python -m py_compile scripts\lib\codex_local.py scripts\codex-interop-check.py`
- `python -m unittest tests.runtime.test_codex_local tests.runtime.test_codex_shared_launcher`
  - result: `Ran 53 tests ... OK`
- `python -m unittest tests.runtime.test_operator_entrypoint tests.runtime.test_operator_ui`
  - result: `Ran 44 tests ... OK`
- `python -m unittest tests.runtime.test_codex_local tests.runtime.test_codex_shared_launcher tests.runtime.test_operator_entrypoint tests.runtime.test_operator_ui`
  - result: `Ran 97 tests ... OK`
- `python -m unittest tests.runtime.test_codex_shared_launcher tests.runtime.test_codex_cockpit_switch_guard tests.runtime.test_operator_entrypoint tests.runtime.test_operator_ui tests.runtime.test_codex_local`
  - result: `Ran 101 tests ... OK`
- `python -m unittest tests.runtime.test_codex_shared_launcher tests.runtime.test_codex_cockpit_switch_guard`
  - result: `Ran 21 tests ... OK`
- `python -m unittest tests.runtime.test_codex_shared_launcher tests.runtime.test_codex_cockpit_switch_guard tests.runtime.test_codex_local tests.runtime.test_operator_entrypoint tests.runtime.test_operator_ui`
  - result: `Ran 103 tests ... OK`
- `python -m unittest tests.runtime.test_codex_cockpit_switch_trace tests.runtime.test_operator_entrypoint`
  - result: `Ran 39 tests ... OK`
- `python -m py_compile scripts\codex-cockpit-switch-trace.py`
  - result: pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Save-CodexCockpitSwitchRecord.ps1 -Label current-provider-first-snapshot-schema-v2 -Json`
  - result: saved `docs\change-evidence\codex-cockpit-snapshots\20260511-230954-current-provider-first-snapshot-schema-v2\record.json`; summary includes `codex_shared_cockpit_api_model_provider = "cmp_1778165666417_1"`.
- Installed snapshot entrypoint:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File "$HOME\.codex\scripts\Save-CodexCockpitSwitchRecord.ps1" -Label installed-current-provider-first-snapshot-schema-v2 -Json`
  - result: saved under repo `docs\change-evidence\codex-cockpit-snapshots\20260511-231329-installed-current-provider-first-snapshot-schema-v2\record.json`, not under `C:\Users\sciman\.codex\docs`.
- Latest full rerun after guard/profile fixes:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\build-runtime.ps1`: `OK python-bytecode`, `OK python-import`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Runtime`: `Completed 111 test files ... failures=0`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Contract`: pass through `OK functional-effectiveness`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\doctor-runtime.ps1`: pass with existing advisory `WARN codex-capability-degraded`
- `python -m py_compile scripts\codex-cockpit-switch-guard.py scripts\codex-interop-check.py scripts\lib\codex_local.py scripts\serve-operator-ui.py`
  - result: pass
- Live API probes using Cockpit API account keys:
  - `http://35.213.82.91:8003/v1/models`: HTTP 200, model_count 9
  - `https://right.codes/codex/v1/models`: HTTP 200, model_count 17
- `python scripts\codex-interop-check.py --codex-home "$HOME\.codex" --cc-switch-db "$HOME\.cc-switch\cc-switch.db" --cockpit-home "$HOME\.antigravity_cockpit" --apply --quick-launch`
  - before: fail on `cockpit_codex_instances_follow_current_account`
  - after: pass
- `python scripts\codex-interop-check.py --codex-home "$HOME\.codex" --cc-switch-db "$HOME\.cc-switch\cc-switch.db" --cockpit-home "$HOME\.antigravity_cockpit" --quick-launch`
  - result: pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Start-CodexCockpitSwitchGuard.ps1 -Status`
  - result: `healthy=true`, `process_count=1`, `process_ids=[33232]`, `task_name=codex-cockpit-switch-guard`
- Live config inspection:
  - `model_providers.cmp_1778165666417_1` has `requires_openai_auth = false` and `supports_websockets = false`
  - `model_providers.cmp_1778246510288_1` has `requires_openai_auth = false` and `supports_websockets = false`
  - `profiles.shared-cockpit-api` points to `model_provider = "cmp_1778165666417_1"`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\operator-ui-service.ps1 -Action Start -UiLanguage zh-CN -Port 8770`
  - result: `ready=true`, `stale=false`, url `http://127.0.0.1:8770/?lang=zh-CN`
- `Invoke-WebRequest http://127.0.0.1:8770/?lang=zh-CN`
  - result: HTTP 200; contains `检查 provider 互操作` and `应用 provider 优先优化`; does not contain old `检查共享历史互操作` or `应用共享历史优化`
- Installed-script scan:
  - `rg "migrate-provider-bucket|ignoring custom ModelProvider|must vary openai_base_url only|openai 共享历史桶|共享历史优化|共享历史互操作|shared-history" "$HOME\.codex\scripts" "$HOME\.local\bin\codex-interop-repair.cmd" -S`
  - result: only the explicit supported parser option `--migrate-provider-bucket` remains in `codex-interop-check.py`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - result: `OK python-bytecode`, `OK python-import`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - result after elevated local permission: `Completed 111 test files ... failures=0`, `OK runtime-unittest`, `OK runtime-service-parity`, `OK runtime-service-wrapper-drift-guard`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - result: pass; final checks included `OK functional-effectiveness`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  - result: pass with existing `WARN codex-capability-degraded`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Doctor`
  - result: `OK runtime-doctor`; existing `WARN codex-capability-degraded` remains advisory.
- `Invoke-WebRequest http://127.0.0.1:8770/api/codex/status?refresh_if_stale=1`
  - result: active profile is currently ChatGPT/OAuth `sciman.top@gmail.com`; saved API profile `api-35-213-82-91` is present but not active.

## Follow-up Root Cause: Native Cockpit Launch Was Blocked

- User-provided Cockpit dialog evidence showed Cockpit Tools has its own "Codex 会话不可见" recovery flow and can repair history visibility before launch.
- Historical Cockpit config backups show the pre-project path used native Cockpit launch semantics:
  - `2026-05-09 12:29:56`: `codex_launch_on_switch = true`, `codex_app_path = ""`, `antigravity_dual_switch_no_restart_enabled = false`
  - `2026-05-10 18:13:47`: `codex_launch_on_switch = true`, `codex_app_path = ""`, `antigravity_dual_switch_no_restart_enabled = false`
- The project later installed a no-op launcher and disabled Cockpit launch:
  - live before repair: `codex_app_path = "C:\Users\sciman\.local\bin\codex-cockpit-noop-launcher.exe"`
  - live before repair: `codex_launch_on_switch = false`
  - live before repair: `antigravity_dual_switch_no_restart_enabled = true`
- This means the earlier "block native Cockpit launch and repair outside it" strategy was wrong for this host. It could break Cockpit Tools' own session visibility recovery and explain why switching API no longer launched Codex App as it did before the shared-history work.

## Follow-up Changes

- `codex-interop-check.py` no longer treats native Cockpit launch-on-switch as a failure.
- `codex-interop-check.py --apply` now restores native Cockpit launch semantics:
  - removes `codex-cockpit-noop-launcher.exe` from `codex_app_path`
  - sets `codex_launch_on_switch = true`
  - sets `codex_restart_specified_app_on_switch = false`
  - clears `codex_specified_app_path`
  - sets `antigravity_dual_switch_no_restart_enabled = false`
- `Install-CodexCockpitNoopLauncher.ps1` is now a deprecated recovery wrapper that restores native launch instead of building/installing a no-op launcher.
- `README.md`, `README.zh-CN.md`, and `docs/quickstart/ai-coding-usage-guide.zh-CN.md` now state that Cockpit Tools owns native launch/recovery, while this project only repairs provider/auth projection and keeps API provider connectivity primary.
- `codex-interop-check.py` now detects saved Cockpit API provider table drift even while the current account is OAuth.

## Follow-up Live Evidence

- Installed-script backup before refreshing live copies:
  - `C:\Users\sciman\.codex\backups\native-cockpit-launch-20260511-234442`
- Live repair:
  - command: `python "$HOME\.codex\scripts\codex-interop-check.py" --codex-home "$HOME\.codex" --cc-switch-db "$HOME\.cc-switch\cc-switch.db" --cockpit-home "$HOME\.antigravity_cockpit" --apply --quick-launch`
  - before: failed on saved API provider `requires_openai_auth = true`, no-op launcher configured, `codex_launch_on_switch = false`, no-restart shim enabled, and fixed Cockpit account binding
  - after: pass
  - config backup: `C:\Users\sciman\.antigravity_cockpit\backups\config.json.20260511_234453_cockpit_restart_wrapper.bak`
  - instances backup: `C:\Users\sciman\.antigravity_cockpit\backups\codex_instances.json.20260511_234453_cockpit_follow_current_account.bak`
  - Codex config backup: `C:\Users\sciman\.codex\backups\config.toml.20260511_234453_cockpit_provider.bak`
- Live post-repair snapshot:
  - `docs/change-evidence/codex-cockpit-snapshots/20260511-234554-after-native-launch-restore/record.json`
  - summary: `codex_launch_on_switch = true`, `codex_app_path = ""`, `antigravity_dual_switch_no_restart_enabled = false`, `cockpit_follow_local_account = true`
- Live interop recheck:
  - command: `python "$HOME\.codex\scripts\codex-interop-check.py" --codex-home "$HOME\.codex" --cc-switch-db "$HOME\.cc-switch\cc-switch.db" --cockpit-home "$HOME\.antigravity_cockpit" --quick-launch`
  - result: pass
- Live guard:
  - command: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Start-CodexCockpitSwitchGuard.ps1 -Start`
  - status: `healthy = true`, `process_count = 1`, `process_ids = [25068]`
- Live API probes with each Cockpit API account's own key:
  - `http://35.213.82.91:8003/v1/models`: HTTP 200, model_count 9, first `gpt-5.2-codex`
  - `https://right.codes/codex/v1/models`: HTTP 200, model_count 17, first `codex-auto-review`
- Current saved provider table:
  - `model_providers.cmp_1778165666417_1`: `requires_openai_auth = false`, `supports_websockets = false`
  - `model_providers.cmp_1778246510288_1`: `requires_openai_auth = false`, `supports_websockets = false`
  - `profiles.shared-cockpit-api`: `model_provider = "cmp_1778165666417_1"`
- No Codex App restart/kill/launch was performed during this follow-up repair.

## Rollback

- Revert this evidence file and source/test changes from git history.
- Restore live installed scripts from `C:\Users\sciman\.codex\backups\provider-first-install-20260511-222406` if needed.
- For native-launch follow-up rollback, restore installed scripts from `C:\Users\sciman\.codex\backups\native-cockpit-launch-20260511-234442`.
- Restore live Cockpit/Codex projections from the timestamped backups listed above if needed.
- Do not run old installed `codex-interop-repair` or `Optimize-CodexLocal.ps1 -Apply` from a pre-fix install if API provider connectivity is the priority.
