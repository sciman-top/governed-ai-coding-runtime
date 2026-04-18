# 20260419 Direct-To-Hybrid Final-State Implementation Plan

## Purpose
- User selected the next step after the new roadmap: write the direct implementation plan.
- Landing point: one future-facing implementation plan under `docs/plans/`.
- Target destination: convert the master outline, roadmap, and executable gap audit into ordered work batches with files, acceptance criteria, verification, and dependency sequencing.

## Clarification Trace
- `issue_id`: `direct-to-hybrid-final-state-implementation-plan`
- `attempt_count`: `1`
- `clarification_mode`: `direct_fix`
- `clarification_scenario`: `n/a`
- `clarification_questions`: `[]`
- `clarification_answers`: `[]`

## Basis
- `docs/architecture/hybrid-final-state-master-outline.md`
- `docs/roadmap/direct-to-hybrid-final-state-roadmap.md`
- `docs/reviews/2026-04-19-hybrid-final-state-executable-gap-audit.md`
- `docs/architecture/local-baseline-to-hybrid-final-state-migration-matrix.md`
- `docs/plans/interactive-session-productization-implementation-plan.md`
- `docs/plans/governance-runtime-strategy-alignment-plan.md`

## Change
- Added `docs/plans/direct-to-hybrid-final-state-implementation-plan.md`
- Updated `docs/plans/README.md` so the new plan is the active future-facing implementation mainline
- Added this evidence file

## Why This Matters
- The repository now has:
  - a canonical master outline
  - a canonical future roadmap
  - a canonical future implementation plan
- This removes the remaining ambiguity about which file owns:
  - final-state definition
  - phase order
  - executable work batches
- The new plan also turns the `HFG-001..007` and `HFG-H1..H3` audit output into explicit tasks instead of leaving them as review findings only.

## Files Added
- `docs/plans/direct-to-hybrid-final-state-implementation-plan.md`
- `docs/change-evidence/20260419-direct-to-hybrid-final-state-implementation-plan.md`

## Files Modified
- `docs/plans/README.md`

## Verification Plan
- Run the repository gate order after writing the plan:
  1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

## Risks
- This plan is intentionally future-facing. It defines exact work batches and likely file destinations, but those runtime files do not all exist yet.
- The new plan does not yet sync backlog or issue seeds. That is intentionally kept as Task 0 inside the plan rather than being silently done here.
- The plan introduces future `apps/`, `packages/agent-runtime/`, `packages/observability/`, and `infra/local-runtime/` file targets; those are planning commitments, not yet landed code.

## Rollback
- Delete:
  - `docs/plans/direct-to-hybrid-final-state-implementation-plan.md`
  - `docs/change-evidence/20260419-direct-to-hybrid-final-state-implementation-plan.md`
- Revert:
  - `docs/plans/README.md`
- Re-run the normal gate order to confirm the repository returns to the prior state.
