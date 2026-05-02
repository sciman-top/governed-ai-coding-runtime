# 2026-05-02 Managed Asset Removal Runtime Flow Integration

## Rule
- Core principle: `target_repo_managed_asset_retirement_before_removal`
- Risk: medium

## Pre Change Review
- `pre_change_review`
- `control_repo_manifest_and_rule_sources`: reviewed `rules/manifest.json`, global rule sources, target rollout contract, managed asset scripts, and `scripts/runtime-flow-preset.ps1`.
- `user_level_deployed_rule_files`: rule sync produced backup snapshots under `docs/change-evidence/rule-sync-backups/20260502-191519/`; user-level deployed files must be compared through the manifest sync flow before changes are treated as complete.
- `target_repo_deployed_rule_files`: no target project rule file is removed by this task; target repo managed asset removal remains dry-run-first unless `-ApplyManagedAssetRemoval` is explicit.
- `target_repo_gate_scripts_and_ci`: reviewed runtime-flow integration for `-PruneRetiredManagedFiles`, `-UninstallGovernance`, JSON reporting, and gate behavior after managed asset actions.
- `target_repo_repo_profile`: target profiles remain inputs for gate execution; uninstall/prune actions operate on managed files and must not silently mutate profile gate semantics.
- `target_repo_readme_and_operator_docs`: linked planning docs describe managed asset retirement/uninstall scope and dry-run/apply boundary.
- `current_official_tool_loading_docs`: no new external loading model change is introduced here; existing Codex/Claude/Gemini rule loading constraints remain in the global/project rule family.
- `drift-integration decision`: rule source edits, manifest changes, and deployed backup evidence are kept as one integration unit; drift must be reconciled through sync checks before completion.

## Basis
- Managed target-repo assets need a safe retirement path separate from normal governance sync so delete actions do not hide inside ordinary apply flows.
- `PruneRetiredManagedFiles` and `UninstallGovernance` must default to dry-run, emit JSON evidence, and require explicit `ApplyManagedAssetRemoval` before deletion.
- Parallel all-target runs must remain structurally compatible with sequential runs even when managed asset removal is inactive.

## Changes
- Integrated managed asset prune/uninstall result fields into `scripts/runtime-flow-preset.ps1` JSON output.
- Kept managed asset removal inactive by default and excluded it from parallel batch eligibility when requested.
- Fixed parallel target-run shape so inactive managed asset actions emit skipped result objects and do not break all-target JSON rendering.
- Connected rollout contract and tests for retired managed file safety metadata.

## Commands
- `python -m unittest tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_single_target_dry_runs_managed_asset_prune_and_uninstall tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_all_targets_json_supports_target_parallelism`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target self-runtime -FlowMode daily -Json -RuntimeFlowTimeoutSeconds 300`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -FlowMode daily -Json -TargetParallelism 3 -RuntimeFlowTimeoutSeconds 300 -BatchTimeoutSeconds 1200`
- `python -m unittest tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_single_target_dry_runs_managed_asset_prune_and_uninstall tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_all_targets_json_supports_target_parallelism tests.runtime.test_target_repo_gate_speed_audit`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

## Evidence
- Focused runtime-flow tests passed after fixing the parallel eligibility line and parallel target-run skipped-action shape: 2 tests in 6.218s.
- A pre-change review block correctly detected missing evidence before this file existed; the block was not bypassed.
- After this evidence was added, `self-runtime` daily passed in 121.699s with `test=pass` and `contract=pass`.
- All-target parallel daily passed after the managed-asset integration fix: measured 108.816s, payload `batch_elapsed_seconds=108`, `target_count=5`, `failure_count=0`.
- Focused runtime-flow/audit tests passed: 5 tests in 5.880s.
- Build gate passed: `OK python-bytecode`, `OK python-import`.
- Runtime gate passed: 99 test files in 153.290s, failures=0.
- Contract gate passed, including `OK pre-change-review`.
- Hotspot gate passed with existing `WARN codex-capability-degraded`.

## Rollback
- Revert `scripts/runtime-flow-preset.ps1`, `scripts/lib/target_repo_managed_assets.py`, `scripts/uninstall-target-repo-governance.py`, managed asset tests, rollout contract changes, and related rule/manifest updates.
- Remove generated dry-run/debug evidence under `docs/change-evidence/target-repo-speed-20260502/` if no longer needed.
