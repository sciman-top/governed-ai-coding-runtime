# Governed AI Coding Runtime Docs Index

## Current Baseline
- This repository is currently `docs-first / contracts-first`.
- `docs/`, `schemas/`, top-level skeleton directories, `scripts/verify-repo.ps1`, `scripts/build-runtime.ps1`, `scripts/doctor-runtime.ps1`, `.github/workflows/verify.yml`, and tested runtime contract primitives are present.
- MVP contract slices, the `Foundation / GAP-020` through `GAP-023` substrate, `Full Runtime / GAP-024` through `GAP-028`, `Public Usable Release / GAP-029` through `GAP-032`, and `Maintenance Baseline / GAP-033` through `GAP-034` are complete.
- `Strategy Alignment Gates / GAP-040` through `GAP-044` are complete on the current branch baseline and remain encoded as satisfied hardening dependencies around the landed `Interactive Session Productization / GAP-035` through `GAP-039` productization slice.

## Current Working Set
- [Hybrid Final-State Master Outline](./architecture/hybrid-final-state-master-outline.md)
- [Direct-To-Hybrid Final-State Roadmap](./roadmap/direct-to-hybrid-final-state-roadmap.md)
- [Direct-To-Hybrid Final-State Implementation Plan](./plans/direct-to-hybrid-final-state-implementation-plan.md)
- [Governance Optimization Lane Roadmap](./roadmap/governance-optimization-lane-roadmap.md)
- [Governance Optimization Lane Implementation Plan](./plans/governance-optimization-lane-implementation-plan.md)
- [Full Lifecycle Plan](./roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md) (history/current posture)
- [Issue-Ready Backlog](./backlog/issue-ready-backlog.md)
- [Issue Seeds YAML](./backlog/issue-seeds.yaml)
- [Interactive Session Productization Implementation Plan](./plans/interactive-session-productization-implementation-plan.md) (history)
- [Interactive Session Productization Plan](./plans/interactive-session-productization-plan.md) (history)
- [Governance Runtime Strategy Alignment Plan](./plans/governance-runtime-strategy-alignment-plan.md) (history)
- [Strategy Index](./strategy/README.md)
- [Positioning And Competitive Layering](./strategy/positioning-and-competitive-layering.md)
- [Runtime Governance Borrowing Matrix](./research/runtime-governance-borrowing-matrix.md)
- [ADR-0007 Source-Of-Truth And Runtime Contract Bundle](./adrs/0007-source-of-truth-and-runtime-contract-bundle.md)
- [Generic Target-Repo Attachment Blueprint](./architecture/generic-target-repo-attachment-blueprint.md)
- [Repo-Native Contract Bundle](./architecture/repo-native-contract-bundle.md)
- [Local Baseline To Hybrid Final-State Migration Matrix](./architecture/local-baseline-to-hybrid-final-state-migration-matrix.md)
- [Interaction Model](./product/interaction-model.md)
- [AI Coding PRD](./prd/governed-ai-coding-runtime-prd.md)
- [20260418 Maintenance Execution Plan](./change-evidence/20260418-maintenance-execution-plan.md)

