# 20260426 Learning Assistance Policy Target Baseline

## Goal
- Turn low-token teaching, observable misunderstanding detection, task restatement triggers, and bug observation guidance into a governed target-repo profile capability.
- Keep the behavior evidence-backed and bounded so it improves user learning without expanding every response.

## Scope
- `schemas/jsonschema/repo-profile.schema.json`
- `schemas/examples/repo-profile/python-service.example.json`
- `docs/specs/repo-profile-spec.md`
- `docs/targets/target-repo-governance-baseline.json`
- `docs/targets/target-repo-rollout-contract.json`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_profile.py`
- `tests/runtime/test_repo_profile.py`
- `tests/runtime/test_target_repo_governance_consistency.py`
- Target repo `.governed-ai/repo-profile.json` files synced by `runtime-flow-preset.ps1 -AllTargets -ApplyGovernanceBaselineOnly -Json`.

## Changes
- Added `learning_assistance_policy` to the repo-profile schema and sample profile.
- Added fail-closed loader validation for:
  - observable-signal-only boolean controls
  - trigger/restatement/checklist arrays
  - low-token caps for terms, restatements, observation items, and clarification questions
  - token-budget compression mode
- Added `learning_assistance_policy` to the active target governance baseline with `sync_revision=2026-04-26.9`.
- Added `low-token-learning-assistance-policy` to the target-repo rollout contract as a `profile_baseline` capability.
- Synchronized the new policy to all 5 catalog targets:
  - `classroomtoolkit`
  - `github-toolkit`
  - `self-runtime`
  - `skills-manager`
  - `vps-ssh-launcher`

## Policy Boundary
- The policy treats user confusion as observable interaction evidence only; it does not infer psychological state.
- Task restatement is checkpoint-based, not every-turn verbosity.
- Teaching defaults to one term per response with definition, task role, and common mistake.
- Bug work prefers a compact `expected / actual / repro_steps / logs_or_screenshot` checklist before long explanations.
- Budget pressure degrades to stage summary or handoff refs instead of expanding explanations.

## Verification
- `python -m json.tool docs\targets\target-repo-governance-baseline.json`
- `python -m json.tool docs\targets\target-repo-rollout-contract.json`
- `python -m json.tool schemas\jsonschema\repo-profile.schema.json`
- `python -m json.tool schemas\examples\repo-profile\python-service.example.json`
- `python -m unittest tests.runtime.test_repo_profile tests.runtime.test_target_repo_governance_consistency tests.runtime.test_target_repo_rollout_contract`
  - result: `Ran 30 tests`, `OK`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\runtime-flow-preset.ps1 -AllTargets -ApplyGovernanceBaselineOnly -Json`
  - result: `failure_count=0`, `target_count=5`
  - changed profile field on each target: `learning_assistance_policy`
- `python scripts\verify-target-repo-governance-consistency.py`
  - result: `status=pass`, `target_count=5`, `drift_count=0`, `sync_revision=2026-04-26.9`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Contract`
  - result: passed
  - key checks: `OK target-repo-rollout-contract`, `OK target-repo-governance-consistency`, `OK agent-rule-sync`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\build-runtime.ps1`
  - result: passed
  - key checks: `OK python-bytecode`, `OK python-import`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Runtime`
  - first run reached successful test output but the outer shell timed out at 180 seconds
  - rerun with longer timeout passed: `409 tests`, `2 skipped`, plus `10 tests`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\doctor-runtime.ps1`
  - result: passed
  - key checks: `OK runtime-policy-compatibility`, `OK codex-capability-ready`, `OK adapter-posture-visible`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Docs`
  - result: passed
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Scripts`
  - result: passed
- `git diff --check`
  - result: no whitespace errors; only expected CRLF/LF working-copy warnings

## Risk
- Risk level: low. This is profile/schema/docs/contract behavior and target `.governed-ai` metadata sync; no target business code was changed.
- Compatibility: `learning_assistance_policy` is optional in repo profiles. Existing profiles without it remain loadable.
- Token risk is explicitly bounded by `max_terms_per_response`, `max_task_restatements_per_stage`, `max_clarification_questions`, and `token_budget_policy`.

## Rollback
- Revert the files listed in Scope through git history.
- Re-run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\runtime-flow-preset.ps1 -AllTargets -ApplyGovernanceBaselineOnly -Json` to restore the previous target profile baseline.
- Re-run `python scripts\verify-target-repo-governance-consistency.py`.
