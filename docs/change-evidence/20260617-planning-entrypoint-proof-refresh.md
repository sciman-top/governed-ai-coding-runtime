# 20260617 Planning EntryPoint Proof Refresh

## Goal
- current landing: `D:\CODE\governed-ai-coding-runtime`
- target home:
  - `README.md`
  - `README.en.md`
  - `README.zh-CN.md`
  - `docs/README.md`
  - `docs/backlog/README.md`
  - `docs/plans/README.md`
  - `docs/plans/host-family-capability-operationalization-plan.md`
  - `docs/strategy/current-best-end-state-blueprint.md`
  - `docs/strategy/positioning-and-competitive-layering.md`
  - `scripts/verify-planning-status.py`
  - `tests/runtime/test_planning_status.py`
- verification path: keep the current active queue and decision gate truthful, downgrade `20260609 Live Posture Recovery` to historical milestone wording, and make the 2026-06-17 active-loop refresh the primary live-posture proof anchor across the repo entrypoints

## Why This Refresh Was Needed
- The repository root, docs index, backlog index, and strategy pages still allowed `20260609 Live Posture Recovery` to read like the latest live-posture proof even after the 2026-06-17 active-loop refresh had become the current authoritative posture proof.
- `docs/architecture/planning-status.json` already pointed at `20260617-active-queue-evidence-upkeep-refresh.md`, so the entrypoint surfaces needed to stop implying that 2026-06-09 was still the primary proof anchor.
- The goal here was not to change the historical evidence itself; it was to make the repo entrypoints, planning-status verifier, and tests agree on which proof is current and which is historical.

## Change Summary
1. Re-centered the main entrypoints on the 2026-06-17 proof anchor
- updated `README.md`, `README.en.md`, `README.zh-CN.md`, and `docs/README.md`
- kept `20260609 Live Posture Recovery` visible as a historical milestone, but no longer as the newest posture proof
- updated `docs/backlog/README.md` so the Codex target-run recovery sentence now cites the 2026-06-17 active-loop refresh

2. Strengthened the planning-status verifier
- added required-token checks that require:
  - `20260617 Active Queue Evidence-Upkeep Refresh` in the main README surfaces
  - `2026-06-17` proof anchoring in strategy/backlog surfaces
- extended stale checks so the verifier fails if the repo still treats `20260609 Live Posture Recovery` as the latest live-posture proof
- added regression coverage for the updated proof ordering and history wording

3. Preserved conditional-queue and active-queue truth
- kept `docs/plans/README.md`, `docs/plans/host-family-capability-operationalization-plan.md`, `docs/strategy/current-best-end-state-blueprint.md`, and `docs/strategy/positioning-and-competitive-layering.md` aligned to `Continuous-Execution`
- retained the current selector posture `defer_ltp_and_refresh_evidence`

## Verification
- `python -m unittest tests.runtime.test_planning_status -v`
  - result: pass
- `python scripts/verify-planning-status.py`
  - result: pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  - result: pass

## Queue Boundary
- This refresh updates proof anchoring and verifier coverage only.
- It does **not** promote any new queue.
- It does **not** change selector behavior or live posture.

## Risk
- risk_level: `low`
- reason:
  - wording and verifier refresh only
  - no contract broadening
  - no execution-path mutation

## Rollback
- revert:
  - `README.md`
  - `README.en.md`
  - `README.zh-CN.md`
  - `docs/README.md`
  - `docs/backlog/README.md`
  - `docs/plans/README.md`
  - `docs/plans/host-family-capability-operationalization-plan.md`
  - `docs/strategy/current-best-end-state-blueprint.md`
  - `docs/strategy/positioning-and-competitive-layering.md`
  - `scripts/verify-planning-status.py`
  - `tests/runtime/test_planning_status.py`
- re-run:
  - `python -m unittest tests.runtime.test_planning_status -v`
  - `python scripts/verify-planning-status.py`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
