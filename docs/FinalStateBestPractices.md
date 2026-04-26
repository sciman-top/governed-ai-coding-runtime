# Final State Best Practices

## Purpose
This repository's earliest bootstrap documents referenced `docs/FinalStateBestPractices.md` before the local documentation baseline was fully organized.

This file now exists as a north-star reference and a short decision bridge. It is not the implementation backlog and should not be read as a requirement to build the full target stack in the first slice.

## Current Source Of Truth
- [AI Coding PRD](./prd/governed-ai-coding-runtime-prd.md)
- [Target Architecture](./architecture/governed-ai-coding-runtime-target-architecture.md)
- [Hybrid Final-State Master Outline](./architecture/hybrid-final-state-master-outline.md)
- [Direct-To-Hybrid Final-State Roadmap](./roadmap/direct-to-hybrid-final-state-roadmap.md)
- [Direct-To-Hybrid Final-State Implementation Plan](./plans/direct-to-hybrid-final-state-implementation-plan.md)
- [Minimum Viable Governance Loop](./architecture/minimum-viable-governance-loop.md)
- [90-Day Plan](./roadmap/governed-ai-coding-runtime-90-day-plan.md)
- [Project Audit And Optimization](./reviews/2026-04-17-project-audit-and-optimization.md)
- [Hybrid Final-State External Benchmark Review](./research/2026-04-27-hybrid-final-state-external-benchmark-review.md)

## Distilled Principles
1. Final-state best practice is the long-term target.
2. Control-plane-first beats runtime-first.
3. Single-agent baseline beats premature multi-agent complexity.
4. Agent products are replaceable execution frontends; governance semantics belong in the kernel.
5. Low-risk work should remain low-friction; high-risk writes must route through approval and rollback references.
6. Delivery requires evidence and ordered verification gates.
7. Repo-specific variation belongs in profiles and bounded overrides, not in platform-kernel semantics.
8. Codex CLI/App compatibility is the first adapter priority, but the kernel must remain compatible with future agent products through capability contracts.
9. Executable tools need deterministic containment: workspace roots, permission tiers, timeouts, resource limits, evidence, and rollback posture.
10. Protocols are boundaries, not owners: MCP and A2A can supply tool/resource/auth/discovery/task shapes, but approval, verification, evidence, replay, and rollback remain runtime-owned.
11. Heavy platform components are introduced by pressure and evidence, not by target-state aesthetics.
12. Release artifacts, generated control packs, and target-repo light packs need provenance or explicit waiver records before stronger distribution claims.

## Usage
- Keep this document only as a stable pointer for early bootstrap references.
- New product, architecture, or planning decisions should land in PRD, ADRs, architecture docs, roadmap, backlog, or specs.
- Treat final-state best practice as a quality target and compatibility posture, not as permission to skip MVP tracer bullets or add infrastructure breadth prematurely.
- When external best practices change, update the benchmark review first, then project the delta into the master outline, roadmap, implementation plan, or specs.


