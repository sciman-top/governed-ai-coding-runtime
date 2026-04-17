# Governed AI Coding Runtime Docs Index

## Current Baseline
- This repository is currently `docs-first / contracts-first`.
- `docs/`, `schemas/`, `scripts/github/create-roadmap-issues.ps1`, top-level skeleton directories for `apps/`, `packages/`, `infra/`, and `tests/`, `scripts/verify-repo.ps1`, `.github/workflows/verify.yml`, one runtime-consumable control-pack asset, and tested runtime contract primitives are present.
- Phase 0 through Phase 4 backlog items are implemented through the current `GAP-017` backlog endpoint.
- Production runtime services, durable workers, real package build artifacts, and deployment targets are not landed yet.

## Current Working Set
- [Latest Deep Audit Review](./reviews/2026-04-17-pre-implementation-deep-audit-and-doc-refresh.md)
- [Latest Audit Evidence](./change-evidence/20260417-pre-implementation-deep-audit-and-doc-refresh.md)
- [Current Closeout Evidence](./change-evidence/20260417-mvp-backlog-closeout-handoff.md)
- [Phase 0 Runnable Baseline Implementation Plan](./plans/phase-0-runnable-baseline-implementation-plan.md)
- [Project AGENTS](../AGENTS.md)

## Current Planning Chain
- Strategy and boundary inputs: [AI Coding PRD](./prd/governed-ai-coding-runtime-prd.md), [Interaction Model](./product/interaction-model.md), [Target Architecture](./architecture/governed-ai-coding-runtime-target-architecture.md), and [Minimum Viable Governance Loop](./architecture/minimum-viable-governance-loop.md)
- Execution ordering: [90-Day Plan](./roadmap/governed-ai-coding-runtime-90-day-plan.md), [Backlog Index](./backlog/README.md), [Issue-Ready Backlog](./backlog/issue-ready-backlog.md), and [Plans Index](./plans/README.md)
- Current handoff baseline: [Latest Deep Audit Review](./reviews/2026-04-17-pre-implementation-deep-audit-and-doc-refresh.md) plus [Latest Audit Evidence](./change-evidence/20260417-pre-implementation-deep-audit-and-doc-refresh.md)

## Navigation Aids
- [Plans Index](./plans/README.md)
- [Backlog Index](./backlog/README.md)
- [Reviews Index](./reviews/README.md)
- [Change Evidence Index](./change-evidence/README.md)
- [Runbooks Index](./runbooks/README.md)

## Current Execution Posture
- The current MVP backlog has been executed through `GAP-017`; the next work should be closeout review, commit grouping, or a new post-MVP plan.
- The working tree is intentionally dirty until the maintainer chooses commit grouping; do not revert unrelated accumulated changes.
- Active verification for this repo currently means runtime contract tests plus scoped checks over live docs, schemas, examples, catalog, and planning scripts; `docs/change-evidence/` remains historical evidence, not active product surface.

## Project Entry
- [Root README](../README.md)
- [Project AGENTS](../AGENTS.md)

## Verification Quickstart
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File ../scripts/verify-repo.ps1 -Check All
```

Runtime contract tests can be run directly from the repository root:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
```

## Foundations
- [Final State Best Practices](./FinalStateBestPractices.md)

## Product
- [Interaction Model](./product/interaction-model.md)
- [First Read-Only Trial](./product/first-readonly-trial.md)
- [Write Policy Defaults](./product/write-policy-defaults.md)
- [Approval Flow](./product/approval-flow.md)
- [Write-Side Tool Governance](./product/write-side-tool-governance.md)
- [Verification Runner](./product/verification-runner.md)
- [Delivery Handoff](./product/delivery-handoff.md)
- [Eval And Trace Baseline](./product/eval-and-trace-baseline.md)
- [Second-Repo Reuse Pilot](./product/second-repo-reuse-pilot.md)
- [Minimal Approval And Evidence Console](./product/minimal-approval-evidence-console.md)
- [AI Coding PRD](./prd/governed-ai-coding-runtime-prd.md)

## Architecture
- [Architecture Index](./architecture/README.md)
- [Target Architecture](./architecture/governed-ai-coding-runtime-target-architecture.md)
- [Minimum Viable Governance Loop](./architecture/minimum-viable-governance-loop.md)
- [Governance Boundary Matrix](./architecture/governance-boundary-matrix.md)
- [MVP Stack Vs Target Stack](./architecture/mvp-stack-vs-target-stack.md)
- [Compatibility Matrix](./architecture/compatibility-matrix.md)

## Roadmap And Execution
- [Plans Index](./plans/README.md)
- [Backlog Index](./backlog/README.md)
- [90-Day Plan](./roadmap/governed-ai-coding-runtime-90-day-plan.md)
- [Phase 0 Runnable Baseline Implementation Plan](./plans/phase-0-runnable-baseline-implementation-plan.md)
- [MVP Backlog Seeds](./backlog/mvp-backlog-seeds.md)
- [Issue-Ready Backlog](./backlog/issue-ready-backlog.md)
- [Issue Seeds YAML](./backlog/issue-seeds.yaml)

## Reviews
- [Reviews Index](./reviews/README.md)
- [Project Audit And Optimization (2026-04-17)](./reviews/2026-04-17-project-audit-and-optimization.md)
- [Second Project Audit And Plan Hardening (2026-04-17)](./reviews/2026-04-17-second-project-audit-and-plan-hardening.md)
- [Pre-Implementation Deep Audit And Doc Refresh (2026-04-17)](./reviews/2026-04-17-pre-implementation-deep-audit-and-doc-refresh.md)
- [FinalStateBestPractices Original Mapping Review (2026-04-17)](./reviews/2026-04-17-final-state-best-practices-original-mapping.md)

