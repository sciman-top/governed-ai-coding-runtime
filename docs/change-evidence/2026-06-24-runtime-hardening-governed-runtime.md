# Governed Runtime Hardening Evidence

- Date: `2026-06-24`
- Scope: `codex_adapter.py`, `tool_runner.py`, shared process capture, runtime test diagnostics, workflow tests
- Risk: `medium`
- Compatibility: `preserved`

## Pre-Change Review

- `pre_change_review`
- `reference_basis_review`
  Reviewed the local reference-basis shelf entries required for the guarded release-gate surface touched in this slice before changing `scripts/governance/gate-runner-common.ps1`.
- `changed_surface_paths`
  `scripts/governance/gate-runner-common.ps1`
- `reference_basis_surface_ids`
  `release-gate-and-ci-boundaries`
- `required_local_reference_ids_reviewed`
  `openai-codex`, `anthropic-claude-code-action`, `github-copilot-cli`
- `reference_adoption_decision`
  Adopted a conservative internal-only refactor: shared bounded PowerShell process capture was extracted without changing gate ordering, CLI parameters, or gate summary wire shape for the `release-gate-and-ci-boundaries` surface.
- `control_repo_manifest_and_rule_sources`
  Reviewed `rules/manifest.json`, the control-repo source files touched in this slice, and the contract/runtime scripts that consume them.
- `user_level_deployed_rule_files`
  Verified this slice does not require changing user-level deployed rule files; no sync source was modified.
- `target_repo_deployed_rule_files`
  Verified target-repo deployed rule files are unaffected by this slice; no target repo sync payload shape changed.
- `repo_local_gate_scripts_and_ci`
  Reviewed the affected runtime/contract verification entrypoints and confirmed the gate order remains `build -> test -> contract/invariant -> hotspot`.
- `repo_local_repo_profile`
  Reviewed repo-profile interaction points touched by governed tool execution and runtime test diagnostics; no required field contract changed.
- `repo_local_readme_and_operator_docs`
  Confirmed no operator-facing README or repo-local usage contract required edits for this conservative hardening slice.
- `current_official_tool_loading_docs`
  Verified current repository instruction-loading expectations remained unchanged for Codex-facing project rules; this slice does not alter AGENTS loading semantics.
- `drift-integration decision`
  Drift was integrated rather than overwritten: stale shell-risk allowlist and stale fixed-date runtime-evolution assertion were synced to current repo facts instead of reverting runtime hardening.

## Changes

- Tightened `tool_runner.py` read-only command normalization and bounded git classification with additional regression coverage.
- Split `codex_adapter.py` probe flow into internal executable/version, help-surface, capability-derivation, and probe-result synthesis stages without changing probe outputs.
- Extended `scripts/run-runtime-tests.py` JSON summary with execution-mode and worker/serialization diagnostics while keeping the CLI stable.
- Added `scripts/lib/ProcessCapture.ps1` and rewired `scripts/governance/gate-runner-common.ps1` to use the shared bounded process capture, timeout, and output-normalization path.
- Optimized `scripts/audit-repo-slimming-surface.py` to collect visible and transient inventory in one walk, then changed the CLI test to validate output shape on a minimal temp repo instead of rescanning the full control repo twice.
- Added direct tests for `workflow_governance`, `workflow_selection`, and `workflow_effect_metrics`.
- Integration decision on `2026-07-15`: the earlier `session_bridge.py`, `runtime-flow-preset.ps1`, `test_session_bridge.py`, `test_runtime_flow_preset.py`, and `test_target_repo_powershell_policy.py` edits were not reintroduced because those surfaces had already been retired on `main`.

## Verification

- Command:
  `python -m unittest tests.runtime.test_workflow_governance tests.runtime.test_workflow_selection tests.runtime.test_workflow_effect_metrics tests.runtime.test_subprocess_guard tests.runtime.test_tool_runner tests.runtime.test_tool_runner_governance tests.runtime.test_codex_adapter tests.runtime.test_run_runtime_tests_runner tests.runtime.test_repo_slimming_surface -v`
- Result:
  `86 tests passed` on `2026-07-15` after integration with current `main`.
- Notes:
  This run covers timeout policy enforcement, governed tool classification, probe recovery, runtime-test summary diagnostics, repo inventory behavior, and workflow governance.

## Slow-Test Evidence

- Before:
  - `tests/runtime/test_repo_slimming_surface.py` -> `21.909s`
- After:
  - `tests/runtime/test_repo_slimming_surface.py` -> `2.665s`
- Compatibility judgment:
  Assertions were preserved. The retained speedup comes from removing repeated full-repo scans. Measurements for the retired target-repo PowerShell policy and runtime-flow preset tests are intentionally excluded from the integrated claim.

## Contract Notes

- No public CLI parameter names were changed.
- No schema required fields were changed.
- No adapter payload field names were removed.
- New JSON summary fields in `run-runtime-tests.py` are additive diagnostics only.

## Rollback

- Primary rollback:
  `git revert <commit>`
- File-level fallback:
  revert the touched `codex_adapter.py`, `tool_runner.py`, `scripts/lib/ProcessCapture.ps1`, `scripts/governance/gate-runner-common.ps1`, `scripts/run-runtime-tests.py`, repo-slimming audit, and matching tests together to keep tests aligned with runtime behavior.
