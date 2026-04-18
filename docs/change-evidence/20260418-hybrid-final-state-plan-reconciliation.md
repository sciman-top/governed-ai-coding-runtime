# 20260418 Hybrid Final-State Plan Reconciliation

## Goal
- Landing point: the branch already contains the strategy-alignment outputs and the active `GAP-035` through `GAP-039` productization plan.
- Target destination: reconcile active planning docs, review/navigation indexes, and governance terminology so the hybrid final state is described consistently and future execution does not re-open already settled boundaries.

## Findings
1. `docs/plans/interactive-session-productization-implementation-plan.md` still listed several completed `GAP-040` through `GAP-044` outputs as future creates and referenced a non-existent source input (`docs/specs/delivery-handoff-spec.md`).
2. The final-state terminology still drifted between older baseline language (`safe / approval-required / blocked`, `allowed / paused`) and the newer `PolicyDecision` interface (`allow / escalate / deny`).
3. `docs/plans/README.md` and `docs/reviews/README.md` did not point readers at a current hybrid-final-state audit baseline.

## Changes
- Clarified the hybrid final-state decomposition in `docs/strategy/positioning-and-competitive-layering.md`.
- Updated the lifecycle roadmap to describe the hybrid boundary explicitly and to map user-facing governance buckets onto `PolicyDecision`.
- Updated `docs/backlog/issue-ready-backlog.md` so `GAP-036` explicitly includes `PolicyDecision` normalization at the session-bridge boundary.
- Added status guardrails to the older `interactive-session-productization-plan.md` and `governance-runtime-strategy-alignment-plan.md` so neither historical plan can be mistaken for the active implementation checklist.
- Reconciled `docs/plans/interactive-session-productization-implementation-plan.md`:
  - moved landed `GAP-042` and `GAP-043` artifacts out of future-create lists
  - fixed the invalid `delivery-handoff` source input reference
  - marked `GAP-040` through `GAP-044` as completed dependency gates rather than an active second queue
  - added explicit future work to normalize legacy write-governance results into `PolicyDecision`
- Updated the PRD to state that runtime execution decisions converge on `PolicyDecision` `allow / escalate / deny`.
- Added a new review anchor at `docs/reviews/2026-04-18-hybrid-final-state-and-plan-reconciliation.md` and repointed plan/review indexes to it.

## Commands
| cmd | exit_code | key_output | timestamp |
|---|---:|---|---|
| `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1` | `0` | `OK python-bytecode`, `OK python-import` | `2026-04-18T20:01:25.3916338+08:00` |
| `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` | `0` | `OK runtime-unittest` | `2026-04-18T20:01:26.1494827+08:00` |
| `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` | `0` | `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing` | `2026-04-18T20:01:44.0030289+08:00` |
| `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1` | `0` | `OK python-command`, `OK gate-command-build`, `OK gate-command-doctor`, `OK adapter-posture-visible` | `2026-04-18T20:01:44.7986025+08:00` |
| `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All` | `0` | `OK runtime-build`, `OK runtime-unittest`, `OK active-markdown-links`, `OK issue-seeding-render` | `2026-04-18T20:01:45.5904496+08:00` |
| `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll` | `0` | `issue_seed_version=3.2`, `rendered_tasks=27`, `rendered_epics=7` | `2026-04-18T20:02:06.4009757+08:00` |

## Risks
- This change reconciles planning and terminology only. It does not implement `GAP-035` through `GAP-039`.
- Legacy local-baseline code still emits `allowed` / `paused` semantics internally until the future productization work performs the planned normalization.

## Rollback
- Revert the planning, roadmap, PRD, strategy, and review-index wording changes in this changeset.
- Delete `docs/reviews/2026-04-18-hybrid-final-state-and-plan-reconciliation.md`.
- Delete this evidence file and remove its index entry from `docs/change-evidence/README.md`.
