# 20260421 GAP-083 Doctor Deterministic Remediation Actions

## Goal
Advance `GAP-083` remediation depth by making doctor outputs provide deterministic, executable remediation actions for attachment posture failures (`missing-light-pack`, `invalid-light-pack`, `stale-binding`).

## Scope
- `scripts/doctor-runtime.ps1`
- `tests/runtime/test_runtime_doctor.py`
- `docs/backlog/issue-ready-backlog.md`

## Changes
1. Added `Resolve-AttachmentRemediationActions` in `doctor-runtime.ps1`.
2. On fail-closed attachment posture, doctor now emits:
   - existing summary hint: `REMEDIATE ...`
   - deterministic action lines: `REMEDIATE-ACTION <command>`
3. Added runtime test assertions for `missing-light-pack`, `invalid-light-pack`, and `stale-binding` failures to require:
   - `REMEDIATE-ACTION` output
   - explicit `scripts/attach-target-repo.py` action guidance
4. Marked GAP-083 criterion "`doctor outputs include deterministic remediation actions for missing, stale, and invalid posture states`" as complete.

## Verification
### Targeted
- `python -m unittest tests.runtime.test_runtime_doctor`
- `python -m unittest tests.service.test_operator_api`

### Gate order
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
5. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`

## Status Note
`GAP-083` remains in progress. This slice closes deterministic doctor remediation output coverage; operator recovery tracking and remediation-retry evidence loops are still pending.

## Rollback
Revert:
- `scripts/doctor-runtime.ps1`
- `tests/runtime/test_runtime_doctor.py`
- `docs/backlog/issue-ready-backlog.md`
- this evidence file
