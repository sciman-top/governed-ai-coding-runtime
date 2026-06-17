# Governed AI Coding Runtime Docs Index

## Current Snapshot
- Single source of planning truth: [planning-status.json](./architecture/planning-status.json)
- current active queue: `Continuous-Execution` (`Continuous Execution Readiness And Rollout`)
- `current decision gate`: `defer_ltp_and_refresh_evidence`
- `current live posture`: target-run freshness is `fresh`; Codex target runs are `native_attach` / ready; Claude workload probe is `native_attach` / ready
- certified baseline: `GAP-104..111`
- latest completed governance hardening slice: `GAP-169..172`
  - adds repo-owned `reference-basis`, release-style `preflight`, and CI `release-preflight`

## Core Operating Principle
- Human-readable summary: `Automation-first, gate-controlled, evidence-measured governance`.
- Compatibility token: `Governance Hub + Reusable Contract + Controlled Evolution loop + outer AI intelligent review/generation`.
- Current end-state wording: `Governance Hub + Reusable Contract + Capability-First Host Adapters + Controlled Evolution + Evidence-First Delivery`.
  - `Automation-first, outer-AI-assisted, gate-controlled evolution` remains the active operating posture.
  - The repo is a governance sidecar and does not authorize automatic host replacement, policy mutation, skill enablement, push, or merge.
  - The repo's proven value is workflow / gate / evidence governance; it has not yet proven a built-in best-workflow auto-executor across repos, hosts, and risk tiers.
  - The intended evolution target is `AI coding workflow governor`, not a replacement host or a single canonical execution recipe.
  - `Context budget and instruction minimalism` and `Least-privilege tool and credential boundary` both require concise, reviewable, bounded tool outputs with auditable permissions, provider secrets, and MCP/tool identities.
- `Measured effect feedback over claims` means completion claims must keep fresh evidence, effect feedback, and trace/replay/trajectory references attached to the verified outcome.
- Efficiency never overrides safety, permissions, evidence, rollback, review, or gate constraints.
- The minimum comparable evidence surface still includes fields such as `freshness_status`, verification commands, effect metrics, and rollback references where the surface supports them.

## Start Here
- [Root README](../README.md)
- [Chinese Guide](../README.zh-CN.md)
- [English Guide](../README.en.md)
- [Project AGENTS](../AGENTS.md)
- [planning-status.json](./architecture/planning-status.json)

## Operator And Daily Use
- [Single-Machine Runtime Quickstart](./quickstart/single-machine-runtime-quickstart.md)
- [单机 Runtime 快速开始](./quickstart/single-machine-runtime-quickstart.zh-CN.md)
- [AI Coding Usage Guide](./quickstart/ai-coding-usage-guide.md)
- [AI 编码使用指南](./quickstart/ai-coding-usage-guide.zh-CN.md)
- [Use With An Existing Repo](./quickstart/use-with-existing-repo.md)
- [在现有仓库中使用](./quickstart/use-with-existing-repo.zh-CN.md)
- [Multi-Repo Trial Quickstart](./quickstart/multi-repo-trial-quickstart.md)
- [多仓试运行快速开始](./quickstart/multi-repo-trial-quickstart.zh-CN.md)
- [Target Repo Attachment Flow](./product/target-repo-attachment-flow.md)
- [Target Repo 接入流程](./product/target-repo-attachment-flow.zh-CN.md)
- [Session Bridge Commands](./product/session-bridge-commands.md)
- [Session Bridge 命令](./product/session-bridge-commands.zh-CN.md)
- [Codex CLI/App Integration Guide](./product/codex-cli-app-integration-guide.md)
- [Codex CLI/App 集成指南](./product/codex-cli-app-integration-guide.zh-CN.md)
- [Agent Continuity Guide](./product/agent-continuity.md)
- [共享上下文连续性指南](./product/agent-continuity.zh-CN.md)
- [Codex / Claude Host Feedback Loop](./product/host-feedback-loop.md)
- [Codex / Claude 功能反馈闭环](./product/host-feedback-loop.zh-CN.md)

## Verification And Release Gates
- Canonical repo verifier: `scripts/verify-repo.ps1`
  - `Build`, `Runtime`, `RuntimeQuick`, `Contract`, `Doctor`, `Docs`, `DocsLinks`, `Scripts`, `All`
- Release-style closeout: `scripts/governance/preflight.ps1`
  - wraps the hard-gate floor `build -> test -> contract/invariant -> hotspot`
  - adds `Docs`, `Scripts`, and `git diff --check`
- Current release CI: [verify.yml](../.github/workflows/verify.yml)
- Related docs:
  - [Change Evidence Index](./change-evidence/README.md)
  - [Runbooks](./runbooks/README.md)
  - [Target Repo Test Slicing Policy](./targets/target-repo-test-slicing-policy.md)
  - [Acceptance Metrics Contract](./product/acceptance-metrics-contract.md)

## Reference Governance
- High-drift changes are now fail-closed in the `Contract` gate.
- Policy entrypoints:
  - [Reference-Required Change Policy](./architecture/reference-required-change-policy.json)
  - [Reference Basis Policy](./architecture/reference-basis-policy.json)
  - [Reference Basis Catalog](./research/reference-basis-catalog.json)
  - [Reference Basis Matrix](./research/reference-basis-matrix.md)
