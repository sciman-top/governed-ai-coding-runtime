# Governed AI Coding Runtime Docs Index

## Current Baseline
- This repository is currently `docs-first / contracts-first`.
- `docs/`, `schemas/`, and `scripts/github/create-roadmap-issues.ps1` are already present.
- `apps/`, `packages/`, `infra/`, and `tests/` are planned but not bootstrapped yet.

## Project Entry
- [Root README](../README.md)
- [Project AGENTS](../AGENTS.md)

## Foundations
- [Final State Best Practices](./FinalStateBestPractices.md)

## Product
- [Interaction Model](./product/interaction-model.md)
- [AI Coding PRD](./prd/governed-ai-coding-runtime-prd.md)

## Architecture
- [Target Architecture](./architecture/governed-ai-coding-runtime-target-architecture.md)
- [Minimum Viable Governance Loop](./architecture/minimum-viable-governance-loop.md)
- [Governance Boundary Matrix](./architecture/governance-boundary-matrix.md)
- [MVP Stack Vs Target Stack](./architecture/mvp-stack-vs-target-stack.md)
- [Compatibility Matrix](./architecture/compatibility-matrix.md)

## Roadmap And Execution
- [90-Day Plan](./roadmap/governed-ai-coding-runtime-90-day-plan.md)
- [Phase 0 Runnable Baseline Implementation Plan](./plans/phase-0-runnable-baseline-implementation-plan.md)
- [MVP Backlog Seeds](./backlog/mvp-backlog-seeds.md)
- [Issue-Ready Backlog](./backlog/issue-ready-backlog.md)
- [Issue Seeds YAML](./backlog/issue-seeds.yaml)

## Reviews
- [Project Audit And Optimization (2026-04-17)](./reviews/2026-04-17-project-audit-and-optimization.md)
- [Second Project Audit And Plan Hardening (2026-04-17)](./reviews/2026-04-17-second-project-audit-and-plan-hardening.md)

## Research
- [Benchmark And Borrowing Notes](./research/benchmark-and-borrowing-notes.md)
- [repo-governance-hub Mechanism Adoption Matrix](./research/repo-governance-hub-borrowing-review.md)

## Decision Records
- [ADR-0001: Control Plane First](./adrs/0001-control-plane-first.md)
- [ADR-0002: No Multi-Repo Distribution In MVP](./adrs/0002-no-multi-repo-distribution-in-mvp.md)
- [ADR-0003: Single-Agent Baseline First](./adrs/0003-single-agent-baseline-first.md)
- [ADR-0004: Rename Project To Governed AI Coding Runtime](./adrs/0004-rename-project-to-governed-ai-coding-runtime.md)
- [ADR-0005: Governance Kernel And Control Packs Before Platform Breadth](./adrs/0005-governance-kernel-and-control-packs-before-platform-breadth.md)

## Specs
- [Control Registry Spec](./specs/control-registry-spec.md)
- [Control Pack Spec](./specs/control-pack-spec.md)
- [Repo Profile Spec](./specs/repo-profile-spec.md)
- [Tool Contract Spec](./specs/tool-contract-spec.md)
- [Hook Contract Spec](./specs/hook-contract-spec.md)
- [Skill Manifest Spec](./specs/skill-manifest-spec.md)
- [Knowledge Source Spec](./specs/knowledge-source-spec.md)
- [Waiver And Exception Spec](./specs/waiver-and-exception-spec.md)
- [Provenance And Attestation Spec](./specs/provenance-and-attestation-spec.md)
- [Repo Map And Context Shaping Spec](./specs/repo-map-context-shaping-spec.md)
- [Risk Tier And Approval Spec](./specs/risk-tier-and-approval-spec.md)
- [Task Lifecycle And State Machine Spec](./specs/task-lifecycle-and-state-machine-spec.md)
- [Evidence Bundle Spec](./specs/evidence-bundle-spec.md)
- [Verification Gates Spec](./specs/verification-gates-spec.md)
- [Eval And Trace Grading Spec](./specs/eval-and-trace-grading-spec.md)

## Schemas
- [Schemas README](../schemas/README.md)
- [Schema Examples README](../schemas/examples/README.md)
- [Schema Catalog](../schemas/catalog/schema-catalog.yaml)

## Example Instances
- [Minimum Governance Kernel Control Pack Sample](../schemas/examples/control-pack/minimum-governance-kernel.example.json)
- [Python Service Repo Profile Sample](../schemas/examples/repo-profile/python-service.example.json)
- [TypeScript Webapp Repo Profile Sample](../schemas/examples/repo-profile/typescript-webapp.example.json)

## Recommended Reading Order
1. PRD
2. Interaction Model
3. Target Architecture
4. Governance Boundary Matrix
5. Minimum Viable Governance Loop
6. 90-Day Plan
7. Issue-Ready Backlog
8. ADRs
9. Specs
10. Schemas
11. Second Project Audit And Plan Hardening
