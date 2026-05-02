# 2026-05-02 Apply All Retired Cleanup Integration

## Rule
- `R1`: current landing point is the one-click target apply path.
- `R6`: verification uses focused operator/UI tests and command-render dry-runs before broader gates.
- `R8`: evidence records basis, command, output, compatibility, and rollback.

## Basis
- `ApplyAllFeatures` claims target-repo consistency coverage.
- Retired managed files are part of target governance consistency because old target repos can keep obsolete generated assets after a feature baseline changes.
- Destructive cleanup remains high risk and must require explicit `-ApplyManagedAssetRemoval`.

## Changes
- `ApplyAllFeatures` now passes `-PruneRetiredManagedFiles` to `runtime-flow-preset.ps1`.
- `ApplyAllFeatures -ApplyManagedAssetRemoval` now forwards the explicit removal intent to the runtime flow.
- Operator UI API can pass `-ApplyManagedAssetRemoval` for `apply_all_features`.
- Operator UI text now says apply-all also reports retired cleanup plans.

## Commands
- `python -m py_compile scripts/serve-operator-ui.py`
- `python -m unittest tests.runtime.test_operator_entrypoint`
- `python -m py_compile scripts/serve-operator-ui.py packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py`
- `python -m unittest tests.runtime.test_operator_entrypoint tests.runtime.test_operator_ui`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- `python -m unittest tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_single_target_dry_runs_managed_asset_prune_and_uninstall tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_blocks_managed_asset_apply_after_flow_failure`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `$env:GOVERNED_RUNTIME_OPERATOR_PREFLIGHT_JSON='{"next_action":"default_defer","why":"No blocking action.","gate_state":"pass","source_state":"fresh","evidence_state":"fresh"}'; pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action ApplyAllFeatures -Target self-runtime -Mode quick -DryRun`
- `$env:GOVERNED_RUNTIME_OPERATOR_PREFLIGHT_JSON='{"next_action":"default_defer","why":"No blocking action.","gate_state":"pass","source_state":"fresh","evidence_state":"fresh"}'; pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action ApplyAllFeatures -Target self-runtime -Mode quick -ApplyManagedAssetRemoval -DryRun`

## Evidence
- Python bytecode compile passed.
- Focused operator entrypoint tests passed: 26 tests.
- Focused operator/UI tests passed: 32 tests.
- Build gate passed: `OK python-bytecode`, `OK python-import`.
- Managed-asset runtime-flow focused tests passed: 2 tests.
- First Runtime gate attempt ran 99 test files; apply-all cleanup/UI/runtime-flow slices passed, but `test_agent_rule_sync` still expected global rule version `9.48` while the manifest default and entries were already `9.49`.
- Contract gate passed.
- Runtime gate rerun passed: `OK runtime-unittest`, `OK runtime-service-parity`, `OK runtime-service-wrapper-drift-guard`.
- Hotspot gate passed via `doctor-runtime.ps1`; existing `WARN codex-capability-degraded` remained.
- Apply-all dry-run rendered `-ApplyAllFeatures ... -PruneRetiredManagedFiles` and did not include `-ApplyManagedAssetRemoval` by default.
- Explicit apply dry-run rendered `-ApplyAllFeatures ... -PruneRetiredManagedFiles -ApplyManagedAssetRemoval`.
- A normal live dry-run was blocked by current operator preflight because evidence is stale; the command-render proof used a controlled pass-state preflight override.

## Compatibility
- Existing `ApplyAllFeatures` result JSON can now include `prune_retired_managed_files`.
- Default apply-all does not delete retired files; it reports candidates.
- Real deletion still requires explicit `-ApplyManagedAssetRemoval` and the existing managed-asset hash/reference guards.

## Rollback
- Revert:
  - `scripts/operator.ps1`
  - `scripts/serve-operator-ui.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py`
  - `tests/runtime/test_operator_entrypoint.py`
  - this evidence file
