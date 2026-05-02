# 2026-05-02 Retired Cleanup Delete Contract Hardening

## Rule
- `R1`: current landing point is the retired managed-file cleanup path.
- `R4`: default real deletion is allowed only for bounded, hash-matched, unreferenced retired managed files.
- `R8`: deletion must expose proof, backup, rollback, and manifest evidence.

## Pre Change Review
- `pre_change_review`
- `control_repo_manifest_and_rule_sources`: reviewed `rules/manifest.json`, project `AGENTS.md`, the current managed asset cleanup plan, and existing managed-asset evidence before hardening the cleanup contract; this slice does not edit rule source files.
- `user_level_deployed_rule_files`: no user-level rule file is changed by this slice; rule deployment drift remains covered by the existing `scripts/sync-agent-rules.py --scope All --fail-on-change` path.
- `target_repo_deployed_rule_files`: no target project rule file is changed by this slice; deletion is constrained to target files already registered in `retired_managed_files`.
- `target_repo_gate_scripts_and_ci`: reviewed `scripts/runtime-flow-preset.ps1`, `scripts/prune-retired-managed-files.py`, and managed-asset tests so default apply-all cleanup cannot run after a failed target flow and reports rollback evidence.
- `target_repo_repo_profile`: repo profiles are not mutated by retired-file cleanup; profile semantics remain inputs to target flow execution only.
- `target_repo_readme_and_operator_docs`: updated operator-facing docs so apply-all default deletion and detect-only escape hatch are explicit.
- `current_official_tool_loading_docs`: no tool loading model change is introduced; existing Codex project/global rule loading semantics remain unchanged.
- `drift-integration decision`: integrate cleanup-script, runtime-flow JSON, docs, and tests together; do not treat a default delete behavior change as complete without evidence and focused gates.

## Basis
- `ApplyAllFeatures` now defaults to real deletion for proven-safe retired managed files, so the cleanup result needs machine-readable proof fields and a stable rollback manifest path.
- A silent or ambiguous delete result would make UI/history evidence hard to audit even when the deletion itself is hash-guarded.

## Changes
- Added `operation_type`, `deletion_policy`, and `safety_contract.delete_requires` to `scripts/prune-retired-managed-files.py` output.
- Kept deletion guarded by baseline registration, bounded repo-relative path resolution, target hash match, no active references, backup, and deletion-time hash recheck.
- Added backup-local `manifest.json` output for apply mode and surfaced `manifest_path`, `operation_type`, and `deletion_policy` through `scripts/runtime-flow-preset.ps1` JSON summaries.
- Extended tests for backup proof, manifest output, deletion-time mutation blocking, and runtime-flow summary fields.

## Commands
- `python -m unittest tests.runtime.test_prune_retired_managed_files tests.runtime.test_operator_entrypoint`
- `python -m unittest tests.runtime.test_prune_retired_managed_files tests.runtime.test_runtime_flow_preset tests.runtime.test_operator_entrypoint`
- `python -m py_compile scripts/prune-retired-managed-files.py scripts/lib/target_repo_managed_assets.py`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`

## Evidence
- Focused prune/operator tests passed: 31 tests.
- Focused prune/runtime-flow/operator tests passed: 51 tests.
- Python bytecode compile passed.
- First Runtime gate attempt ran 99 test files and confirmed the touched focused suites passed, but failed closed because this evidence file did not yet exist and pre-change review tokens were missing for `scripts/runtime-flow-preset.ps1`.
- Runtime gate rerun passed: 99 test files, failures=0; `OK runtime-unittest`, `OK runtime-service-parity`, `OK runtime-service-wrapper-drift-guard`.
- Build gate passed: `OK python-bytecode`, `OK python-import`.
- Contract gate passed, including `OK pre-change-review`, `OK target-repo-governance-consistency`, and `OK functional-effectiveness`.
- Hotspot gate passed via `doctor-runtime.ps1`; existing `WARN codex-capability-degraded` remained.

## Compatibility
- Existing consumers can keep reading `summary`, `delete_candidates`, `deleted_files`, `blocked_files`, and `missing_files`.
- New fields are additive and make real-delete results easier to audit.
- `CleanupTargets` and `UninstallGovernance` still require explicit `-ApplyManagedAssetRemoval`; `ApplyAllFeatures -DisableManagedAssetRemoval` remains the detect-only escape hatch.

## Rollback
- Revert `scripts/prune-retired-managed-files.py`, `scripts/runtime-flow-preset.ps1`, managed-asset tests, operator docs, and this evidence file.
- Restore deleted target files by copying from the `backup_root/manifest.json` backup paths recorded by the cleanup payload.
