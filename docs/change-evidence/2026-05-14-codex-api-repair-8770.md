# 2026-05-14 Codex API Projection Repair In 8770

## Scope
- landing: `scripts/operator.ps1`, `scripts/serve-operator-ui.py`, `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py`, `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui_text.py`, `run.ps1`, `tests/runtime/test_operator_entrypoint.py`, `tests/runtime/test_operator_ui.py`
- destination: expose the already verified Cockpit API projection repair through the `http://127.0.0.1:8770/?lang=zh-CN` Codex panel as one explicit, narrow write action.
- risk: low-to-medium local state repair entrypoint; guarded by confirmation text, an allowlisted operator action, dry-run coverage, and the existing backup behavior in `scripts/codex-interop-check.py`.

## Commands
- `python -m unittest tests.runtime.test_operator_ui tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_operator_codex_api_projection_repair_is_available_as_dry_run tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_operator_ui_server_helpers_are_bounded_to_repo_actions_and_files tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_root_run_entrypoint_help_succeeds tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_root_run_entrypoint_codex_api_repair_alias`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\operator.ps1 -Action CodexApiProjectionRepair -DryRun`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\build-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\doctor-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\operator-ui-service.ps1 -Action Restart`
- `Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:8770/?lang=zh-CN'`
- `Invoke-RestMethod -Uri 'http://127.0.0.1:8770/api/run' -Method Post -ContentType 'application/json' -Body '{"action":"codex_api_projection_repair","dry_run":true}'`

## Key Output
- Targeted UI/operator tests: `Ran 11 tests ... OK`.
- `CodexApiProjectionRepair -DryRun` maps to `scripts/codex-interop-check.py --quick-launch --repair-current-cockpit-api-projection --prefer-cockpit-api-account`.
- build: `OK python-bytecode`, `OK python-import`.
- runtime: `Completed 113 test files ... failures=0`.
- contract/invariant: all checks passed, including `agent-rule-sync`, `pre-change-review`, and `functional-effectiveness`.
- hotspot: all checks passed except existing `WARN codex-capability-degraded`; this warning concerns native attach/status handshake support and is unrelated to the 8770 repair action.
- operator UI service after restart: `status=running`, `ready=true`, `stale=false`, `url=http://127.0.0.1:8770/?lang=zh-CN`.
- live page probe: HTTP `200`, page contains `codex_api_projection_repair`, `修复 API 投影`, and `不会重启 Codex`.
- live `/api/run` dry-run returns `exit_code=0` and the same explicit API projection repair command.

## Compatibility
- Keeps deprecated generic actions out of the 8770 allowlist: no `codex_interop_repair`, no guard start, no local optimize.
- The new UI action is named `codex_api_projection_repair` and maps only to `CodexApiProjectionRepair`.
- `CodexInteropRepair` remains as a CLI compatibility alias but delegates to the same API projection repair implementation.
- The repair path does not restart, stop, kill, or auto-launch Codex.

## Rollback
- Revert this change set.
- Restart the operator UI service with `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\operator-ui-service.ps1 -Action Restart`.
- Confirm `http://127.0.0.1:8770/?lang=zh-CN` no longer exposes `codex_api_projection_repair`.