- Verifiers:
  - `scripts/verify-reference-required-changes.py`
  - `scripts/verify-reference-basis.py`
- Current hardening docs:
  - [Reference Governance And Release Preflight Roadmap](./roadmap/reference-governance-and-preflight-roadmap.md)
- [Reference Governance And Release Preflight Plan](./plans/reference-governance-and-preflight-plan.md)
- [Workflow Governor Governance Plan](./plans/workflow-governor-governance-plan.md)
- [Workflow Governor Governance Roadmap](./roadmap/workflow-governor-governance-roadmap.md)
- [Workflow Governance Spec](./specs/workflow-governance-spec.md)
- [Workflow Effect Metrics Spec](./specs/workflow-effect-metrics-spec.md)
  - [20260609 Reference Basis And Preflight Hardening](./change-evidence/20260609-reference-basis-and-preflight-hardening.md)
  - [20260609 Reference-Required Change Enforcement](./change-evidence/20260609-reference-required-change-enforcement.md)

## Planning, Strategy, And Architecture
- Planning truth:
  - [Plans Index](./plans/README.md)
  - [Backlog Index](./backlog/README.md)
  - [Issue-Ready Backlog](./backlog/issue-ready-backlog.md)
- Strategy:
  - [Strategy Index](./strategy/README.md)
  - [Current Best-End-State Blueprint](./strategy/current-best-end-state-blueprint.md)
  - [Positioning And Competitive Layering](./strategy/positioning-and-competitive-layering.md)
- Architecture:
  - [Architecture Index](./architecture/README.md)
  - [Hybrid Final-State Master Outline](./architecture/hybrid-final-state-master-outline.md)
  - [Generic Target-Repo Attachment Blueprint](./architecture/generic-target-repo-attachment-blueprint.md)
  - [Repo-Native Contract Bundle](./architecture/repo-native-contract-bundle.md)
  - [Host Family Capability Surface Blueprint](./architecture/host-family-capability-surface-blueprint.md)
- Product and PRD:
  - [AI Coding PRD](./prd/governed-ai-coding-runtime-prd.md)
  - [Interaction Model](./product/interaction-model.md)
  - [Continuous Execution Output Envelope](./product/continuous-execution-output-envelope.md)
  - [Adapter Capability Tiers](./product/adapter-capability-tiers.md)

## Targets, Rules, And Managed Assets
- Managed target-repo metadata:
  - [target-repos-catalog.json](./targets/target-repos-catalog.json)
  - [target-repo-governance-baseline.json](./targets/target-repo-governance-baseline.json)
  - [target-repo-rollout-contract.json](./targets/target-repo-rollout-contract.json)
- Managed templates:
  - `docs/targets/templates/claude-code/`
  - `docs/targets/templates/git-hooks/`
  - `docs/targets/templates/verify-powershell-policy.py`
  - `docs/targets/templates/search-context.ignore`
- Rule sync source of truth:
  - [rules/manifest.json](../rules/manifest.json)

## Evidence, History, And Rollback
- Current evidence index: [Change Evidence Index](./change-evidence/README.md)
- Latest posture proof:
  - [20260618 Active Queue Evidence-Upkeep Refresh](./change-evidence/20260618-active-queue-evidence-upkeep-refresh.md)
  - [20260617 Active Queue Evidence-Upkeep Refresh](./change-evidence/20260617-active-queue-evidence-upkeep-refresh.md)
  - [20260617 Planning EntryPoint Proof Refresh](./change-evidence/20260617-planning-entrypoint-proof-refresh.md)
  - [20260616 Continuous Execution Runtime Gate Refresh](./change-evidence/20260616-continuous-execution-runtime-gate-refresh.md)
  - [20260614 Continuous Execution Promotion](./change-evidence/20260614-continuous-execution-promotion.md)
  - [20260613 README And Index Refresh](./change-evidence/20260613-readme-and-index-refresh.md)
- Completed history:
  - [20260609 Live Posture Recovery](./change-evidence/20260609-live-posture-recovery.md) (historical recovery milestone, archived)
  - [Completed GAP History](./archive/completed-gap-history.md)
  - [已完成 GAP 历史归档](./archive/completed-gap-history.zh-CN.md)
- Recovery docs:
  - [Runbooks](./runbooks/README.md)
  - [Control Rollback](./runbooks/control-rollback.md)
  - [Failed Rollout Recovery](./runbooks/failed-rollout-recovery.md)

## Bilingual Coverage
Operator-facing docs that are expected to stay bilingual include:
- `README.md`, `README.zh-CN.md`, `README.en.md`
- `docs/quickstart/*`
- `docs/product/codex-cli-app-integration-guide*`
- `docs/product/agent-continuity*`
- `docs/product/target-repo-attachment-flow*`
- `docs/product/session-bridge-commands*`
- `docs/product/host-feedback-loop*`

Policy, research, architecture, ADR, planning, and schema/spec companions are not automatically required to be bilingual unless they become the primary operator path.

## Verification Quickstart
```powershell
.\run.ps1 fast
```

```powershell
.\run.ps1 readiness -OpenUi
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/governance/preflight.ps1 -DisableAutoCommit
```
