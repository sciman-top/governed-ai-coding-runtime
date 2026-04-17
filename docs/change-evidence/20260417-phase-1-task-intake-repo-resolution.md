# 20260417 Phase 1 Task Intake And Repo Resolution

## Goal
Start `GAP-004 Deterministic Task Intake And Repo Resolution` with a narrow, dependency-free Python contract layer.

## Current Landing
- Runtime contract package: `packages/contracts/`
- Runtime tests: `tests/runtime/`
- Verification entrypoint: `scripts/verify-repo.ps1 -Check Runtime`
- Rollback path: file-level git diff review because the worktree was already dirty before this slice

## Implemented Slice
- `TaskIntake` requires `goal`, `scope`, `acceptance`, `repo`, and `budgets`.
- `validate_transition` only allows required lifecycle transitions from `docs/specs/task-lifecycle-and-state-machine-spec.md`.
- `RepoProfile` loads existing sample repo profiles and exposes command ids.
- `RepoProfile.from_dict` enforces minimum admission checks for identity, commands, tools, and read scope.
- `scripts/verify-repo.ps1` now supports `-Check Runtime` and includes runtime tests in `-Check All`.

## TDD Evidence
```powershell
python -m unittest tests.runtime.test_task_intake -v
python -m unittest tests.runtime.test_repo_profile -v
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```

## Observed Red/Green
- Initial task intake tests failed because `TaskIntake` and `validate_transition` did not exist.
- Task behavior tests failed until required field validation and explicit transition allowlist were implemented.
- Initial repo profile tests failed because `RepoProfile.from_dict` and `command_ids` did not exist.
- Repo profile tests passed after minimal parser and admission checks were implemented.

## Verification Results
- `python -m unittest tests.runtime.test_task_intake -v` -> pass
- `python -m unittest tests.runtime.test_repo_profile -v` -> pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` -> pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All` -> pass

## Gate Status
| gate | status | command | result | reason | alternative_verification | evidence_link | expires_at |
|---|---|---|---|---|---|---|---|
| build | `gate_na` | `n/a` | not run | no buildable Python package or runtime service artifact exists yet | runtime unit tests plus repo verifier | `docs/change-evidence/20260417-phase-1-task-intake-repo-resolution.md` | `2026-05-31` |
| test | `active` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` | pass | Python runtime contract tests exist under `tests/runtime/` | direct `python -m unittest discover -s tests/runtime -p "test_*.py"` | `docs/change-evidence/20260417-phase-1-task-intake-repo-resolution.md` | `n/a` |
| contract/invariant | `active` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` | pass via `-Check All` | schema, examples, catalog, and paired specs remain the active contract baseline | full repository verification also passed | `docs/change-evidence/20260417-phase-1-task-intake-repo-resolution.md` | `n/a` |
| hotspot | `gate_na` | `n/a` | not run | no runtime doctor or health entrypoint exists yet | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs` via `-Check All` | `docs/change-evidence/20260417-phase-1-task-intake-repo-resolution.md` | `2026-05-31` |

## Residual Risks
- Task persistence is not implemented yet; `TaskIntake` is an in-memory domain object only.
- Repo profile validation is a minimum runtime admission check, not full JSON Schema validation.
- API, database, workspace allocation, and agent execution remain out of scope for this slice.
- Build remains `gate_na` until Python packaging or a runtime service build entrypoint lands.
