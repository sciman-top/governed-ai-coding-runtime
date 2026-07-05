# 2026-07-05 Claim Catalog Freshness Refresh

## Goal
- Refresh stale claim-catalog evidence links for `CLM-001..010` without changing claim scope, source references, or product boundary.
- Keep Docs gate freshness aligned with the current 30-day claim evidence window while the repo closes the 2026-07-05 evidence refresh loop.

## Root Cause And Changes
- `scripts/verify-repo.ps1 -Check Docs` enforces that each `docs/product/claim-catalog.json` evidence link is no older than 30 days.
- On `2026-07-05`, the evidence links for `CLM-001..010` still pointed to `2026-05-28` claim-refresh notes, which were older than the 30-day freshness window.
- Updated `CLM-001..010` to point to this fresh claim-catalog evidence note.
- This is a claim-freshness refresh only. The original implementation closeouts remain the historical implementation evidence for each underlying claim.

## Verification
- `CLM-001`: host-neutral boundary source refs remain in `README.en.md` and `README.zh-CN.md`.
- `CLM-002`: onboarding inference source refs remain in `docs/quickstart/use-with-existing-repo.md` and `docs/quickstart/use-with-existing-repo.zh-CN.md`.
- `CLM-003`: medium/high-risk governed write source refs remain in `README.en.md` and `README.zh-CN.md`.
- `CLM-004`: canonical acceptance-chain source refs remain in `README.en.md` and `README.zh-CN.md`.
- `CLM-005`: speed-posture source refs remain in `docs/product/multi-repo-trial-loop.md` and `docs/product/multi-repo-trial-loop.zh-CN.md`.
- `CLM-006`: hybrid final-state closure source refs remain in `README.md` and `docs/architecture/hybrid-final-state-master-outline.md`.
- `CLM-007`: current-source compatibility source refs remain in `docs/architecture/hybrid-final-state-master-outline.md` and `docs/roadmap/optimized-hybrid-final-state-long-term-roadmap.md`.
- `CLM-008`: LTP promotion fence source refs remain in `docs/adrs/0008-autonomous-ltp-promotion-scope-fence.md` and `docs/architecture/ltp-autonomous-promotion-policy.json`.
- `CLM-009`: autonomous next-work selector source refs remain in `docs/architecture/autonomous-next-work-selection-policy.json` and `docs/architecture/hybrid-final-state-master-outline.md`.
- `CLM-010`: Claude Code first-class host source refs remain in `docs/plans/claude-code-first-class-entrypoint-plan.md` and `docs/backlog/issue-ready-backlog.md`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs` is the proof command that re-validates source refs, freshness, and active markdown links.
  - result: pass; Docs gate closed through `OK claim-drift-sentinel`, `OK claim-evidence-freshness`, and `OK post-closeout-queue-sync`

## Rollback
- Restore `CLM-001..010` evidence links in `docs/product/claim-catalog.json` to their previous evidence files.
- Remove `docs/change-evidence/20260705-claim-catalog-freshness-refresh.md`.
