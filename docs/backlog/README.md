# Backlog Index

## Purpose
This directory holds the human and machine planning artifacts that bridge strategy into implementation-ready work.

## Artifact Roles
- [MVP Backlog Seeds](./mvp-backlog-seeds.md)
  - historical seed list for the completed 90-day MVP
  - use this to understand how `Phase 0` through `Phase 4` were sequenced
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
- Current behavior:
  - task titles and seed metadata are now injected from `issue-seeds.yaml`
  - task issue bodies are now rendered from `issue-ready-backlog.md` plus seed metadata
  - initiative and epic issue bodies are now rendered from `governed-ai-coding-runtime-full-lifecycle-plan.md`
  - `-ValidateOnly` can be used to verify the script sees the current seed set without calling GitHub
  - `-ValidateOnly -RenderAll` renders every task, epic, and initiative body without calling GitHub
- Current limitation:
  - the seeding script depends on stable markdown heading structure in both the backlog and lifecycle roadmap
  - this parser contract is covered by `scripts/verify-repo.ps1 -Check Scripts`, which fails if the source docs can no longer render the issue bodies

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
