# Governed AI Coding Runtime

## Overview
`governed-ai-coding-runtime` is a docs-first, contracts-first repository for a governed runtime around AI coding agents.

The current repository now includes the product definition, architecture, roadmap, backlog, schema drafts, bootstrap scripts, local verification, CI wiring, and a tested runtime contract layer for the current MVP backlog.

## Current Baseline
- Available now: PRD, architecture, ADRs, roadmap, backlog, JSON Schema drafts, schema examples, sample repo profiles, a GitHub issue seeding script, top-level skeleton directories for `apps/`, `packages/`, `infra/`, and `tests/`, a local repository verifier, CI wiring, one runtime-consumable control-pack metadata asset, and tested runtime contract primitives under `packages/contracts/`.
- Current plan status: Phase 0 through Phase 4 backlog items are implemented through the current `GAP-017` backlog endpoint.
- Not landed yet: production runtime services, durable workers, real package build artifacts, and deployment targets.
- The active documentation index lives in [docs/README.md](docs/README.md).

## Current Working Set
- Latest deep audit review: [Pre-Implementation Deep Audit And Doc Refresh](docs/reviews/2026-04-17-pre-implementation-deep-audit-and-doc-refresh.md)
- Latest audit evidence: [20260417 Pre-Implementation Deep Audit And Doc Refresh](docs/change-evidence/20260417-pre-implementation-deep-audit-and-doc-refresh.md)
- Current closeout evidence: [20260417 MVP Backlog Closeout Handoff](docs/change-evidence/20260417-mvp-backlog-closeout-handoff.md)
- Historical bootstrap plan: [Phase 0 Runnable Baseline Implementation Plan](docs/plans/phase-0-runnable-baseline-implementation-plan.md)
- Planning and audit indexes: [Plans Index](docs/plans/README.md), [Backlog Index](docs/backlog/README.md), [Reviews Index](docs/reviews/README.md), [Evidence Index](docs/change-evidence/README.md)
- Deep-dive indexes: [Architecture Index](docs/architecture/README.md), [Specs Index](docs/specs/README.md)
- Active repo rules: [Project AGENTS](AGENTS.md)

## Repository Map
- `docs/`: product definition, architecture, roadmap, ADRs, reviews, and change evidence
- `schemas/`: machine-readable governance contract drafts, example instances, and the schema catalog
- `scripts/github/`: GitHub backlog/bootstrap automation
- `packages/contracts/`: tested runtime contract primitives for task intake, repo profiles, tool governance, approvals, verification, handoff, eval/trace, pilot checks, and console facade
- `apps/`, `infra/`: repository skeleton boundaries for future applications and infrastructure
- `tests/runtime/`: runtime contract test suite

## Read First
1. [docs/README.md](docs/README.md)
2. [Pre-Implementation Deep Audit And Doc Refresh](docs/reviews/2026-04-17-pre-implementation-deep-audit-and-doc-refresh.md)
3. [Phase 0 Runnable Baseline Implementation Plan](docs/plans/phase-0-runnable-baseline-implementation-plan.md)
4. [AI Coding PRD](docs/prd/governed-ai-coding-runtime-prd.md)
5. [Interaction Model](docs/product/interaction-model.md)
6. [Final State Best Practices](docs/FinalStateBestPractices.md)
7. [Minimum Viable Governance Loop](docs/architecture/minimum-viable-governance-loop.md)
8. [MVP Stack Vs Target Stack](docs/architecture/mvp-stack-vs-target-stack.md)
9. [Compatibility Matrix](docs/architecture/compatibility-matrix.md)
10. [Target Architecture](docs/architecture/governed-ai-coding-runtime-target-architecture.md)
11. [90-Day Plan](docs/roadmap/governed-ai-coding-runtime-90-day-plan.md)
12. [Issue-Ready Backlog](docs/backlog/issue-ready-backlog.md)
13. [Schemas README](schemas/README.md)
14. [Project AGENTS](AGENTS.md)

## Naming
The active project name is `governed-ai-coding-runtime`.
Historical evidence may still mention `governed-agent-platform` where preserving the original record is the correct audit behavior.

## Current Verification Entry Points
The repository does not have production runtime services or build artifacts yet, so the current verification baseline is repository integrity plus runtime contract tests:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```

Runtime unit tests only:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
```

First read-only trial:

```powershell
python scripts/run-readonly-trial.py `
  --goal "inspect repository" `
  --scope "readonly trial" `
  --acceptance "readonly request accepted" `
  --repo-profile "schemas/examples/repo-profile/python-service.example.json" `
  --target-path "src/service.py" `
  --max-steps 1 `
  --max-minutes 5
```

Active integrity scans should target live repository docs/specs/schemas/scripts. Historical archives under `docs/change-evidence/` and snapshot copies intentionally preserve old paths, commands, and naming for auditability, so they are not part of the active link-integrity baseline.

CI:
- `.github/workflows/verify.yml`

## Immediate Next Steps
1. Review and commit the accumulated Phase 0-4 changes in coherent groups.
2. Decide whether the next slice should introduce a real package/build artifact or keep expanding the contract layer.
3. Replace remaining `gate_na` build/hotspot entries only after real build and doctor commands exist.


