# 20260505 Uninstall Governance Safety

## Goal
- Current landing point: `scripts/uninstall-target-repo-governance.py` and managed asset reference classification.
- Target destination: make one-click uninstall and one-click cleanup avoid self-owned reference blocks, recheck content at mutation time, fail closed on incomplete reference scans, and leave durable rollback evidence.
- Verification path: focused regression tests followed by the hard gate order `build -> test -> contract/invariant -> hotspot`.

## pre_change_review
- `pre_change_review`: required because this change modifies governance uninstall, retired managed-file cleanup, and managed-asset classification code used by target-repo one-click cleanup flows.
- `control_repo_manifest_and_rule_sources`: reviewed the active project rule contract and manifest ownership boundary; this patch does not change `rules/manifest.json` or managed rule source content.
- `user_level_deployed_rule_files`: no user-level deployed rule file is changed by this patch.
- `target_repo_deployed_rule_files`: no target-repo deployed `AGENTS.md`, `CLAUDE.md`, or `GEMINI.md` file is changed by this patch.
- `target_repo_gate_scripts_and_ci`: reviewed uninstall, retired managed-file cleanup, runtime-flow managed cleanup tests, and operator entrypoint tests; added focused regression coverage for uninstall safety and inventory reference filtering.
- `target_repo_repo_profile`: profile file uninstall patches now carry before-content hashes and are rechecked before mutation; profile schema and catalog fields are unchanged.
- `target_repo_readme_and_operator_docs`: no operator command surface is changed; the existing one-click uninstall and cleanup entrypoints keep their CLI behavior while producing safer rollback evidence.
- `current_official_tool_loading_docs`: no Codex, Claude, or Gemini instruction loading semantics are changed; this is repository-local runtime cleanup behavior.
- `drift-integration decision`: integrate the review findings into the control repo uninstall planner instead of manually deleting blocked target files; planned post-uninstall references and runtime-owned provenance sidecars are treated as cleanup state, while real remaining references still fail closed.

## Changes
- Added a per-run reference index for managed asset inspection instead of scanning the target repository once per asset.
- Skipped runtime-owned provenance sidecars and bulk/archive/vendor directories during reference scanning.
- Added structured `reference_scan_errors` and fail-closed status for unreadable scanned files; uninstall and retired cleanup block apply when the reference scan is incomplete.
- Changed uninstall planning to evaluate references after planned deletes and JSON/profile patches, so files scheduled for removal or references removed by patches are not false blockers.
- Added runtime-owned managed-file provenance sidecars to uninstall delete candidates when their managed file is removed.
- Added deletion-time SHA-256 rechecks before deleting files and before applying shared JSON or profile patches.
- Changed apply to back up and recheck all candidates before the first mutation; mutation-time drift blocks the run without partial changes.
- Added a target-local `manifest.json` under the uninstall backup root for successful mutations and mutation-time blocks.

## Evidence
- Focused uninstall and inventory tests passed: `python -m unittest tests.runtime.test_uninstall_target_repo_governance tests.runtime.test_target_repo_managed_asset_inventory` -> `Ran 15 tests`, `OK`.
- Focused uninstall, inventory, and retired cleanup tests passed after structured scan-error handling: `python -m unittest tests.runtime.test_uninstall_target_repo_governance tests.runtime.test_target_repo_managed_asset_inventory tests.runtime.test_prune_retired_managed_files` -> `Ran 22 tests`, `OK`.
- Related cleanup and rollout contract tests passed: `python -m unittest tests.runtime.test_prune_retired_managed_files tests.runtime.test_uninstall_target_repo_governance tests.runtime.test_target_repo_managed_asset_inventory tests.runtime.test_target_repo_rollout_contract` -> `Ran 34 tests`, `OK`.
- Runtime-flow managed cleanup slice passed: `python -m unittest tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_single_target_dry_runs_managed_asset_prune_and_uninstall tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_apply_all_features_defaults_to_retired_managed_file_apply tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_apply_all_features_disable_managed_asset_removal_is_dry_run tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_blocks_managed_asset_apply_after_flow_failure` -> `Ran 4 tests`, `OK`.
- Operator entrypoint tests passed: `python -m unittest tests.runtime.test_operator_ui tests.runtime.test_operator_entrypoint` -> `Ran 37 tests`, `OK`.
- Real target dry-run evidence: `python scripts/uninstall-target-repo-governance.py --target-repo D:\CODE\skills-manager --dry-run` now blocks only `.governed-ai/quick-test-slice.prompt.md` with `generated_hash_differs`; `.governed-ai/verify-powershell-policy.py` and `.claude/hooks/governed-pre-tool-use.py` are delete candidates, and `.claude/settings.json` is a shared patch candidate with `references_removed_by_plan`.
- Pre-change review verifier passed: `python scripts/verify-pre-change-review.py --repo-root .`.
- Build passed: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1` -> `OK python-bytecode`, `OK python-import`.
- Runtime passed after test import isolation fix: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` -> `Completed 105 test files`, `failures=0`, `OK runtime-unittest`, `OK runtime-service-parity`, `OK runtime-service-wrapper-drift-guard`.
- Contract passed: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` -> includes `OK target-repo-rollout-contract`, `OK target-repo-governance-consistency`, `OK agent-rule-sync`, and `OK pre-change-review`.
- Hotspot passed: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1` -> existing `WARN codex-capability-degraded`; required checks passed.

## Compatibility
- Existing dry-run output remains JSON and keeps the current candidate/blocker shape.
- Apply remains fail-closed: active remaining references, generated-content drift, delete-time drift, and patch-time drift block mutation.
- Backup directories remain target-local; the new manifest only adds durable rollback metadata.
- The one-click operator surface is unchanged.

## Rollback
- Revert `scripts/uninstall-target-repo-governance.py`, `scripts/lib/target_repo_managed_assets.py`, `scripts/prune-retired-managed-files.py`, `scripts/inspect-target-repo-managed-assets.py`, related tests, and this evidence file.
- For target repositories where apply has already run, use the target-local uninstall backup `manifest.json` and copied backup files, or revert the target repo with git history when available.
