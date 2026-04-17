# Plans Index

## Purpose
This directory holds executable implementation plans that translate strategy and backlog into ordered work.

## Current Authoritative Plan
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
3. Use the roadmap and backlog to choose the next implementation queue:
   - `Full Runtime / GAP-024` is now the active next-stage queue
   - author a dedicated `Full Runtime` execution plan before treating any new plan file as the authoritative checklist
   - keep evidence in `docs/change-evidence/`

## Boundaries
- Plans here should be execution-oriented, not a duplicate of the PRD or architecture docs.
- Roadmap timing stays in `docs/roadmap/`.
- Gap ordering and dependencies stay in `docs/backlog/`.
- Historical plans remain useful evidence, but only one plan should be treated as the active next-step entrypoint at a time.
