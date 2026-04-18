# 2026-04-18 Full Runtime Execution Plan

## Goal
- Close `Full Runtime / GAP-024` through `GAP-028` on the active branch baseline.
- Move the active next-step queue from `Full Runtime / GAP-024` to `Public Usable Release / GAP-029`.

## Scope
- Local execution runtime, managed workspace binding, and synchronous worker path.
- Local artifact store, replay references, and artifact-backed evidence or handoff records.
- Gate execution bound to `task_id` and `run_id`.
- CLI-first runtime status surface and doctor integration.
- Entry docs, backlog, roadmap, plans index, specs, schemas, and schema catalog alignment.

## Runtime Outcome
- One governed task completed end to end through `python scripts/run-governed-task.py run --json`.
- Latest delivered task:
  - `task_id`: `task-b21f2279`
  - `run_id`: `run-63f11fdd0f90`
  - `state`: `delivered`
  - `workspace_root`: `.governed-workspaces/python-service-sample/task-b21f2279/run-63f11fdd0f90`
  - `rollback_ref`: `docs/runbooks/control-rollback.md`
- Persisted runtime outputs:
  - `artifacts/task-b21f2279/run-63f11fdd0f90/execution-output/worker-summary.txt`
  - `artifacts/task-b21f2279/run-63f11fdd0f90/verification-output/build.txt`
  - `artifacts/task-b21f2279/run-63f11fdd0f90/verification-output/test.txt`
  - `artifacts/task-b21f2279/run-63f11fdd0f90/verification-output/contract.txt`
  - `artifacts/task-b21f2279/run-63f11fdd0f90/verification-output/doctor.txt`
  - `artifacts/task-b21f2279/run-63f11fdd0f90/evidence/bundle.json`
  - `artifacts/task-b21f2279/run-63f11fdd0f90/handoff/package.json`

## Verification
| gate | command | exit_code | result |
|---|---|---:|---|
| build | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1` | 0 | `OK python-bytecode`, `OK python-import` |
| test | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` | 0 | `Ran 100 tests`, `OK runtime-unittest` |
| contract/invariant | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` | 0 | `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing` |
| hotspot | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1` | 0 | `OK gate-command-operator`, `OK runtime-status-surface` |

## Changes
- Added runtime orchestration modules:
  - `execution_runtime.py`
  - `worker.py`
  - `artifact_store.py`
  - `replay.py`
  - `runtime_status.py`
- Extended Foundation primitives:
  - `task_store.py` now persists run metadata, active run identity, workspace root, and rollback references.
  - `workspace.py` now binds workspace allocation to `run_id` and `attempt_id`.
  - `verification_runner.py` now binds plans to `task_id` and `run_id` and persists gate artifacts.
  - `evidence.py` now builds artifact-backed evidence bundles.
- Added CLI-first runtime operator path:
  - `scripts/run-governed-task.py`
  - `scripts/doctor-runtime.ps1` now verifies the runtime status surface.
  - `scripts/build-runtime.ps1` now byte-compiles the full `scripts/` Python surface.
- Added runtime tests:
  - `test_execution_runtime.py`
  - `test_worker.py`
  - `test_artifact_store.py`
  - `test_replay.py`
  - `test_runtime_status.py`
  - extended `test_verification_runner.py`
- Added runtime operator surface contract:
  - `docs/specs/runtime-operator-surface-spec.md`
  - `schemas/jsonschema/runtime-operator-surface.schema.json`
  - `schemas/catalog/schema-catalog.yaml`
- Updated entry docs and planning docs so the active queue now starts at `Public Usable Release / GAP-029`.

## Risks
- The worker remains synchronous and single-machine only; queue-backed execution is still deferred.
- The operator surface is intentionally CLI-first and read-model only; a richer UI shell is still future work under `Public Usable Release`.
- Repo profile defaults for end-to-end smoke still use the sample repo profile path for workspace policy inputs; broader packaged onboarding belongs to `GAP-029+`.

## Rollback
- Git revert the Full Runtime implementation changeset and restore the active queue references from `Public Usable Release / GAP-029` back to `Full Runtime / GAP-024`.
- If local runtime state must be discarded, remove `.runtime/` and `.governed-workspaces/` after reverting code or docs; both are local state only and ignored by git.

## Evidence Fields
- `issue_id`: `GAP-024..GAP-028`
- `attempt_count`: `1`
- `clarification_mode`: `direct_fix`
- `clarification_scenario`: `n/a`
- `clarification_questions`: `[]`
- `clarification_answers`: `[]`
