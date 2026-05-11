# Disable Project Codex Interop for Clean Cockpit Switching

## Goal

Restore a clean Cockpit Tools -> Codex App path by disabling this repository's shared-history/openai-bucket/launcher interception chain. API provider connectivity is primary; shared history is secondary and must not force API accounts into the `openai` provider bucket.

## Source Attribution

- Cockpit Tools source inspected from `https://github.com/jlcodes99/cockpit-tools` at local clone `C:\Users\sciman\AppData\Local\Temp\cockpit-tools-src`.
- `src-tauri/src/modules/codex_account.rs` writes custom Codex providers as `model_provider = <provider_id>`, `wire_api = "responses"`, and `requires_openai_auth = true`. It does not write `forced_login_method`.
- `src-tauri/src/modules/codex_session_visibility.rs` implements Cockpit's own history visibility repair by reading the current `model_provider`, rewriting rollout provider metadata, and updating SQLite `threads.model_provider`. This is one-shot repair logic, not a persistent trigger.
- Local project logs showed this repository's guard previously called `codex-interop-check.py --apply --migrate-provider-bucket --quick-launch`, ensured `trg_threads_shared_provider_*` SQLite triggers, and installed/no-op launcher paths. That chain is owned by this repository, not Cockpit Tools.

## Changes

- Added `scripts/Disable-CodexProjectInterop.ps1`.
- Live apply disabled the scheduled task `codex-cockpit-switch-guard` and stopped only the matching guard Python worker.
- Restored Cockpit native launch settings:
  - `codex_app_path = ""`
  - `codex_launch_on_switch = true`
  - `codex_restart_specified_app_on_switch = false`
  - `antigravity_dual_switch_no_restart_enabled = false`
  - default instance follows current Cockpit account with `launchMode = "app"`
- Removed project-installed SQLite provider bucket triggers:
  - `trg_threads_shared_provider_after_insert`
  - `trg_threads_shared_provider_after_update`
- Disabled project-installed shortcuts/wrappers in `C:\Users\sciman\.local\bin` by renaming them to `.disabled-20260512-001340`.
- Updated shell-risk contract allowlist for the new script's bounded `Move-Item` use after adding explicit source/target containment under the configured bin directory.

## Live Evidence

- Apply record: `docs/change-evidence/disable-codex-project-interop-20260512-001340.json`
- Runtime reload diagnostic record: `docs/change-evidence/disable-codex-project-interop-20260512-003352.json`
- Post-reload diagnostic record: `docs/change-evidence/disable-codex-project-interop-20260512-003749.json`
- Backup root: `C:\Users\sciman\.codex\backups\disable-project-interop-20260512-001340`
- Snapshot after cleanup: `docs/change-evidence/codex-cockpit-snapshots/20260512-001509-after-disable-project-interop/record.json`
- Snapshot before Cockpit Tools reload: `docs/change-evidence/codex-cockpit-snapshots/20260512-003640-before-cockpit-tools-reload/record.json`
- Snapshot after Cockpit Tools reload: `docs/change-evidence/codex-cockpit-snapshots/20260512-003655-after-cockpit-tools-reload/record.json`
- Snapshot summary showed:
  - current Cockpit account `auth_mode = oauth`
  - `codex_launch_on_switch = true`
  - `codex_app_path = ""`
  - `antigravity_dual_switch_no_restart_enabled = false`
  - `cockpit_follow_local_account = true`
  - `cockpit_launch_mode = app`
  - `changed_files_within_watch = []`
- Guard status after cleanup:
  - scheduled task `codex-cockpit-switch-guard` is `Disabled`
  - no real `codex-cockpit-switch-guard.py` worker process remains
- SQLite trigger query returned `[]`.
- API endpoint probes:
  - `http://35.213.82.91:8003/v1/models` returned HTTP `200`, first model `gpt-5.2-codex`
  - `https://right.codes/codex/v1/models` returned HTTP `200`, first model `codex-auto-review`
