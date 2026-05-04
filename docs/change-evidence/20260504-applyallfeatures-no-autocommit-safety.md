# 20260504 ApplyAllFeatures No-Auto-Commit Safety

## Rule
- `R1`: current landing point is the all-target `ApplyAllFeatures` run; target destination is safe target-repo governance application without absorbing unrelated worktree changes.
- `R4`: medium-risk orchestration change because milestone gates can otherwise auto-commit dirty target repos.
- `R8`: evidence covers basis, command, result, compatibility, and rollback.

## Basis
- Running `scripts/runtime-flow-preset.ps1 -AllTargets -ApplyAllFeatures` uses the milestone gate path.
- The milestone gate runner previously allowed auto-commit through `git add -A`, which is unsafe when a target repo has existing unrelated local changes.
- `python scripts/classify-target-repo-worktree-changes.py` showed `k12-question-graph` had target-local unrelated changes before this run; therefore auto-commit needed an explicit caller-side disable switch.

## pre_change_review
- `pre_change_review`: required because this change modifies `scripts/runtime-flow-preset.ps1`, `scripts/governance/gate-runner-common.ps1`, `scripts/governance/full-check.ps1`, and `scripts/governance/fast-check.ps1`.
- `control_repo_manifest_and_rule_sources`: reviewed current dirty rule-source and manifest changes from the v9.52 rule convergence slice; this slice does not modify `rules/manifest.json` or rule source semantics.
- `user_level_deployed_rule_files`: no additional user-level rule deployment is introduced by the no-auto-commit switch.
- `target_repo_deployed_rule_files`: target repo rule files remain governed by the existing rule-sync manifest; this slice does not edit target rule content.
- `target_repo_gate_scripts_and_ci`: reviewed milestone gate entrypoints and added a focused gate-runner test plus runtime-flow-preset propagation test.
- `target_repo_repo_profile`: no target repo profile schema, catalog field, or profile value is changed; the switch only suppresses post-gate auto-commit at invocation time.
- `target_repo_readme_and_operator_docs`: no operator documentation is changed; `-Help` now exposes `-DisableMilestoneAutoCommit` as the safe explicit CLI boundary.
- `current_official_tool_loading_docs`: no Codex, Claude, or Gemini loading semantics are changed.
- `drift-integration decision`: keep `ApplyAllFeatures` feature application, baseline sync, runtime flow, fast/full milestone gates, and managed-asset cleanup semantics unchanged; only add an explicit no-auto-commit path for dirty multi-target runs and improve mixed stdout JSON parsing.

## Changes
- Added `-DisableAutoCommit` to `scripts/governance/full-check.ps1` and `scripts/governance/fast-check.ps1`.
- Added `DisabledByCaller` handling to `Invoke-AutoCommit` so the gate still runs but auto-commit returns `skipped / disabled_by_caller`.
- Added `-DisableMilestoneAutoCommit` to `scripts/runtime-flow-preset.ps1` and propagated it to milestone gates.
- Improved `runtime-flow-preset.ps1` JSON parsing so target gate logs before JSON do not erase `auto_commit_*` evidence fields.
- Added regression tests for the gate-runner disable path and all-target `ApplyAllFeatures` propagation.

## Commands
- `python scripts/classify-target-repo-worktree-changes.py`
- `python -m unittest tests.runtime.test_governance_gate_runner.GovernanceGateRunnerTests.test_full_check_can_disable_auto_commit_for_managed_batch_runs`
- `python -m unittest tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_apply_all_features_can_disable_milestone_auto_commit`
- `python -m unittest tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_all_targets_apply_all_features tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_apply_all_features_can_disable_milestone_auto_commit tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_all_targets_apply_all_features_supports_fast_milestone_gate_mode`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -ApplyAllFeatures -DisableMilestoneAutoCommit -MilestoneGateMode fast -MilestoneGateTimeoutSeconds 300 -RuntimeFlowTimeoutSeconds 360 -GovernanceSyncTimeoutSeconds 180 -BatchTimeoutSeconds 1800 -Json`
- `python scripts/sync-agent-rules.py --scope All --fail-on-change`
- `python scripts/verify-target-repo-governance-consistency.py`
- `python scripts/verify-target-repo-rollout-contract.py`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

## Evidence
- Initial all-target run evidence: `docs/change-evidence/target-applyallfeatures-20260504-104914.json`.
- Initial all-target result: 5 targets passed; `self-runtime` failed because this evidence file did not yet exist and the pre-change review gate failed closed.
- Managed cleanup results in the initial all-target run: `classroomtoolkit`, `github-toolkit`, `k12-question-graph`, `skills-manager`, and `vps-ssh-launcher` all reported `delete_candidates=0` and `deleted=0`.
- Focused tests passed after the no-auto-commit switch and mixed-output JSON parser changes.
- Final all-target run evidence: `docs/change-evidence/target-applyallfeatures-20260504-111402-final.json`.
- Final all-target result: `target_count=6`, `failure_count=0`; every target reported `milestone_commit_status=pass`, `auto_commit_status=skipped`, `auto_commit_reason=disabled_by_caller`, and managed cleanup `delete_candidates=0` / `deleted=0`.
- Rule-sync dry-run passed with `changed_count=0`, `blocked_count=0`.
- Target governance consistency passed with `drift_count=0`.
- Target rollout contract passed with `errors=[]`.
- Full build, Runtime, Contract, and doctor gates passed; doctor retained the known `WARN codex-capability-degraded` host-capability warning.

## Compatibility
- Existing milestone auto-commit behavior is unchanged unless callers explicitly pass `-DisableMilestoneAutoCommit` or `-DisableAutoCommit`.
- `ApplyAllFeatures` still runs governance baseline sync, runtime flow, milestone gate, and managed-asset cleanup.
- The JSON parser change is backward compatible: exact JSON remains preferred, mixed stdout only falls back to extracting a JSON object or array.

## Rollback
- Revert `scripts/governance/gate-runner-common.ps1`, `scripts/governance/full-check.ps1`, `scripts/governance/fast-check.ps1`, `scripts/runtime-flow-preset.ps1`, `tests/runtime/test_governance_gate_runner.py`, `tests/runtime/test_runtime_flow_preset.py`, and this evidence file.
