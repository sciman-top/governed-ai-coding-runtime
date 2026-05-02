# 2026-05-02 Operator UI Cleanup Uninstall Integration

## Rule
- `R1`: current landing point is the operator UI/API entrypoint.
- `R6`: verification follows build -> runtime tests -> contract/invariant -> hotspot.
- `R8`: evidence records basis, commands, key output, compatibility, and rollback.
- `pre_change_review`: this slice exposes existing cleanup/uninstall governance paths through the operator surface without changing target-repo rule semantics.

## Pre Change Review
- `control_repo_manifest_and_rule_sources`: no rule manifest or managed-rule source is changed by this UI slice.
- `user_level_deployed_rule_files`: no user-level Codex/Claude/Gemini rule file is changed.
- `target_repo_deployed_rule_files`: no target project rule file is changed or distributed.
- `target_repo_gate_scripts_and_ci`: cleanup/uninstall still delegates to `scripts/runtime-flow-preset.ps1`, which preserves dry-run by default and requires `-ApplyManagedAssetRemoval` for real removal.
- `target_repo_repo_profile`: UI/API only selects targets and forwards explicit apply intent; repo-profile patch semantics remain owned by uninstall CLI.
- `target_repo_readme_and_operator_docs`: README zh/en/root usage text was updated to describe multi-target cleanup/uninstall.
- `current_official_tool_loading_docs`: no Codex/Claude/Gemini loading model change is introduced.
- `drift-integration decision`: integrate with existing `run.ps1` / `scripts/operator.ps1` / `scripts/runtime-flow-preset.ps1` paths instead of adding a parallel uninstall implementation.

## Changes
- Added `cleanup-targets` and `uninstall-governance` aliases to `run.ps1`.
- Added `CleanupTargets` and `UninstallGovernance` operator actions that call `runtime-flow-preset.ps1` with `-PruneRetiredManagedFiles` or `-UninstallGovernance`.
- Added 8770 API allowlist entries and support for `targets: [...]` batch dispatch.
- Added target repo checkboxes, a managed-removal apply switch, and cleanup/uninstall buttons to the interactive operator UI.
- Updated operator UI tests and entrypoint tests for new controls and batch uninstall dispatch.

## Commands
- `python -m py_compile scripts/serve-operator-ui.py packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action Help`
- `python -m unittest tests.runtime.test_operator_ui tests.runtime.test_operator_entrypoint`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action CleanupTargets -Target self-runtime -Mode quick -DryRun`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action UninstallGovernance -Target self-runtime -Mode quick -DryRun`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action OperatorUi -UiLanguage zh-CN`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator-ui-service.ps1 -Action Restart -UiLanguage zh-CN -Port 8770`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator-ui-service.ps1 -Action Status`
- `Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8770/?lang=zh-CN`

## Evidence
- Python bytecode compile passed.
- Operator help renders `CleanupTargets` and `UninstallGovernance`.
- Focused UI/entrypoint tests passed: 26 tests in 19.641s.
- Cleanup dry-run command rendered `runtime-flow-preset.ps1 -Target self-runtime -FlowMode daily -Mode quick -Json -PruneRetiredManagedFiles`.
- Uninstall dry-run command rendered `runtime-flow-preset.ps1 -Target self-runtime -FlowMode daily -Mode quick -Json -UninstallGovernance`.
- Build gate passed: `OK python-bytecode`, `OK python-import`.
- First Runtime gate attempt executed 99 files; the new focused UI/operator tests passed, and the run failed before evidence existed for concurrent sensitive managed-asset uninstall review-fix changes.
- Runtime gate rerun passed after evidence was present: `OK runtime-unittest`, `OK runtime-service-parity`, `OK runtime-service-wrapper-drift-guard`.
- Contract/invariant gate passed, including `OK agent-rule-sync`, `OK pre-change-review`, and `OK functional-effectiveness`.
- Hotspot gate passed via `doctor-runtime.ps1`; only existing `WARN codex-capability-degraded` remained.
- 8770 service restart passed; status reported `ready=true` for `http://127.0.0.1:8770/?lang=zh-CN`.
- HTTP page verification passed with expected markers: `一键清理退役文件`, `一键卸载治理`, `ui-target-all`, `data-ui-target-option`, `ui-apply-removal`, `apply_managed_asset_removal`.

## Compatibility
- Existing `/api/run` payloads with single `target` remain supported.
- Batch target selection is opt-in via `targets`.
- Cleanup/uninstall actions still dry-run unless `apply_managed_asset_removal=true` and UI dry-run is off.
- Existing all-target behavior still uses `__all__` and delegates to the established runtime-flow all-target path.

## Rollback
- Revert this file plus:
  - `README.md`
  - `README.zh-CN.md`
  - `README.en.md`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py`
  - `run.ps1`
  - `scripts/operator.ps1`
  - `scripts/serve-operator-ui.py`
  - `tests/runtime/test_operator_entrypoint.py`
  - `tests/runtime/test_operator_ui.py`
