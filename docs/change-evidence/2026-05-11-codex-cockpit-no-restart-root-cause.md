# 2026-05-11 Codex/Cockpit No-Restart Root Cause

## Goal

Prevent Cockpit Tools Codex account/API switching from disconnecting the running Codex App UI, causing `Reconnecting` or an empty history view.

## Root Cause

The repeated failure was not caused by the local Codex history database being emptied. The live SQLite history still had all active threads in the shared `openai` provider bucket.

The failing switch path was Cockpit process management:

- `launchMode=app` lets Cockpit raw-start Codex App through the Windows Store entry after a switch.
- The attempted `launchMode=cli` workaround avoided the Store raw-start, but Cockpit then entered `CodexWakeup[CLI]` and logged `当前系统暂不支持生成 Codex CLI 启动命令`.
- Cockpit also logged `[AG Close] taskkill ...` after switching, which killed the Codex App/app-server process group. Codex Desktop logs then showed app-server transport disconnects and `Failed to parse MCP message` from `taskkill` output.
- `antigravity_dual_switch_no_restart_enabled = true` is not sufficient for Codex switching. The 2026-05-11 02:17-02:22 logs still show `[Codex Start] 启动策略=system-store-entry` and `[AG Close] taskkill` after Codex account switches while that flag is enabled.

This made the UI appear empty or stuck reconnecting even though `C:\Users\sciman\.codex\state_5.sqlite` still contained the history.

## Fix

- Keep `model_provider = "openai"` and shared history bucket behavior unchanged.
- Require Cockpit `config.json` to keep:
  - `codex_launch_on_switch = false`
  - `codex_restart_specified_app_on_switch = false`
  - `codex_specified_app_path = ""`
  - `antigravity_dual_switch_no_restart_enabled = true`
- Restore Cockpit default Codex instance launch mode from unsupported `cli` back to `app`, because `cli` is unsupported on this Windows host.
- Divert Cockpit's app launch target to a no-window no-op launcher:
  - `codex_app_path = "C:\Users\sciman\.local\bin\codex-cockpit-noop-launcher.exe"`
  - installer: `scripts/Install-CodexCockpitNoopLauncher.ps1`
  - backup: `C:\Users\sciman\.antigravity_cockpit\config.json.codex_noop_launcher.20260511-023141.bak`
- Extend `codex-interop-check.py` to fail closed on:
  - missing `antigravity_dual_switch_no_restart_enabled`
  - recent `[AG Close] taskkill` after a Codex switch
  - recent unsupported `CodexWakeup[CLI]` launch after a Codex switch
  - `defaultSettings.launchMode = "cli"`
  - any non-empty `defaultSettings.lastPid`
- Fix `codex-interop-check.py` so later Cockpit state writes no longer hide a recent bad `[Codex Start]` or `[AG Close] taskkill` event.
- Extend switch records to capture and print `antigravity_dual_switch_no_restart_enabled` and `codex_app_path`.

## Evidence

- Current live history check:
  - `state_5.sqlite` contains active threads in the shared provider bucket.
  - provider distribution is `openai:1639` in the latest quick check.
- Current saved snapshot:
  - `docs/change-evidence/codex-cockpit-snapshots/20260511-023305-after-noop-launcher-record-schema/record.json`
  - summary shows `cockpit no_restart: True`, `cockpit launchMode: app`, `cockpit app_path: C:\Users\sciman\.local\bin\codex-cockpit-noop-launcher.exe`, `model_provider: openai`.
- Current interop dry-run:
  - `python scripts\codex-interop-check.py --codex-home C:\Users\sciman\.codex --cc-switch-db C:\Users\sciman\.cc-switch\cc-switch.db --cockpit-home C:\Users\sciman\.antigravity_cockpit --quick-launch`
  - result after correcting the detector: `status = fail` because the last real Cockpit switch at `2026-05-11T02:22:34+08:00` already logged Store raw-start and taskkill. A new post-fix switch is required to prove whether the no-op app path blocks that path.
- Targeted tests:
  - `python -m unittest tests.runtime.test_codex_cockpit_switch_trace tests.runtime.test_codex_shared_launcher.CodexSharedLauncherTests.test_interop_checker_detects_recent_cockpit_raw_start_after_switch tests.runtime.test_codex_shared_launcher.CodexSharedLauncherTests.test_interop_checker_does_not_mask_cockpit_raw_start_after_state_write tests.runtime.test_codex_shared_launcher.CodexSharedLauncherTests.test_interop_checker_repairs_cc_switch_shared_history_blockers`
  - result: `Ran 5 tests OK`.

## Rollback

Use git to revert the changed repo files if the guard behavior must be rolled back. Live Cockpit state can be restored from:

- `C:\Users\sciman\.antigravity_cockpit\backups\codex_instances.json.20260511_020833_cockpit_default_launch_mode.bak`
- `C:\Users\sciman\.antigravity_cockpit\config.json.codex_noop_launcher.20260511-023141.bak`
- the latest `config.json` backup created by `codex-interop-check.py` when `cockpit_restart_wrapper` repair runs.
