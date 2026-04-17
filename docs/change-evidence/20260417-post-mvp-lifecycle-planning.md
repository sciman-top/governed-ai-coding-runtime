# 20260417 Post-MVP Lifecycle Planning

## Goal
Turn the repository's post-MVP boundary from a documentation note into an executable lifecycle plan, task backlog, machine-readable issue seeds, and synchronized GitHub issue seeding script.

## Current Landing
- Roadmap status: `docs/roadmap/governed-ai-coding-runtime-post-mvp-lifecycle-plan.md`
- Backlog status: `docs/backlog/post-mvp-backlog-seeds.md`
- Active issue backlog: `docs/backlog/issue-ready-backlog.md`
- Active issue seeds: `docs/backlog/issue-seeds.yaml`
- Docs index status: `docs/README.md`
- Root status: `README.md`
- Chinese usage guide: `README.zh-CN.md`
- English usage guide: `README.en.md`
- GitHub seeding script: `scripts/github/create-roadmap-issues.ps1`

## Basis
- `docs/README.md` already states that MVP execution is complete through `GAP-017` and the next work should be a new post-MVP plan.
- `docs/backlog/README.md` already states that work beyond `GAP-017` should create a post-MVP roadmap/backlog and then sync the active backlog, YAML, and seeding script.
- `docs/adrs/0001-control-plane-first.md`, `0003-single-agent-baseline-first.md`, `0005-governance-kernel-and-control-packs-before-platform-breadth.md`, and `0006-final-state-best-practice-agent-compatibility.md` define the non-negotiable post-MVP boundaries.
- `docs/research/repo-governance-hub-borrowing-review.md` identifies the first post-MVP mechanism wave: clarification, rollout, compatibility, evidence completeness, and control lifecycle metadata.

## Files Changed
- `README.md`
- `README.en.md`
- `README.zh-CN.md`
- `docs/README.md`
- `docs/backlog/README.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/issue-seeds.yaml`
- `docs/backlog/post-mvp-backlog-seeds.md`
- `docs/change-evidence/README.md`
- `docs/change-evidence/20260417-post-mvp-lifecycle-planning.md`
- `docs/roadmap/governed-ai-coding-runtime-post-mvp-lifecycle-plan.md`
- `scripts/github/create-roadmap-issues.ps1`

## Change
- Added a new post-MVP lifecycle roadmap with `Phase 5` through `Phase 9`.
- Added a post-MVP seed document that turns the deferred-item direction into phase-level execution slices.
- Replaced the active `issue-ready-backlog.md` and `issue-seeds.yaml` queue so it now starts at `GAP-018`.
- Repointed docs and README entry surfaces to the new active queue while preserving the 90-day MVP plan as historical baseline.
- Replaced the GitHub seeding script so it now seeds the post-MVP initiative, epics, labels, and tasks.

## Verification Commands
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
git diff --check
git status --short
```

## Gate Status
| gate | status | command | result | reason | alternative_verification | evidence_link | expires_at |
|---|---|---|---|---|---|---|---|
| build | `gate_na` | `n/a` | not run | the repository still does not ship a real buildable runtime package or production runtime service on the active branch | repo verifier plus runtime contract tests | `docs/change-evidence/20260417-post-mvp-lifecycle-planning.md` | `2026-05-31` |
| test | `active` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` | pass via `-Check All` | runtime contract tests remain the active test gate | direct `python -m unittest discover -s tests/runtime -p "test_*.py"` | `docs/change-evidence/20260417-post-mvp-lifecycle-planning.md` | `n/a` |
| contract/invariant | `active` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` | pass via `-Check All` | schemas, examples, catalog, docs, and scripts remain the active contract boundary | full repository verification | `docs/change-evidence/20260417-post-mvp-lifecycle-planning.md` | `n/a` |
| hotspot | `gate_na` | `n/a` | not run | no runtime doctor or health entrypoint exists yet on the current branch | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs` | `docs/change-evidence/20260417-post-mvp-lifecycle-planning.md` | `2026-05-31` |

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
- `git status --short` -> modified tracked docs/scripts plus three new planning files

## Residual Risks
- The repository still lacks real build and hotspot commands; this plan only makes them executable backlog items.
- The seeding script still owns its issue body text directly instead of generating from YAML, so future planning edits must keep those three surfaces aligned manually.
- The worktree remains dirty; this documentation change does not group or clean unrelated edits.

## Rollback
- Prefer git history for rollback once the change is committed.
- Before commits exist, rollback is by targeted diff reversal of the files listed above; do not use broad reset commands against the dirty worktree.
