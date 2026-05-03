# 2026-05-03 Target Run KPI And Effect Report Refresh

## Goal

Keep target-repo speed evidence current when `scripts/runtime-flow-preset.ps1 -ExportTargetRepoRuns` writes fresh target-run JSON. The change is intentionally scoped to evidence refresh coupling: exported run JSON now refreshes `kpi-latest.json`, `kpi-rolling.json`, and existing `effect-report-*.json` files together.

## pre_change_review

- `pre_change_review`: required because this change modifies `scripts/runtime-flow-preset.ps1`, a sensitive target-repo orchestration entrypoint.
- `control_repo_manifest_and_rule_sources`: reviewed current `rules/manifest.json` ownership boundary and confirmed this patch does not change managed rule source files or distributed rule contents.
- `user_level_deployed_rule_files`: no user-level `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` files are changed by this patch.
- `target_repo_deployed_rule_files`: no target-repo deployed rule files are changed; the run uses existing catalog/profile commands.
- `target_repo_gate_scripts_and_ci`: reviewed `scripts/runtime-flow-preset.ps1`, `scripts/export-target-repo-speed-kpi.py`, `scripts/build-target-repo-reuse-effect-report.py`, `scripts/verify-target-repo-reuse-effect-report.py`, and `scripts/verify-repo.ps1 -Check Contract`; the gate order remains unchanged.
- `target_repo_repo_profile`: no target repo `.governed-ai/repo-profile.json` content is changed by this patch; `-SkipGovernanceBaselineSync` was used for the fresh all-target evidence run.
- `target_repo_readme_and_operator_docs`: no README/operator usage semantics change; `-ExportTargetRepoRuns` keeps the same public switch and only makes its evidence outputs complete.
- `current_official_tool_loading_docs`: no Codex/Claude/Gemini loading model assumptions are changed; current host posture remains `process_bridge` where native attach is unavailable.
- `drift-integration decision`: integrate evidence refresh at the runtime-flow export boundary rather than requiring a separate manual KPI/report command after every target run.

## Changes

- Added `Export-TargetRepoSpeedKpiSnapshots` to refresh latest and rolling KPI snapshots after target-run export.
- Added `Update-TargetRepoReuseEffectReports` to rebuild existing `effect-report-*.json` files after KPI refresh.
- Added JSON output fields `target_repo_speed_kpi` and `target_repo_effect_reports`.
- Added regression coverage in `tests/runtime/test_runtime_flow_preset.py`.

## Verification

- `python -m unittest tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests`: pass.
- `python -m unittest tests.runtime.test_target_repo_speed_kpi tests.runtime.test_target_repo_reuse_effect_feedback`: pass.
- Fresh all-target detection with export was executed:
  `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -FlowMode daily -Mode quick -SkipGovernanceBaselineSync -Json -ExportTargetRepoRuns -RuntimeFlowTimeoutSeconds 360 -BatchTimeoutSeconds 1800`.
- First all-target result exposed `self-runtime` contract failure caused by stale `effect-report-classroomtoolkit.json` after KPI refresh; root cause is now addressed by rebuilding existing effect reports during export.

## Rollback

Revert `scripts/runtime-flow-preset.ps1`, `tests/runtime/test_runtime_flow_preset.py`, this evidence file, and the generated `docs/change-evidence/target-repo-runs/*20260503*.json` / KPI / effect-report updates.
