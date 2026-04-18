# Governed AI Coding Runtime Docs Index

## Current Baseline
- This repository is currently `docs-first / contracts-first`.
- `docs/`, `schemas/`, top-level skeleton directories, `scripts/verify-repo.ps1`, `scripts/build-runtime.ps1`, `scripts/doctor-runtime.ps1`, `.github/workflows/verify.yml`, and tested runtime contract primitives are present.
- MVP contract slices, the `Foundation / GAP-020` through `GAP-023` substrate, `Full Runtime / GAP-024` through `GAP-028`, `Public Usable Release / GAP-029` through `GAP-032`, and `Maintenance Baseline / GAP-033` through `GAP-034` are complete.
- The active next-step queue is `Interactive Session Productization / GAP-035` through `GAP-039`.

## Current Working Set
- [Full Lifecycle Plan](./roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md)
- [Issue-Ready Backlog](./backlog/issue-ready-backlog.md)
- [Issue Seeds YAML](./backlog/issue-seeds.yaml)
- [Interactive Session Productization Plan](./plans/interactive-session-productization-plan.md)
- [Generic Target-Repo Attachment Blueprint](./architecture/generic-target-repo-attachment-blueprint.md)
- [Interaction Model](./product/interaction-model.md)
- [AI Coding PRD](./prd/governed-ai-coding-runtime-prd.md)
- [20260418 Maintenance Execution Plan](./change-evidence/20260418-maintenance-execution-plan.md)

## Current Planning Chain
- Strategy and boundary inputs: [AI Coding PRD](./prd/governed-ai-coding-runtime-prd.md), [Interaction Model](./product/interaction-model.md), [Generic Target-Repo Attachment Blueprint](./architecture/generic-target-repo-attachment-blueprint.md), [Target Architecture](./architecture/governed-ai-coding-runtime-target-architecture.md), and [Minimum Viable Governance Loop](./architecture/minimum-viable-governance-loop.md)
- Execution ordering: [Backlog Index](./backlog/README.md), [Issue-Ready Backlog](./backlog/issue-ready-backlog.md), [Full Lifecycle Plan](./roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md), and [Plans Index](./plans/README.md)
- Current implementation history: [Foundation Runtime Substrate Implementation Plan](./plans/foundation-runtime-substrate-implementation-plan.md), [Full Runtime Implementation Plan](./plans/full-runtime-implementation-plan.md), [Public Usable Release Implementation Plan](./plans/public-usable-release-implementation-plan.md), and [Maintenance Implementation Plan](./plans/maintenance-implementation-plan.md)

## Navigation Aids
- [Plans Index](./plans/README.md)
- [Backlog Index](./backlog/README.md)
- [Architecture Index](./architecture/README.md)
- [Reviews Index](./reviews/README.md)
- [Change Evidence Index](./change-evidence/README.md)
- [Runbooks Index](./runbooks/README.md)

## Current Execution Posture
- `Foundation / GAP-020` through `GAP-023` are complete on the current branch baseline.
- `Full Runtime / GAP-024` through `GAP-028` are complete on the current branch baseline.
- `Public Usable Release / GAP-029` through `GAP-032` are complete on the current branch baseline.
- `Maintenance Baseline / GAP-033` through `GAP-034` are complete on the current branch baseline.
- `Interactive Session Productization / GAP-035` through `GAP-039` are the active next-step queue.
- Active verification for this repo remains `build -> test -> contract/invariant -> doctor`, with docs and script checks still included in `verify-repo -Check All`.
- `docs/change-evidence/` remains historical evidence and planning trace, not the primary user-facing product surface.

## Project Entry
- [Root README](../README.md)
- [中文 README](../README.zh-CN.md)
- [English README](../README.en.md)
- [Project AGENTS](../AGENTS.md)

## Verification Quickstart
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File ../scripts/verify-repo.ps1 -Check All
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
```

Local baseline runtime commands:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/bootstrap-runtime.ps1
```

```powershell
python scripts/run-governed-task.py status --json
```

```powershell
python scripts/run-governed-task.py run --json
```

