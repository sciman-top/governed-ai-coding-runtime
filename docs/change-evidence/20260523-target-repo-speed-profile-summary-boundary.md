# 2026-05-23 Target Repo Speed Profile Summary Boundary

## Goal
- Current landing point: `D:\CODE\governed-ai-coding-runtime`.
- Target destination: target-repo speed-profile reporting, rollout contract, and one-click apply evidence.
- Intent: make one-click speed apply honest about the boundary between profile-level quick feedback and physical full-gate speedup.

## pre_change_review
- `pre_change_review`: required because this slice changes `scripts/runtime-flow-preset.ps1`, `scripts/audit-target-repo-gate-speed.py`, and the rollout contract.
- `control_repo_manifest_and_rule_sources`: reviewed root `AGENTS.md`, `docs/targets/target-repo-rollout-contract.json`, `docs/targets/target-repo-governance-baseline.json`, `docs/targets/target-repos-catalog.json`, and `docs/targets/target-repo-test-slicing-policy.md`.
- `user_level_deployed_rule_files`: not changed; this slice does not edit global user-level Codex/Claude/Gemini rule files.
- `target_repo_deployed_rule_files`: not changed; this slice does not edit target `AGENTS.md`, `CLAUDE.md`, or `GEMINI.md` files.
- `target_repo_gate_scripts_and_ci`: reviewed current k12 full-gate boundary through `D:\CODE\k12-question-graph\tools\run-gate-group.ps1` and `tools/run-gates.ps1`; no target-local gate script or CI file is modified by this control-repo patch.
- `target_repo_repo_profile`: reviewed `D:\CODE\k12-question-graph\.governed-ai\repo-profile.json`; it already carries `quick_gate_commands`, `full_gate_commands`, and `full_gate_optimization`.
- `target_repo_readme_and_operator_docs`: reviewed `docs/targets/target-repo-test-slicing-policy.md`; it states that `quick_test_command` is daily feedback only and `full_gate_optimization` does not replace the full gate.
- `current_official_tool_loading_docs`: N/A for this slice; Codex/Claude/Gemini loading semantics are not changed.
- `drift-integration decision`: do not overwrite target-local full-gate scripts. The control repo now emits `coding_speed_profile_summary` and audit `speed_profile_summary` so k12 remains visibly pending for physical full-gate optimization until grouped/affected-path coverage equivalence is proven.

## Changes
- Added `speed_profile_summary` to `scripts/audit-target-repo-gate-speed.py`.
- Added `coding_speed_profile_summary` to `scripts/runtime-flow-preset.ps1` JSON output.
- Registered the new JSON field in `docs/targets/target-repo-rollout-contract.json`.
- Added tests covering the pending physical full-gate summary.

## Verification Plan
- `python -m unittest tests.runtime.test_target_repo_gate_speed_audit tests.runtime.test_target_repo_rollout_contract tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_apply_coding_speed_profile_alias_uses_baseline_sync`
- `python scripts/verify-target-repo-rollout-contract.py`
- `python scripts/audit-target-repo-gate-speed.py --repo-root .`
- Full control-repo gate order: build, Runtime, Contract, doctor.
- One-click rollout proof: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\runtime-flow-preset.ps1 -AllTargets -ApplyCodingSpeedProfile -Json`.

## Compatibility
- Existing target repo `quick_gate_commands` and `full_gate_commands` semantics are preserved.
- This does not change `test_command` or replace `tools/run-gates.ps1` for `k12-question-graph`.
- The new summary is reporting and contract telemetry only.

## Rollback
- Preferred rollback: restore this change from git history.
- File-level rollback candidates:
  - `docs/targets/target-repo-rollout-contract.json`
  - `scripts/audit-target-repo-gate-speed.py`
  - `scripts/runtime-flow-preset.ps1`
  - `tests/runtime/test_runtime_flow_preset.py`
  - `tests/runtime/test_target_repo_gate_speed_audit.py`
