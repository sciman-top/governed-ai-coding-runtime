# 2026-05-02 Target Repo Gate Speed Review And Effect

## Rule
- Core principle: `effect_feedback_before_completion`
- Risk: medium

## Pre Change Review
- `pre_change_review`
- `control_repo_manifest_and_rule_sources`: reviewed `rules/manifest.json`, `AGENTS.md`, and the project-level rule contract before changing gate/runtime scripts.
- `user_level_deployed_rule_files`: no user-level rule file was changed by this task.
- `target_repo_deployed_rule_files`: no target repo rule file was changed by this task.
- `target_repo_gate_scripts_and_ci`: reviewed target profiles under `D:\CODE\*\.governed-ai\repo-profile.json`, `scripts/governance/gate-runner-common.ps1`, and `scripts/runtime-flow-preset.ps1`.
- `target_repo_repo_profile`: reviewed generated `quick_gate_commands`, `full_gate_commands`, timeout fields, and `satisfies_gate_ids`.
- `target_repo_readme_and_operator_docs`: no README/operator doc changed; this evidence records the operator-facing review result.
- `current_official_tool_loading_docs`: searched official/project docs for GitHub Actions, pytest, pytest-xdist, Microsoft `dotnet test`, Pester, Nx, Turborepo, and Bazel on 2026-05-02.
- `drift-integration decision`: this task does not sync managed rule files; runtime script changes stay in the control repo and target repo profiles remain observed inputs.

## Basis
- Coding feedback speed depends on layered gates, changed-scope execution, cache reuse, bounded timeouts, and structured duration evidence.
- Existing target repo speed profiles already materialize quick/full gate groups and per-gate timeouts, but the all-target JSON did not always report real elapsed time and did not expose per-target durations.
- `runtime-flow-preset.ps1` killed only the parent worker process on timeout; a hanging child test process could outlive the guard.

## External Practices
- GitHub Actions supports job/step `timeout-minutes`, matrix `fail-fast`, `max-parallel`, `concurrency.cancel-in-progress`, and dependency caching.
- pytest supports `--maxfail`, last-failed/failed-first cache workflows, and duration reporting.
- pytest-xdist supports CPU-level parallel test distribution with `-n auto`.
- Microsoft `dotnet test` supports `--filter`, `--no-build`, `--no-restore`, and `--blame-hang-timeout`.
- Pester supports tag filters and test result output.
- Nx affected runs, Turborepo caching/remote caching, and Bazel remote caching all reinforce the same pattern: run the smallest valid task set, cache deterministic work, and keep enough evidence to prove correctness.

## Changes
- Added `Stop-ProcessTree` in `scripts/runtime-flow-preset.ps1` and used it for runtime command and parallel batch timeouts.
- Added structured duration evidence: `duration_ms`, `flow_duration_ms`, `target_duration_ms`, `governance_sync_duration_ms`, and nonzero `batch_elapsed_seconds` even without a batch timeout.
- Added exported target run duration fields so later KPI/effect reports can compare real wall-clock cost.
- Added regression coverage for elapsed reporting without `-BatchTimeoutSeconds` and per-target duration reporting in all-target JSON.

## Commands
- `python -m unittest tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_all_targets_json_reports_elapsed_without_batch_timeout tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_all_targets_json_supports_target_parallelism tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_all_targets_batch_timeout_guard`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -FlowMode daily -Json -TargetParallelism 1 -RuntimeFlowTimeoutSeconds 300 -BatchTimeoutSeconds 1200`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target self-runtime -FlowMode daily -Json -RuntimeFlowTimeoutSeconds 300`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -FlowMode daily -Json -TargetParallelism 1 -RuntimeFlowTimeoutSeconds 300 -BatchTimeoutSeconds 1200`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -FlowMode daily -Json -TargetParallelism 3 -RuntimeFlowTimeoutSeconds 300 -BatchTimeoutSeconds 1200`
- `python -m unittest tests.runtime.test_governance_gate_runner tests.runtime.test_target_repo_governance_consistency tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_apply_governance_baseline_only_bootstraps_blank_target tests.runtime.test_target_repo_rollout_contract tests.runtime.test_target_repo_speed_kpi`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

## Evidence
- Focused runtime-flow tests passed: 3 tests in 9.983s.
- Serial all-target daily baseline wrote `docs/change-evidence/target-repo-speed-20260502/daily-serial-targetparallelism1.json`.
- Serial all-target daily baseline: measured 261.258s, payload `batch_elapsed_seconds=260`, `target_count=5`, `failure_count=1`.
- Serial target durations: `classroomtoolkit=91030ms`, `github-toolkit=11927ms`, `self-runtime=119929ms`, `skills-manager=19794ms`, `vps-ssh-launcher=17644ms`.
- `self-runtime` failure was contract pre-change-review evidence, not a test timeout: `contract=fail`, `test=pass`.
- After adding this evidence, `self-runtime` daily passed in 103.992s with `test=pass` and `contract=pass`.
- All-green serial all-target daily wrote `docs/change-evidence/target-repo-speed-20260502/daily-serial-targetparallelism1-after-evidence.json`: measured 308.826s, payload `batch_elapsed_seconds=308`, `target_count=5`, `failure_count=0`.
- All-green serial target durations: `classroomtoolkit=131157ms`, `github-toolkit=16447ms`, `self-runtime=120818ms`, `skills-manager=19459ms`, `vps-ssh-launcher=20038ms`.
- All-green parallel all-target daily wrote `docs/change-evidence/target-repo-speed-20260502/daily-parallel-targetparallelism3-after-evidence.json`: measured 142.528s, payload `batch_elapsed_seconds=141`, `target_count=5`, `failure_count=0`.
- All-green parallel target durations: `github-toolkit=18610ms`, `skills-manager=33315ms`, `vps-ssh-launcher=26144ms`, `classroomtoolkit=137152ms`, `self-runtime=141520ms`.
- Effect: `TargetParallelism 3` reduced all-target daily wall time from 308.826s to 142.528s, a 53.85% reduction and 2.17x speedup for this run.
- Quick feedback passed: 49 tests in 27.026s.
- Build gate passed: `OK python-bytecode`, `OK python-import`.
- Runtime gate passed after rerun: 95 test files in 189.713s, failures=0.
- Contract gate passed: includes `OK pre-change-review` and `OK functional-effectiveness`.
- Hotspot gate passed with existing `WARN codex-capability-degraded`.

## Rollback
- Revert `scripts/runtime-flow-preset.ps1` and `tests/runtime/test_runtime_flow_preset.py`.
- Remove `docs/change-evidence/20260502-target-repo-gate-speed-review-and-effect.md` and `docs/change-evidence/target-repo-speed-20260502/` if the evidence snapshot is no longer needed.
