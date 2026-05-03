# 20260504 k12-question-graph Target Onboarding

## Rule
- `R1`: current landing point is `docs/targets/target-repos-catalog.json`; target destination is the active target-repo catalog and one-click governance application path.
- `R4`: medium-risk target onboarding; it writes repo-local governance assets into `D:\CODE\k12-question-graph` through the managed baseline after catalog verification.
- `R8`: this file records target gate selection, commands, key outputs, compatibility, and rollback.

## pre_change_review
- `pre_change_review`: required because this change modifies the target catalog and runs the target-governance apply path.
- `control_repo_manifest_and_rule_sources`: no `rules/manifest.json` entry or rule source file is changed.
- `user_level_deployed_rule_files`: no deployed user-level rule file is changed.
- `target_repo_deployed_rule_files`: k12 has existing `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md`; this slice does not rewrite them.
- `target_repo_gate_scripts_and_ci`: reviewed k12 `AGENTS.md`, `README.md`, `tools/README.md`, and `tools/run-gates.ps1` before catalog selection.
- `target_repo_repo_profile`: k12 had no `.governed-ai/repo-profile.json` before onboarding; the one-click baseline should bootstrap it.
- `target_repo_readme_and_operator_docs`: k12 `README.md` and `tools/README.md` identify `tools/run-gates.ps1` as the full gate and `tools/run-c002-dry-run-suite.ps1` as a database-free dry-run suite.
- `current_official_tool_loading_docs`: no Codex, Claude, or Gemini loading semantics are changed.
- `drift-integration decision`: do not overwrite k12 project rule files. Use managed baseline only for `.governed-ai/*` and shared Claude settings/hooks with `block_on_drift`/`json_merge`.

## Gate Selection
- `build_command`: `dotnet build apps/api/K12QuestionGraph.Api.csproj`.
- `test_command`: `pwsh -NoProfile -ExecutionPolicy Bypass -File tools/run-gates.ps1`.
- `quick_test_command`: `pwsh -NoProfile -ExecutionPolicy Bypass -File tools/run-c002-dry-run-suite.ps1`.
- `contract_command`: `pwsh -NoProfile -ExecutionPolicy Bypass -File tools/run-roadmap-guard.ps1`.
- `quick_test_reason`: the dry-run suite requires no database, writes no production activation, and is representative for daily C002 dynamic-asset feedback. The contract gate uses the existing roadmap dependency guard so daily quick covers a different invariant instead of running the same dry-run suite twice. The full gate remains `tools/run-gates.ps1` because it includes API, frontend, worker, PostgreSQL-backed checks, and broader product invariants.

## Commands
- `git status --short` in control repo and target repo.
- `dotnet build apps/api/K12QuestionGraph.Api.csproj`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File tools/run-c002-dry-run-suite.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File tools/run-roadmap-guard.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target k12-question-graph -ListTargets -Json`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target k12-question-graph -ApplyGovernanceBaselineOnly -ApplyCodingSpeedProfile -Json`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target k12-question-graph -FlowMode daily -Mode quick -Json`
- `python scripts/verify-target-repo-rollout-contract.py`
- `python scripts/verify-target-repo-governance-consistency.py`
- `python scripts/verify-pre-change-review.py --repo-root .`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

## Evidence
- Initial control repo and k12 target repo status were clean except for the current in-progress control-repo governance edits from this run.
- k12 build passed: `0 warnings`, `0 errors`.
- k12 C002 dry-run suite passed with `databaseRequired=false` and `productionActivationAllowed=false`.
- k12 roadmap dependency guard passed.
- Catalog list included `k12-question-graph`.
- One-click governance baseline apply passed and bootstrapped k12 `.governed-ai/repo-profile.json`, light pack, dependency baseline, managed PowerShell guard, shared Claude settings, hook, and managed-file provenance.
- Managed file apply had no blocked files.
- After changing the catalog `contract_command` from the duplicate C002 dry-run suite to `tools/run-roadmap-guard.ps1`, the next apply intentionally failed closed with `catalog_field_blocked` because the existing target repo profile still had the old contract command. The generated profile was integrated to the new catalog value, then apply passed and refreshed only `quick_gate_commands` and `full_gate_commands`.
- Daily quick flow passed for k12 with `overall_status=pass`, `mode=quick`, `results.test=pass`, and `results.contract=pass`.
- Daily quick executed distinct commands: `tools/run-c002-dry-run-suite.ps1` for `test`, and `tools/run-roadmap-guard.ps1` for `contract`.
- Live target governance consistency passed with `target_count=6` and `drift_count=0`.
- Rollout contract verification passed with `sync_revision=2026-05-02.3`.
- Pre-change review verification passed and matched this evidence file.
- Final control-repo hard gates passed in fixed order: build, Runtime, Contract, doctor.
- Runtime gate passed with `103` test files and `failures=0`.
- Contract gate passed, including `target-repo-rollout-contract`, `target-repo-governance-consistency`, and `pre-change-review`.
- Doctor passed with the existing `WARN codex-capability-degraded` host capability warning; all repo and target-governance checks were `OK`.

## Compatibility
- No k12 `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `README.md`, or application code is changed by catalog onboarding.
- k12 full gate remains available as `tools/run-gates.ps1`; daily quick feedback uses the smaller dry-run suite.
- Managed baseline application must block same-name drift instead of overwriting target-local changes.
- Target repo working tree has expected generated governance assets under `.governed-ai/` and `.claude/`; they are not application-code changes.

## Rollback
- Remove the `k12-question-graph` entry from `docs/targets/target-repos-catalog.json`.
- Revert target repo generated governance assets with git or remove `.governed-ai/` / managed Claude settings and hooks only after checking provenance and local use.
- Re-run `python scripts/verify-target-repo-governance-consistency.py`.