## Current Planning Chain
- Strategy and boundary inputs: [AI Coding PRD](./prd/governed-ai-coding-runtime-prd.md), [Interaction Model](./product/interaction-model.md), [Positioning And Competitive Layering](./strategy/positioning-and-competitive-layering.md), [Runtime Governance Borrowing Matrix](./research/runtime-governance-borrowing-matrix.md), [ADR-0007 Source-Of-Truth And Runtime Contract Bundle](./adrs/0007-source-of-truth-and-runtime-contract-bundle.md), [Generic Target-Repo Attachment Blueprint](./architecture/generic-target-repo-attachment-blueprint.md), [Repo-Native Contract Bundle](./architecture/repo-native-contract-bundle.md), [Local Baseline To Hybrid Final-State Migration Matrix](./architecture/local-baseline-to-hybrid-final-state-migration-matrix.md), [Target Architecture](./architecture/governed-ai-coding-runtime-target-architecture.md), [Minimum Viable Governance Loop](./architecture/minimum-viable-governance-loop.md), and [Governance Runtime Strategy Alignment Plan](./plans/governance-runtime-strategy-alignment-plan.md)
- Execution ordering: [Hybrid Final-State Master Outline](./architecture/hybrid-final-state-master-outline.md), [Direct-To-Hybrid Final-State Roadmap](./roadmap/direct-to-hybrid-final-state-roadmap.md), [Direct-To-Hybrid Final-State Implementation Plan](./plans/direct-to-hybrid-final-state-implementation-plan.md), [Backlog Index](./backlog/README.md), [Issue-Ready Backlog](./backlog/issue-ready-backlog.md), [Issue Seeds YAML](./backlog/issue-seeds.yaml), and [Plans Index](./plans/README.md)
- Follow-on optimization ordering: [Governance Optimization Lane Roadmap](./roadmap/governance-optimization-lane-roadmap.md), [Governance Optimization Lane Implementation Plan](./plans/governance-optimization-lane-implementation-plan.md), [Backlog Index](./backlog/README.md), [Issue-Ready Backlog](./backlog/issue-ready-backlog.md), and [Issue Seeds YAML](./backlog/issue-seeds.yaml); this lane was the governance-only follow-on after `GAP-060` and is complete on the current branch baseline (verified on 2026-04-20)
- Current implementation history: [Foundation Runtime Substrate Implementation Plan](./plans/foundation-runtime-substrate-implementation-plan.md), [Full Runtime Implementation Plan](./plans/full-runtime-implementation-plan.md), [Public Usable Release Implementation Plan](./plans/public-usable-release-implementation-plan.md), and [Maintenance Implementation Plan](./plans/maintenance-implementation-plan.md); use the migration matrix when comparing those completed slices with the active hybrid final-state queue.

## Planning Completeness
- For direct hybrid final-state closure, the canonical planning package now exists end-to-end: master outline, direct roadmap, direct implementation plan, issue-ready backlog, issue seeds, and executable gap audit.
- For post-closeout governance optimization, the canonical lane package is now execution-closed with evidence: governance lane roadmap, governance lane implementation plan, `GAP-061` through `GAP-068` backlog/seeds, the shared acceptance/rollback template, dedicated epic-rendering support, and closeout evidence linkage.
- Historical lifecycle and productization plans remain execution history and rationale, not competing active mainlines.

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
- `Strategy Alignment Gates / GAP-040` through `GAP-044` are complete on the current branch baseline.
- `Interactive Session Productization / GAP-035` through `GAP-039` are complete on the current branch baseline.
- `Direct-To-Hybrid-Final-State Mainline / GAP-045` is complete on the current branch baseline as planning rebaseline closeout.
- `Direct-To-Hybrid-Final-State Mainline / GAP-046` through `GAP-060` are complete on the current branch baseline (verified on 2026-04-20).
- `Governance Optimization Lane / GAP-061` through `GAP-068` are complete on the current branch baseline (verified on 2026-04-20).
- `Post-Closeout Optimization Queue / GAP-069` through `GAP-074` is complete on the current branch baseline (verified on 2026-04-20).
- `Near-Term Gap Horizon Queue / GAP-080` and `GAP-081` are complete on the current branch baseline (verified on 2026-04-21), and `GAP-082` through `GAP-084` remain the active execution-horizon queue from the optimized best-state package.
- Active verification for this repo remains `build -> test -> contract/invariant -> doctor`, with docs and script checks still included in `verify-repo -Check All`.
- `docs/change-evidence/` remains historical evidence and planning trace, not the primary user-facing product surface.

## Project Entry
- [Root README](../README.md)
- [中文 README](../README.zh-CN.md)
- [English README](../README.en.md)
- [Project AGENTS](../AGENTS.md)

## Bilingual Coverage
- Mandatory bilingual coverage applies to operator-facing usage docs.
- At minimum, the following document classes must be available in both Chinese and English:
  - root entry guides: `README.md`, `README.zh-CN.md`, `README.en.md`
  - quickstarts under `docs/quickstart/`
  - product docs that directly explain operator actions or runnable flows, including `*guide*`, `*flow*`, `*commands*`, `*trial*`, `*pilot*`, `*console*`, and `*criteria*`
- Policy, research, architecture, ADR, planning, and spec/schema companion docs are not automatically required to be bilingual when they are not direct operator entrypoints.
- When a document becomes the primary operator path, it must either:
  - provide a Chinese and an English version, or
  - link clearly to an equivalent bilingual entrypoint that covers the same workflow

