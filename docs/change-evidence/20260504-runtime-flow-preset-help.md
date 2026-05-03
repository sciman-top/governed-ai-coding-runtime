# 20260504 Runtime Flow Preset Help Guard

## Rule
- `R1`: current landing point is `scripts/runtime-flow-preset.ps1`; target destination is the runtime-flow preset operator entrypoint.
- `R4`: low risk CLI behavior fix; `-Help` now exits before target catalog loading or runtime flow execution.
- `R8`: the change is covered by a focused regression test and this rollback note.

## Basis
- A help query must be read-only. Before this change, `-Help` was not declared as a switch and could fall through into the default `classroomtoolkit` daily quick flow.

## pre_change_review
- `pre_change_review`: required because this change modifies `scripts/runtime-flow-preset.ps1`, a sensitive target-repo orchestration entrypoint.
- `control_repo_manifest_and_rule_sources`: no `rules/manifest.json` entry or rule source file is changed.
- `user_level_deployed_rule_files`: no deployed user-level rule file is changed.
- `target_repo_deployed_rule_files`: no deployed target project rule file is changed.
- `target_repo_gate_scripts_and_ci`: reviewed runtime-flow preset behavior and added a regression test before expanding verification.
- `target_repo_repo_profile`: no target repo profile schema, catalog, or profile value is changed.
- `target_repo_readme_and_operator_docs`: no operator documentation or UI contract is changed; `-Help` output is additive CLI text.
- `current_official_tool_loading_docs`: no Codex, Claude, or Gemini loading semantics are changed.
- `drift-integration decision`: keep target governance drift behavior unchanged; this slice only prevents accidental flow execution from a help request.

## Changes
- Added an explicit `-Help` switch to `scripts/runtime-flow-preset.ps1`.
- Added an early `Show-RuntimeFlowPresetHelp` exit path before environment initialization, catalog loading, or target flow execution.
- Added a regression test that passes a fake runtime-flow script and verifies the fake script is not invoked.

## Commands
- `python -m unittest tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_help_does_not_run_default_target`
- `python -m unittest tests.runtime.test_runtime_flow_preset`
- `python scripts/verify-pre-change-review.py --repo-root .`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

## Evidence
- Focused regression test passed: 1 test.
- Runtime-flow preset test file passed: 25 tests.
- Pre-change review gate passed after this evidence file was completed.
- Build gate passed: `OK python-bytecode`, `OK python-import`.
- Runtime gate passed: 103 test files, `failures=0`, `OK runtime-unittest`, `OK runtime-service-parity`, `OK runtime-service-wrapper-drift-guard`.
- Contract gate passed, including `OK target-repo-governance-consistency`, `OK agent-rule-sync`, `OK pre-change-review`, and `OK functional-effectiveness`.
- Hotspot gate passed via `doctor-runtime.ps1`; existing `WARN codex-capability-degraded` remained.
- The first Runtime replay failed closed because this evidence file did not yet contain the required `pre_change_review` drift-review tokens for the sensitive script change. The evidence gap is now closed and the final replay passed.

## Compatibility
- Existing target flow, list-target, and governance apply options are unchanged.
- `-Help` is additive and exits with status `0`.

## Rollback
- Revert `scripts/runtime-flow-preset.ps1`, `tests/runtime/test_runtime_flow_preset.py`, and this evidence file.
