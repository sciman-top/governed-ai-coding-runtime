# 2026-05-02 Target Managed Asset Retirement And Uninstall

## Rule
- Core principle: target-repo managed files must not be blindly overwritten or blindly removed.
- Risk: high for destructive apply; implemented default behavior is dry-run and fail-closed.

## Basis
- Target repositories may have locally repaired or optimized project rules, gate scripts, prompts, and profiles.
- A one-click apply surface needs a matching one-click removal surface, but removal must prove ownership before deleting or patching anything.
- Shared files must be patched by owned fields or overlay values, not deleted as whole files.

## Changes
- Added managed asset classification helpers in `scripts/lib/target_repo_managed_assets.py`.
- Added read-only inventory CLI: `scripts/inspect-target-repo-managed-assets.py`.
- Added retired managed file prune CLI: `scripts/prune-retired-managed-files.py`.
- Added governance uninstall CLI: `scripts/uninstall-target-repo-governance.py`.
- Added `retired_managed_files` baseline/rollout contract support and safety validation.
- Added one-click flags in `scripts/runtime-flow-preset.ps1`:
  - `-PruneRetiredManagedFiles`
  - `-UninstallGovernance`
  - `-ApplyManagedAssetRemoval`
- Added regression tests for inventory, retired prune, uninstall, generated-file hash blocking, and runtime-flow dry-run JSON.

## Safety Behavior
- Normal `ApplyAllFeatures` does not remove files.
- `PruneRetiredManagedFiles` and `UninstallGovernance` default to dry-run.
- Destructive apply requires explicit `-ApplyManagedAssetRemoval`.
- Retired files are deleted only when target content matches the recorded previous hash/source and no active references are found.
- Active source-backed files are deleted only when target content matches expected managed content.
- `json_merge` shared files are patched by removing the runtime overlay while preserving target-local settings.
- Generated files are blocked unless the baseline supplies hash evidence that proves the target file is exactly generated content.
- Unknown ownership, target-local drift, and missing source/hash evidence block destructive actions.

## Commands
- `python -m py_compile scripts/lib/target_repo_managed_assets.py scripts/inspect-target-repo-managed-assets.py scripts/prune-retired-managed-files.py scripts/uninstall-target-repo-governance.py`
- `python -m unittest tests.runtime.test_target_repo_rollout_contract tests.runtime.test_target_repo_managed_asset_inventory tests.runtime.test_prune_retired_managed_files tests.runtime.test_uninstall_target_repo_governance tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_single_target_dry_runs_managed_asset_prune_and_uninstall`
- `python scripts/verify-target-repo-rollout-contract.py`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target self-runtime -FlowMode daily -Mode quick -Json -PruneRetiredManagedFiles -UninstallGovernance`

## Evidence
- Python bytecode compile passed for the four new/updated managed-asset scripts.
- Focused regression tests passed: 21 tests in 3.838s.
- Rollout contract verifier passed with `sync_revision=2026-05-02.3`, `capability_count=14`, and zero errors.
- Build gate passed: `OK python-bytecode`, `OK python-import`.
- Runtime gate passed: 99 test files in 158.384s, failures=0.
- Contract gate passed, including `OK target-repo-rollout-contract`, `OK target-repo-governance-consistency`, `OK agent-rule-sync`, `OK pre-change-review`, and `OK functional-effectiveness`.
- Doctor gate passed with the existing `WARN codex-capability-degraded`.
- Real `self-runtime` one-click dry-run passed:
  - `prune_retired_managed_files`: `dry_run=true`, `delete_candidates=0`, `deleted=0`, `blocked=0`.
  - `uninstall_governance`: `dry_run=true`, `delete_candidates=2`, `shared_patch_candidates=1`, `deleted=0`, `shared_patched=0`, `blocked=0`.

## Compatibility
- Existing apply behavior is preserved; removal does not run unless explicitly requested.
- JSON output adds new fields but does not remove existing fields.
- Generated managed files without hash evidence are now protected from accidental uninstall deletion.

## Rollback
- Revert:
  - `scripts/lib/target_repo_managed_assets.py`
  - `scripts/inspect-target-repo-managed-assets.py`
  - `scripts/prune-retired-managed-files.py`
  - `scripts/uninstall-target-repo-governance.py`
  - `scripts/runtime-flow-preset.ps1`
  - `docs/targets/target-repo-governance-baseline.json`
  - `docs/targets/target-repo-rollout-contract.json`
  - related tests under `tests/runtime/`
- Remove this evidence file if the feature slice is reverted.