Current operator-facing bilingual set includes:
- [Root README](../README.md)
- [中文 README](../README.zh-CN.md)
- [English README](../README.en.md)
- [Single-Machine Runtime Quickstart](./quickstart/single-machine-runtime-quickstart.md)
- [单机 Runtime 快速开始](./quickstart/single-machine-runtime-quickstart.zh-CN.md)
- [AI Coding Usage Guide](./quickstart/ai-coding-usage-guide.md)
- [AI 编码使用指南](./quickstart/ai-coding-usage-guide.zh-CN.md)
- [Use With An Existing Repo](./quickstart/use-with-existing-repo.md)
- [在现有仓库中使用](./quickstart/use-with-existing-repo.zh-CN.md)
- [Multi-Repo Trial Quickstart](./quickstart/multi-repo-trial-quickstart.md)
- [多仓试运行快速开始](./quickstart/multi-repo-trial-quickstart.zh-CN.md)
- [Codex CLI/App Integration Guide](./product/codex-cli-app-integration-guide.md)
- [Codex CLI/App 集成指南](./product/codex-cli-app-integration-guide.zh-CN.md)
- [Target Repo Attachment Flow](./product/target-repo-attachment-flow.md)
- [Target Repo 接入流程](./product/target-repo-attachment-flow.zh-CN.md)
- [Session Bridge Commands](./product/session-bridge-commands.md)
- [Session Bridge 命令](./product/session-bridge-commands.zh-CN.md)

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

