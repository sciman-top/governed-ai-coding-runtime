# 2026-05-03 Managed Drift Resolution Guidance

## Rule
- `R1`: current landing point is `scripts/apply-target-repo-governance.py` and `scripts/verify-target-repo-governance-consistency.py`; target destination is deterministic target-repo drift resolution guidance.
- `R4`: this slice is low-risk output-contract hardening; it does not expand overwrite authority.
- `R8`: blocked managed-file drift must expose source, target, expected hashes, conflict policy, and recommended recovery action.

## Pre Change Review
- `pre_change_review`
- `control_repo_manifest_and_rule_sources`: no rule source or manifest file is changed.
- `user_level_deployed_rule_files`: no user-level deployed rule copy is changed.
- `target_repo_deployed_rule_files`: no target project rule file is changed.
- `target_repo_gate_scripts_and_ci`: reviewed target governance apply and consistency verification scripts before changing drift output.
- `target_repo_repo_profile`: repo profile write behavior remains unchanged; only blocked/drift diagnostics are enriched.
- `target_repo_readme_and_operator_docs`: no operator command surface changes.
- `current_official_tool_loading_docs`: no Codex/Claude/Gemini loading semantics are changed.
- `drift-integration decision`: keep `block_on_drift` behavior; add machine-readable next-step fields so automation can integrate rather than force overwrite.

## Basis
- Existing apply behavior already blocks content drift for `replace` and `block_on_drift` managed files.
- Existing consistency verification already reports drift, but the payload did not carry enough resolution metadata for follow-on automation.

## Changes
- Added `conflict_policy` and `recommended_action` to blocked catalog, generated-file, and managed-file apply results.
- Added source/target/expected sha256 and recommended action fields to managed-file consistency drift.
- Added equivalent generated-file consistency drift metadata.
- Added tests for blocked drift and missing-file recovery guidance.

## Commands
- `python -m unittest tests.runtime.test_target_repo_governance_consistency`
- `python scripts/verify-target-repo-governance-consistency.py`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

## Evidence
- Focused governance consistency tests passed: 28 tests.
- Live target governance consistency passed: `target_count=5`, `drift_count=0`.
- Build gate passed: `OK python-bytecode`, `OK python-import`.
- Runtime gate passed: 102 test files, `failures=0`, `OK runtime-unittest`, `OK runtime-service-parity`, `OK runtime-service-wrapper-drift-guard`.
- Contract gate passed, including `OK target-repo-governance-consistency`, `OK agent-rule-sync`, `OK pre-change-review`, and `OK functional-effectiveness`.
- Hotspot gate passed via `doctor-runtime.ps1`; existing `WARN codex-capability-degraded` remained.

## Compatibility
- No new write path is introduced.
- Existing blocked statuses and reason values are preserved.
- New fields are additive JSON output fields.

## Rollback
- Revert `scripts/apply-target-repo-governance.py`, `scripts/verify-target-repo-governance-consistency.py`, related tests, and this evidence file.
