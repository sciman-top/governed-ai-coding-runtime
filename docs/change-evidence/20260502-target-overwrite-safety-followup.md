# Target Overwrite Safety Follow-up Evidence

- date: 2026-05-02
- rule_id: R6/R7/R8/E6
- risk_level: medium
- current_landing: `scripts/run-governed-task.py`, `scripts/runtime-flow-preset.ps1`, runtime write plumbing
- target_home: target-repo governance sync and attached write execution contracts
- rollback: revert this change set with git; re-run the commands below

## Issue

The target overwrite safety changes added if-match semantics for attached writes and fail-closed drift handling for generated/catalog-managed target files. Follow-up verification found two compatibility gaps:

- parallel `runtime-flow-preset.ps1` passed an empty `-WriteExpectedSha256` argument to child runs;
- `execute_attachment_write()` required `expected_sha256` at the Python helper boundary, breaking older service-wrapper callers before the lower-level fail-closed guard could run.

## Change

- `scripts/runtime-flow-preset.ps1`: only forwards `-WriteExpectedSha256` when the value is non-empty.
- `scripts/run-governed-task.py`: keeps `expected_sha256` optional at the helper boundary; existing-file writes remain protected by the lower-level if-match requirement.
- CLI/session bridge/spec plumbing keeps exposing `expected_sha256` for callers that intentionally replace existing files.

## Verification

- `python -m unittest tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_all_targets_json_supports_target_parallelism tests.runtime.test_run_governed_task_cli.RunGovernedTaskCliTests.test_run_default_profile_executes_repo_local_quick_gate`
  - result: pass, 2 tests
- `python -m unittest tests.runtime.test_run_governed_task_service_wrapper.RunGovernedTaskServiceWrapperTests.test_execute_attachment_write_uses_two_service_dispatch_calls tests.runtime.test_run_governed_task_service_wrapper.RunGovernedTaskServiceWrapperTests.test_execute_attachment_write_passes_expected_sha256_to_execute_payload`
  - result: pass, 2 tests
- `python -m unittest tests.runtime.test_target_repo_governance_consistency tests.runtime.test_target_repo_rollout_contract tests.runtime.test_attached_write_execution tests.runtime.test_repo_attachment tests.runtime.test_runtime_flow_preset tests.runtime.test_attached_repo_e2e tests.runtime.test_session_bridge tests.runtime.test_run_governed_task_cli`
  - result: pass, 151 tests, skipped=2
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - result: pass, `OK python-bytecode`, `OK python-import`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - first run: failed on missing optional `expected_sha256` helper default
  - final run after compatibility and wrapper tests: pass, 95 test files, failures=0, `OK runtime-unittest`, `OK runtime-service-parity`, `OK runtime-service-wrapper-drift-guard`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - result: pass, including `OK target-repo-rollout-contract`, `OK target-repo-governance-consistency`, `OK agent-rule-sync`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  - result: pass with non-blocking `WARN codex-capability-degraded`
- `python scripts/sync-agent-rules.py --scope All --fail-on-change`
  - result: pass, `changed_count=0`, `blocked_count=0`
- `python scripts/verify-target-repo-rollout-contract.py`
  - result: pass, `sync_revision=2026-05-02.2`
- `python scripts/verify-target-repo-governance-consistency.py`
  - result: pass, `drift_count=0`

## Compatibility

- Existing callers that do not pass `expected_sha256` can still request a write flow.
- Replacing an existing target file still requires a matching current hash at execution time.
- Generated/catalog-managed target files now fail closed on drift instead of overwriting target-local fixes.