```powershell
python scripts/run-multi-repo-trial.py
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
- [单机 Runtime 快速开始](./quickstart/single-machine-runtime-quickstart.zh-CN.md)
- [AI Coding Usage Guide](./quickstart/ai-coding-usage-guide.md)
- [AI 编码使用指南](./quickstart/ai-coding-usage-guide.zh-CN.md)
- [Use With An Existing Repo](./quickstart/use-with-existing-repo.md)
- [在现有仓库中使用](./quickstart/use-with-existing-repo.zh-CN.md)
- [Multi-Repo Trial Quickstart](./quickstart/multi-repo-trial-quickstart.md)
- [多仓试运行快速开始](./quickstart/multi-repo-trial-quickstart.zh-CN.md)
- [Codex CLI/App Integration Guide](./product/codex-cli-app-integration-guide.md)
- [Codex CLI/App 集成指南](./product/codex-cli-app-integration-guide.zh-CN.md)
- [Codex Direct Adapter](./product/codex-direct-adapter.md)
- [Positioning And Competitive Layering](./strategy/positioning-and-competitive-layering.md)
- [Runtime Governance Borrowing Matrix](./research/runtime-governance-borrowing-matrix.md)
- [ADR-0007 Source-Of-Truth And Runtime Contract Bundle](./adrs/0007-source-of-truth-and-runtime-contract-bundle.md)
- [Generic Target-Repo Attachment Blueprint](./architecture/generic-target-repo-attachment-blueprint.md)
- [Repo-Native Contract Bundle](./architecture/repo-native-contract-bundle.md)
- [Local Baseline To Hybrid Final-State Migration Matrix](./architecture/local-baseline-to-hybrid-final-state-migration-matrix.md)
- [Interactive Session Productization Implementation Plan](./plans/interactive-session-productization-implementation-plan.md)
- [Interactive Session Productization Plan](./plans/interactive-session-productization-plan.md)
- [Governance Runtime Strategy Alignment Plan](./plans/governance-runtime-strategy-alignment-plan.md)

## Product
- [中文使用说明](../README.zh-CN.md)
- [English Usage Guide](../README.en.md)
- [Use With An Existing Repo](./quickstart/use-with-existing-repo.md)
- [在现有仓库中使用](./quickstart/use-with-existing-repo.zh-CN.md)
- [AI Coding Usage Guide](./quickstart/ai-coding-usage-guide.md)
- [AI 编码使用指南](./quickstart/ai-coding-usage-guide.zh-CN.md)
- [Strategy Index](./strategy/README.md)
- [Positioning And Competitive Layering](./strategy/positioning-and-competitive-layering.md)
- [Interaction Model](./product/interaction-model.md)
- [Target Repo Attachment Flow](./product/target-repo-attachment-flow.md)
- [Session Bridge Commands](./product/session-bridge-commands.md)
- [Target Repo 接入流程](./product/target-repo-attachment-flow.zh-CN.md)
- [Session Bridge 命令](./product/session-bridge-commands.zh-CN.md)
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
- [Adapter Capability Tiers](./product/adapter-capability-tiers.md)
- [Adapter Conformance Parity Matrix](./product/adapter-conformance-parity-matrix.md)
- [Codex CLI/App Integration Guide](./product/codex-cli-app-integration-guide.md)
- [Codex CLI/App 集成指南](./product/codex-cli-app-integration-guide.zh-CN.md)
- [Codex Direct Adapter](./product/codex-direct-adapter.md)
- [Multi-Repo Trial Loop](./product/multi-repo-trial-loop.md)
- [Runtime Compatibility And Upgrade Policy](./product/runtime-compatibility-and-upgrade-policy.md)
- [Maintenance, Deprecation, And Retirement Policy](./product/maintenance-deprecation-and-retirement-policy.md)
- [AI Coding PRD](./prd/governed-ai-coding-runtime-prd.md)

## Architecture
- [Architecture Index](./architecture/README.md)
- [ADR-0007 Source-Of-Truth And Runtime Contract Bundle](./adrs/0007-source-of-truth-and-runtime-contract-bundle.md)
- [Generic Target-Repo Attachment Blueprint](./architecture/generic-target-repo-attachment-blueprint.md)
- [Repo-Native Contract Bundle](./architecture/repo-native-contract-bundle.md)
- [Local Baseline To Hybrid Final-State Migration Matrix](./architecture/local-baseline-to-hybrid-final-state-migration-matrix.md)
- [Target Architecture](./architecture/governed-ai-coding-runtime-target-architecture.md)
- [Minimum Viable Governance Loop](./architecture/minimum-viable-governance-loop.md)
- [Governance Boundary Matrix](./architecture/governance-boundary-matrix.md)
- [MVP Stack Vs Target Stack](./architecture/mvp-stack-vs-target-stack.md)
- [Compatibility Matrix](./architecture/compatibility-matrix.md)

## Roadmap And Execution
- [Plans Index](./plans/README.md)
- [Backlog Index](./backlog/README.md)
- [Hybrid Final-State Master Outline](./architecture/hybrid-final-state-master-outline.md)
- [Direct-To-Hybrid Final-State Roadmap](./roadmap/direct-to-hybrid-final-state-roadmap.md)
- [Direct-To-Hybrid Final-State Implementation Plan](./plans/direct-to-hybrid-final-state-implementation-plan.md)
- [90-Day Plan](./roadmap/governed-ai-coding-runtime-90-day-plan.md)
- [Full Lifecycle Plan](./roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md)
- [Interactive Session Productization Implementation Plan](./plans/interactive-session-productization-implementation-plan.md)
- [Interactive Session Productization Plan](./plans/interactive-session-productization-plan.md)
- [Governance Runtime Strategy Alignment Plan](./plans/governance-runtime-strategy-alignment-plan.md)
- [Maintenance Implementation Plan](./plans/maintenance-implementation-plan.md)
- [Public Usable Release Implementation Plan](./plans/public-usable-release-implementation-plan.md)
- [Full Runtime Implementation Plan](./plans/full-runtime-implementation-plan.md)
- [Foundation Runtime Substrate Implementation Plan](./plans/foundation-runtime-substrate-implementation-plan.md)
- [Phase 0 Runnable Baseline Implementation Plan](./plans/phase-0-runnable-baseline-implementation-plan.md)
- [MVP Backlog Seeds](./backlog/mvp-backlog-seeds.md)
- [Full Lifecycle Backlog Seeds](./backlog/full-lifecycle-backlog-seeds.md)
- [Issue-Ready Backlog](./backlog/issue-ready-backlog.md)
- [Issue Seeds YAML](./backlog/issue-seeds.yaml)

## Strategy And Research
- [Strategy Index](./strategy/README.md)
- [Positioning And Competitive Layering](./strategy/positioning-and-competitive-layering.md)
- [Runtime Governance Borrowing Matrix](./research/runtime-governance-borrowing-matrix.md)
- [ADR-0007 Source-Of-Truth And Runtime Contract Bundle](./adrs/0007-source-of-truth-and-runtime-contract-bundle.md)
- [Local Baseline To Hybrid Final-State Migration Matrix](./architecture/local-baseline-to-hybrid-final-state-migration-matrix.md)
