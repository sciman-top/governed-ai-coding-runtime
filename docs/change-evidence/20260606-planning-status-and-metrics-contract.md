# 20260606 Planning Status And Metrics Contract

## Goal
- Establish a single source of planning truth for active queue, current decision gate, certified baseline, and current live posture.
- Separate historical certification from current live posture so stale or degraded host evidence cannot hide behind older closeout language.
- Turn PRD acceptance metrics into an executable contract vocabulary instead of a concept-only list.

## Root Cause And Changes
- Root cause:
  - Multiple documentation entrypoints disagreed on what the current active queue was.
  - Historical certification wording was easier to find than current stale/degraded host posture.
  - PRD metrics existed as labels, but not as operational definitions.
- Changes:
  - Added `docs/architecture/planning-status.json` as the single source of planning truth.
  - Added `scripts/verify-planning-status.py` and `tests/runtime/test_planning_status.py`.
  - Wired `planning-status` into `scripts/verify-repo.ps1 -Check Docs`.
  - Updated `README.md`, `README.en.md`, `README.zh-CN.md`, `docs/README.md`, `docs/plans/README.md`, `docs/backlog/README.md`, `docs/strategy/positioning-and-competitive-layering.md`, and `docs/product/interaction-model.md` to reference the new status source.
  - Added `docs/product/acceptance-metrics-contract.md`.
  - Downgraded `CLM-010` wording so it no longer overstates current dual-host `native_attach` parity while Codex target-run evidence is still stale/degraded.

## Verification
- `python scripts/select-next-work.py`
  - result: `next_action=refresh_evidence_first`; stale evidence and degraded host-capability posture are still active blockers.
- `python scripts/host-feedback-summary.py --assert-minimum`
  - result: overall `attention`; Claude workload probe is `native_attach` / ready, but latest target-run evidence is stale and Codex target runs remain `process_bridge` / degraded.
- `python scripts/verify-functional-effectiveness.py`
  - result: pass; latest functional-effectiveness evidence dated `2026-05-28` is still within freshness window.
- `python -m unittest tests.runtime.test_current_source_compatibility tests.runtime.test_planning_status tests.runtime.test_functional_effectiveness -v`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`

## Risks
- More doc entrypoints may still carry stale “active queue” wording outside the newly-checked surfaces.
- The status source is only trustworthy if future updates keep the docs gate green.
- Metrics are now defined, but not every metric is automatically emitted yet; some remain `manual_review_required`.

## Rollback
- Revert `docs/architecture/planning-status.json`, `docs/product/acceptance-metrics-contract.md`, `scripts/verify-planning-status.py`, `tests/runtime/test_planning_status.py`, the `verify-repo.ps1` gate wiring, and the linked doc wording updates.
