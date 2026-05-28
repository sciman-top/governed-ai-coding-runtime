# 2026-05-28 Claim Catalog Freshness Refresh

## Goal
- Refresh stale claim-catalog evidence links for `CLM-002..010` without changing claim text, source references, or product scope.
- Keep Docs gate freshness aligned with the current 30-day claim evidence window.

## Root Cause And Changes
- `scripts/verify-repo.ps1 -Check Docs` enforces that each `docs/product/claim-catalog.json` evidence link is no older than 30 days.
- On `2026-05-28`, `CLM-002..010` still pointed to April 2026 evidence files that were 31-38 days old.
- Updated `CLM-002..010` to point to this freshness refresh evidence file.
- This is a claim freshness refresh only. The original implementation closeouts remain historical evidence for the underlying GAP work.

## Verification
- `CLM-002`: onboarding inference source refs remain in `docs/quickstart/use-with-existing-repo.md` and `docs/quickstart/use-with-existing-repo.zh-CN.md`.
- `CLM-003`: medium/high-risk governed write source refs remain in `README.en.md` and `README.zh-CN.md`.
- `CLM-004`: canonical acceptance chain source refs remain in `README.en.md` and `README.zh-CN.md`.
- `CLM-005`: speed posture source refs remain in `docs/product/multi-repo-trial-loop.md` and `docs/product/multi-repo-trial-loop.zh-CN.md`.
- `CLM-006`: hybrid final-state closure source refs remain in roadmap, implementation plan, and claim catalog surfaces.
- `CLM-007`: current-source compatibility source refs remain in policy and docs surfaces.
- `CLM-008`: LTP promotion fence source refs remain in policy, ADR, and plan surfaces.
- `CLM-009`: autonomous next-work selector source refs remain in policy and operator-facing surfaces.
- `CLM-010`: Claude Code first-class host source refs remain in plan/evidence surfaces.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs` is the proof command that re-validates source refs, freshness, and active markdown links.

## Rollback
- Restore `CLM-002..010` evidence links in `docs/product/claim-catalog.json` to their previous April 2026 evidence files.
- Remove `docs/change-evidence/20260528-claim-catalog-freshness-refresh.md`.
