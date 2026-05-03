# 2026-05-03 GAP-151 Managed Asset Export Evidence

## Rule
- `R1`: current landing point is `scripts/runtime-flow-preset.ps1` target-run evidence export; target home is `GAP-151` active-target managed-asset dry-run closeout evidence.
- `R4`: medium-risk runtime-flow script change; this slice only exports already-computed dry-run action results and does not enable apply.
- `R8`: record basis, commands, evidence, compatibility, and rollback before changing the sensitive runtime-flow script.

## Pre-Change Review
- Control entrypoint: `scripts/runtime-flow-preset.ps1`.
- Regression surface: `tests/runtime/test_runtime_flow_preset.py`.
- Evidence target: `docs/change-evidence/target-repo-runs/*-daily-*.json`.
- Target-repo safety posture: `-PruneRetiredManagedFiles` and `-UninstallGovernance` remain dry-run unless `-ApplyManagedAssetRemoval` is explicitly supplied.
- Platform/tooling review: no Codex/Claude/Gemini rule source, provider, MCP, auth, login chain, or permission setting is changed.

## pre_change_review
- `control_repo_manifest_and_rule_sources`: reviewed the loaded project `AGENTS.md` contract, `rules/manifest.json` ownership posture, and the existing managed-asset plan before touching runtime-flow export behavior.
- `user_level_deployed_rule_files`: no user-level deployed Codex/Claude/Gemini rule file is changed by this slice.
- `target_repo_deployed_rule_files`: no target-repo deployed rule file is changed by this slice; target-run JSON export is control-repo evidence only.
- `target_repo_gate_scripts_and_ci`: reviewed `scripts/verify-repo.ps1` gate expectations and added a focused runtime-flow regression before closeout.
- `target_repo_repo_profile`: no target repo `repo-profile.json` is edited by this slice; uninstall profile candidates remain dry-run evidence.
- `target_repo_readme_and_operator_docs`: no target README or operator guide is distributed by this slice.
- `current_official_tool_loading_docs`: no tool loading model is changed; current session rules remain context while deterministic enforcement stays in scripts and gates.
- `drift-integration decision`: integrate the missing export fields in the control runtime first, discard the failed dirty self-runtime run as closeout evidence, then rerun active-target dry-run from a clean control repo.

## Basis
- `GAP-151` acceptance requires durable all-target dry-run reports for prune and uninstall.
- Console JSON already contained `prune_retired_managed_files` and `uninstall_governance`, but exported target-run JSON omitted those action sections.
- The missing export made the all-target dry-run evidence non-durable, so GAP-151 could not be honestly closed.

## Changes
- Added `prune_retired_managed_files` and `uninstall_governance` sections to target-run JSON export when the target run contains managed-asset action results.
- Reused the existing `Convert-ManagedAssetActionForJson` converter so console and file evidence keep the same shape.
- Extended the single-target dry-run regression to enable `-ExportTargetRepoRuns` and assert that the exported JSON includes both managed-asset dry-run sections.

