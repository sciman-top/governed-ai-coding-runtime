# 20260502 Managed File Governance Modes

## Goal
- Reduce unnecessary hard-overwrite behavior in target-repo managed files while keeping one-click governance fail-closed.
- Add a reusable managed-file mode for files that may exist in target repos with legitimate local drift and therefore must not be silently overwritten.

## Changes
- Kept project rule sync auto-merge and managed-file `json_merge` behavior from the current rollout batch in place.
- Extended `scripts/apply-target-repo-governance.py` to support `management_mode=block_on_drift`.
- Extended `scripts/verify-target-repo-governance-consistency.py` to validate `block_on_drift` entries consistently.
- `block_on_drift` semantics:
  - missing target file: create from source template during apply
  - existing target file with content drift: return `status=blocked`, report `blocked_managed_files`, and do not overwrite the target file
- Added runtime tests for `block_on_drift` apply/create/block behavior and consistency drift detection.

## Commands And Evidence
- `python -m unittest tests.runtime.test_target_repo_governance_consistency tests.runtime.test_target_repo_rollout_contract tests.runtime.test_agent_rule_sync`
  - result: pass
- `python scripts/verify-target-repo-rollout-contract.py`
  - result: pass
- `python scripts/verify-target-repo-governance-consistency.py`
  - result: pass, `target_count=5`, `drift_count=0`
- `python -m unittest tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_all_targets_onboard_applies_governance_baseline tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_all_targets_apply_all_features`
  - result: pass

## Rollback
- Revert `scripts/apply-target-repo-governance.py` and `scripts/verify-target-repo-governance-consistency.py` to remove `block_on_drift`.
- Revert the new runtime tests if the mode is intentionally abandoned.
- If a future baseline starts using `block_on_drift`, remove or change those entries before re-running one-click governance apply.
