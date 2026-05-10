# 2026-05-10 Target Full Gate Optimization Intent

## Goal
- Landing: `D:\CODE\governed-ai-coding-runtime`
- Target home: target-repo governance catalog, baseline sync, rollout contract, audit, and tests.
- Intent: make heavy target full-gate optimization visible to one-click apply instead of treating quick feedback profiles as proof that the physical full gate became faster.

## Changes
- Added catalog/profile field `full_gate_optimization` for target-local full-gate physical optimization intent.
- Marked `k12-question-graph` as `status=planned` because its full gate still runs a long serial `tools/run-gates.ps1`, while the target-local grouped gate entrypoint now exists but has not yet proven affected-path routing and coverage equivalence.
- Wired `full_gate_optimization` through `RuntimeFlow.Targets.ps1`, `runtime-flow-preset.ps1`, and `apply-target-repo-governance.py`.
- Added reviewed catalog drift overwrite support via `-AllowCatalogFieldOverwrite` so one-click apply can intentionally advance a catalog-owned field after drift review while default behavior remains fail-closed.
- Extended the target gate speed audit to warn when a heavy target has pending physical full-gate optimization, while still preserving the fallback full gate command.
- Updated repo-profile schema/spec and target slicing policy docs.

## Pre Change Review
- `pre_change_review`: completed for this low-risk control-plane change before target-local gate scripts are modified.
- `control_repo_manifest_and_rule_sources`: reviewed `AGENTS.md`, `docs/targets/target-repo-governance-baseline.json`, `docs/targets/target-repo-rollout-contract.json`, and `docs/targets/target-repos-catalog.json`.
- `user_level_deployed_rule_files`: not changed; this slice does not edit global user rules.
- `target_repo_deployed_rule_files`: not changed; this slice syncs `.governed-ai/repo-profile.json` intent only.
- `target_repo_gate_scripts_and_ci`: reviewed `D:\CODE\k12-question-graph\tools\run-gates.ps1`; no target-local gate script or CI file was modified.
- `target_repo_repo_profile`: applied `full_gate_optimization` to `D:\CODE\k12-question-graph\.governed-ai\repo-profile.json` through `runtime-flow-preset.ps1 -Target k12-question-graph -ApplyCodingSpeedProfile -Json`.
- `target_repo_readme_and_operator_docs`: unchanged; user-facing guidance remains in control-repo target slicing policy until target-local grouped gate runner exists.
- `current_official_tool_loading_docs`: not applicable to this slice because no AGENTS/Claude/Gemini loading semantics changed.
- `drift-integration decision`: do not overwrite target-local `tools/run-gates.ps1`; record pending physical optimization intent and keep fallback full gate command until k12 proves a grouped runner preserves coverage.

## Verification
- `python -m unittest tests.runtime.test_target_repo_governance_consistency tests.runtime.test_target_repo_gate_speed_audit tests.runtime.test_target_repo_rollout_contract`
  - exit_code: `0`
  - key_output: `Ran 47 tests`; `OK`
- `python scripts/audit-target-repo-gate-speed.py --repo-root .`
  - exit_code: `0`
  - key_output: `status=pass`, `target_count=6`, `error_count=0`, `warn_count=1`
  - warning interpretation: expected `full_gate_physical_optimization_pending` for `k12-question-graph`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target k12-question-graph -ApplyCodingSpeedProfile -Json`
  - exit_code: `0`
  - key_output: `governance_baseline_sync.status=pass`; `catalog_changed=["full_gate_optimization"]`; `sync_revision=2026-05-10.1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target k12-question-graph -ApplyCodingSpeedProfile -AllowCatalogFieldOverwrite full_gate_optimization -Json`
  - exit_code: `0`
  - key_output: refreshed profile after target-local grouped runner landed; `governance_baseline_sync.status=pass`; `catalog_changed=["full_gate_optimization"]`; `sync_revision=2026-05-10.1`
- `pwsh -NoProfile -Command '$null = [scriptblock]::Create((Get-Content -Raw scripts/runtime-flow-preset.ps1)); "OK powershell-parse"'`
  - exit_code: `0`
  - key_output: `OK powershell-parse`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - exit_code: `0`
  - key_output: `OK python-bytecode`; `OK python-import`
- `python scripts/verify-target-repo-rollout-contract.py`
  - exit_code: `0`
  - key_output: `status=pass`; `sync_revision=2026-05-10.1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - exit_code: `0`
  - key_output: `OK target-repo-rollout-contract`; `OK target-repo-governance-consistency`; `OK pre-change-review`; `OK functional-effectiveness`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - exit_code: `0`
  - key_output: `Completed 109 test files`; `failures=0`; `OK runtime-unittest`; `OK runtime-service-parity`; `OK runtime-service-wrapper-drift-guard`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  - exit_code: `0`
  - key_output: runtime checks `OK`; `WARN codex-capability-degraded` remains a known host capability warning

## Compatibility
- Existing quick/full gate semantics are preserved.
- `full_gate_optimization` is intent and routing metadata only; it does not replace `test_commands` or `full_gate_commands`.
- Targets without `full_gate_optimization` keep the previous behavior.

## Rollback
- Preferred rollback: restore this change from git history.
- File-level rollback candidates:
  - `docs/targets/target-repos-catalog.json`
  - `docs/targets/target-repo-governance-baseline.json`
  - `docs/targets/target-repo-rollout-contract.json`
  - `docs/targets/target-repo-test-slicing-policy.md`
  - `scripts/lib/RuntimeFlow.Targets.ps1`
  - `scripts/runtime-flow-preset.ps1`
  - `scripts/apply-target-repo-governance.py`
  - `scripts/audit-target-repo-gate-speed.py`
  - `schemas/jsonschema/repo-profile.schema.json`
  - `docs/specs/repo-profile-spec.md`
  - `tests/runtime/test_target_repo_governance_consistency.py`
  - `tests/runtime/test_target_repo_gate_speed_audit.py`
