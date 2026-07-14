# Governed AI Coding Runtime Docs Index

## Current Snapshot
- Single source of planning truth: [planning-status.json](./architecture/planning-status.json)
- planning status anchor: `updated_on=2026-07-05`
- latest archived multi-repo evidence refresh: `2026-07-05`
- latest governance / self-evolution machine-readable refresh: `2026-06-24`
- current active queue: `Continuous-Execution` (`Continuous Execution Readiness And Rollout`)
- `current decision gate`: `defer_ltp_and_refresh_evidence`
- `current live posture`: repo-local gates, host feedback, and self-evolution evidence remain live; archived target-run posture is historical only
  - historical archive note: the latest archived 2026-07-05 batch still records target-run freshness is `fresh` and paired Codex/Claude host probes at `native_attach` / ready, but that archive no longer implies a live target-repo capability
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

## Repository Surfaces
- [Apps](../apps/README.md)
- [Infra](../infra/README.md)
- [Packages](../packages/README.md)
- [Contracts](../packages/contracts/README.md)
- [Schemas](../schemas/README.md)
- [Tests](../tests/README.md)

## Operator And Daily Use
- [Single-Machine Runtime Quickstart](./quickstart/single-machine-runtime-quickstart.md)
- [单机 Runtime 快速开始](./quickstart/single-machine-runtime-quickstart.zh-CN.md)
- [AI Coding Usage Guide](./quickstart/ai-coding-usage-guide.md)
- [AI 编码使用指南](./quickstart/ai-coding-usage-guide.zh-CN.md)
- [Use With An Existing Repo](./quickstart/use-with-existing-repo.md)
- [在现有仓库中使用](./quickstart/use-with-existing-repo.zh-CN.md)
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
  - [Acceptance Metrics Contract](./product/acceptance-metrics-contract.md)

## Portable Packaging And Install
- Package staging, release zip, sha256, manifest, and provenance: `scripts/package-runtime.ps1`
- Release wrapper: `release.ps1`
- Portable/User runtime initialization: `install.ps1`
- Related criteria:
  - [Public Usable Release Criteria](./product/public-usable-release-criteria.md)
  - [公开可用发布标准（Chinese）](./product/public-usable-release-criteria.zh-CN.md)

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
  - [Repo-Native Contract Bundle](./architecture/repo-native-contract-bundle.md)
  - [Host Family Capability Surface Blueprint](./architecture/host-family-capability-surface-blueprint.md)
- Product and PRD:
  - [AI Coding PRD](./prd/governed-ai-coding-runtime-prd.md)
  - [Interaction Model](./product/interaction-model.md)
  - [Continuous Execution Output Envelope](./product/continuous-execution-output-envelope.md)
  - [Adapter Capability Tiers](./product/adapter-capability-tiers.md)

## Rules And Managed Assets
- Automated target-repo rollout, attachment, session-bridge, and managed template distribution have been retired. Target rules are maintained in place; direct-child Git-root discovery is reconciled with an explicit allowlist before audit, but discovery never auto-enrolls a repository.
- Retained global-only rule-sync source of truth:
  - [rules/manifest.json](../rules/manifest.json)
- Target-project coordination audit source of truth:
  - [rules/target-project-rule-coordination.json](../rules/target-project-rule-coordination.json)
- Coordination contract and evidence:
  - [Agent Rule Coordination v2 Spec](./specs/agent-rule-coordination-v2-spec.md)
  - [Official And Community Practices Research](./research/2026-07-10-agent-rules-official-and-community-practices.md)
- Verifiers:
  - `python scripts/verify-agent-rule-family.py`
  - `python scripts/verify-target-project-rules.py --require-all`
  - `python scripts/export-target-rule-ci-matrix.py`
- Each target owns a rule-only CI workflow matching `rules/templates/github/agent-rule-contract.yml`; the control workflow generates a nine-target matrix for scheduled/manual aggregate audits.
- The control-repository `Contract` gate also validates the coordination manifest against schema `2.3`, reconciles direct-child Git roots with the allowlist, and audits locally available targets; release verification uses `--require-all` for the full nine-repository scope.
- Deterministic enforcement stays in `.codex`, `.claude/settings.json`, hooks, permissions, MCP, and CI; it is not solved by blind text synchronization.

## Evidence, History, And Rollback
- Current evidence index: [Change Evidence Index](./change-evidence/README.md)
- Latest posture proof:
  - [20260711 Agent Rule Cross-Repo CI](./change-evidence/20260711-agent-rule-cross-repo-ci.md)
  - [20260710 Agent Rule Coordination v2](./change-evidence/20260710-agent-rule-coordination-v2.md)
  - [20260705 Readme And Docs Current-State Refresh](./change-evidence/20260705-readme-and-docs-current-state-refresh.md)
  - [20260705 Runtime Evolution Functional Verification](./change-evidence/20260705-runtime-evolution-functional-verification.md)
  - [20260705 Claim Catalog Freshness Refresh](./change-evidence/20260705-claim-catalog-freshness-refresh.md)
  - [20260623 Active Queue Evidence-Upkeep Refresh](./change-evidence/20260623-active-queue-evidence-upkeep-refresh.md)
  - [20260623 Self-Evolution Review Refresh](./change-evidence/20260623-self-evolution-review-refresh.md)
  - [20260620 Active Queue Evidence-Upkeep Refresh](./change-evidence/20260620-active-queue-evidence-upkeep-refresh.md)
  - [20260620 Self-Evolution Review Refresh](./change-evidence/20260620-self-evolution-review-refresh.md)
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
