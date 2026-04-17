# 20260417 Full Lifecycle Functional Planning

## Goal
Replace the intermediate post-MVP planning baseline with a function-first full lifecycle plan for the final product.

## Current Landing
- Roadmap status: `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- Backlog status: `docs/backlog/full-lifecycle-backlog-seeds.md`
- Active issue backlog: `docs/backlog/issue-ready-backlog.md`
- Active issue seeds: `docs/backlog/issue-seeds.yaml`
- Docs index status: `docs/README.md`
- Root status: `README.md`
- Chinese usage guide: `README.zh-CN.md`
- English usage guide: `README.en.md`
- GitHub seeding script: `scripts/github/create-roadmap-issues.ps1`

## Basis
- The user explicitly clarified that this project remains a personal free open-source project and that planning should emphasize function completeness while minimizing non-essential operational scope.
- The final design confirmed in-session was:
  - single-machine self-hosted first
  - internal service-shaped boundaries
  - function-first lifecycle stages: `Vision -> MVP -> Foundation -> Full Runtime -> Public Usable Release -> Maintenance`
  - a final capability boundary covering task lifecycle, repo admission, governed execution, approval, durable runtime, verification, evidence/replay, operator surface, and adapter compatibility

## Files Changed
- `README.md`
- `README.en.md`
- `README.zh-CN.md`
- `docs/README.md`
- `docs/backlog/README.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/issue-seeds.yaml`
- `docs/backlog/full-lifecycle-backlog-seeds.md`
- `docs/change-evidence/README.md`
- `docs/change-evidence/20260417-full-lifecycle-functional-planning.md`
- `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- `scripts/github/create-roadmap-issues.ps1`

## Change
- Added a new active full-lifecycle roadmap focused on the final functional product.
- Added a new active full-lifecycle seed file.
- Replaced the active `issue-ready-backlog.md` and `issue-seeds.yaml` queue so it now follows the new lifecycle grouping while preserving `GAP-018+`.
- Repointed root/docs entry surfaces from the intermediate post-MVP plan to the new full-lifecycle plan.
- Replaced the GitHub seeding script so it now seeds the full-lifecycle initiative, epics, labels, and tasks.

## Verification Commands
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
git diff --check
git status --short
```

## Gate Status
| gate | status | command | result | reason | alternative_verification | evidence_link | expires_at |
|---|---|---|---|---|---|---|---|
| build | `gate_na` | `n/a` | not run | the repository still does not ship a real buildable runtime package or production runtime service on the active branch | repo verifier plus runtime contract tests | `docs/change-evidence/20260417-full-lifecycle-functional-planning.md` | `2026-05-31` |
| test | `active` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` | pass via `-Check All` | runtime contract tests remain the active test gate | direct `python -m unittest discover -s tests/runtime -p "test_*.py"` | `docs/change-evidence/20260417-full-lifecycle-functional-planning.md` | `n/a` |
| contract/invariant | `active` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` | pass via `-Check All` | schemas, examples, catalog, docs, and scripts remain the active contract boundary | full repository verification | `docs/change-evidence/20260417-full-lifecycle-functional-planning.md` | `n/a` |
| hotspot | `gate_na` | `n/a` | not run | no runtime doctor or health entrypoint exists yet on the current branch | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs` | `docs/change-evidence/20260417-full-lifecycle-functional-planning.md` | `2026-05-31` |

## Verification Result
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All` -> pass
  - `OK runtime-unittest`
  - `OK schema-json-parse`
  - `OK schema-example-validation`
  - `OK schema-catalog-pairing`
  - `OK active-markdown-links`
  - `OK backlog-yaml-ids`
  - `OK old-project-name-historical-only`
  - `OK powershell-parse`
  - `Ran 64 tests`
  - `OK`
- `git diff --check` -> pass with line-ending warnings only; no whitespace errors
- `git status --short` -> modified tracked docs/scripts plus new full-lifecycle planning files; the dirty worktree still also contains preserved untracked post-MVP bridge files

## Residual Risks
- The full lifecycle plan still schedules real `build` and `doctor|hotspot` commands as future work rather than landing them immediately.
- The GitHub seeding script still owns its issue bodies directly instead of generating from YAML, so future planning edits still need three-surface synchronization.
- The worktree remains dirty; this planning refresh does not group unrelated changes into commits.

## Rollback
- Prefer git history for rollback once the change is committed.
- Before commits exist, rollback is by targeted diff reversal of the files listed above; do not use broad reset commands against the dirty worktree.
