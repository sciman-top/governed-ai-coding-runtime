# 2026-05-09 Codex Cockpit stale lastPid repair

## Goal
- Prevent repeated Codex CLI/App startup noise such as `没有找到进程 "33896"` after Cockpit Tools keeps a stale Codex App PID in `codex_instances.json`.

## Landing
- Current landing: `scripts/codex-interop-check.py`
- Durable destination: shared Codex/Cockpit pre-launch repair path invoked by `scripts/Start-CodexShared.ps1`
- Live synced copy: `C:\Users\sciman\.codex\scripts\codex-interop-check.py`

## Change
- Added `cockpit_codex_instances_last_pid_current` to detect Cockpit `defaultSettings.lastPid`.
- Added `cockpit_codex_stale_last_pid_cleared` to clear a missing process PID to JSON `null` during `--apply`.
- Kept live PID values untouched when the process still exists.

## Evidence
- `Get-CimInstance Win32_Process -Filter "ProcessId=33896"` returned no process.
- Historical session evidence mapped `33896` to the governed runtime operator UI process started by `scripts\operator-ui-service.ps1 -Action Restart -UiLanguage zh-CN -Port 8770`.
- Current Cockpit state has `C:\Users\sciman\.antigravity_cockpit\codex_instances.json` with `defaultSettings.lastPid = 33708`.
- `Get-CimInstance Win32_Process -Filter "ProcessId=33708"` shows a live `Codex.exe`, so the current value is valid and was not cleared.

## Verification
- `python -m py_compile scripts\codex-interop-check.py`
- `python -m unittest tests.runtime.test_codex_shared_launcher.CodexSharedLauncherTests.test_interop_checker_repairs_cc_switch_shared_history_blockers`
- `python -m unittest tests.runtime.test_codex_shared_launcher`
- `python C:\Users\sciman\.codex\scripts\codex-interop-check.py --codex-home C:\Users\sciman\.codex --cc-switch-db C:\Users\sciman\.cc-switch\cc-switch.db --cockpit-home C:\Users\sciman\.antigravity_cockpit --apply --migrate-provider-bucket`
- `codex-cockpit --version`

## Key Output
- Live repair status: `pass`
- Live lastPid check: `lastPid=33708`, `stale_lastPid=null`
- CLI launch wrapper probe: `interop_repair_status=pass`, `codex-cli 0.129.0`

## Rollback
- Revert `scripts/codex-interop-check.py`, `tests/runtime/test_codex_shared_launcher.py`, and this evidence file.
- If a live Cockpit `lastPid` was cleared unexpectedly, restore from `C:\Users\sciman\.antigravity_cockpit\backups\*cockpit_lastpid*.json`.
