# 2026-05-02 Managed Asset Uninstall Review Fixes

## Rule
- `pre_change_review`
- Core principle: `target_repo_managed_asset_retirement_before_removal`
- Risk: high for destructive apply paths.

## Pre Change Review
- `control_repo_manifest_and_rule_sources`: reviewed the managed asset rollout contract, governance baseline ownership fields, cleanup scripts, and `scripts/runtime-flow-preset.ps1` one-click surface.
- `user_level_deployed_rule_files`: no user-level rule file is edited by this fix; existing rule sync drift remains governed by `scripts/sync-agent-rules.py --scope All --fail-on-change` before any future rule distribution.
- `target_repo_deployed_rule_files`: no target project rule file is removed by this fix; uninstall remains explicit and dry-run/apply separated.
- `target_repo_gate_scripts_and_ci`: referenced managed files are now blocked before deletion so target CI/hooks are not broken by uninstall.
- `target_repo_repo_profile`: uninstall now removes only runtime-owned repo-profile fields declared by `repo_profile_field_ownership`; catalog and target-owned fields are preserved.
- `target_repo_readme_and_operator_docs`: existing managed-asset retirement plan already states dry-run-first, referenced-file blocking, repo-profile owned-field removal, and rollback evidence requirements; this fix aligns code to that documented contract.
- `current_official_tool_loading_docs`: no Codex/Claude/Gemini loading model change is introduced.
- `drift-integration decision`: this is a review-fix slice for existing managed asset removal code; unrelated dirty operator/UI/doc changes are not reverted or absorbed.

## Basis
- Review found that uninstall could delete active managed files even when `referenced_by` reported active references.
- One-click JSON output summarized destructive actions but dropped per-file candidates, blocked reasons, backup paths, and rollback evidence.
- Uninstall did not detach runtime-owned `.governed-ai/repo-profile.json` fields.
- Blocked destructive apply paths could partially delete safe candidates before reporting blocked.
- Shared JSON overlay removal by value lacks ownership proof and can remove target-owned values.

## Changes
- `scripts/prune-retired-managed-files.py` no longer deletes any candidate when blocked files exist.
- `scripts/uninstall-target-repo-governance.py` now:
  - blocks active/generated managed files with `referenced_by`;
  - applies no deletion or patch when any blocked item exists;
  - removes runtime-owned repo-profile fields only;
  - blocks `json_merge` shared-file uninstall unless ownership evidence is explicit.
- `scripts/runtime-flow-preset.ps1` now exposes full managed-action evidence in JSON, including candidate items, blocked files, deleted files, patched files, backup paths, and profile patch results.
- Regression tests cover referenced-file blocking, non-partial blocked apply, repo-profile field detach, and one-click evidence passthrough.

## Commands
- `python -m py_compile scripts/lib/target_repo_managed_assets.py scripts/inspect-target-repo-managed-assets.py scripts/prune-retired-managed-files.py scripts/uninstall-target-repo-governance.py`
- `python -m unittest tests.runtime.test_prune_retired_managed_files tests.runtime.test_uninstall_target_repo_governance tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_single_target_dry_runs_managed_asset_prune_and_uninstall`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`

## Evidence
- Python bytecode compile passed for managed asset scripts.
- Focused regression tests passed: 9 tests in 2.510s.
- Build gate passed: `OK python-bytecode`, `OK python-import`.
- First Runtime gate attempt executed 99 test files; cleanup/uninstall focused files passed, but the run failed because this pre-change evidence file did not exist yet and pre-change review correctly blocked sensitive-path changes.
- After adding this evidence file, the CLI regression passed: `test_run_default_profile_executes_repo_local_quick_gate`.
- Focused regression tests passed again: 9 tests in 2.735s.
- Runtime gate passed: 99 test files in 172.613s, failures=0.
- Contract gate passed, including `OK pre-change-review` and `OK functional-effectiveness`.
- Hotspot gate passed with existing `WARN codex-capability-degraded`.

## Compatibility
- Normal apply flows still do not remove files.
- Destructive removal still requires explicit prune/uninstall flags and `-ApplyManagedAssetRemoval`.
- Shared JSON uninstall is more conservative until ownership evidence is available.

## Rollback
- Revert this file plus:
  - `scripts/prune-retired-managed-files.py`
  - `scripts/uninstall-target-repo-governance.py`
  - `scripts/runtime-flow-preset.ps1`
  - `tests/runtime/test_prune_retired_managed_files.py`
  - `tests/runtime/test_uninstall_target_repo_governance.py`
  - `tests/runtime/test_runtime_flow_preset.py`
