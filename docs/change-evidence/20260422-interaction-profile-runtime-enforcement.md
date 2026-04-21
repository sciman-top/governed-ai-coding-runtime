# 20260422 Interaction Profile Runtime Enforcement

## Goal
先执行用户指定的 `1`：把 repo-profile 的 `interaction_profile` 接入 runtime/task intake/evidence 执行路径，使 interaction defaults 不再只停留在 spec/schema/example 层。

## Scope
- `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_profile.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/task_intake.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/__init__.py`
- `scripts/run-governed-task.py`
- `schemas/examples/repo-profile/python-service.example.json`
- `tests/runtime/test_repo_profile.py`
- `tests/runtime/test_task_intake.py`
- `tests/runtime/test_run_governed_task_service_wrapper.py`

## Changes
1. Repo profile loader now exposes bounded interaction defaults
- `RepoProfile` now carries `interaction_profile`.
- Loader validates `default_mode` and `compaction_preference` fail-closed.
- `python-service.example.json` now declares the same bounded interaction defaults used by the reusable target template.

2. Task intake can adopt repo-profile defaults
- Added `apply_interaction_profile_defaults(...)`.
- Explicit task-level `interaction_defaults` win over repo-profile defaults.
- The helper preserves the clarification cap and existing `interaction_budget_overrides`.

3. Runtime execution path applies and records defaults
- `run-governed-task.py run` now loads the repo profile before creating ad hoc tasks.
- Newly created runtime tasks receive interaction defaults from `profile.interaction_profile`.
- Existing planned tasks without explicit defaults are updated with profile defaults before execution.
- Generated evidence bundles now include an `interaction_trace.applied_policies` entry that records the adopted mode/posture/compression preference.

## Verification
### Gate order
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
- result: all pass
- key output:
  - build: `OK python-bytecode`, `OK python-import`
  - runtime: `OK runtime-unittest`, `OK runtime-service-parity`, `OK runtime-service-wrapper-drift-guard`
  - contract: `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing`
  - hotspot/doctor: `OK runtime-policy-compatibility`, `OK runtime-policy-maintenance`, `OK codex-capability-ready`, `OK adapter-posture-visible`

### Supporting checks
1. `python -m unittest tests.runtime.test_run_governed_task_service_wrapper tests.runtime.test_repo_profile tests.runtime.test_task_intake -v`
- result: pass
- key output:
  - `Ran 24 tests`
  - `OK`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- result: pass
- key output:
  - `OK schema-json-parse`
  - `OK schema-example-validation`
  - `OK schema-catalog-pairing`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- result: pass
- key output:
  - `OK active-markdown-links`
  - `OK claim-drift-sentinel`
  - `OK claim-evidence-freshness`

## Risks
- Runtime enforcement currently covers the CLI governed task path. Other future runtime entrypoints must reuse `apply_interaction_profile_defaults(...)` or an equivalent service-layer helper to avoid drift.
- The evidence trace records adopted defaults, not full teaching/clarification behavior telemetry.

## Rollback
Revert:
- `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_profile.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/task_intake.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/__init__.py`
- `scripts/run-governed-task.py`
- `schemas/examples/repo-profile/python-service.example.json`
- `tests/runtime/test_repo_profile.py`
- `tests/runtime/test_task_intake.py`
- `tests/runtime/test_run_governed_task_service_wrapper.py`
- `docs/change-evidence/20260422-interaction-profile-runtime-enforcement.md`
- `docs/change-evidence/README.md`
