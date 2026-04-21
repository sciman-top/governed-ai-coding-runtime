# 20260421 Layered Verification Gates L1 L2 L3

## Goal
Promote verification layering to a first-class runtime capability (`l1/l2/l3`) so target repos can run tiered gate plans while preserving `quick/full` compatibility.

## Scope
- `packages/contracts/src/governed_ai_coding_runtime_contracts/verification_runner.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/delivery_handoff.py`
- `scripts/run-governed-task.py`
- `scripts/session-bridge.py`
- `scripts/runtime-check.ps1`
- `scripts/runtime-flow.ps1`
- `scripts/runtime-flow-preset.ps1`
- `scripts/runtime-flow-classroomtoolkit.ps1`
- `tests/runtime/test_verification_runner.py`
- `tests/runtime/test_session_bridge.py`
- `tests/runtime/test_run_governed_task_service_wrapper.py`
- `tests/runtime/test_run_governed_task_cli.py`
- `tests/runtime/test_delivery_handoff.py`
- `docs/specs/verification-gates-spec.md`
- `schemas/jsonschema/verification-gates.schema.json`

## Changes
1. Added layered verification modes in contract runner:
   - `l1`: `test -> contract`
   - `l2`: `build -> test -> contract`
   - `l3`: `build -> test -> contract -> doctor`
   - compatibility aliases preserved: `quick -> l1`, `full -> l3`
2. Extended repo-profile gate resolution for layered execution:
   - `l2` requires `build/test/contract` and ignores `doctor`
   - `l3` can consume `doctor` when declared
3. Updated session bridge and wrapper entrypoints to pass explicit `gate_level`:
   - `run_quick_gate` for `quick/l1`
   - `run_full_gate` for `full/l2/l3`
4. Expanded operator scripts to accept layered modes:
   - `runtime-check.ps1`
   - `runtime-flow.ps1`
   - `runtime-flow-preset.ps1`
   - `runtime-flow-classroomtoolkit.ps1`
5. Updated handoff validation to treat `l3` as fully validated, matching legacy `full` semantics.
6. Updated verification gate spec/schema to declare layered levels and alias compatibility.

## Verification
### Focused unit/integration set
- `python -m unittest tests.runtime.test_verification_runner tests.runtime.test_delivery_handoff tests.runtime.test_session_bridge tests.runtime.test_run_governed_task_service_wrapper tests.runtime.test_run_governed_task_cli`
  - `Ran 63 tests`
  - `OK`

### Gate order
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
5. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`

## Rollback
Revert the files listed in Scope and rerun gate order verification.
