# 2026-05-03 GAP-151 Managed Asset Export Evidence

## Rule
- `R1`: current landing point is `scripts/runtime-flow-preset.ps1` target-run evidence export; target home is `GAP-151` active-target managed-asset dry-run closeout evidence.
- `R4`: medium-risk runtime-flow script change; this slice only exports already-computed dry-run action results and does not enable apply.
- `R8`: record basis, commands, evidence, compatibility, and rollback before changing the sensitive runtime-flow script.

## Pre-Change Review
- Control entrypoint: `scripts/runtime-flow-preset.ps1`.
- Regression surface: `tests/runtime/test_runtime_flow_preset.py`.
- Evidence target: `docs/change-evidence/target-repo-runs/*-daily-*.json`.
- Target-repo safety posture: `-PruneRetiredManagedFiles` and `-UninstallGovernance` remain dry-run unless `-ApplyManagedAssetRemoval` is explicitly supplied.
- Platform/tooling review: no Codex/Claude/Gemini rule source, provider, MCP, auth, login chain, or permission setting is changed.

## pre_change_review
- `control_repo_manifest_and_rule_sources`: reviewed the loaded project `AGENTS.md` contract, `rules/manifest.json` ownership posture, and the existing managed-asset plan before touching runtime-flow export behavior.
- `user_level_deployed_rule_files`: no user-level deployed Codex/Claude/Gemini rule file is changed by this slice.
- `target_repo_deployed_rule_files`: no target-repo deployed rule file is changed by this slice; target-run JSON export is control-repo evidence only.
- `target_repo_gate_scripts_and_ci`: reviewed `scripts/verify-repo.ps1` gate expectations and added a focused runtime-flow regression before closeout.
- `target_repo_repo_profile`: no target repo `repo-profile.json` is edited by this slice; uninstall profile candidates remain dry-run evidence.
- `target_repo_readme_and_operator_docs`: no target README or operator guide is distributed by this slice.
- `current_official_tool_loading_docs`: no tool loading model is changed; current session rules remain context while deterministic enforcement stays in scripts and gates.
- `drift-integration decision`: integrate the missing export fields in the control runtime first, discard the failed dirty self-runtime run as closeout evidence, then rerun active-target dry-run from a clean control repo.

## Basis
- `GAP-151` acceptance requires durable all-target dry-run reports for prune and uninstall.
- Console JSON already contained `prune_retired_managed_files` and `uninstall_governance`, but exported target-run JSON omitted those action sections.
- The missing export made the all-target dry-run evidence non-durable, so GAP-151 could not be honestly closed.

## Changes
- Added `prune_retired_managed_files` and `uninstall_governance` sections to target-run JSON export when the target run contains managed-asset action results.
- Reused the existing `Convert-ManagedAssetActionForJson` converter so console and file evidence keep the same shape.
- Extended the single-target dry-run regression to enable `-ExportTargetRepoRuns` and assert that the exported JSON includes both managed-asset dry-run sections.

## Verification
- `python -m unittest tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_single_target_dry_runs_managed_asset_prune_and_uninstall`: pass; `Ran 1 test in 2.219s`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`: pass; `OK powershell-parse`, `OK issue-seeding-render`.
- Commit pre-check initially blocked as expected because `scripts/runtime-flow-preset.ps1` is sensitive and required this pre-change review evidence.

## Compatibility
- Existing target-run JSON consumers continue to receive the previous top-level fields.
- The new fields are additive and appear only when managed-asset action results exist.
- Dry-run/apply semantics are unchanged; this slice does not delete, patch, or sync any target repo files.

## Rollback
- Revert this evidence file and the related changes to `scripts/runtime-flow-preset.ps1` and `tests/runtime/test_runtime_flow_preset.py`.
- If any exported target-run JSON produced by this slice is considered invalid, remove the affected `docs/change-evidence/target-repo-runs/*-daily-*.json` files and regenerate from the prior runtime-flow version.
