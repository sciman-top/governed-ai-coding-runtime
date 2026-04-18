# 20260419 Session Bridge Execution Bus Expansion

## Purpose
- Continue automatic execution after `Task 0` planning sync by closing the first Task 1 slice from the direct-to-hybrid-final-state implementation plan.
- Landing point: expand the session bridge from posture or plan probe into the first governed execution bus slice.
- Target destination: support write-flow commands, evidence inspection, handoff inspection, and stable execution ids through the local session bridge contract.

## Clarification Trace
- `issue_id`: `session-bridge-execution-bus-expansion`
- `attempt_count`: `1`
- `clarification_mode`: `direct_fix`
- `clarification_scenario`: `n/a`
- `clarification_questions`: `[]`
- `clarification_answers`: `[]`

## Basis
- `docs/plans/direct-to-hybrid-final-state-implementation-plan.md`
- `docs/specs/session-bridge-command-spec.md`
- `schemas/jsonschema/session-bridge-command.schema.json`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/attached_write_governance.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/attached_write_execution.py`

## Change
- Expanded session bridge command coverage to include:
  - `write_request`
  - `write_approve`
  - `write_execute`
  - `write_status`
  - `inspect_evidence`
  - `inspect_handoff`
- Added stable `execution_id` handling for write-flow results.
- Implemented local task-level evidence inspection and handoff inspection.
- Routed the first attached write governance and execution flow through the session bridge handler.
- Extended the CLI entrypoint, spec, schema, product doc, and tests to cover the new command surface.

## Files Modified
- `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
- `scripts/session-bridge.py`
- `schemas/jsonschema/session-bridge-command.schema.json`
- `docs/specs/session-bridge-command-spec.md`
- `docs/product/session-bridge-commands.md`
- `tests/runtime/test_session_bridge.py`
- `tests/runtime/test_issue_seeding.py`

## Why This Matters
- Before this change, `inspect_evidence` was defined in the contract surface but degraded by default, and the bridge had no write command surface.
- After this change, the bridge can:
  - request governed writes
  - record approval decisions
  - execute approved writes
  - inspect write status
  - inspect evidence refs and handoff refs for a task or run
- This is still not complete hybrid final-state closure, but it moves the bridge from posture-only toward a real runtime-owned execution boundary.

## Verification
1. `python -m unittest tests.runtime.test_session_bridge -v`
   - Result: pass
   - Evidence: `23` session-bridge tests passed, including write flow, evidence inspection, handoff inspection, and schema validation
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
   - Result: pass
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
   - Result: pass
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`
   - Result: pass
5. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
   - Result: pass
   - Evidence: `Ran 204 tests`
6. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
   - Result: pass
7. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
   - Result: pass

## Risks
- `write_execute` currently accepts a stable `policy_decision_ref` without requiring the full `PolicyDecision` object, which is useful for bridge continuation but still leaves richer policy replay semantics for later slices.
- `inspect_handoff` is currently derived from known refs in task runs or explicit payload refs; it is not yet a dedicated persisted handoff registry.
- This slice proves the first bridge execution surface, not the full final-state live-host attach chain.

## Rollback
- Revert:
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
  - `scripts/session-bridge.py`
  - `schemas/jsonschema/session-bridge-command.schema.json`
  - `docs/specs/session-bridge-command-spec.md`
  - `docs/product/session-bridge-commands.md`
  - `tests/runtime/test_session_bridge.py`
  - `tests/runtime/test_issue_seeding.py`
  - `docs/change-evidence/20260419-session-bridge-execution-bus-expansion.md`
- Re-run:
  - `python -m unittest tests.runtime.test_session_bridge -v`
  - the repository gate order
