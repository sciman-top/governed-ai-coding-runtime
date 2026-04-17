# 20260417 Phase 1 Scripted Trial Entrypoint

## Goal
Execute `GAP-007 Codex-Compatible CLI Or Scripted Trial Entrypoint` as a documented scripted read-only trial.

## Current Landing
- Entrypoint module: `packages/contracts/src/governed_ai_coding_runtime_contracts/trial_entrypoint.py`
- Repo-root script: `scripts/run-readonly-trial.py`
- First-run docs: `docs/product/first-readonly-trial.md`
- Runtime tests: `tests/runtime/test_trial_entrypoint.py`

## Implemented Slice
- `codex_cli_adapter_declaration` declares Codex-compatible adapter capabilities.
- `auth_ownership` is `user_owned_upstream_auth`.
- Unsupported capabilities degrade to `degrade_to_manual_handoff`.
- `run_scripted_readonly_trial` attaches repo profile and budgets, validates a read-only request, records evidence, and returns a reviewable output summary.
- `scripts/run-readonly-trial.py` exposes one documented command for the first read-only trial.

## TDD Evidence
```powershell
python -m unittest tests.runtime.test_trial_entrypoint -v
python -m unittest discover -s tests/runtime -p "test_*.py" -v
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```

## Observed Red/Green
- Initial tests failed because `trial_entrypoint` did not exist.
- Script entrypoint test failed because `scripts/run-readonly-trial.py` did not exist.
- Tests passed after adding the minimal trial module and repo-root script.

## Verification Results
- `python -m unittest tests.runtime.test_trial_entrypoint -v` -> pass
- `python -m unittest discover -s tests/runtime -p "test_*.py" -v` -> pass
- `python scripts/run-readonly-trial.py --goal "inspect repository" --scope "readonly trial" --acceptance "readonly request accepted" --repo-profile "schemas/examples/repo-profile/python-service.example.json" --target-path "src/service.py" --max-steps 1 --max-minutes 5` -> pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` -> pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All` -> pass

## Gate Status
| gate | status | command | result | reason | alternative_verification | evidence_link | expires_at |
|---|---|---|---|---|---|---|---|
| build | `gate_na` | `n/a` | not run | no buildable Python package or runtime service artifact exists yet | runtime unit tests plus repo verifier | `docs/change-evidence/20260417-phase-1-scripted-trial-entrypoint.md` | `2026-05-31` |
| test | `active` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` | pass | Python runtime contract tests cover the scripted trial entrypoint | direct `python -m unittest discover -s tests/runtime -p "test_*.py"` | `docs/change-evidence/20260417-phase-1-scripted-trial-entrypoint.md` | `n/a` |
| contract/invariant | `active` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` | pass via `-Check All` | schema, examples, catalog, and paired specs remain the active contract baseline | full repository verification | `docs/change-evidence/20260417-phase-1-scripted-trial-entrypoint.md` | `n/a` |
| hotspot | `gate_na` | `n/a` | not run | no runtime doctor or health entrypoint exists yet | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs` | `docs/change-evidence/20260417-phase-1-scripted-trial-entrypoint.md` | `2026-05-31` |

## Residual Risks
- The entrypoint is scripted and read-only; it does not invoke Codex or run an autonomous agent session.
- Workspace allocation remains future work under `GAP-008`.
- This slice validates governance orchestration but not real agent output quality.