- Current Cockpit Tools source keeps `config.json` in process memory via `modules/config.rs` `RUNTIME_STATE: OnceLock<RwLock<RuntimeState>>`; `get_user_config()` reads memory, and only Cockpit's own `save_user_config()` updates both memory and disk.
- The running Cockpit Tools process `PID 14588` still used stale in-memory launch settings after the disk repair. Its log at `2026-05-12T00:29:37.960246300+08:00` said `已关闭切换 Codex 时自动启动 Codex App`, so native launch was not attempted.
- `scripts/Disable-CodexProjectInterop.ps1` now emits `cockpit_runtime_reload_required` when Cockpit is running, because external disk repair alone cannot hot-load Cockpit's cached settings. Remediation is to reload Cockpit Tools or toggle/save the Cockpit UI setting for Codex launch-on-switch.
- After explicit user authorization, only Cockpit Tools was reloaded. Old PID `14588` exited; the new running `cockpit-tools.exe` PID is `8028`. Codex App was not stopped or restarted.
- Post-reload snapshot showed:
  - `cockpit_current_account_auth_mode = "apikey"`
  - `cockpit_current_account_api_provider_name = "35.213.82.91"`
  - `cockpit_current_account_base_url = "http://35.213.82.91:8003/v1"`
  - `codex_launch_on_switch = true`
  - `codex_app_path = ""`
  - `antigravity_dual_switch_no_restart_enabled = false`
- Post-reload diagnostic now reports `cockpit_runtime_config_reload_not_currently_indicated`; no disabled native-launch log was observed after the latest Cockpit Tools process start.

## Verification

- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Disable-CodexProjectInterop.ps1 -DisableProjectShortcuts`
  - Result: dry-run pass after apply; all project shortcuts absent and no triggers remain.
- `python scripts\verify-shell-risk-contract.py --json`
  - Result: `status = pass`, `finding_count = 0`, `stale_allowlist_count = 0`.
- `python -m unittest tests.runtime.test_shell_risk_contract tests.runtime.test_codex_local tests.runtime.test_codex_cockpit_switch_guard tests.runtime.test_codex_cockpit_switch_trace tests.runtime.test_codex_shared_launcher`
  - Result: `Ran 67 tests`, `OK`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Disable-CodexProjectInterop.ps1`
  - Result: dry-run pass with `cockpit_runtime_reload_required`, `process_ids = [14588]`, and latest disabled-launch log evidence.
- `python -m unittest tests.runtime.test_shell_risk_contract tests.runtime.test_codex_shared_launcher`
  - Result: `Ran 23 tests`, `OK`.
- Post-reload `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Disable-CodexProjectInterop.ps1`
  - Result: dry-run pass with `cockpit_runtime_config_reload_not_currently_indicated`, `process_ids = [8028]`, and `latest_process_start = 2026-05-12T00:36:49.1399920+08:00`.
- Post-reload `python -m unittest tests.runtime.test_shell_risk_contract tests.runtime.test_codex_shared_launcher`
  - Result: `Ran 23 tests`, `OK`.
- Post-reload `python scripts\verify-shell-risk-contract.py --json`
  - Result: `status = pass`, `finding_count = 0`, `stale_allowlist_count = 0`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Runtime`
  - Result: `Completed 111 test files`, `failures=0`, `OK runtime-unittest`, `OK runtime-service-parity`, `OK runtime-service-wrapper-drift-guard`.

## Rollback

- Restore files from `C:\Users\sciman\.codex\backups\disable-project-interop-20260512-001340`.
- Rename `.disabled-20260512-001340` files in `C:\Users\sciman\.local\bin` back to their original names if the project wrappers are intentionally re-enabled.
- Re-enable the scheduled task only if the guard is redesigned to be provider-first and not bucket-forcing:
  - `Enable-ScheduledTask -TaskName codex-cockpit-switch-guard`

## Residual Risk

- This cleanup did not launch or restart Cockpit Tools or Codex App by design. The verified state is file/config/process/API reachability plus Cockpit log attribution.
- If Cockpit Tools is already running while disk config is repaired, it can keep stale in-memory `codex_launch_on_switch=false`. Native launch will remain disabled until Cockpit reloads settings through its UI or process restart.
- Cockpit Tools current source still writes `requires_openai_auth = true` for custom Codex providers. If clean Cockpit switching still fails after this repository's interference is disabled, the next likely root is Cockpit's custom provider projection or Codex App's interpretation of that field.
