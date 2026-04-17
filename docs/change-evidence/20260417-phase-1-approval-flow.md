# 20260417 Phase 1 Approval Flow

## Goal
Execute `GAP-010 Approval Service And Interruption Flow` as an approval state and audit contract slice.

## Current Landing
- Approval module: `packages/contracts/src/governed_ai_coding_runtime_contracts/approval.py`
- Runtime tests: `tests/runtime/test_approval.py`
- Policy record: `docs/product/approval-flow.md`
- Backlog trace: `docs/backlog/issue-ready-backlog.md`

## Implemented Slice
- `ApprovalLedger.create` records pending approval requests.
- `approve`, `reject`, `revoke`, and `timeout` move pending requests to terminal states.
- `interruption_for` exposes `approval_pending` task interruption state.
- `get` retrieves persisted request snapshots by `approval_id`.
- `audit_trail` returns creation and decision events.

## TDD Evidence
```powershell
python -m unittest tests.runtime.test_approval -v
python -m unittest discover -s tests/runtime -p "test_*.py" -v
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```

## Observed Red/Green
- Initial tests failed because `governed_ai_coding_runtime_contracts.approval` did not exist.
- Tests passed after adding the minimal approval ledger module.

## Verification Results
- `python -m unittest tests.runtime.test_approval -v` -> pass
- `python -m unittest discover -s tests/runtime -p "test_*.py" -v` -> pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` -> pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All` -> pass
- `git diff --check` -> pass with CRLF normalization warnings only

## Gate Status
| gate | status | command | result | reason | alternative_verification | evidence_link | expires_at |
|---|---|---|---|---|---|---|---|
| build | `gate_na` | `n/a` | not run | no buildable Python package or runtime service artifact exists yet | runtime unit tests plus repo verifier | `docs/change-evidence/20260417-phase-1-approval-flow.md` | `2026-05-31` |
| test | `active` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` | pass | Python runtime contract tests cover approval state and audit primitives | direct `python -m unittest discover -s tests/runtime -p "test_*.py"` | `docs/change-evidence/20260417-phase-1-approval-flow.md` | `n/a` |
| contract/invariant | `active` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` | pass via `-Check All` | schema, examples, catalog, and paired specs remain the active contract baseline | full repository verification | `docs/change-evidence/20260417-phase-1-approval-flow.md` | `n/a` |
| hotspot | `gate_na` | `n/a` | not run | no runtime doctor or health entrypoint exists yet | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs` | `docs/change-evidence/20260417-phase-1-approval-flow.md` | `2026-05-31` |

## Residual Risks
- Persistence is currently in-memory and contract-level only.
- Production approval services must preserve these status names, decision events, and interruption semantics.
