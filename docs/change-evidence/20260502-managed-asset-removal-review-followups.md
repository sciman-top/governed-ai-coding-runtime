# Managed Asset Removal Review Followups

- date: 2026-05-02
- rule_ids: R4, R6, R8, E4, E6
- risk_level: high
- scope: cleanup/uninstall managed-asset removal, operator preflight, target repo baseline uninstall evidence

## Basis

Code review found four cleanup/uninstall risks:

- destructive managed-asset apply could still run after target flow failure or timeout.
- `CleanupTargets` and `UninstallGovernance` bypassed operator preflight while `next_action=repair_gate_first`.
- malformed shared JSON or repo profile JSON could produce a Python traceback instead of structured blocked evidence.
- target repo baseline did not provide enough ownership/provenance evidence for complete uninstall of shared settings and generated quick-test prompt.

## Pre Change Review

- `pre_change_review`
- `control_repo_manifest_and_rule_sources`: reviewed `rules/manifest.json`, global rule sources, `docs/targets/target-repo-governance-baseline.json`, managed-asset scripts, operator surfaces, and `scripts/runtime-flow-preset.ps1` before integrating cleanup/uninstall follow-ups.
- `user_level_deployed_rule_files`: user-level Codex/Claude/Gemini deployed rule files are controlled by `rules/manifest.json`; rule sync backup evidence exists under `docs/change-evidence/rule-sync-backups/20260502-204106/` and must be treated as sync evidence, not as a separate source of truth.
- `target_repo_deployed_rule_files`: no target project rule file is intentionally deleted by this slice; target repo deployed rule drift remains governed by manifest sync and target governance consistency checks.
- `target_repo_gate_scripts_and_ci`: reviewed `scripts/governance/fast-check.ps1`, `scripts/governance/full-check.ps1`, `scripts/runtime-flow-preset.ps1`, and the managed cleanup/uninstall call path so destructive asset removal cannot hide behind a failed target flow.
- `target_repo_repo_profile`: reviewed `.governed-ai/repo-profile.json` semantics for quick/full gate groups, generated quick-test prompt hashes, and profile patch removal; malformed profile JSON now fails closed instead of producing unstructured traceback output.
- `target_repo_readme_and_operator_docs`: reviewed operator-facing entrypoints in `run.ps1`, `scripts/operator.ps1`, and `scripts/serve-operator-ui.py`; cleanup/uninstall remains dry-run-first and destructive removal requires `-ApplyManagedAssetRemoval`.
- `current_official_tool_loading_docs`: no new Codex/Claude/Gemini loading model is introduced here; global rule version/sync changes remain manifest-managed and must be checked through the existing rule loading contract.
- `drift-integration decision`: keep baseline, rule-source, operator, runtime-flow, managed-asset script, tests, and evidence updates as one integration unit; any drift must be reconciled through `sync-agent-rules`, target governance consistency, and pre-change review before claiming completion.

## Changes

- `scripts/runtime-flow-preset.ps1` now blocks `-ApplyManagedAssetRemoval` actions when the preceding target flow exits non-zero.
- `scripts/operator.ps1` and `scripts/serve-operator-ui.py` now include cleanup/uninstall in `repair_gate_first` blocking.
- `scripts/uninstall-target-repo-governance.py` now reports malformed JSON as structured `blocked_files` reasons.
- `docs/targets/target-repo-governance-baseline.json` now records shared ownership evidence for `.claude/settings.json`.
- `scripts/lib/target_repo_managed_assets.py` can compute expected quick-test prompt hashes from repo profile for generated prompt uninstall, while malformed profiles fail closed.

## Commands

```powershell
python -m py_compile scripts/lib/target_repo_managed_assets.py scripts/inspect-target-repo-managed-assets.py scripts/prune-retired-managed-files.py scripts/uninstall-target-repo-governance.py scripts/serve-operator-ui.py
python -m unittest tests.runtime.test_uninstall_target_repo_governance
python -m unittest tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_single_target_dry_runs_managed_asset_prune_and_uninstall tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_blocks_managed_asset_apply_after_flow_failure
python -m unittest tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_operator_preflight_blocks_high_impact_actions tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_next_work_summary_blocks_cleanup_and_uninstall_for_repair_gate_first tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_operator_preflight_blocks_cleanup_and_uninstall_actions tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_operator_preflight_does_not_block_readiness
python -m unittest tests.runtime.test_prune_retired_managed_files tests.runtime.test_uninstall_target_repo_governance tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_single_target_dry_runs_managed_asset_prune_and_uninstall tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_blocks_managed_asset_apply_after_flow_failure tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_operator_preflight_blocks_high_impact_actions tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_next_work_summary_blocks_cleanup_and_uninstall_for_repair_gate_first tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_operator_preflight_blocks_cleanup_and_uninstall_actions tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_operator_preflight_does_not_block_readiness tests.runtime.test_operator_ui.OperatorUiTests.test_operator_ui_interactive_mode_renders_actions_and_ref_buttons
python scripts/verify-target-repo-rollout-contract.py
python scripts/verify-target-repo-governance-consistency.py
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
```

## Key Output

- py_compile: pass
- uninstall governance regression tests: 9 passed
- runtime-flow managed removal regression tests: 2 passed
- operator preflight regression tests: 4 passed
- combined focused cleanup/uninstall/operator regression slice: 18 passed
- target repo rollout contract: pass
- target repo governance consistency: pass
- build gate: pass
- runtime gate: blocked by existing unrelated dirty rule/version/pre-change evidence failures; cleanup/uninstall focused tests passed inside the same run.
- contract gate: checks passed until pre-change review; final status blocked by missing pre-change review evidence for the broader dirty worktree.
- doctor gate: pass with `codex-capability-degraded` warning for native attach status handshake.

## Compatibility

- Dry-run cleanup/uninstall still reports candidates after target flow failure.
- Destructive cleanup/uninstall now requires the target flow to pass first.
- Existing generated prompt entries with `expected_sha256` keep their previous behavior.
- Generated quick-test prompt entries without a stored hash are removable only when the current repo profile can reproduce the exact prompt hash.

## Rollback

Use git history to revert the script, baseline, and test changes from this evidence set. For any target repo touched by `--apply`, restore from the backup path emitted in `deleted_files`, `patched_shared_files`, or `patched_profile_files`.
