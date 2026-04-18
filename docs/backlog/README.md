# Backlog Index

## Purpose
This directory holds the human and machine planning artifacts that bridge strategy into implementation-ready work.

## Artifact Roles
- [MVP Backlog Seeds](./mvp-backlog-seeds.md)
  - historical seed list for the completed 90-day MVP
  - use this to understand how `Phase 0` through `Phase 4` were sequenced
- [Full Lifecycle Backlog Seeds](./full-lifecycle-backlog-seeds.md)
  - active phase-level seed list for the full lifecycle including the interactive session productization queue
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
- `Full Runtime / GAP-024` through `GAP-028` are complete on the current branch baseline.
- `Public Usable Release / GAP-029` through `GAP-032` are complete on the current branch baseline.
- `Maintenance Baseline / GAP-033` through `GAP-034` are complete on the current branch baseline.
- `Interactive Session Productization / GAP-035` through `GAP-039` are the active next-step queue.
- The active lifecycle is now anchored by:
  - [Full Lifecycle Plan](../roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md)
  - [Full Lifecycle Backlog Seeds](./full-lifecycle-backlog-seeds.md)
  - [Issue-Ready Backlog](./issue-ready-backlog.md)
  - [Issue Seeds YAML](./issue-seeds.yaml)
- The interactive productization direction also depends on:
  - [Generic Target-Repo Attachment Blueprint](../architecture/generic-target-repo-attachment-blueprint.md)
  - [Interaction Model](../product/interaction-model.md)
  - [Interactive Session Productization Plan](../plans/interactive-session-productization-plan.md)
- The local baseline and maintenance surfaces still depend on:
  - [Single-Machine Runtime Quickstart](../quickstart/single-machine-runtime-quickstart.md)
  - [Public Usable Release Criteria](../product/public-usable-release-criteria.md)
  - [Adapter Degrade Policy](../product/adapter-degrade-policy.md)
  - [Runtime Compatibility And Upgrade Policy](../product/runtime-compatibility-and-upgrade-policy.md)
  - [Maintenance, Deprecation, And Retirement Policy](../product/maintenance-deprecation-and-retirement-policy.md)
- The completed implementation checklists remain useful execution history:
  - [Maintenance Implementation Plan](../plans/maintenance-implementation-plan.md)
  - [Full Runtime Implementation Plan](../plans/full-runtime-implementation-plan.md)
  - [Foundation Runtime Substrate Implementation Plan](../plans/foundation-runtime-substrate-implementation-plan.md)
- Historical phase plans under `docs/plans/` remain evidence of earlier work; the new active implementation queue is the interactive session productization slice.