## Runbooks
- [Runbooks Index](./runbooks/README.md)
- [Failed Rollout Recovery](./runbooks/failed-rollout-recovery.md)
- [Expired Waiver Handling](./runbooks/expired-waiver-handling.md)
- [Control Rollback](./runbooks/control-rollback.md)
- [Repeated Trial Recovery](./runbooks/repeated-trial-recovery.md)

## Change Evidence
- [Change Evidence Index](./change-evidence/README.md)
- [20260417 MVP Backlog Closeout Handoff](./change-evidence/20260417-mvp-backlog-closeout-handoff.md)
- [20260417 Phase 1 Scripted Trial Entrypoint](./change-evidence/20260417-phase-1-scripted-trial-entrypoint.md)
- [20260417 Phase 1 Workspace Allocation](./change-evidence/20260417-phase-1-workspace-allocation.md)
- [20260417 Phase 1 Write Policy Defaults](./change-evidence/20260417-phase-1-write-policy-defaults.md)
- [20260417 Phase 1 Approval Flow](./change-evidence/20260417-phase-1-approval-flow.md)
- [20260417 Phase 1 Write-Side Tool Governance](./change-evidence/20260417-phase-1-write-side-tool-governance.md)
- [20260417 Phase 1 Verification Runner](./change-evidence/20260417-phase-1-verification-runner.md)
- [20260417 Phase 1 Delivery Handoff](./change-evidence/20260417-phase-1-delivery-handoff.md)
- [20260417 Phase 1 Eval And Trace Baseline](./change-evidence/20260417-phase-1-eval-trace-baseline.md)
- [20260417 Phase 1 Second-Repo Reuse Pilot](./change-evidence/20260417-phase-1-second-repo-reuse-pilot.md)
- [20260417 Phase 1 Minimal Approval And Evidence Console](./change-evidence/20260417-phase-1-minimal-approval-evidence-console.md)
- [20260417 Phase 1 Evidence Timeline](./change-evidence/20260417-phase-1-evidence-timeline.md)
- [20260417 Phase 1 Read-Only Tool Runner](./change-evidence/20260417-phase-1-readonly-tool-runner.md)
- [20260417 Phase 1 Task Intake And Repo Resolution](./change-evidence/20260417-phase-1-task-intake-repo-resolution.md)
- [20260417 Pre-Implementation Deep Audit And Doc Refresh](./change-evidence/20260417-pre-implementation-deep-audit-and-doc-refresh.md)
- [20260417 Phase 0 Runnable Baseline](./change-evidence/20260417-phase-0-runnable-baseline.md)

## Repository Skeleton
- [Apps Boundary](../apps/README.md)
- [Packages Boundary](../packages/README.md)
- [Contracts Package](../packages/contracts/README.md)
- [Infra Boundary](../infra/README.md)
- [Tests Boundary](../tests/README.md)

## Research
- [Benchmark And Borrowing Notes](./research/benchmark-and-borrowing-notes.md)
- [repo-governance-hub Mechanism Adoption Matrix](./research/repo-governance-hub-borrowing-review.md)

## Decision Records
- [ADR-0001: Control Plane First](./adrs/0001-control-plane-first.md)
- [ADR-0002: No Multi-Repo Distribution In MVP](./adrs/0002-no-multi-repo-distribution-in-mvp.md)
- [ADR-0003: Single-Agent Baseline First](./adrs/0003-single-agent-baseline-first.md)
- [ADR-0004: Rename Project To Governed AI Coding Runtime](./adrs/0004-rename-project-to-governed-ai-coding-runtime.md)
- [ADR-0005: Governance Kernel And Control Packs Before Platform Breadth](./adrs/0005-governance-kernel-and-control-packs-before-platform-breadth.md)
- [ADR-0006: Final-State Best Practice And Agent Compatibility](./adrs/0006-final-state-best-practice-agent-compatibility.md)

## Specs
- [Specs Index](./specs/README.md)
- [Repo Admission Minimums Spec](./specs/repo-admission-minimums-spec.md)
- [Control Registry Spec](./specs/control-registry-spec.md)
- [Control Pack Spec](./specs/control-pack-spec.md)
- [Repo Profile Spec](./specs/repo-profile-spec.md)
- [Tool Contract Spec](./specs/tool-contract-spec.md)
- [Agent Adapter Contract Spec](./specs/agent-adapter-contract-spec.md)
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
- [Control Packs README](../schemas/control-packs/README.md)
- [Minimum Governance Kernel Runtime Pack](../schemas/control-packs/minimum-governance-kernel.control-pack.json)

## Example Instances
- [Minimum Governance Kernel Control Pack Sample](../schemas/examples/control-pack/minimum-governance-kernel.example.json)
- [Python Service Repo Profile Sample](../schemas/examples/repo-profile/python-service.example.json)
- [TypeScript Webapp Repo Profile Sample](../schemas/examples/repo-profile/typescript-webapp.example.json)

## Recommended Reading Order
1. PRD
2. Latest Deep Audit Review
3. Phase 0 Runnable Baseline Implementation Plan
4. Interaction Model
5. Final State Best Practices
6. Governance Boundary Matrix
7. Minimum Viable Governance Loop
8. MVP Stack Vs Target Stack
9. Compatibility Matrix
10. Target Architecture
11. 90-Day Plan
12. Issue-Ready Backlog
13. ADRs
14. Specs
15. Schemas
16. Latest Audit Evidence
