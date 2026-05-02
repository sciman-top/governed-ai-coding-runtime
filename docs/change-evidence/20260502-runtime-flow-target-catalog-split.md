# 2026-05-02 Runtime Flow Target Catalog Split

## Rule
- `R1`: current landing point is Task 5 runtime-flow maintainability; target landing point is one extracted responsibility with the root script still owning the public entrypoint.
- `R4`: this slice is low-risk refactoring only; it does not change target-repo rollout scope, approval posture, or evidence semantics.
- `R8`: extracted file ownership, verification commands, compatibility, and rollback are recorded here.

## Basis
- Task 5 of `docs/plans/repo-slimming-and-speed-plan.md`
- Goal: split one stable responsibility out of `scripts/runtime-flow-preset.ps1` without changing the public CLI or JSON contract

## pre_change_review
- This working slice is part of the broader 2026-05-02 repo-slimming lane and touches a sensitive path: `scripts/runtime-flow-preset.ps1`.
- The same working tree also carries controlled slimming-lane changes under root README files, `.governed-ai/repo-map-context-shaping.json`, `docs/plans/README.md`, `docs/plans/repo-slimming-and-speed-plan.md`, generated evidence indexes, and focused runtime tests.
- control_repo_manifest_and_rule_sources: no `rules/manifest.json` or managed rule-source content is changed in this slice.
- user_level_deployed_rule_files: no user-home deployed rule copies are modified by this slice.
- target_repo_deployed_rule_files: no target repository distributed rule files are modified by this slice.
- target_repo_gate_scripts_and_ci: no target-repo gate script or CI contract is changed by this slice; the only sensitive execution entrypoint touched is the control-repo `scripts/runtime-flow-preset.ps1`.
- target_repo_repo_profile: no target-repo `.governed-ai/repo-profile.json` semantic contract is changed by this slice.
- target_repo_readme_and_operator_docs: root and language README slimming keeps operator-facing entrypoints, readiness commands, and current posture links intact; history-only text moved behind stable archive links.
- current_official_tool_loading_docs: no host loading model assumption changed; Codex project instructions, existing host-compatibility claims, and runtime entrypoint semantics remain aligned with the current verified docs and contracts.
- drift-integration decision: keep the inventory, evidence-index, repo-map routing, README slimming, and first `runtime-flow-preset.ps1` extraction in the same bounded optimization lane, and fail closed on verification rather than bypassing pre-change review or hard gates.

## Slice
- Extracted target catalog parsing helpers into `scripts/lib/RuntimeFlow.Targets.ps1`
- Kept `scripts/runtime-flow-preset.ps1` as the canonical entrypoint
- Left flow orchestration, governance sync, milestone logic, and JSON shaping in the root script
- Added focused coverage proving `-ListTargets -Json` still reads and sorts catalog-backed targets through the canonical entrypoint

## Commands
- `python -m unittest tests.runtime.test_runtime_flow_preset`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`

## Key Output
- `Ran 21 tests`, `OK`
- `Completed 101 test files in 197.325s; failures=0`
- `OK runtime-unittest`
- `OK runtime-service-parity`
- `OK runtime-service-wrapper-drift-guard`

## Verification
- Focused runtime-flow preset tests passed after the extraction.
- Repo-level Runtime gate passed with zero failing test files.

## Compatibility
- No parameter names changed
- No output fields changed
- Existing catalog template expansion and target selection behavior remain owned by the same tests

## Rollback
- Revert `scripts/runtime-flow-preset.ps1`, `scripts/lib/RuntimeFlow.Targets.ps1`, and the related test changes in git history
