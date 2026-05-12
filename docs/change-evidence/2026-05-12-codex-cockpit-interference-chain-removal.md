# Codex/Cockpit Interference Chain Removal

- rule_id: `local-codex-cockpit-startup-boundary`
- risk: `medium`
- landing:
  - `scripts/Optimize-CodexLocal.ps1`
  - `scripts/Start-CodexShared.ps1`
  - `scripts/operator.ps1`
  - `scripts/serve-operator-ui.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui*.py`
  - `run.ps1`
  - `scripts/Disable-CodexProjectInterop.ps1`
- timestamp: `2026-05-12`

## Root Cause

The local symptom was reproducible as a project-owned interference chain rather than a single bad `config.toml` value:

- `Optimize-CodexLocal.ps1` still contained a live path that wrote Codex config, profiles, provider state, trusted projects, and project launcher shims.
- `Start-CodexShared.ps1` still contained a live path that projected Cockpit auth/provider state and wrapped Codex CLI/App startup.
- `operator.ps1`, Operator UI, and quickstart docs still exposed these paths through `CodexLocalOptimize`, `codex_local_optimize`, shared launchers, and Cockpit compatibility buttons.
- Operator UI still exposed Codex write actions for auth/profile switching, API profile save, Cockpit import, snapshot sync, and snapshot delete.
- `Disable-CodexProjectInterop.ps1` did not yet disable `codex-account.cmd`, so an old account-switching shim could remain on PATH even after project launcher cleanup.

This made it possible for a user-visible button or shortcut to re-enter project-managed Codex/Cockpit mutation after Cockpit Tools or the official Codex CLI had already established the correct OAuth state.

## Changes

- Replaced `Optimize-CodexLocal.ps1` with a compatibility stub that returns `status=deprecated`, `changed=false`, and exits `2`.
- Replaced `Start-CodexShared.ps1` with a compatibility stub that refuses to project Cockpit auth, rewrite Codex config, stop/restart Codex App, or wrap Codex startup.
- Removed `CodexLocalOptimize` from `scripts/operator.ps1`.
- Removed `codex_local_optimize` from Operator UI backend allowlist and UI rendering.
- Removed Codex write controls/routes from Operator UI:
  - account switch
  - active snapshot sync
  - active snapshot save
  - API profile save
  - Cockpit account import
  - payload import
  - auth profile delete
- Kept only read-only Codex UI functions:
  - local status refresh
  - optional online usage refresh
  - provider/account probe
  - history metadata query
  - switch record capture
  - interop check
  - deprecated guard status
- Updated `README.md`, `docs/README.md`, and `docs/quickstart/ai-coding-usage-guide.zh-CN.md` to state that Codex CLI/App startup and Cockpit launch state belong to official Codex/Cockpit controls, not this repository.
- Extended `Disable-CodexProjectInterop.ps1 -DisableProjectShortcuts` to disable `codex-account.cmd` and `codex-account.ps1`.

## Live Cleanup

Command:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Disable-CodexProjectInterop.ps1 -Apply -DisableProjectShortcuts
```

Key output:

- evidence: `docs/change-evidence/disable-codex-project-interop-20260512-215910.json`
- disabled:
  - `C:\Users\sciman\.local\bin\codex.cmd`
  - `C:\Users\sciman\.local\bin\codex.ps1`
  - `C:\Users\sciman\.local\bin\codex-account.cmd`
- absent after cleanup:
  - `codex-cockpit*.cmd`
  - `codex-shared*.cmd`
  - `codex-relay*.cmd`
  - `codex-interop-repair.cmd`
  - `codex-switch-guard*.cmd`
- backup root: `C:\Users\sciman\.codex\backups\disable-project-interop-20260512-215910`

Post-cleanup PATH evidence:

- `Get-Command codex -All` now resolves first to `C:\Users\sciman\AppData\Roaming\npm\codex.ps1`, then official/native Codex paths.
- `Get-Command codex-account -All` returns no command.

## Verification

Commands:

```powershell
python -m unittest tests.runtime.test_codex_shared_launcher tests.runtime.test_operator_entrypoint tests.runtime.test_operator_ui
python -m unittest tests.runtime.test_codex_shared_launcher tests.runtime.test_operator_entrypoint tests.runtime.test_operator_ui tests.runtime.test_codex_cockpit_switch_guard tests.runtime.test_codex_cockpit_switch_trace
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\build-runtime.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Runtime
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Contract
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\doctor-runtime.ps1
python scripts\codex-interop-check.py --codex-home "$HOME\.codex" --cc-switch-db "$HOME\.cc-switch\cc-switch.db" --cockpit-home "$HOME\.antigravity_cockpit" --quick-launch
codex exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox "请只运行一个 PowerShell 命令输出当前目录：Get-Location；然后输出 OK；不要修改文件。"
```

Results:

- targeted unit tests: `67` tests passed.
- build: `OK python-bytecode`, `OK python-import`.
- runtime gate: `112` test files passed; `failures=0`.
- contract gate: passed.
- doctor: exit `0`; residual `WARN codex-capability-degraded` only.
- interop check: `status=pass`.
- `codex exec`: reached official Codex CLI with `workdir: D:\CODE\governed-ai-coding-runtime`, `provider: openai`, `approval: never`, `sandbox: danger-full-access`; command then stopped on current Codex usage quota, not login:
  - `You've hit your usage limit... try again at May 13th, 2026 2:05 AM.`

## Compatibility

- Historical evidence files still mention removed launchers; those are immutable records and were not rewritten.
- `scripts/codex-interop-check.py`, switch trace, and guard status remain for read-only diagnosis and legacy cleanup validation.
- `auth_mode = "chatgpt"` is expected when the current Cockpit account is OAuth; it is not itself a failure.

## Rollback

- Restore repository changes from git history.
- Restore live files from `C:\Users\sciman\.codex\backups\disable-project-interop-20260512-215910` if the old project-managed shims are intentionally needed.
- Rename disabled shortcuts back from `*.disabled-20260512-215910` only after explicitly accepting the old project-managed Codex/Cockpit mutation behavior.
