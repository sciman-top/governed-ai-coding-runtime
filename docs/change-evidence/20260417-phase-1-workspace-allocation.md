# 20260417 Phase 1 Workspace Allocation

## Goal
Execute `GAP-008 Isolated Workspace Allocation` as a pure runtime contract slice.

## Current Landing
- Workspace module: `packages/contracts/src/governed_ai_coding_runtime_contracts/workspace.py`
- Runtime tests: `tests/runtime/test_workspace_allocation.py`
- Backlog trace: `docs/backlog/issue-ready-backlog.md`

## Implemented Slice
- `allocate_workspace` creates a task-scoped allocation under `.governed-workspaces/<repo>/<task>`.
- Arbitrary absolute live directories are rejected before allocation.
- `validate_write_path` enforces `write_allow` and `blocked` policies from the repo profile.
- The slice intentionally does not create real directories or invoke `git worktree`.

## TDD Evidence
```powershell
python -m unittest tests.runtime.test_workspace_allocation -v
python -m unittest discover -s tests/runtime -p "test_*.py" -v
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```

## Observed Red/Green
- Initial tests failed because `governed_ai_coding_runtime_contracts.workspace` did not exist.
- Tests passed after adding the minimal workspace allocation module.

## Verification Results
- `python -m unittest tests.runtime.test_workspace_allocation -v` -> pass
- `python -m unittest discover -s tests/runtime -p "test_*.py" -v` -> pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` -> pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All` -> pass
- `git diff --check` -> pass with CRLF normalization warnings only

## Gate Status
| gate | status | command | result | reason | alternative_verification | evidence_link | expires_at |
|---|---|---|---|---|---|---|---|
| build | `gate_na` | `n/a` | not run | no buildable Python package or runtime service artifact exists yet | runtime unit tests plus repo verifier | `docs/change-evidence/20260417-phase-1-workspace-allocation.md` | `2026-05-31` |
| test | `active` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` | pass | Python runtime contract tests cover workspace allocation | direct `python -m unittest discover -s tests/runtime -p "test_*.py"` | `docs/change-evidence/20260417-phase-1-workspace-allocation.md` | `n/a` |
| contract/invariant | `active` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` | pass via `-Check All` | schema, examples, catalog, and paired specs remain the active contract baseline | full repository verification | `docs/change-evidence/20260417-phase-1-workspace-allocation.md` | `n/a` |
| hotspot | `gate_na` | `n/a` | not run | no runtime doctor or health entrypoint exists yet | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs` | `docs/change-evidence/20260417-phase-1-workspace-allocation.md` | `2026-05-31` |

## Residual Risks
- This is allocation policy only; real filesystem isolation and cleanup remain future implementation work.
- Write policy matching is intentionally minimal and should be hardened before allowing broad mutation workflows.
