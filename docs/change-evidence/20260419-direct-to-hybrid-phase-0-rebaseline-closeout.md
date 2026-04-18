# 20260419 Direct-To-Hybrid Phase 0 Rebaseline Closeout

## Goal
- close the remaining `Phase 0 / GAP-045` planning sync work on the current branch baseline
- remove duplicate future-task queuing for already-landed session-bridge and attached-write capabilities
- align docs, backlog, issue seeds, GitHub issue seeding, and tests around one direct-to-hybrid-final-state mainline

## Basis
- `docs/architecture/hybrid-final-state-master-outline.md`
- `docs/roadmap/direct-to-hybrid-final-state-roadmap.md`
- `docs/plans/direct-to-hybrid-final-state-implementation-plan.md`
- `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/issue-seeds.yaml`
- `docs/reviews/2026-04-19-hybrid-final-state-executable-gap-audit.md`
- `scripts/github/create-roadmap-issues.ps1`

## Current Landing
- worktree: `D:\OneDrive\CODE\governed-ai-coding-runtime`
- branch: `main`
- planning package:
  - `docs/architecture/hybrid-final-state-master-outline.md`
  - `docs/roadmap/direct-to-hybrid-final-state-roadmap.md`
  - `docs/plans/direct-to-hybrid-final-state-implementation-plan.md`
- active queue surfaces:
  - `docs/backlog/issue-ready-backlog.md`
  - `docs/backlog/issue-seeds.yaml`
  - `scripts/github/create-roadmap-issues.ps1`

## Changes
- added a capability-closure snapshot to the master outline so landed surfaces and remaining closure gaps are separated explicitly
- corrected the executable-gap audit so `HFG-001` and `HFG-002` no longer describe already-landed bridge or attached-write capabilities as missing
- added an interpretation guardrail to the lifecycle plan so `Stage 7/8 complete` no longer reads like `complete hybrid final-state closure`
- marked `Phase 0 / GAP-045` complete on the current branch baseline and narrowed `GAP-046` plus `GAP-047` to the real residual work
- updated the direct roadmap and implementation plan so `Phase 1` now targets plan-only gates, live-session identity binding, and remaining governed-execution closure instead of re-adding existing bridge commands
- extended the GitHub issue seeding script to render both historical lifecycle epics and active direct-mainline `Phase 0..5` epics
- changed GitHub task issue creation to skip backlog items whose status is already `complete`, while still validating all seed bodies for history consistency
- updated the issue-seeding runtime test to validate the new epic count instead of the historical `7`-epic assumption
- updated the issue-seeding runtime test to validate that issue creation only targets the active backlog queue

## Commands And Evidence

| cmd | exit_code | key_output |
|---|---:|---|
| `python -m unittest tests.runtime.test_issue_seeding.IssueSeedingScriptTests.test_validate_only_render_all_checks_all_issue_body_sources` | 1 | pre-fix red: `AssertionError: 43 != 15` |
| `python -m unittest tests.runtime.test_issue_seeding.IssueSeedingScriptTests.test_validate_only_render_all_checks_all_issue_body_sources` | 0 | post-fix green: `Ran 1 test` / `OK` |
| `python -m unittest tests.runtime.test_issue_seeding` | 0 | `Ran 8 tests` / `OK` |
| `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1` | 0 | `OK python-bytecode`; `OK python-import` |
| `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` | 0 | `Ran 204 tests` / `OK runtime-unittest` |
| `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` | 0 | `OK schema-json-parse`; `OK schema-example-validation`; `OK schema-catalog-pairing` |
| `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1` | 0 | `OK gate-command-build`; `OK gate-command-test`; `OK gate-command-contract`; `OK gate-command-doctor` |
| `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs` | 0 | `OK active-markdown-links`; `OK backlog-yaml-ids`; `OK old-project-name-historical-only` |
| `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts` | 0 | `OK powershell-parse`; `OK issue-seeding-render` |
| `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll` | 0 | `issue_seed_version = 3.4`; `rendered_tasks = 43`; `rendered_issue_creation_tasks = 15`; `rendered_epics = 13` |
| `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -EpicId "Phase 0"` | 0 | `title = [Epic] Phase 0 Canonical Re-Baseline`; body includes completed Phase 0 status |
| `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All` | 0 | `OK runtime-build`; `OK runtime-doctor`; `OK issue-seeding-render`; `Ran 204 tests` |

## Risks
- the new `Phase 0..5` GitHub epics now coexist with the historical lifecycle epics; this is intentional, but future issue hygiene should decide whether to keep both or eventually freeze the historical epic set
- historical completed GAP tasks remain renderable for validation, but new GitHub task issue creation now only targets active backlog entries; if a future workflow needs full-history issue recreation, it should add an explicit mode instead of overloading the default seeding path
- `GAP-046` and `GAP-047` were narrowed to the real residual work, but they still depend on future runtime behavior changes that are not part of this closeout
- the current repository still does not satisfy complete hybrid final-state closure; this closeout only fixes the planning baseline and claim discipline

## Rollback
- prefer git diff or commit-level rollback for the planning docs, backlog, issue seeds, test update, and seeding script change
- if selective rollback is needed, revert:
  - `docs/architecture/hybrid-final-state-master-outline.md`
  - `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
  - `docs/roadmap/direct-to-hybrid-final-state-roadmap.md`
  - `docs/plans/direct-to-hybrid-final-state-implementation-plan.md`
  - `docs/plans/README.md`
  - `docs/backlog/issue-ready-backlog.md`
  - `docs/backlog/issue-seeds.yaml`
  - `docs/reviews/2026-04-19-hybrid-final-state-executable-gap-audit.md`
  - `scripts/github/create-roadmap-issues.ps1`
  - `tests/runtime/test_issue_seeding.py`

## Status
- `Phase 0 / GAP-045`: complete on the current branch baseline
- direct-to-hybrid-final-state planning package: canonical and validated
- active future-facing runtime queue: `GAP-046` through `GAP-060`