Operator and packaging helpers:

```powershell
python scripts/serve-operator-ui.py
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/package-runtime.ps1
```

Primary reading entrypoints:
- [Single-Machine Runtime Quickstart](./quickstart/single-machine-runtime-quickstart.md)
- [Codex CLI/App Integration Guide](./product/codex-cli-app-integration-guide.md)
- [Codex CLI/App 集成指南](./product/codex-cli-app-integration-guide.zh-CN.md)
- [Generic Target-Repo Attachment Blueprint](./architecture/generic-target-repo-attachment-blueprint.md)
- [Interactive Session Productization Plan](./plans/interactive-session-productization-plan.md)

## Product
- [中文使用说明](../README.zh-CN.md)
- [English Usage Guide](../README.en.md)
- [Interaction Model](./product/interaction-model.md)
- [定位、路线图与竞品分层说明](./product/positioning-roadmap-competitive-layers.zh-CN.md)
- [First Read-Only Trial](./product/first-readonly-trial.md)
- [Write Policy Defaults](./product/write-policy-defaults.md)
- [Approval Flow](./product/approval-flow.md)
- [Write-Side Tool Governance](./product/write-side-tool-governance.md)
- [Verification Runner](./product/verification-runner.md)
- [Delivery Handoff](./product/delivery-handoff.md)
- [Eval And Trace Baseline](./product/eval-and-trace-baseline.md)
- [Second-Repo Reuse Pilot](./product/second-repo-reuse-pilot.md)
- [Minimal Approval And Evidence Console](./product/minimal-approval-evidence-console.md)
- [Public Usable Release Criteria](./product/public-usable-release-criteria.md)
- [Adapter Degrade Policy](./product/adapter-degrade-policy.md)
- [Codex CLI/App Integration Guide](./product/codex-cli-app-integration-guide.md)
- [Codex CLI/App 集成指南](./product/codex-cli-app-integration-guide.zh-CN.md)
- [Runtime Compatibility And Upgrade Policy](./product/runtime-compatibility-and-upgrade-policy.md)
- [Maintenance, Deprecation, And Retirement Policy](./product/maintenance-deprecation-and-retirement-policy.md)
- [AI Coding PRD](./prd/governed-ai-coding-runtime-prd.md)

## Architecture
- [Architecture Index](./architecture/README.md)
- [Generic Target-Repo Attachment Blueprint](./architecture/generic-target-repo-attachment-blueprint.md)
- [Target Architecture](./architecture/governed-ai-coding-runtime-target-architecture.md)
- [Minimum Viable Governance Loop](./architecture/minimum-viable-governance-loop.md)
- [Governance Boundary Matrix](./architecture/governance-boundary-matrix.md)
- [MVP Stack Vs Target Stack](./architecture/mvp-stack-vs-target-stack.md)
- [Compatibility Matrix](./architecture/compatibility-matrix.md)

## Roadmap And Execution
- [Plans Index](./plans/README.md)
- [Backlog Index](./backlog/README.md)
- [90-Day Plan](./roadmap/governed-ai-coding-runtime-90-day-plan.md)
- [Full Lifecycle Plan](./roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md)
- [Interactive Session Productization Plan](./plans/interactive-session-productization-plan.md)
- [Maintenance Implementation Plan](./plans/maintenance-implementation-plan.md)
- [Public Usable Release Implementation Plan](./plans/public-usable-release-implementation-plan.md)
- [Full Runtime Implementation Plan](./plans/full-runtime-implementation-plan.md)
- [Foundation Runtime Substrate Implementation Plan](./plans/foundation-runtime-substrate-implementation-plan.md)
- [Phase 0 Runnable Baseline Implementation Plan](./plans/phase-0-runnable-baseline-implementation-plan.md)
- [MVP Backlog Seeds](./backlog/mvp-backlog-seeds.md)
- [Full Lifecycle Backlog Seeds](./backlog/full-lifecycle-backlog-seeds.md)
- [Issue-Ready Backlog](./backlog/issue-ready-backlog.md)
- [Issue Seeds YAML](./backlog/issue-seeds.yaml)
