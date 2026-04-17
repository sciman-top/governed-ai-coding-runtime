# 2026-04-17 GAP-023 Task 4 Control Registry And Evidence Completeness

## Goal
- Land `Foundation / GAP-023 / Task 4`.
- Make control health and evidence completeness mechanically checkable.

## Files Changed
- `packages/contracts/src/governed_ai_coding_runtime_contracts/control_registry.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/evidence.py`
- `tests/runtime/test_control_registry.py`
- `tests/runtime/test_evidence_timeline.py`
- `docs/specs/control-registry-spec.md`
- `schemas/jsonschema/control-registry.schema.json`

## Decisions Landed
- Hard controls without observability signals are unhealthy for enforced mode.
- Progressive controls now require review cadence and rollback visibility metadata to be healthy for enforcement.
- Evidence completeness can fail on missing `rollback_ref` independently from advisory verification results.

## Verification Result
- `python -m unittest tests.runtime.test_control_registry tests.runtime.test_evidence_timeline -v`: pass
- `python -m unittest discover -s tests/runtime -p "test_*.py"`: pass, `Ran 87 tests`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`: pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`: pass

## issue_id / clarification_mode
- `issue_id`: `GAP-023`
- `attempt_count`: `1`
- `clarification_mode`: `direct_fix`
- `clarification_scenario`: `bugfix`
- `clarification_questions`: `[]`
- `clarification_answers`: `[]`

## Rollback
- Revert the new `control_registry.py` helper and the related spec/schema/test changes from git history for branch `feature/gap-020-task-1`.
