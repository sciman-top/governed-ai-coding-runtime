# 2026-05-09 Codex interop fail-closed hardening

- rule_id: `local-codex-cockpit-auth-interop`
- risk: `medium`
- landing: `scripts/codex-interop-check.py`, `scripts/operator.ps1`, `tests/runtime/test_codex_shared_launcher.py`, `tests/runtime/test_operator_entrypoint.py`
- destination: make Codex/Cockpit interop checks fail closed instead of reporting success or mutating auth state on unrepairable inputs.

## Commands

- `python -m unittest tests.runtime.test_codex_shared_launcher.CodexSharedLauncherTests.test_interop_checker_repairs_cc_switch_shared_history_blockers tests.runtime.test_codex_shared_launcher.CodexSharedLauncherTests.test_interop_checker_refuses_api_account_without_base_url tests.runtime.test_codex_shared_launcher.CodexSharedLauncherTests.test_interop_checker_does_not_mutate_existing_auth_for_unprojectable_api_account tests.runtime.test_codex_shared_launcher.CodexSharedLauncherTests.test_interop_checker_flags_unreadable_codex_state_schema`
- `python -m unittest tests.runtime.test_codex_shared_launcher`
- `python -m unittest tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_operator_preserves_codex_interop_check_failure_exit_code`
- `python -m unittest tests.runtime.test_codex_shared_launcher tests.runtime.test_operator_entrypoint tests.runtime.test_operator_ui`
- `python -m py_compile scripts\codex-interop-check.py scripts\serve-operator-ui.py`
- `codex-interop-check`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\operator.ps1 -Action CodexInteropCheck`
- `codex-interop-repair`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\build-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\doctor-runtime.ps1`

## Evidence

- Added regression coverage for dry-run `status = "fail"` returning process exit code `2`.
- Added regression coverage that unprojectable Cockpit API-key accounts without `api_base_url` do not create or overwrite Codex `auth.json`.
- Added regression coverage that malformed Codex `state_5.sqlite` schema is reported as a failed provider-distribution check instead of an empty passing distribution.
- Removed dormant CC Switch repair and automatic Cockpit restart-wrapper write paths from `codex-interop-check.py`.
- Synced the repaired checker to `C:\Users\sciman\.codex\scripts\codex-interop-check.py`.
- Live shortcut returned `exit_code=2` with `status=fail`, proving the local command no longer reports a failing interop state as success.
- Live operator returned `exit_code=2` for `CodexInteropCheck`, proving wrapper failure propagation preserves the checker exit code.
- Live repair returned `exit_code=0` with `status=pass`; actions included `codex_live_config_cockpit_provider:changed`, `codex_auth_cockpit_projected:changed`, `codex_state_db_backup:ok`, and `codex_threads_provider_bucket_migrated:changed`.
- Post-repair live shortcut returned `exit_code=0` with `status=pass`.
- Post-repair live operator `CodexInteropCheck` returned `exit_code=0`.
- Full gate passed in fixed order: build, Runtime, Contract, doctor. Doctor returned exit code 0 with existing `WARN codex-capability-degraded`.

## Compatibility

- Existing successful repair flow remains covered by `test_interop_checker_repairs_cc_switch_shared_history_blockers`.
- Operator dry-run behavior remains covered by `test_operator_codex_interop_check_is_available_as_dry_run`.
- Failure status is intentionally fail-closed for command-line and operator callers.

## Rollback

- Revert this change from git history.
- Restore `C:\Users\sciman\.codex\scripts\codex-interop-check.py` from the previous installed copy or rerun the previous release of `Optimize-CodexLocal.ps1` if needed.
