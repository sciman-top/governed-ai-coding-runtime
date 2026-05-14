# 2026-05-15 Codex Cockpit Policy Contract Hardening

- rule_id: `local-codex-cockpit-auth-interop`
- risk: low repo documentation/test hardening; no live `~/.codex` or Cockpit state mutation
- landing: `AGENTS.md`, README files, `docs/runbooks/codex-cockpit-api-provider-repair.md`, `tests/runtime/test_codex_cockpit_policy_contract.py`
- destination: make OAuth/API roundtrips, history bucket alignment, and repair boundaries a highest-priority local interoperability contract that future changes cannot silently loosen
- rollback: revert this commit or restore the edited repo files from git

## Changes

- Promoted Codex/Cockpit OAuth/API roundtrips, `state_5.sqlite.threads.model_provider` history buckets, picker visibility metadata, and repair entrypoints into a project-level hard boundary in `AGENTS.md`.
- Documented that any related change must first read the repair runbook and run `CodexProjectionSmoke` or `codex-interop-check.py --quick-launch`.
- Reaffirmed the only allowed write entrypoints: `CodexApiProjectionRepair`, `CodexOauthProjectionRepair`, and `CodexLaunchBindingRepair`.
- Reaffirmed forbidden regressions: generic `--apply`, `--migrate-provider-bucket`, SQLite provider triggers, background guards, no-op launchers, restart wrappers, CLI preflight wrappers, `[model_providers.openai]`, and automatic Codex restarts.
- Added `tests.runtime.test_codex_cockpit_policy_contract` so AGENTS, the runbook, and README files must retain the high-priority contract wording and forbidden-action boundary.

## Verification

- `python -m unittest tests.runtime.test_codex_cockpit_policy_contract`
  - result: `OK`, 3 tests
- `python -m unittest tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_operator_codex_api_projection_repair_is_available_as_dry_run tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_operator_codex_oauth_projection_repair_is_available_as_dry_run tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_operator_codex_projection_smoke_is_read_only_dry_run tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_operator_codex_launch_binding_repair_is_available_as_dry_run`
  - result: `OK`, 4 tests

## Live State Note

- This change intentionally did not run `CodexApiProjectionRepair`, `CodexOauthProjectionRepair`, or `CodexLaunchBindingRepair`; those mutate live `~/.codex` or Cockpit state and should be executed only as explicit repair actions.
