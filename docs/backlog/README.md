# Backlog Index

## Purpose
This directory holds the human and machine planning artifacts that bridge strategy into implementation-ready work.

## Artifact Roles
- [MVP Backlog Seeds](./mvp-backlog-seeds.md)
  - historical seed list for the completed 90-day MVP
  - use this to understand how `Phase 0` through `Phase 4` were sequenced
- [Post-MVP Backlog Seeds](./post-mvp-backlog-seeds.md)
  - historical bridge plan between the MVP and the later full-lifecycle plan
  - keep this as planning history, not the active queue
- [Full Lifecycle Backlog Seeds](./full-lifecycle-backlog-seeds.md)
  - active phase-level seed list for the final function-first lifecycle
  - use this for current sequencing and scope checks
- [Issue-Ready Backlog](./issue-ready-backlog.md)
  - current human-readable full-lifecycle implementation backlog
  - use this for dependencies, acceptance criteria, and execution order
- [Issue Seeds YAML](./issue-seeds.yaml)
  - machine-readable active issue ids, types, blockers, and user-story mapping
  - use this for drift checks and automation

## Script Relationship
- GitHub issue bootstrap helper:
  - [`scripts/github/create-roadmap-issues.ps1`](../../scripts/github/create-roadmap-issues.ps1)
- Current limitation:
  - the script still owns its issue body text directly instead of loading `issue-seeds.yaml`
  - keep the script, backlog markdown, and YAML aligned when planning changes are made

## Current Execution Posture
- The 90-day MVP backlog reached its endpoint at `GAP-017`.
- `Vision / GAP-018` and `GAP-019` are complete through planning alignment and capability freeze.
- `Foundation / GAP-020` through `GAP-023` are complete on the current branch baseline.
- The active executable queue now starts at `Full Runtime / GAP-024` and is defined by:
  - [Full Lifecycle Plan](../roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md)
  - [Full Lifecycle Backlog Seeds](./full-lifecycle-backlog-seeds.md)
  - [Issue-Ready Backlog](./issue-ready-backlog.md)
  - [Issue Seeds YAML](./issue-seeds.yaml)
- The completed Foundation execution checklist remains useful implementation history:
  - [Foundation Runtime Substrate Implementation Plan](../plans/foundation-runtime-substrate-implementation-plan.md)
- Historical phase plans under `docs/plans/` remain evidence of earlier work; they are not the current next-step queue unless a later stage explicitly points back to them.
