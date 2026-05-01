# Backlog Index

## Purpose
This directory holds the human and machine planning artifacts that bridge strategy into implementation-ready work.

## Artifact Roles
- [MVP Backlog Seeds](./mvp-backlog-seeds.md)
  - historical seed list for the completed 90-day MVP
  - use this to understand how `Phase 0` through `Phase 4` were sequenced
- [Full Lifecycle Backlog Seeds](./full-lifecycle-backlog-seeds.md)
  - phase-level seed history for the full lifecycle baseline from `GAP-018` through `GAP-044`
  - use this for historical sequencing context
- [Issue-Ready Backlog](./issue-ready-backlog.md)
  - current human-readable full-lifecycle implementation backlog
  - use this for dependencies, acceptance criteria, and execution order
- [Issue Seeds YAML](./issue-seeds.yaml)
  - machine-readable active issue ids, types, blockers, and user-story mapping
  - use this for drift checks and automation

## Script Relationship
- GitHub issue bootstrap helper:
  - [`scripts/github/create-roadmap-issues.ps1`](../../scripts/github/create-roadmap-issues.ps1)
- Current behavior:
  - task titles and seed metadata are now injected from `issue-seeds.yaml`
  - task issue bodies are now rendered from `issue-ready-backlog.md` plus seed metadata
  - initiative and epic issue bodies for the current direct-to-hybrid mainline are rendered from `governed-ai-coding-runtime-full-lifecycle-plan.md`
  - the governance-optimization lane now renders as a dedicated follow-on epic after the direct-to-hybrid `Phase 5` chain
  - `-ValidateOnly` can be used to verify the script sees the current seed set without calling GitHub
  - `-ValidateOnly -RenderAll` renders every task, epic, and initiative body and verifies the actual task creation definitions without calling GitHub
- Current limitation:
  - the seeding script depends on stable markdown heading structure in both the backlog and lifecycle roadmap
  - this parser contract is covered by `scripts/verify-repo.ps1 -Check Scripts`, which fails if the source docs can no longer render the issue bodies

