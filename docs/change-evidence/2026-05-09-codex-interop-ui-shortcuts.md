# 2026-05-09 Codex interop UI shortcuts

- rule_id: R8
- risk: medium, user-local shortcut installation is persistent but explicit and backed by dry-run/check commands
- landing: `scripts/operator.ps1`, `run.ps1`, `scripts/Optimize-CodexLocal.ps1`, Operator UI, tests
- destination: make Codex / CC Switch / Cockpit Tools shared-history interop check available from the 8770 UI and from local shortcut commands after third-party tool updates

## Commands

- `python -m unittest tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_operator_codex_interop_check_is_available_as_dry_run tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_operator_codex_local_optimize_is_available_as_dry_run tests.runtime.test_operator_ui.OperatorUiTests.test_operator_ui_interactive_mode_renders_actions_and_ref_buttons tests.runtime.test_operator_ui.OperatorUiTests.test_operator_ui_translation_keys_stay_in_sync tests.runtime.test_codex_shared_launcher.CodexSharedLauncherTests.test_optimizer_installs_interop_shortcuts_when_switcher_install_is_enabled`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\operator.ps1 -Action CodexInteropCheck -DryRun`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File run.ps1 codex-interop -DryRun`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Optimize-CodexLocal.ps1 -Apply`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\operator.ps1 -Action CodexInteropCheck`
- `codex-interop-check`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\operator-ui-service.ps1 -Action Restart -UiLanguage zh-CN -Port 8770`
- Browser verification at `http://127.0.0.1:8770/?lang=zh-CN`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\build-runtime.ps1`
- `python -m unittest tests.runtime.test_operator_entrypoint tests.runtime.test_operator_ui tests.runtime.test_codex_shared_launcher`
- `python -m py_compile scripts\serve-operator-ui.py scripts\codex-interop-check.py`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check RuntimeQuick`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Contract`

## Evidence

- `CodexInteropCheck` is available as a read-only operator action and `.\run.ps1 codex-interop` alias.
- The 8770 Codex panel renders `检查共享历史互操作`; clicking it ran `codex_interop_check` with `exit_code: 0`.
- `Optimize-CodexLocal.ps1 -Apply` installed `codex-interop-check.cmd` and `codex-interop-repair.cmd` under `C:\Users\sciman\.local\bin`.
- `codex-interop-check` resolved from PATH and returned `pass`.
- Current real interop status is `pass` for CC Switch common sqlite/log/history, current provider storage, Cockpit account inventory, Cockpit provider inventory, and Cockpit shared instance state.
- Focused tests, build, RuntimeQuick, and Contract gates passed.

## Rollback

- Revert the listed repo files from git history.
- Remove `C:\Users\sciman\.local\bin\codex-interop-check.cmd`, `C:\Users\sciman\.local\bin\codex-interop-repair.cmd`, and `C:\Users\sciman\.codex\scripts\codex-interop-check.py` if the local shortcut installation must be undone.
- Restore `C:\Users\sciman\.codex\config-backups\config-20260509-125813.toml` if the final local optimizer apply must be undone.
