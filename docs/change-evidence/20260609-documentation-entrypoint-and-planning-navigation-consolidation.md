# 20260609 Documentation Entrypoint And Planning Navigation Consolidation

## Goal
- Current landing point: root/docs/plans/backlog entrypoints already contained the right facts, but they still forced readers to reconstruct `current truth` versus `history` from several long pages.
- Target home: make the authoritative entry surfaces say the same `Now / Next / Later / History` story without changing product direction, queue truth, or verification semantics.

## Scope
- Updated:
  - `README.md`
  - `README.zh-CN.md`
  - `README.en.md`
  - `docs/README.md`
  - `docs/plans/README.md`
  - `docs/backlog/README.md`
  - `docs/backlog/issue-ready-backlog.md`
  - `docs/change-evidence/README.md`
- Explicit non-goal:
  - no change to `planning-status.json`
  - no backlog id renumbering
  - no queue activation or claim upgrade

## Changes
- Added a top-level `Current Truth / Work Horizon` summary to `README.md`, `README.zh-CN.md`, and `README.en.md` so all three root entrypoints now separate current authority, active queue, conditional next queue, later trigger-based work, and history.
- Added `Quick Navigation` to `docs/README.md` to point readers directly to `Now / Next / Later / History` sources instead of forcing them through the entire working-set list first.
- Reframed `docs/plans/README.md` around `Current Navigation` plus `Plan Catalog`, so the active plan, conditional next plan, later trigger plans, and historical plans are separated before the full index.
- Reframed `docs/backlog/README.md` around `Current Navigation`, keeping `Issue-Ready Backlog` authoritative for dependency detail while making the active queue and conditional follow-on queue explicit.
- Added a small `Current Navigation` block to `docs/backlog/issue-ready-backlog.md` so the giant backlog ledger can still render as before while exposing the active/conditional/history split near the top.
- Added this evidence file and indexed it in `docs/change-evidence/README.md`.

## Compatibility Judgment
- `planning-status.json` remains the single source of current active queue, decision gate, and live posture.
- The new headings are additive and do not rename `### GAP-*` sections, so the issue-rendering parser contract should remain intact.
- This slice changes navigation and claim hygiene only; it does not strengthen any host capability or completion claim by itself.

## Verification
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  - result: pass
  - key output: `OK planning-status`, `OK claim-drift-sentinel`, `OK post-closeout-queue-sync`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`
  - result: pass
  - key output: `OK powershell-parse`, `OK issue-seeding-render`
- `git diff --check`
  - result: pass
  - note: returned only line-ending warnings for tracked files and no diff-format errors
- Full runtime hard gates: `gate_na`
  - reason: this slice only changes documentation entrypoints, indexes, and navigation wording
  - alternative_verification: `Docs` gate, `Scripts` gate, and `git diff --check`
  - evidence_link: this file
  - expires_at: `2026-06-09`

## Risks
- The main risk is future drift if a later doc refresh updates `planning-status.json` or the active queue but forgets to keep these summary sections aligned.
- The mitigation is to keep these new sections short and anchored to the same explicit sources instead of duplicating detailed queue history.

## Rollback
- Revert the eight documentation files changed in this slice plus this evidence file.
- If a later review decides the summary sections are still too verbose, keep the `Now / Next / Later / History` split but move more detail behind the linked source docs rather than removing the split entirely.
