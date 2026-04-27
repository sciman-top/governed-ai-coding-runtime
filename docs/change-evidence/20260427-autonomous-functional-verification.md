# 2026-04-27 Autonomous Functional Verification

## Goal
- Autonomously execute the project runtime, verification, preset, package, target-flow, and write-governance surfaces.
- Fix real failures found during execution instead of stopping at diagnostics.

## Root Cause And Changes
- `scripts/run-governed-task.py run --task-id <new-id>` failed with `FileNotFoundError` because `run_task()` only created a task when `task_id` was omitted.
- `scripts/run-governed-task.py run --mode quick` ignored the loaded repo profile and used the fixed built-in verification plan, so the current repo quick smoke ran the long Runtime gate instead of `quick_gate_commands`.
- Fixed `run_task()` to create a missing explicit task id before execution.
- Switched `run_task()` to `build_repo_profile_verification_plan()` so `quick/full/l1/l2/l3` honor the selected repo profile.
- Changed the CLI default `--profile` to `schemas/examples/repo-profile/governed-ai-coding-runtime.example.json`, keeping explicit `--profile` for sample/external profiles.
- Added regression coverage for explicit task id creation and default profile quick execution.

## Verification
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1` -> pass.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` -> pass, 444 runtime tests and 12 service tests.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` -> pass.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1` -> pass.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts` -> pass.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs` -> pass.
- `python -m unittest tests.runtime.test_run_governed_task_service_wrapper.RunGovernedTaskServiceWrapperTests.test_run_task_with_new_explicit_task_id_creates_task_before_execution -v` -> pass.
- `python -m unittest tests.runtime.test_run_governed_task_cli.RunGovernedTaskCliTests.test_run_default_profile_executes_repo_local_quick_gate -v` -> pass.
- `python scripts/run-governed-task.py --runtime-root .runtime\smoke-self-profile run --mode quick --json --task-id codex-runtime-self-profile-20260427 --goal "Self profile smoke" --scope "functional verification" --repo governed-ai-coding-runtime` -> pass; task state `delivered`.
- `python scripts/run-governed-task.py --runtime-root .runtime\smoke-default-full run --json --task-id codex-runtime-default-full-20260427 --goal "Default full governed run" --scope "functional verification" --repo governed-ai-coding-runtime` -> pass; task state `delivered`, verification refs include `build/test/contract/doctor`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -ApplyGovernanceBaselineOnly -Json -BatchTimeoutSeconds 300 -GovernanceSyncTimeoutSeconds 120` -> pass; 5 targets, 0 failures, 0 changed fields.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -FlowMode daily -Mode quick -SkipGovernanceBaselineSync -Json -RuntimeFlowTimeoutSeconds 360 -BatchTimeoutSeconds 1800 -FailFast` -> pass; 5 targets, 0 failures, elapsed 167 seconds.
- Temporary target attach/write smoke -> pass; `runtime-flow.ps1` created `.governed-ai` light pack, ran quick gates, executed low-tier write to `docs/write-smoke.txt`, and produced `live_closure_ready`.
- `python scripts/run-readonly-trial.py --goal "inspect repository" --scope "readonly trial" --acceptance "readonly request accepted" --repo-profile "schemas/examples/repo-profile/python-service.example.json" --target-path "src/service.py" --max-steps 1 --max-minutes 5` -> pass.
- `python scripts/run-codex-adapter-trial.py --repo-id "python-service" --task-id "task-codex-trial" --binding-id "binding-python-service"` -> pass.
- `python scripts/run-multi-repo-trial.py` -> pass; 2 repo profiles, 0 gate failures.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/package-runtime.ps1` -> pass; provenance verification status `verified`.
- `python scripts/serve-operator-ui.py` -> pass; wrote `.runtime/artifacts/operator-ui/index.html`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/install-repo-hooks.ps1` -> pass; `core.hooksPath=.githooks`.
- `python scripts/sync-agent-rules.py --scope All --fail-on-change` -> pass; 18 entries, 0 changed, 0 blocked.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\governance\fast-check.ps1 -RepoProfilePath schemas\examples\repo-profile\governed-ai-coding-runtime.example.json -WorkingDirectory . -Json` -> pass; `runtime-status` gate passed.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All` -> pass; 446 runtime tests, 12 service tests, build/contract/doctor/docs/scripts checks all OK.

## Rollback
- Code rollback:
  - `git restore -- scripts/run-governed-task.py tests/runtime/test_run_governed_task_cli.py tests/runtime/test_run_governed_task_service_wrapper.py docs/change-evidence/20260427-autonomous-functional-verification.md`
- Generated local artifacts rollback:
  - `Remove-Item -Recurse -Force .runtime\smoke-self-profile, .runtime\smoke-default-profile, .runtime\smoke-default-full, .runtime\dist, .runtime\artifacts\operator-ui -ErrorAction SilentlyContinue`
