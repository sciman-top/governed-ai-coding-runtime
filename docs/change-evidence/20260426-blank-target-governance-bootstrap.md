# 20260426 Blank Target Governance Bootstrap

## Goal
- Allow an existing but blank target repository directory to enter the one-click governance baseline path without a manual pre-step.

## Change
- `scripts/runtime-flow-preset.ps1`
  - `Invoke-GovernanceBaselineSync` now detects a missing `.governed-ai/repo-profile.json`.
  - When missing, it bootstraps the target through `scripts/attach-target-repo.py` using catalog metadata, then applies `scripts/apply-target-repo-governance.py`.
  - The sync result includes a `bootstrap` object with status, reason, exit code, payload, and output for traceability.
- `tests/runtime/test_runtime_flow_preset.py`
  - Added a regression test for `-ApplyGovernanceBaselineOnly` against a blank existing target directory.

## Verification
- `python -m unittest tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_apply_governance_baseline_only_bootstraps_blank_target tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_apply_governance_baseline_only_skips_runtime_flow`
- `python -m unittest tests.runtime.test_runtime_flow_preset tests.runtime.test_target_repo_governance_consistency tests.runtime.test_repo_attachment`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

## Result
- All commands passed.
- A blank existing target directory can now be bootstrapped by the baseline-only one-click governance path when the catalog provides enough target metadata.

## Rollback
- Revert the `Invoke-GovernanceBaselineSync` bootstrap block and the associated regression test.
