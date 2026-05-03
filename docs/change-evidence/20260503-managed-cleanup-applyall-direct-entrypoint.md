# 2026-05-03 Managed Cleanup ApplyAll Direct Entrypoint

## Rule
- `R1`: current landing point is `scripts/runtime-flow-preset.ps1`; target destination is the all-target retired managed-file cleanup path.
- `R4`: real deletion remains limited to registered, hash-matched, unreferenced retired managed files.
- `R8`: cleanup output must expose proof, backup, rollback manifest, and blocked-state evidence.

## Pre Change Review
- `pre_change_review`
- `control_repo_manifest_and_rule_sources`: reviewed project `AGENTS.md`, `docs/targets/target-repo-governance-baseline.json`, `docs/targets/target-repo-rollout-contract.json`, and prior managed-asset cleanup evidence before changing the runtime-flow direct entrypoint.
- `user_level_deployed_rule_files`: no user-level rule files are changed by this slice; rule deployment remains covered by `scripts/sync-agent-rules.py --scope All --fail-on-change`.
- `target_repo_deployed_rule_files`: no target project rule files are changed by this slice; cleanup only touches files declared in `retired_managed_files` and only after target flow succeeds.
- `target_repo_gate_scripts_and_ci`: reviewed `scripts/runtime-flow-preset.ps1`, `scripts/operator.ps1`, and runtime-flow preset tests; direct `-ApplyAllFeatures` now matches operator semantics.
- `target_repo_repo_profile`: repo profiles are not changed by retired-file cleanup; profile state is only an input to target daily flow and governance sync.
- `target_repo_readme_and_operator_docs`: existing operator docs already state `ApplyAllFeatures` defaults to safe retired managed-file deletion and supports `-DisableManagedAssetRemoval` detection mode.
- `current_official_tool_loading_docs`: no Codex/Claude/Gemini loading semantics are changed.
- `drift-integration decision`: integrate the direct runtime-flow entrypoint with the already documented/operator-exposed behavior instead of leaving `operator.ps1` and `runtime-flow-preset.ps1` with different cleanup semantics.

## Basis
- `scripts/operator.ps1 -Action ApplyAllFeatures` already passed `-PruneRetiredManagedFiles` and defaulted to `-ApplyManagedAssetRemoval`.
- The direct canonical entrypoint `scripts/runtime-flow-preset.ps1 -ApplyAllFeatures` did not enable the same cleanup behavior and had no `-DisableManagedAssetRemoval` switch.

## Changes
- Added `-DisableManagedAssetRemoval` to `scripts/runtime-flow-preset.ps1`.
- Made direct `-ApplyAllFeatures` enable `PruneRetiredManagedFiles`; default mode applies deletion, while `-DisableManagedAssetRemoval` keeps it dry-run.
- Preserved explicit cleanup behavior for `CleanupTargets`: `-PruneRetiredManagedFiles` still requires explicit `-ApplyManagedAssetRemoval` for real deletion.
- Changed no-op `prune-retired-managed-files.py --apply` so it does not create empty backup manifest directories when there are no delete candidates, no deletions, and no backup-backed blocks.
- Added runtime-flow tests for default apply and disable/dry-run behavior.
- Added prune tests for no-op apply not creating an empty backup manifest.

## Commands
- `python -m unittest tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_apply_all_features_defaults_to_retired_managed_file_apply tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_apply_all_features_disable_managed_asset_removal_is_dry_run tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_single_target_dry_runs_managed_asset_prune_and_uninstall tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_blocks_managed_asset_apply_after_flow_failure`
- `python -m unittest tests.runtime.test_prune_retired_managed_files tests.runtime.test_runtime_flow_preset`
- `python -m unittest tests.runtime.test_runtime_flow_preset`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -FlowMode daily -Mode quick -Json -PruneRetiredManagedFiles -ApplyManagedAssetRemoval -RuntimeFlowTimeoutSeconds 300 -BatchTimeoutSeconds 1800`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

## Evidence
- Focused runtime-flow preset cleanup tests passed: 4 tests.
- First all-target cleanup apply reached 5 targets. `classroomtoolkit`, `github-toolkit`, `skills-manager`, and `vps-ssh-launcher` passed cleanup with `delete_candidates=0`, `deleted=0`, `blocked=0`.
- `self-runtime` cleanup was blocked before deletion because the contract gate required this pre-change review evidence for the `runtime-flow-preset.ps1` change.
- After this evidence file was added, `self-runtime` cleanup apply passed with `delete_candidates=0`, `deleted=0`, `blocked=0`.
- Final all-target cleanup apply passed: `target_count=5`, `failure_count=0`, `batch_timed_out=false`, `batch_elapsed_seconds=322`; every target reported `delete_candidates=0`, `deleted=0`, `blocked=0`.
- After no-op backup cleanup hardening, final all-target cleanup apply passed again: `target_count=5`, `failure_count=0`, `batch_timed_out=false`, `batch_elapsed_seconds=326`; every target reported `delete_candidates=0`, `deleted=0`, `blocked=0`, and `manifest_path=""`.
- Target repo worktrees checked clean after the final no-op cleanup run: `ClassroomToolkit`, `github-toolkit`, `skills-manager`, and `vps-ssh-launcher`.
- Focused prune/runtime-flow tests passed together: 29 tests.
- Full `tests.runtime.test_runtime_flow_preset` passed: 24 tests.
- Build gate passed: `OK python-bytecode`, `OK python-import`.
- Runtime gate passed: 102 test files, `failures=0`, `OK runtime-unittest`, `OK runtime-service-parity`, `OK runtime-service-wrapper-drift-guard`.
- Contract gate passed, including `OK pre-change-review`, `OK target-repo-governance-consistency`, and `OK functional-effectiveness`.
- Hotspot gate passed via `doctor-runtime.ps1`; existing `WARN codex-capability-degraded` remained.

## Compatibility
- Existing direct `-PruneRetiredManagedFiles` behavior is preserved.
- `-ApplyAllFeatures -DisableManagedAssetRemoval` provides the documented detect-only mode.
- JSON fields remain additive or previously declared: `prune_retired_managed_files_active`, `apply_managed_asset_removal`, and per-target `prune_retired_managed_files`.

## Rollback
- Revert `scripts/runtime-flow-preset.ps1`, `scripts/prune-retired-managed-files.py`, runtime managed-asset tests, and this evidence file.
- Restore any deleted target files from each target repo `.governed-ai/backups/retired-managed-files/<timestamp>/manifest.json` if a future cleanup run deletes candidates.
