# Plans Index

## Purpose
This directory holds executable implementation plans that translate strategy and backlog into ordered work.

## Current Authoritative Plan
- [Interactive Session Productization Plan](./interactive-session-productization-plan.md)
  - Status: active execution plan
  - Scope: `GAP-035` through `GAP-039` covering generic target-repo attachment, attach-first session bridge, direct Codex integration, capability-tiered adapters, and multi-repo trial feedback capture
- [Maintenance Implementation Plan](./maintenance-implementation-plan.md)
  - Status: completed execution plan kept as the local baseline maintenance checklist
  - Scope: `GAP-033` through `GAP-034` covering compatibility and upgrade policy, maintenance and triage rules, and deprecation or retirement visibility through runtime status and doctor checks
- [Public Usable Release Implementation Plan](./public-usable-release-implementation-plan.md)
  - Status: completed execution plan kept as the Public Usable Release closeout checklist
  - Scope: `GAP-029` through `GAP-032` covering bootstrap, quickstart, richer local operator surface, sample/demo profiles, packaging, release criteria, and adapter degrade behavior
- [Full Runtime Implementation Plan](./full-runtime-implementation-plan.md)
  - Status: completed execution plan kept as the Full Runtime closeout checklist
  - Scope: `GAP-024` through `GAP-028` covering worker execution, managed workspaces, artifact persistence, operational verification, replay data, and runtime status surfaces
- [Foundation Runtime Substrate Implementation Plan](./foundation-runtime-substrate-implementation-plan.md)
  - Status: completed Foundation execution plan kept as implementation history
  - Scope: `GAP-020` through `GAP-023` covering clarification and compatibility maturity, live build and doctor gates, durable task persistence skeleton, and control lifecycle or evidence completeness checks
- [Phase 0 Runnable Baseline Implementation Plan](./phase-0-runnable-baseline-implementation-plan.md)
  - Status: historical MVP-era implementation plan
  - Scope: repository skeleton, local verifier, CI minimums, runtime-consumable control-pack reference asset, repo admission planning, and gate routing cleanup

## How To Use This Directory
1. Read the latest audit review:
   - [Pre-Implementation Deep Audit And Doc Refresh](../reviews/2026-04-17-pre-implementation-deep-audit-and-doc-refresh.md)
2. Read the latest supporting evidence:
   - [20260417 Foundation Execution Plan](../change-evidence/20260417-foundation-execution-plan.md)
   - [20260418 Full Runtime Execution Plan](../change-evidence/20260418-full-runtime-execution-plan.md)
   - [20260418 Public Usable Release Execution Plan](../change-evidence/20260418-public-usable-release-execution-plan.md)
   - [20260418 Maintenance Execution Plan](../change-evidence/20260418-maintenance-execution-plan.md)
3. Use the roadmap and backlog to understand current posture:
   - the local runtime baseline through `Maintenance Baseline / GAP-034` is complete on the current branch baseline
   - use [Interactive Session Productization Plan](./interactive-session-productization-plan.md) as the active next-step entrypoint
   - use [Maintenance Implementation Plan](./maintenance-implementation-plan.md) as the latest completed baseline closeout history
   - keep future maintenance evidence in `docs/change-evidence/`

## Boundaries
- Plans here should be execution-oriented, not a duplicate of the PRD or architecture docs.
- Roadmap timing stays in `docs/roadmap/`.
- Gap ordering and dependencies stay in `docs/backlog/`.
- Historical plans remain useful evidence, but only one plan should be treated as the active next-step entrypoint at a time.
