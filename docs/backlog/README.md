# Backlog Index

## Purpose
This directory holds the human and machine planning artifacts that bridge strategy into implementation-ready work.

## Artifact Roles
- [MVP Backlog Seeds](./mvp-backlog-seeds.md)
  - phase-level seed list
  - use this for broad sequencing and scope checks
- [Issue-Ready Backlog](./issue-ready-backlog.md)
  - current human-readable implementation backlog
  - use this for dependencies, acceptance criteria, and execution order
- [Issue Seeds YAML](./issue-seeds.yaml)
  - machine-readable issue ids, types, blockers, and user-story mapping
  - use this for drift checks and automation

## Script Relationship
- GitHub issue bootstrap helper:
  - [`scripts/github/create-roadmap-issues.ps1`](../../scripts/github/create-roadmap-issues.ps1)
- Current limitation:
  - the script still owns its issue body text directly instead of loading `issue-seeds.yaml`
  - keep the script, backlog markdown, and YAML aligned when planning changes are made

## Current Execution Posture
- The 90-day MVP backlog has reached its current endpoint at `GAP-017`.
- There is no active post-MVP executable backlog in this directory yet.
- Treat new implementation beyond `GAP-017` as new planning work: create a post-MVP roadmap/backlog first, then sync `issue-ready-backlog.md`, `issue-seeds.yaml`, and `scripts/github/create-roadmap-issues.ps1`.
- Historical phase plans under `docs/plans/` remain evidence of how the MVP was executed; they are not the current next-step queue.
