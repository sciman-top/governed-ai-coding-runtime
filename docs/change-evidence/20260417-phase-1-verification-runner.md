# 20260417 Phase 1 Verification Runner

## Goal
Execute `GAP-012 Quick And Full Verification Runner` as a verification plan and evidence artifact contract slice.

## Current Landing
- Verification module: `packages/contracts/src/governed_ai_coding_runtime_contracts/verification_runner.py`
- Runtime tests: `tests/runtime/test_verification_runner.py`
- Policy record: `docs/product/verification-runner.md`
- Backlog trace: `docs/backlog/issue-ready-backlog.md`

## Implemented Slice
- `build_verification_plan("full")` enforces `build -> test -> contract/invariant -> hotspot`.
- `build_verification_plan("quick")` preserves active-gate ordering for `test -> contract/invariant`.
- Escalation conditions are explicit in the plan.
- `build_verification_artifact` attaches mode, gate order, results, escalation conditions, and evidence link.

## TDD Evidence
```powershell
python -m unittest tests.runtime.test_verification_runner -v
python -m unittest discover -s tests/runtime -p "test_*.py" -v
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```

## Observed Red/Green
- Initial tests failed because `governed_ai_coding_runtime_contracts.verification_runner` did not exist.
- Tests passed after adding the minimal verification runner contract module.

## Verification Results
- `python -m unittest tests.runtime.test_verification_runner -v` -> pass
- `python -m unittest discover -s tests/runtime -p "test_*.py" -v` -> pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` -> pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All` -> pass
- `git diff --check` -> pass with CRLF normalization warnings only

## Gate Status
| gate | status | command | result | reason | alternative_verification | evidence_link | expires_at |
|---|---|---|---|---|---|---|---|
| build | `gate_na` | `n/a` | not run | no buildable Python package or runtime service artifact exists yet | runtime unit tests plus repo verifier | `docs/change-evidence/20260417-phase-1-verification-runner.md` | `2026-05-31` |
| test | `active` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` | pass | Python runtime contract tests cover verification runner plans | direct `python -m unittest discover -s tests/runtime -p "test_*.py"` | `docs/change-evidence/20260417-phase-1-verification-runner.md` | `n/a` |
| contract/invariant | `active` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` | pass via `-Check All` | schema, examples, catalog, and paired specs remain the active contract baseline | full repository verification | `docs/change-evidence/20260417-phase-1-verification-runner.md` | `n/a` |
| hotspot | `gate_na` | `n/a` | not run | no runtime doctor or health entrypoint exists yet | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs` | `docs/change-evidence/20260417-phase-1-verification-runner.md` | `2026-05-31` |

## Residual Risks
- The PowerShell verifier remains the active command runner; this slice defines the runtime contract for plans and artifacts.
- Build and hotspot are still `gate_na` until runtime services and doctor checks exist.
