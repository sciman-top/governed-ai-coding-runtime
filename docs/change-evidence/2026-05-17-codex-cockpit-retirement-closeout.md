# 2026-05-17 Codex/Cockpit Retirement Closeout

- rule_id: `LocalCodexCockpit`
- risk: medium
- landing: governed runtime control repo
- destination: Cockpit Tools fully owns Codex Direct OAuth, Direct API, and Cockpit API service roundtrip switching
- compatibility: active governed-runtime repair/smoke/gateway/switch helpers removed; historical evidence files remain immutable audit records

## Changes

- pre_change_review: completed before landing this cleanup in the current worktree.
- control_repo_manifest_and_rule_sources: inspected and updated `AGENTS.md` plus `rules/projects/governed-ai-coding-runtime/codex/AGENTS.md`; both now assign Direct OAuth, Direct API, and Cockpit API service switching to Cockpit Tools only.
- user_level_deployed_rule_files: no user-level rule file was changed in this slice; this is a control-repo source update and should be synchronized through the existing rule sync flow only after review.
- target_repo_deployed_rule_files: no target repo rule file was changed in this slice; target repo drift is outside this local retirement cleanup.
- target_repo_gate_scripts_and_ci: updated operator entrypoint, run shortcut, UI service source tracking, and runtime tests; deleted active repair/gateway/switch helper tests with their deleted scripts.
- target_repo_repo_profile: no target repo profile change; repository profile behavior remains governed by existing target catalog and runtime-flow scripts.
- target_repo_readme_and_operator_docs: updated README trio, docs index, quickstart, product guide, runbook index, and plans index to remove active governed-runtime Codex/Cockpit switching ownership.
- current_official_tool_loading_docs: no external docs lookup was needed; this cleanup follows the already-landed local boundary that Cockpit Tools owns switching and the current repo rules only need source alignment.
- drift-integration decision: integrate by deleting active governed-runtime switch/repair/gateway/trace/no-op/restart helpers, retaining only `Disable-CodexProjectInterop.ps1` and `Test-CodexGuardAbsence.ps1` as cleanup/absence verification tools.
- Removed active governed-runtime Codex/Cockpit switch, repair, trace, gateway, no-op launcher, restart-guard helper, and 8770 Codex history API test/style remnants.
- Removed active runbooks and the hot-switch implementation plan that still described governed-runtime ownership of Codex/Cockpit switching or LiteLLM gateway mode.
- Updated README, quickstart, product guide, AGENTS sources, operator entrypoint, run shortcut, and operator UI service source tracking to state that Cockpit Tools owns switching and this repo only retains old-shim cleanup plus guard absence verification.
- Updated contract tests so retired files must remain absent and 8770/operator actions stay unavailable.

## Verification Plan

- `git diff --check`
- `python -m unittest tests.runtime.test_operator_entrypoint tests.runtime.test_operator_ui tests.runtime.test_codex_guard_absence tests.runtime.test_codex_cockpit_policy_contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action Help`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

## Verification Result

- `git diff --check`: pass
- targeted unittest (`test_operator_entrypoint`, `test_operator_ui`, `test_codex_guard_absence`, `test_codex_cockpit_policy_contract`): 51 tests passed
- focused regression rerun after evidence/staging fixes: 76 tests passed
- `scripts/operator.ps1 -Action Help`: pass; no retired Codex/Cockpit repair/gateway/switch actions listed
- `scripts/build-runtime.ps1`: pass (`OK python-bytecode`, `OK python-import`)
- `scripts/verify-repo.ps1 -Check Runtime`: pass, 111 test files, failures=0
- `scripts/verify-repo.ps1 -Check Contract`: pass through `functional-effectiveness`
- `scripts/doctor-runtime.ps1`: pass; only existing `WARN codex-capability-degraded`

## Rollback

- Revert this commit if governed-runtime ownership of Codex/Cockpit switching is intentionally restored.
- Do not restore individual repair/gateway/guard scripts without also updating `LocalCodexCockpit` policy, tests, and README boundaries.
