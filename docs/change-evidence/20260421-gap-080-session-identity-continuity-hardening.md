# 20260421 GAP-080 Session Identity Continuity Hardening

## Goal
Implement the first executable slice of `GAP-080` by guaranteeing write-flow session identity continuity across:
- `write_request`
- `write_approve`
- `write_execute`
- `write_status`

## Scope
- `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/attached_write_governance.py`
- `scripts/session-bridge.py`
- `tests/runtime/test_session_bridge.py`

## Changes
1. Persisted `session_identity` into approval records for both:
   - attached write approval requests
   - governed tool approval requests
2. Added automatic approval-record identity rehydration in session bridge:
   - when follow-up commands only provide `approval_id`, session/resume/continuation identity is restored from the same approval flow
3. Added approval-record identity refresh helper so subsequent flow steps keep stable `session_identity`.
4. Extended CLI bridge common options to allow explicit identity propagation:
   - `--session-id`
   - `--resume-id`
   - `--continuation-id`
5. Strengthened runtime test coverage to assert:
   - approval record stores `session_id/resume_id/continuation_id`
   - `write_request -> write_approve -> write_execute -> write_status` all report the same session identity on one flow.

## Verification
### Targeted tests
- `python -m unittest tests.runtime.test_session_bridge -v`
- `python -m unittest tests.runtime.test_attached_write_governance -v`
- `python -m unittest tests.runtime.test_attached_write_execution -v`
- `python scripts/session-bridge.py --help`

### Mandatory gate order
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

All commands passed on the current branch.

## Risks
- This slice closes identity continuity for write-flow approval chains but does not by itself prove full live-host closure for every adapter posture.
- Full `GAP-080` closeout still requires broader end-to-end live-session evidence coverage.

## Rollback
Revert these files to pre-change state:
- `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/attached_write_governance.py`
- `scripts/session-bridge.py`
- `tests/runtime/test_session_bridge.py`
- `docs/change-evidence/20260421-gap-080-session-identity-continuity-hardening.md`
