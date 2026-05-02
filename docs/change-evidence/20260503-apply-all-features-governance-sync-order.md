# 2026-05-03 ApplyAllFeatures Governance Sync Order

## Scope
- rule_id: R6/R8/E4/E6
- risk_level: medium
- changed_paths: `scripts/runtime-flow-preset.ps1`, `tests/runtime/test_runtime_flow_preset.py`
- rollback_action: revert this change set with git history, then rerun the verification commands below.

## pre_change_review
- control_repo_manifest_and_rule_sources: checked the repo-level AGENTS instructions and the managed rollout surfaces for the one-click target governance path.
- user_level_deployed_rule_files: no user-level rule file rewrite is part of this slice; rule sync remains governed by `scripts/sync-agent-rules.ps1`.
- target_repo_deployed_rule_files: no target-repo rule files are rewritten by this slice; target sync still flows through `runtime-flow-preset.ps1` and `apply-target-repo-governance.py`.
- target_repo_gate_scripts_and_ci: reviewed `scripts/governance/full-check.ps1`, `scripts/governance/fast-check.ps1`, and the runtime-flow preset call order that selects them.
- target_repo_repo_profile: reviewed `.governed-ai/repo-profile.json` ownership semantics via `apply-target-repo-governance.py`; the fix makes `ApplyAllFeatures` sync profile overrides before daily flow.
- target_repo_readme_and_operator_docs: operator-facing entrypoints remain unchanged; `ApplyAllFeatures` still runs through the same operator/UI action and target selection arguments.
- current_official_tool_loading_docs: no Codex/Claude/Gemini loading semantics changed in this slice; existing project-rule loading assumptions stay unchanged.
- drift-integration decision: integrate the review finding into the orchestrator by moving governance baseline sync before runtime flow for `ApplyAllFeatures`, while preserving fail-closed drift blocking and milestone gate behavior.

## Evidence
- `python -m unittest tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_apply_all_features_syncs_baseline_before_daily_flow tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_all_targets_apply_all_features_supports_fast_milestone_gate_mode tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_auto_fast_skips_clean_milestone_gate tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_blocks_managed_asset_apply_after_flow_failure` -> pass.
- `python -m unittest tests.runtime.test_runtime_flow_preset tests.runtime.test_target_repo_governance_consistency tests.runtime.test_target_repo_rollout_contract` -> pass, 62 tests.
- `python scripts/verify-target-repo-rollout-contract.py` -> pass, `capability_count=14`, `feature_count=6`.
- `python scripts/verify-target-repo-governance-consistency.py` -> pass, `target_count=5`, `drift_count=0`.
- `git diff --check` -> pass with CRLF normalization warnings only.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1` -> pass.

## Notes
- A first full `verify-repo.ps1 -Check Runtime` run failed because this evidence file did not exist yet and the pre-change review gate correctly blocked the sensitive `runtime-flow-preset.ps1` change.
- The same run also surfaced one unrelated `test_run_governed_task_cli.py` failure while the contract gate was blocked; rerun after this evidence should be treated as the authoritative result for this slice.
