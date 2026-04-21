# 20260421 GAP-082 Service Parity Expansion

## Goal
Expand `GAP-082 NTP-03` parity coverage so runtime CI fails on API/CLI drift for execution-like commands and operator reads.

## Scope
- `tests/service/test_session_api.py`
- `tests/service/test_operator_api.py`
- `scripts/verify-repo.ps1`
- `docs/backlog/issue-ready-backlog.md`

## Changes
1. Added service-vs-session-bridge parity tests for:
   - `run_full_gate` plan-only flow
   - `write_execute` approval-required path (execution-like command parity)
2. Extended operator API tests to compare service route responses against direct session-bridge read results for:
   - `inspect_status`
   - `inspect_evidence`
   - `inspect_handoff`
3. Updated runtime gate to run both parity modules in CI:
   - `tests.service.test_session_api`
   - `tests.service.test_operator_api`
4. Refreshed `GAP-082` status text to reflect the expanded parity baseline.

## Verification
### Targeted
- `python -m unittest tests.service.test_session_api`
- `python -m unittest tests.service.test_operator_api`

### Gate order
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
   - `OK python-bytecode`
   - `OK python-import`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
   - `OK runtime-unittest`
   - `OK runtime-service-parity`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
   - `OK schema-json-parse`
   - `OK schema-example-validation`
   - `OK schema-catalog-pairing`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
   - `OK runtime-status-surface`
   - `OK codex-capability-ready`
   - `OK adapter-posture-visible`

## Status Note
`GAP-082` remains in progress. This slice closes most parity drift gaps, but CLI wrapper-only convergence (removing remaining parallel runtime paths) is still pending before closeout.

## Rollback
Revert:
- `tests/service/test_session_api.py`
- `tests/service/test_operator_api.py`
- `scripts/verify-repo.ps1`
- `docs/backlog/issue-ready-backlog.md`
- this evidence file
