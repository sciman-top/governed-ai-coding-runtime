# 20260417 Phase 1 Minimal Approval And Evidence Console

## Goal
Execute `GAP-016 Minimal Approval And Evidence Console` as a control-plane facade contract slice.

## Current Landing
- Console module: `packages/contracts/src/governed_ai_coding_runtime_contracts/control_console.py`
- Runtime tests: `tests/runtime/test_control_console.py`
- Policy record: `docs/product/minimal-approval-evidence-console.md`
- Backlog trace: `docs/backlog/issue-ready-backlog.md`

## Implemented Slice
- `ControlPlaneConsole.approve` records approval decisions through the approval ledger.
- `ControlPlaneConsole.reject` records rejection decisions through the approval ledger.
- `ControlPlaneConsole.evidence_for_task` returns evidence timeline events by task id.
- Console scope is explicitly `control_plane` and does not expose tool execution.

## TDD Evidence
```powershell
python -m unittest tests.runtime.test_control_console -v
python -m unittest discover -s tests/runtime -p "test_*.py" -v
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```

## Observed Red/Green
- Initial tests failed because `governed_ai_coding_runtime_contracts.control_console` did not exist.
- Tests passed after adding the minimal control console facade.

## Verification Results
- `python -m unittest tests.runtime.test_control_console -v` -> pass
- `python -m unittest discover -s tests/runtime -p "test_*.py" -v` -> pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` -> pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All` -> pass
- `git diff --check` -> pass with CRLF normalization warnings only

## Gate Status
| gate | status | command | result | reason | alternative_verification | evidence_link | expires_at |
|---|---|---|---|---|---|---|---|
| build | `gate_na` | `n/a` | not run | no buildable Python package or runtime service artifact exists yet | runtime unit tests plus repo verifier | `docs/change-evidence/20260417-phase-1-minimal-approval-evidence-console.md` | `2026-05-31` |
| test | `active` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` | pass | Python runtime contract tests cover control console operations | direct `python -m unittest discover -s tests/runtime -p "test_*.py"` | `docs/change-evidence/20260417-phase-1-minimal-approval-evidence-console.md` | `n/a` |
| contract/invariant | `active` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` | pass via `-Check All` | schema, examples, catalog, and paired specs remain the active contract baseline | full repository verification | `docs/change-evidence/20260417-phase-1-minimal-approval-evidence-console.md` | `n/a` |
| hotspot | `gate_na` | `n/a` | not run | no runtime doctor or health entrypoint exists yet | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs` | `docs/change-evidence/20260417-phase-1-minimal-approval-evidence-console.md` | `2026-05-31` |

## Residual Risks
- This is a control-plane facade, not a visual web UI.
- Evidence inspection is in-memory until durable evidence storage exists.
