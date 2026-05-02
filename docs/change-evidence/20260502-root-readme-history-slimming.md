# 2026-05-02 Root README History Slimming

## Basis
- Task 4 of `docs/plans/repo-slimming-and-speed-plan.md`
- Goal: keep root entrypoints focused on current posture and commands while moving long completion history behind stable archive links

## Commands
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`

## Changes
- Added archive pages for completed GAP history:
  - `docs/archive/completed-gap-history.md`
  - `docs/archive/completed-gap-history.zh-CN.md`
- Slimmed repeated completion-history blocks in:
  - `README.md`
  - `README.en.md`
  - `README.zh-CN.md`
- Slimmed long status lines in `docs/plans/README.md` and routed detailed completion history to the archive pages

## Compatibility
- No commands, gates, rule-sync entrypoints, rollback semantics, or safety boundaries were removed
- Existing certification and controlled-evolution evidence links remain reachable
- Root documentation still preserves Chinese and English operator-facing guidance

## Rollback
- Revert the touched files in git history if the shorter root entrypoint loses required operator context
