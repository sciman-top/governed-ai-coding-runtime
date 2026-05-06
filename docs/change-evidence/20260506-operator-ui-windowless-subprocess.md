# 2026-05-06 Operator UI Windowless Subprocess Evidence

- rule_id: `R3/R6/R8`
- risk_level: `low`
- current_home: `http://127.0.0.1:8770/?lang=zh-CN refresh path`
- target_home: `operator UI status probes may run local CLIs without flashing console windows`
- rollback: `git revert` the changes to subprocess window flags in `scripts/lib/codex_local.py`, `scripts/lib/claude_local.py`, `scripts/serve-operator-ui.py`, and `packages/contracts/src/governed_ai_coding_runtime_contracts/subprocess_guard.py`

## Root Cause

Refreshing the 8770 operator UI starts local status probes for Codex and Claude. The live process watch showed the long-running `pythonw.exe scripts/serve-operator-ui.py --serve --port 8770` process spawning short-lived `cmd.exe` children for commands such as:

- `claude.CMD --version`
- `claude.CMD mcp list`
- `codex.cmd login status`

Because `pythonw.exe` is a windowless GUI parent, Windows console children launched without `CREATE_NO_WINDOW` can briefly flash visible console windows.

## Change

- Added Windows-only `CREATE_NO_WINDOW` subprocess kwargs to Codex local probes.
- Added the same behavior to Claude local probes.
- Added the same behavior to the operator UI backend command runner and stale-service restart request.
- Added the same behavior to the shared `subprocess_guard.run_subprocess()` path used by adapter, feedback, session bridge, and governed command helpers.

## Verification

```powershell
python -m unittest tests.runtime.test_subprocess_guard.SubprocessGuardTests.test_run_subprocess_uses_no_window_creationflag_on_windows tests.runtime.test_codex_local.CodexLocalTests.test_local_status_subprocesses_are_windowless_on_windows tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_operator_ui_backend_subprocesses_are_windowless_on_windows
```

Result: `Ran 3 tests ... OK`

```powershell
python -m unittest tests.runtime.test_operator_ui tests.runtime.test_codex_local tests.runtime.test_subprocess_guard
```

Result: `Ran 43 tests ... OK`

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator-ui-service.ps1 -Action Restart -UiLanguage zh-CN -Port 8770
```

Result: `status=running`, `ready=true`, `stale=false`, `pid=30460`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
```

Result: `OK python-bytecode`, `OK python-import`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
```

Result: `Completed 105 test files ... failures=0`, `OK runtime-unittest`, `OK runtime-service-parity`, `OK runtime-service-wrapper-drift-guard`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
```

Result: `OK functional-effectiveness` and all preceding contract checks passed.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
```

Result: hotspot checks passed with the existing `WARN codex-capability-degraded` host-capability warning.
