# 2026-04-17 GAP-022 Task 3 Durable Task Store

## Goal
- Land `Foundation / GAP-022 / Task 3`.
- Give governed tasks a file-backed single-machine lifecycle store with deterministic pause/resume/retry behavior.

## Files Changed
- `packages/contracts/src/governed_ai_coding_runtime_contracts/task_store.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/workflow.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/task_intake.py`
- `tests/runtime/test_task_store.py`
- `tests/runtime/test_workflow.py`
- `tests/runtime/test_task_intake.py`
- `docs/specs/task-lifecycle-and-state-machine-spec.md`
- `schemas/jsonschema/task-lifecycle.schema.json`
- `docs/specs/repo-profile-spec.md`
- `schemas/jsonschema/repo-profile.schema.json`
- `schemas/examples/repo-profile/python-service.example.json`
- `schemas/examples/repo-profile/typescript-webapp.example.json`

## Decisions Landed
- Persistence stays file-backed in Foundation: one JSON artifact per task id.
- `pause/resume` is represented by a persisted `paused` state plus `resume_state`.
- `retry` is represented by `failed -> planned` with persisted `retry_count`.
- `timeout` remains failure metadata rather than a separate worker/runtime subsystem.

## Verification Result
- `python -m unittest tests.runtime.test_task_store tests.runtime.test_workflow tests.runtime.test_task_intake tests.runtime.test_repo_profile -v`: pass
- `python -m unittest discover -s tests/runtime -p "test_*.py"`: pass, `Ran 87 tests`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`: pass

## issue_id / clarification_mode
- `issue_id`: `GAP-022`
- `attempt_count`: `1`
- `clarification_mode`: `direct_fix`
- `clarification_scenario`: `bugfix`
- `clarification_questions`: `[]`
- `clarification_answers`: `[]`

## Rollback
- Revert the new `task_store.py`, `workflow.py`, and the lifecycle/repo-profile contract changes from git history for branch `feature/gap-020-task-1`.
