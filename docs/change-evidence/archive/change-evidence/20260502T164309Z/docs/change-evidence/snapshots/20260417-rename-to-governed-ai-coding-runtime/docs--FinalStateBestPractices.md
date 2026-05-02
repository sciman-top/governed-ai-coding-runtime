# Final State Best Practices

## Purpose
This repository's earliest bootstrap documents referenced `docs/FinalStateBestPractices.md` before the local documentation baseline was fully organized.

This file now exists as a compatibility reference and a short decision bridge. It is not the primary source of truth.

## Current Source Of Truth
- [AI Coding PRD](./prd/governed-agent-platform-ai-coding-prd.md)
- [Target Architecture](./architecture/governed-agent-platform-target-architecture.md)
- [Minimum Viable Governance Loop](./architecture/minimum-viable-governance-loop.md)
- [90-Day Plan](./roadmap/governed-agent-platform-90-day-plan.md)
- [Project Audit And Optimization](./reviews/2026-04-17-project-audit-and-optimization.md)

## Distilled Principles
1. Control-plane-first beats runtime-first.
2. Single-agent baseline beats premature multi-agent complexity.
3. High-risk writes must route through approval and rollback references.
4. Delivery requires evidence and ordered verification gates.
5. Repo-specific variation belongs in profiles and bounded overrides, not in platform-kernel semantics.

## Usage
- Keep this document only as a stable pointer for early bootstrap references.
- New product, architecture, or planning decisions should land in PRD, ADRs, architecture docs, roadmap, backlog, or specs.
