# 2026-05-08 Codex shared history local optimize

- rules: R1/R6/R8, E4/E6
- risk: medium, user-local Codex config is persisted but backed up before write
- landing: `scripts/Optimize-CodexLocal.ps1` and `scripts/Start-CodexShared.ps1`
- destination: one shared `~/.codex` state root for Codex CLI/App coding history, with auth/provider switching inside that root

## Commands

- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/Optimize-CodexLocal.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/Optimize-CodexLocal.ps1 -Apply`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action CodexLocalOptimize -DryRun`
- `python -m unittest tests.runtime.test_codex_shared_launcher tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_root_run_entrypoint_help_succeeds tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_operator_entrypoint_help_succeeds tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_operator_codex_local_optimize_is_available_as_dry_run`
- `python -m unittest tests.runtime.test_operator_ui tests.runtime.test_operator_entrypoint tests.runtime.test_codex_shared_launcher`
- `python -m unittest tests.runtime.test_codex_local tests.runtime.test_codex_shared_launcher tests.runtime.test_operator_entrypoint`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check RuntimeQuick`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator-ui-service.ps1 -Action Restart -UiLanguage zh-CN`
- `Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:8770/?lang=zh-CN'`
- `run_operator_action({'action': 'codex_local_optimize', 'dry_run': True, 'language': 'zh-CN', 'target': '__all__'})`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

## Evidence

- Dry-run reports `cc_switch_installed=true` and `cockpit_tools_installed=true`.
- Apply wrote `C:\Users\sciman\.codex\config.toml`, backed up the previous config to `C:\Users\sciman\.codex\config-backups\config-20260508-225012.toml`, and installed `codex-account.cmd`, `codex-shared.cmd`, `codex-shared-exec.cmd`, and `codex-shared-app.cmd`.
- Live config readback shows `sqlite_home = "C:\\Users\\sciman\\.codex"`, `log_dir = "C:\\Users\\sciman\\.codex\\log"`, `[history] persistence = "save-all"`, and shared profiles; `disable_response_storage` is absent.
- `scripts/operator.ps1 -Action CodexLocalOptimize -DryRun` forwards to `scripts/Optimize-CodexLocal.ps1 -Apply`; no extra short root alias is exposed.
- Operator UI Codex panel exposes `data-action='codex_local_optimize'`, backed by the same `CodexLocalOptimize` action; live `http://127.0.0.1:8770/?lang=zh-CN` HTML contains `应用共享历史优化`.
- UI backend dry-run returns exit code `0` and runs `run.ps1 CodexLocalOptimize ... -DryRun`, which forwards to `scripts/Optimize-CodexLocal.ps1 -Apply` under operator dry-run.
- Unit tests cover shared history config generation, launcher surfaces, root help, operator help, and operator dry-run.
- Official Codex config reference confirms `history.persistence`, `sqlite_home`, `log_dir`, `profiles.<name>`, and `model_provider` are supported config keys.
- Full gate result: build pass, Runtime pass, Contract pass, doctor pass with existing `WARN codex-capability-degraded` for native attach status handshake.

## Compatibility

- `Cockpit Tools` remains responsible for account/API projection into the default Codex home.
- `CC Switch` remains responsible for Codex provider switching.
- This runtime fixes the shared state root and launch convention; isolated `CODEX_HOME` remains the rollback or privacy boundary.

## Rollback

- Restore the latest `C:\Users\sciman\.codex\config-backups\config-*.toml`.
- Remove `C:\Users\sciman\.local\bin\codex-shared*.cmd` if the launchers are no longer wanted.
- Revert `scripts/Optimize-CodexLocal.ps1`, `scripts/Start-CodexShared.ps1`, `scripts/operator.ps1`, Operator UI updates, README updates, and tests from git history.
