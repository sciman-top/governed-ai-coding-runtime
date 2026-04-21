# 20260421 GAP-083 Operator Remediation Depth Closeout

## Goal
Close `GAP-083` by completing operator remediation-depth query coverage, deterministic doctor actions, and remediation retry evidence persistence.

## Scope
- `apps/control-plane/routes/operator.py`
- `packages/agent-runtime/service_facade.py`
- `scripts/doctor-runtime.ps1`
- `tests/service/test_operator_api.py`
- `tests/runtime/test_runtime_doctor.py`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/README.md`
- `docs/backlog/full-lifecycle-backlog-seeds.md`

## Changes
1. Added operator action `write_status` through control-plane service boundary (`operator -> facade -> session bridge`).
2. Added service/session parity coverage for `write_status` in operator API tests.
3. Added deterministic doctor remediation actions (`REMEDIATE-ACTION`) for:
   - `missing-light-pack`
   - `invalid-light-pack`
   - `stale-binding`
4. Added remediation retry evidence persistence in doctor:
   - writes `doctor/remediation-<timestamp>.json`
   - updates `doctor/latest-remediation.json`
   - prints `REMEDIATE-EVIDENCE <path>`
5. Promoted backlog posture:
   - `GAP-083` set to complete with all acceptance criteria checked
   - near-term active queue advanced to `GAP-084` only

## Verification
### Targeted
- `python -m unittest tests.service.test_operator_api`
- `python -m unittest tests.runtime.test_runtime_doctor`
- `python -m unittest tests.service.test_session_api`
- `python -m unittest tests.runtime.test_run_governed_task_cli tests.runtime.test_run_governed_task_service_wrapper`

### Gate order
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
5. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`

## Status Note
`GAP-083` is complete on current branch baseline. `GAP-084` is now the remaining active near-term execution item.

## Rollback
Revert:
- `apps/control-plane/routes/operator.py`
- `packages/agent-runtime/service_facade.py`
- `scripts/doctor-runtime.ps1`
- `tests/service/test_operator_api.py`
- `tests/runtime/test_runtime_doctor.py`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/README.md`
- `docs/backlog/full-lifecycle-backlog-seeds.md`
- this evidence file
