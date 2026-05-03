# 20260504 Managed File Replace Legacy Contract

## Rule
- `R1`: current landing point is target-repo managed-file mode handling; target destination is the one-click governance managed-file contract.
- `R4`: low-risk output-contract hardening; this does not expand overwrite authority or change the active target baseline.
- `R8`: managed-file mode behavior is now visible through machine-readable output fields and regression tests.

## pre_change_review
- `pre_change_review`: required because this change modifies target-governance apply, consistency, rollout-contract, and managed-asset inspection scripts.
- `control_repo_manifest_and_rule_sources`: no `rules/manifest.json` entry or rule source file is changed.
- `user_level_deployed_rule_files`: no deployed user-level rule file is changed.
- `target_repo_deployed_rule_files`: no deployed target project rule file is changed.
- `target_repo_gate_scripts_and_ci`: reviewed managed-file apply, consistency, rollout-contract, and inventory paths before changing outputs.
- `target_repo_repo_profile`: no target repo profile schema, catalog field, or target profile value is changed.
- `target_repo_readme_and_operator_docs`: no operator command surface is changed; output fields are additive JSON contract metadata.
- `current_official_tool_loading_docs`: no Codex, Claude, or Gemini loading semantics are changed.
- `drift-integration decision`: keep fail-closed drift handling. `replace` remains accepted only as a legacy fail-closed alias and must not be interpreted as silent overwrite authority.

## Basis
- The active baseline already uses `block_on_drift` and `json_merge`; no active managed-file entry uses `replace`.
- Existing apply behavior already blocked existing target drift for both `replace` and `block_on_drift`.
- The remaining risk was naming ambiguity: future maintainers could read `replace` as permission to silently overwrite target-local drift.

## Changes
- Added `scripts/lib/target_repo_managed_file_modes.py` as the shared source for allowed modes and mode metadata.
- Added additive output fields:
  - `mode_status=legacy_fail_closed` for `replace`
  - `overwrite_policy=create_missing_block_existing_drift` for `replace` and `block_on_drift`
  - `overwrite_policy=json_merge_overlay_preserve_target_local_keys` for `json_merge`
- Updated apply, consistency verification, rollout-contract validation, and managed-asset inventory to use the shared mode contract.
- Updated tests so `replace` drift explicitly proves legacy fail-closed behavior.

## Commands
- `python -m unittest tests.runtime.test_target_repo_governance_consistency`
- `python -m unittest tests.runtime.test_target_repo_rollout_contract tests.runtime.test_target_repo_managed_asset_inventory`
- `python scripts/verify-target-repo-rollout-contract.py`
- `python scripts/verify-target-repo-governance-consistency.py`
- `python scripts/verify-pre-change-review.py --repo-root .`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

## Evidence
- Target-governance consistency tests passed: 30 tests.
- Rollout contract and managed-asset inventory tests passed: 14 tests.
- Rollout contract verifier passed: `status=pass`, `capability_count=14`, `feature_count=6`.
- Live target governance consistency passed: `target_count=5`, `drift_count=0`.
- Pre-change review gate passed with this evidence file as the matched evidence.
- Build gate passed: `OK python-bytecode`, `OK python-import`.
- Runtime gate passed: 103 test files, `failures=0`, `OK runtime-unittest`, `OK runtime-service-parity`, `OK runtime-service-wrapper-drift-guard`.
- Contract gate passed, including `OK target-repo-rollout-contract`, `OK target-repo-governance-consistency`, `OK agent-rule-sync`, `OK pre-change-review`, and `OK functional-effectiveness`.
- Hotspot gate passed via `doctor-runtime.ps1`; existing `WARN codex-capability-degraded` remained.

## Compatibility
- Existing `management_mode` values remain accepted.
- Existing statuses, drift reasons, `conflict_policy`, hashes, and recommended-action fields remain present.
- New JSON fields are additive.
- No target repo is modified by this slice.

## Rollback
- Revert `scripts/lib/target_repo_managed_file_modes.py`, the changed target-governance scripts, the related tests, and this evidence file.
