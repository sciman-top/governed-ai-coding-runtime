# 20260425 Target Repo Rollout Contract Hardening

## Goal
- Stop repeated drift where target-repo features are documented or partially implemented but not forced through the unified one-click rollout path.
- Make milestone auto-commit requirements machine-verifiable, including Chinese commit message templates.

## Root Cause
- The existing implementation had working switches such as `-ApplyAllFeatures` and `-ApplyFeatureBaselineAndMilestoneCommit`, but the invariant lived in docs and operator memory rather than a hard contract.
- `verify-repo.ps1 -Check Contract` only checked target profile consistency after sync; it did not fail when a new target-repo baseline field was added without being registered as an all-features rollout item.
- Auto-commit existed in `auto_commit_policy`, but no Contract gate verified the milestone trigger, required markers, `require_all_required_gates_pass`, or Chinese message tokens.

## Changes
- Added `docs/targets/target-repo-rollout-contract.json` as the machine-readable source for:
  - canonical all-target one-click entrypoint
  - target-repo capability classification (`profile_baseline`, `runtime_orchestrated`, `repo_local_artifact`, `runtime_only`)
  - target profile features that must be covered by `ApplyAllFeatures`
  - milestone auto-commit trigger and Chinese message requirements
- Added `scripts/verify-target-repo-rollout-contract.py` to fail closed when:
  - a target-repo-related capability is not classified with a distribution decision and reason
  - a `profile_baseline` capability is not represented in both `required_profile_overrides` and `target_profile_features`
  - a non-profile capability tries to declare baseline fields
  - a baseline override field is not registered in the rollout contract
  - a registered feature is not covered by `apply_all_features`
  - the canonical one-click script does not expose the declared arguments or JSON fields
  - milestone auto-commit is disabled, missing the `milestone` trigger, missing required markers, or using a non-Chinese/incomplete commit template
- Wired the new verifier into `scripts/verify-repo.ps1 -Check Contract`.
- Added regression tests in `tests/runtime/test_target_repo_rollout_contract.py`.

## Verification
- `python -m unittest tests.runtime.test_target_repo_rollout_contract`
- `python scripts/verify-target-repo-rollout-contract.py`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`

## Rollback
- Revert:
  - `docs/targets/target-repo-rollout-contract.json`
  - `scripts/verify-target-repo-rollout-contract.py`
  - `tests/runtime/test_target_repo_rollout_contract.py`
  - `scripts/verify-repo.ps1`
  - this evidence file and its index entry
