# 20260502 Target Profile Ownership And Runtime Contracts

## Goal
- Close the remaining gap where target-repo rollout knew feature classification but did not yet expose a machine-checkable repo-profile ownership contract.
- Close the remaining gap where `runtime_orchestrated` capabilities were classified in prose/metadata but not all tied to explicit execution evidence in the unified one-click contract.
- Move at least one real managed file from “engine supports `block_on_drift`” to “baseline strategy actually uses it”.

## Changes
- Added `repo_profile_field_ownership` to `docs/targets/target-repo-governance-baseline.json`.
- Added `repo_profile_ownership_contract` to `docs/targets/target-repo-rollout-contract.json`.
- Added `runtime_orchestrated_capability_contracts` to `docs/targets/target-repo-rollout-contract.json`.
- Updated `scripts/verify-target-repo-rollout-contract.py` to fail-closed when:
  - repo-profile ownership lists drift from baseline override/runtime-derived/catalog-input reality
  - a runtime-orchestrated capability is missing an execution contract
  - a runtime-orchestrated capability contract references JSON fields or script tokens not present in `runtime-flow-preset.ps1`
- Updated `scripts/apply-target-repo-governance.py` and `scripts/verify-target-repo-governance-consistency.py` to validate repo-profile ownership metadata when present while still inferring defaults for minimal test baselines.
- Switched `.claude/hooks/governed-pre-tool-use.py` from `replace` to `block_on_drift` in the active baseline and rollout contract.

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
- Revert ownership and runtime-orchestrated contract additions in `docs/targets/target-repo-governance-baseline.json` and `docs/targets/target-repo-rollout-contract.json`.
- Revert validation changes in `scripts/verify-target-repo-rollout-contract.py`, `scripts/apply-target-repo-governance.py`, and `scripts/verify-target-repo-governance-consistency.py`.
- Revert the `.claude/hooks/governed-pre-tool-use.py` `management_mode` change if future target repos require hard replacement again.