## Current Execution Posture
- The 90-day MVP backlog reached its endpoint at `GAP-017`.
- `Vision / GAP-018` and `GAP-019` are complete through planning alignment and capability freeze.
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
- `Near-Term Gap Horizon Queue / GAP-080` through `GAP-089` are complete on the current branch baseline (`GAP-080` through `GAP-084` verified on 2026-04-21; `GAP-085` through `GAP-089` verified on 2026-04-22).
- `Long-Term Gap Trigger Audit Queue / GAP-090` through `GAP-092` is complete; all `LTP-01..05` packages remain deferred pending future trigger evidence.
- `Optimized Hybrid Long-Term Implementation Queue / GAP-093` through `GAP-103` is complete on the current branch baseline. No `LTP-01..06` package was selected or implemented; `GAP-103` refreshes all-target daily workload evidence after the `GAP-102` closeout.
- `Complete Hybrid Final-State Realization Queue / GAP-104` through `GAP-111` is complete. `GAP-111` certifies full hybrid final-state closure on the current branch baseline with fresh service, adapter, execution, data/provenance, operations, all-target, and claim-drift evidence.
- `Post-Certification Guard Queue / GAP-112` is complete. It adds a machine-readable current-source compatibility guard for A2A/MCP/Codex sandbox, host guardrails, and supply-chain provenance assumptions.
- `Post-Certification Promotion Queue / GAP-113` is complete. It adds the autonomous `LTP-01..06` promotion scope fence that answers whether, why, and how to advance after certification.
- `Post-Certification Selection Queue / GAP-114` is complete. It turns the promotion fence into the autonomous next-work selector.
- `Dual First-Class Host Entrypoint Queue / GAP-115` through `GAP-119` is complete as owner-directed bounded scope. Codex and Claude Code are dual first-class entrypoints with current evidence-backed `native_attach` tier parity; host APIs remain different and future drift must degrade explicitly.
- `Runtime Evolution Review Queue / GAP-120` through `GAP-124` is dry-run only. It defines the 30-day self-evolution policy, source collection, candidate evaluation, operator entrypoint, and freshness gate without enabling automatic mutation; AI coding experience is extracted through `ExperienceReview` only after it is captured as reviewable evidence, controlled proposals, knowledge records, or skill manifests.
- `Runtime Evolution Materialization Queue / GAP-125` through `GAP-129` starts controlled auto-apply. It may materialize low-risk proposals and disabled skill candidates as files, but it must not enable skills, auto-apply policy, sync target repos, or push/merge without review.
- `Governance Hub Reuse And Controlled Evolution Queue / GAP-130` is complete as the scope rebaseline, `GAP-131` is complete as the capability portfolio classifier baseline, `GAP-132` is complete as the control-pack execution contract baseline, `GAP-133` is complete as the inheritance override baseline, `GAP-134` is complete as the target-repo reuse effect feedback baseline, `GAP-135` is complete as the knowledge-memory lifecycle baseline, `GAP-136` is complete as the promotion lifecycle baseline, and `GAP-137` is complete as the repo-map context artifact baseline; `GAP-138` through `GAP-139` are the next planned implementation queue. It moves the clarified strategy into executable work: Codex and Claude Code remain cooperation hosts, Claude Code is treated as local third-party-provider usage rather than an official subscription dependency, Hermes/OpenHands/SWE-agent/Letta/Mem0/Aider-style projects become selective mechanism sources, and every added, retained, improved, deprecated, retired, or deleted capability must produce real effect feedback before certification.
- Any heavy LTP implementation package after this selector must use ids beyond the bounded host-support queue and must pass the autonomous or owner-directed scope fence.
- Historical `GAP-018` through `GAP-044` remain completion history and dependency context.
- The active lifecycle is now anchored by:
  - [Hybrid Final-State Master Outline](../architecture/hybrid-final-state-master-outline.md)
  - [Direct-To-Hybrid Final-State Roadmap](../roadmap/direct-to-hybrid-final-state-roadmap.md)
  - [Direct-To-Hybrid Final-State Implementation Plan](../plans/direct-to-hybrid-final-state-implementation-plan.md)
  - [Optimized Hybrid Final-State Long-Term Roadmap](../roadmap/optimized-hybrid-final-state-long-term-roadmap.md)
  - [Optimized Hybrid Final-State Long-Term Implementation Plan](../plans/optimized-hybrid-final-state-long-term-implementation-plan.md)
  - [Claude Code First-Class Entrypoint Plan](../plans/claude-code-first-class-entrypoint-plan.md)
  - [Runtime Evolution Review Plan](../plans/runtime-evolution-review-plan.md)
  - [Governance Hub Reuse And Controlled Evolution Plan](../plans/governance-hub-reuse-and-controlled-evolution-plan.md)
  - [Governance Optimization Lane Roadmap](../roadmap/governance-optimization-lane-roadmap.md)
  - [Governance Optimization Lane Implementation Plan](../plans/governance-optimization-lane-implementation-plan.md)
  - [Long-Term Gap Trigger Audit Plan](../plans/long-term-gap-trigger-audit-plan.md)
  - [Full Lifecycle Plan](../roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md)
  - [Full Lifecycle Backlog Seeds](./full-lifecycle-backlog-seeds.md)
  - [Issue-Ready Backlog](./issue-ready-backlog.md)
  - [Issue Seeds YAML](./issue-seeds.yaml)
- The interactive productization direction also depends on:
  - [Generic Target-Repo Attachment Blueprint](../architecture/generic-target-repo-attachment-blueprint.md)
  - [Interaction Model](../product/interaction-model.md)
  - [Interactive Session Productization Implementation Plan](../plans/interactive-session-productization-implementation-plan.md)
  - [Interactive Session Productization Plan](../plans/interactive-session-productization-plan.md)
  - [Governance Runtime Strategy Alignment Plan](../plans/governance-runtime-strategy-alignment-plan.md)
- The local baseline and maintenance surfaces still depend on:
  - [Single-Machine Runtime Quickstart](../quickstart/single-machine-runtime-quickstart.md)
  - [Public Usable Release Criteria](../product/public-usable-release-criteria.md)
  - [Adapter Degrade Policy](../product/adapter-degrade-policy.md)
  - [Runtime Compatibility And Upgrade Policy](../product/runtime-compatibility-and-upgrade-policy.md)
  - [Maintenance, Deprecation, And Retirement Policy](../product/maintenance-deprecation-and-retirement-policy.md)
- The completed implementation checklists remain useful execution history:
  - [Maintenance Implementation Plan](../plans/maintenance-implementation-plan.md)
  - [Full Runtime Implementation Plan](../plans/full-runtime-implementation-plan.md)
  - [Foundation Runtime Substrate Implementation Plan](../plans/foundation-runtime-substrate-implementation-plan.md)
- Historical phase plans under `docs/plans/` remain evidence of earlier work and can keep unchecked checkbox syntax for execution-history readability.
