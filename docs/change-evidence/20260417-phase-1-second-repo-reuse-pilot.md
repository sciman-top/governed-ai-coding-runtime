# 20260417 Phase 1 Second-Repo Reuse Pilot

## Goal
Execute `GAP-015 Second-Repo Reuse Pilot` against existing sample repo profiles without creating external repository facts.

## Current Landing
- Pilot module: `packages/contracts/src/governed_ai_coding_runtime_contracts/second_repo_pilot.py`
- Runtime tests: `tests/runtime/test_second_repo_pilot.py`
- Policy record: `docs/product/second-repo-reuse-pilot.md`
- Backlog trace: `docs/backlog/issue-ready-backlog.md`

## Implemented Slice
- `run_second_repo_reuse_pilot` compares the Python service and TypeScript webapp profiles.
- The pilot verifies both profiles use the same kernel-required sections.
- Differences are reported as repo profile values, not kernel overrides.
- `generic_process_adapter_declaration` represents a non-Codex product shape.
- `classify_adapter_compatibility` records logs-only visibility as an adapter gap.

## TDD Evidence
```powershell
python -m unittest tests.runtime.test_second_repo_pilot -v
python -m unittest discover -s tests/runtime -p "test_*.py" -v
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```

## Observed Red/Green
- Initial tests failed because `governed_ai_coding_runtime_contracts.second_repo_pilot` did not exist.
- Tests passed after adding the pilot module and generic process adapter declaration.

## Verification Results
- `python -m unittest tests.runtime.test_second_repo_pilot -v` -> pass
- `python -m unittest discover -s tests/runtime -p "test_*.py" -v` -> pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` -> pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All` -> pass
- `git diff --check` -> pass with CRLF normalization warnings only

## Gate Status
| gate | status | command | result | reason | alternative_verification | evidence_link | expires_at |
|---|---|---|---|---|---|---|---|
| build | `gate_na` | `n/a` | not run | no buildable Python package or runtime service artifact exists yet | runtime unit tests plus repo verifier | `docs/change-evidence/20260417-phase-1-second-repo-reuse-pilot.md` | `2026-05-31` |
| test | `active` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` | pass | Python runtime contract tests cover second-repo pilot checks | direct `python -m unittest discover -s tests/runtime -p "test_*.py"` | `docs/change-evidence/20260417-phase-1-second-repo-reuse-pilot.md` | `n/a` |
| contract/invariant | `active` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` | pass via `-Check All` | schema, examples, catalog, and paired specs remain the active contract baseline | full repository verification | `docs/change-evidence/20260417-phase-1-second-repo-reuse-pilot.md` | `n/a` |
| hotspot | `gate_na` | `n/a` | not run | no runtime doctor or health entrypoint exists yet | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs` | `docs/change-evidence/20260417-phase-1-second-repo-reuse-pilot.md` | `2026-05-31` |

## Residual Risks
- This pilot uses sample repo profiles, not a checked-out external repository.
- The generic process adapter is a compatibility declaration; no process execution adapter is implemented yet.