## Verification
- `python -m unittest tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_single_target_dry_runs_managed_asset_prune_and_uninstall`: pass; `Ran 1 test in 2.219s`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`: pass; `OK powershell-parse`, `OK issue-seeding-render`.
- Commit pre-check initially blocked as expected because `scripts/runtime-flow-preset.ps1` is sensitive and required this pre-change review evidence.

## GAP-151 Closeout Evidence
- Active-target dry-run command: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -FlowMode daily -Mode quick -PruneRetiredManagedFiles -UninstallGovernance -ExportTargetRepoRuns -TargetParallelism 5 -BatchTimeoutSeconds 900 -Json`.
- Exit code: `1`, expected for this closeout command because `UninstallGovernance` dry-run fails closed on blocked active references or drifted generated files.
- Batch result: `target_count=5`, `failure_count=5`, `batch_timed_out=false`, `batch_elapsed_seconds=352`, `apply_managed_asset_removal=false`.
- Normal target flow result: every active target exported `overall_status=pass` with `runtime_check.exit_code=0`.
- Prune result: every active target exported `prune_retired_managed_files.status=pass`, `dry_run=true`, `apply=false`, `deleted=0`, `blocked=0`.
- Uninstall result: every active target exported `uninstall_governance.status=blocked`, `dry_run=true`, `apply=false`, `deleted=0`; block counts were `classroomtoolkit=2`, `github-toolkit=1`, `self-runtime=2`, `skills-manager=2`, and `vps-ssh-launcher=3`.
- Exported run evidence:
  - `docs/change-evidence/target-repo-runs/classroomtoolkit-daily-20260503190522.json`
  - `docs/change-evidence/target-repo-runs/github-toolkit-daily-20260503190522.json`
  - `docs/change-evidence/target-repo-runs/self-runtime-daily-20260503190522.json`
  - `docs/change-evidence/target-repo-runs/skills-manager-daily-20260503190522.json`
  - `docs/change-evidence/target-repo-runs/vps-ssh-launcher-daily-20260503190522.json`
- Target repo mutation check: before the dry-run all five active target repos were clean; after the dry-run `D:\CODE\ClassroomToolkit`, `D:\CODE\github-toolkit`, `D:\CODE\skills-manager`, and `D:\CODE\vps-ssh-launcher` remained clean. The control repo only received generated evidence files under `docs/change-evidence/target-repo-runs/`.
- Generated feedback artifacts: `docs/change-evidence/target-repo-runs/kpi-latest.json`, `docs/change-evidence/target-repo-runs/kpi-rolling.json`, and `docs/change-evidence/target-repo-runs/effect-report-classroomtoolkit.json`.

## Hard-Gate Closeout
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`: pass; `OK python-bytecode`, `OK python-import`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`: pass; `102` test files, `failures=0`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`: pass; includes `OK target-repo-rollout-contract`, `OK target-repo-governance-consistency`, `OK pre-change-review`, and `OK functional-effectiveness`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`: pass; hard checks OK with existing `WARN codex-capability-degraded`.
- `python scripts/verify-target-repo-rollout-contract.py`: pass; `capability_count=14`, `feature_count=6`, `errors=[]`.
- `python scripts/verify-target-repo-governance-consistency.py`: pass; `target_count=5`, `drift_count=0`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`: pass; includes `OK autonomous-next-work-selection` and `OK post-closeout-queue-sync`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`: pass; `completed_task_count=136`, `active_task_count=0`.
- `python scripts/select-next-work.py`: pass; `gate_state=pass`, `source_state=fresh`, `evidence_state=stale`, `ltp_decision=defer_all`, `next_action=refresh_evidence_first`.

## Compatibility
- Existing target-run JSON consumers continue to receive the previous top-level fields.
- The new fields are additive and appear only when managed-asset action results exist.
- Dry-run/apply semantics are unchanged; this slice does not delete, patch, or sync any target repo files.
- GAP-151 is closed by dry-run evidence and hard gates; real governance uninstall remains explicitly blocked unless a future operator supplies destructive intent and resolves active references or drift first.
- No `LTP-01..06` package is selected or implemented by this closeout; selector output remains `ltp_decision=defer_all`.

## Rollback
- Revert this evidence file and the related changes to `scripts/runtime-flow-preset.ps1` and `tests/runtime/test_runtime_flow_preset.py`.
- If any exported target-run JSON produced by this slice is considered invalid, remove the affected `docs/change-evidence/target-repo-runs/*-daily-*.json` files and regenerate from the prior runtime-flow version.
- Revert the GAP-151 status updates in `docs/plans/target-repo-managed-asset-retirement-and-uninstall-plan.md`, `docs/backlog/issue-ready-backlog.md`, `docs/backlog/README.md`, and `docs/README.md` if a later audit rejects the `20260503190522` closeout run.
