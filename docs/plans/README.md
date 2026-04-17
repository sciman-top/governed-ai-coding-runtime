# Plans Index

## Purpose
This directory holds executable implementation plans that translate strategy and backlog into ordered work.

## Current Authoritative Plan
- [Phase 0 Runnable Baseline Implementation Plan](./phase-0-runnable-baseline-implementation-plan.md)
  - Status: ready to execute after Task 0 freezes or explicitly carries forward the current dirty worktree
  - Scope: repository skeleton, local verifier, CI minimums, runtime-consumable control-pack reference asset, repo admission planning, and gate routing cleanup

## How To Use This Directory
1. Read the latest audit review:
   - [Pre-Implementation Deep Audit And Doc Refresh](../reviews/2026-04-17-pre-implementation-deep-audit-and-doc-refresh.md)
2. Read the latest supporting evidence:
   - [20260417 Pre-Implementation Deep Audit And Doc Refresh](../change-evidence/20260417-pre-implementation-deep-audit-and-doc-refresh.md)
3. Use the plan document as the execution checklist:
   - start at Task 0
   - do not skip the dirty-worktree decision
   - keep evidence in `docs/change-evidence/`

## Boundaries
- Plans here should be execution-oriented, not a duplicate of the PRD or architecture docs.
- Roadmap timing stays in `docs/roadmap/`.
- Gap ordering and dependencies stay in `docs/backlog/`.
