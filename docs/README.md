# Governed AI Coding Runtime Docs Index

## Current Baseline
- This repository is currently `docs-first / contracts-first`.
- `docs/`, `schemas/`, top-level skeleton directories, `scripts/verify-repo.ps1`, `scripts/build-runtime.ps1`, `scripts/doctor-runtime.ps1`, `.github/workflows/verify.yml`, and tested runtime contract primitives are present.
- MVP contract slices, the `Foundation / GAP-020` through `GAP-023` substrate, `Full Runtime / GAP-024` through `GAP-028`, `Public Usable Release / GAP-029` through `GAP-032`, and `Maintenance Baseline / GAP-033` through `GAP-034` are complete.
- `Strategy Alignment Gates / GAP-040` through `GAP-044` are complete on the current branch baseline and remain encoded as satisfied hardening dependencies around the landed `Interactive Session Productization / GAP-035` through `GAP-039` productization slice.

## Core Operating Principle
- Human-readable summary: `Automation-first, gate-controlled, evidence-measured governance`.
- This repository is a governance sidecar / control plane, not a replacement host product for Codex or Claude Code.
- `Efficiency first, safety bounded`: low interruption, continuous execution, lower token and cost burn, necessary explanatory density, and high throughput are long-lived targets, while concrete defaults such as model, reasoning level, context window, compact threshold, provider mapping, or auth storage remain replaceable implementation details. Efficiency never overrides safety, permissions, evidence, rollback, review, or gate constraints for effective changes.
- `Automation-first, outer-AI-assisted, gate-controlled evolution`: the repository should automate deterministic governance work and may automatically trigger outer AI for intelligent review, knowledge extraction, candidate generation, and evolution proposals, while effective changes remain blocked by structured candidates, risk gates, machine gates, evidence, rollback, and required review boundaries.
- `Governance hub, reusable contract, host-compatible execution`: the best engineering final state is Governance Hub + Reusable Contract + Controlled Evolution loop + outer AI intelligent review/generation capability, implemented as governed controls rather than a competing AI coding host.
- `Context budget and instruction minimalism` plus `Least-privilege tool and credential boundary`: core rules, instruction files, repo maps, memory artifacts, and bounded tool outputs must stay concise, high-signal, and verifiable; permissions, sandbox scope, provider secrets, mounted paths, network access, and MCP/tool identities must stay auditable and deterministic where possible.
- `Measured effect feedback over claims`: completion claims require fresh target-run evidence, eval traces, trace/replay/trajectory references where available, effect feedback, verification commands, and rollback paths; documentation, code existence, or candidate files alone do not prove completion.
- Minimum comparable evidence fields are `freshness_status`, `target_run_id`, `gate_result`, `effect_metric_delta`, `verification_command`, and `rollback_ref` when the task surface can provide them.

## Current Working Set
- [Hybrid Final-State Master Outline](./architecture/hybrid-final-state-master-outline.md)
- [Direct-To-Hybrid Final-State Roadmap](./roadmap/direct-to-hybrid-final-state-roadmap.md)
- [Direct-To-Hybrid Final-State Implementation Plan](./plans/direct-to-hybrid-final-state-implementation-plan.md)
- [Optimized Hybrid Final-State Long-Term Roadmap](./roadmap/optimized-hybrid-final-state-long-term-roadmap.md)
- [Optimized Hybrid Final-State Long-Term Implementation Plan](./plans/optimized-hybrid-final-state-long-term-implementation-plan.md)
- [Claude Code First-Class Entrypoint Plan](./plans/claude-code-first-class-entrypoint-plan.md)
- [Runtime Evolution Review Plan](./plans/runtime-evolution-review-plan.md)
- [Governance Hub Reuse And Controlled Evolution Plan](./plans/governance-hub-reuse-and-controlled-evolution-plan.md)
- [Target Repo Managed Asset Retirement And Uninstall Plan](./plans/target-repo-managed-asset-retirement-and-uninstall-plan.md)
- [Capability Portfolio Classifier](./architecture/capability-portfolio-classifier.json)
- [Runtime Evolution Policy](./architecture/runtime-evolution-policy.json)
- [Long-Term Gap Trigger Audit Plan](./plans/long-term-gap-trigger-audit-plan.md)
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
- [Hybrid Final-State External Benchmark Review](./research/2026-04-27-hybrid-final-state-external-benchmark-review.md)
- [ADR-0007 Source-Of-Truth And Runtime Contract Bundle](./adrs/0007-source-of-truth-and-runtime-contract-bundle.md)
- [ADR-0008 Autonomous LTP Promotion Scope Fence](./adrs/0008-autonomous-ltp-promotion-scope-fence.md)
- [Generic Target-Repo Attachment Blueprint](./architecture/generic-target-repo-attachment-blueprint.md)
- [Repo-Native Contract Bundle](./architecture/repo-native-contract-bundle.md)
- [Local Baseline To Hybrid Final-State Migration Matrix](./architecture/local-baseline-to-hybrid-final-state-migration-matrix.md)
- [Interaction Model](./product/interaction-model.md)
- [AI Coding PRD](./prd/governed-ai-coding-runtime-prd.md)
- [20260418 Maintenance Execution Plan](./change-evidence/20260418-maintenance-execution-plan.md)

## Current Planning Chain
- Strategy and boundary inputs: [AI Coding PRD](./prd/governed-ai-coding-runtime-prd.md), [Interaction Model](./product/interaction-model.md), [Positioning And Competitive Layering](./strategy/positioning-and-competitive-layering.md), [Runtime Governance Borrowing Matrix](./research/runtime-governance-borrowing-matrix.md), [Hybrid Final-State External Benchmark Review](./research/2026-04-27-hybrid-final-state-external-benchmark-review.md), [ADR-0007 Source-Of-Truth And Runtime Contract Bundle](./adrs/0007-source-of-truth-and-runtime-contract-bundle.md), [ADR-0008 Autonomous LTP Promotion Scope Fence](./adrs/0008-autonomous-ltp-promotion-scope-fence.md), [Generic Target-Repo Attachment Blueprint](./architecture/generic-target-repo-attachment-blueprint.md), [Repo-Native Contract Bundle](./architecture/repo-native-contract-bundle.md), [Local Baseline To Hybrid Final-State Migration Matrix](./architecture/local-baseline-to-hybrid-final-state-migration-matrix.md), [Target Architecture](./architecture/governed-ai-coding-runtime-target-architecture.md), [Minimum Viable Governance Loop](./architecture/minimum-viable-governance-loop.md), and [Governance Runtime Strategy Alignment Plan](./plans/governance-runtime-strategy-alignment-plan.md)
- Execution ordering: [Hybrid Final-State Master Outline](./architecture/hybrid-final-state-master-outline.md), [Direct-To-Hybrid Final-State Roadmap](./roadmap/direct-to-hybrid-final-state-roadmap.md), [Direct-To-Hybrid Final-State Implementation Plan](./plans/direct-to-hybrid-final-state-implementation-plan.md), [Optimized Hybrid Final-State Long-Term Roadmap](./roadmap/optimized-hybrid-final-state-long-term-roadmap.md), [Optimized Hybrid Final-State Long-Term Implementation Plan](./plans/optimized-hybrid-final-state-long-term-implementation-plan.md), [Claude Code First-Class Entrypoint Plan](./plans/claude-code-first-class-entrypoint-plan.md), [Runtime Evolution Review Plan](./plans/runtime-evolution-review-plan.md), [Governance Hub Reuse And Controlled Evolution Plan](./plans/governance-hub-reuse-and-controlled-evolution-plan.md), [Backlog Index](./backlog/README.md), [Issue-Ready Backlog](./backlog/issue-ready-backlog.md), [Issue Seeds YAML](./backlog/issue-seeds.yaml), and [Plans Index](./plans/README.md)
- Follow-on optimization ordering: [Governance Optimization Lane Roadmap](./roadmap/governance-optimization-lane-roadmap.md), [Governance Optimization Lane Implementation Plan](./plans/governance-optimization-lane-implementation-plan.md), [Backlog Index](./backlog/README.md), [Issue-Ready Backlog](./backlog/issue-ready-backlog.md), and [Issue Seeds YAML](./backlog/issue-seeds.yaml); this lane was the governance-only follow-on after `GAP-060` and is complete on the current branch baseline (verified on 2026-04-20)
- Current implementation history: [Foundation Runtime Substrate Implementation Plan](./plans/foundation-runtime-substrate-implementation-plan.md), [Full Runtime Implementation Plan](./plans/full-runtime-implementation-plan.md), [Public Usable Release Implementation Plan](./plans/public-usable-release-implementation-plan.md), and [Maintenance Implementation Plan](./plans/maintenance-implementation-plan.md); use the migration matrix when comparing those completed slices with the active hybrid final-state queue.

## Planning Completeness
- For direct hybrid final-state closure, the canonical planning package now exists end-to-end: master outline, direct roadmap, direct implementation plan, issue-ready backlog, issue seeds, and executable gap audit.
- For post-closeout governance optimization, the canonical lane package is now execution-closed with evidence: governance lane roadmap, governance lane implementation plan, `GAP-061` through `GAP-068` backlog/seeds, the shared acceptance/rollback template, dedicated epic-rendering support, and closeout evidence linkage.
- For long-term gap work, `GAP-090` through `GAP-092` define a completed trigger-audit queue that refreshes evidence and selects at most one LTP before implementation starts; all `LTP-01..05` packages remain deferred on the current branch baseline.
- For optimized long-term implementation, `GAP-093` through `GAP-103` define the completed queue for containment/provenance, transition-stack convergence, trigger reviews, selected `LTP` scope fence, first selected-package implementation, sustained release-readiness closeout, and fresh all-target workload evidence.
- For complete hybrid final-state realization, `GAP-104` through `GAP-111` are complete on the current branch baseline. `GAP-111` certifies complete hybrid final-state closure with fresh evidence across service boundary, live Codex continuity, non-Codex parity, governed executable coverage, data/provenance release paths, operations recovery, all-target workload, and claim-drift gates.
- For post-certification guard work, `GAP-112` is complete on the current branch baseline. It adds a machine-readable current-source compatibility guard for A2A/MCP/Codex sandbox, host guardrails, and provenance assumptions.
- For post-certification promotion work, `GAP-113` is complete on the current branch baseline. It adds a machine-readable autonomous `LTP-01..06` promotion fence that currently returns `defer_all` unless exactly one package has fresh trigger evidence and scope.
- For post-certification next-work selection, `GAP-114` is complete on the current branch baseline. It turns `GAP-113` output into a deterministic autonomous next action.
- For dual first-class host support, `GAP-115` through `GAP-119` are complete. Current live probe and conformance evidence keep both Codex and Claude Code at `native_attach` / supported when the host exposes the required session, resume, structured-output, and managed hook surfaces.
- For runtime self-evolution, `GAP-120` through `GAP-124` are dry-run only. They define a 30-day evolution review policy, source collection, candidate evaluation, operator entrypoint, and freshness gate without enabling automatic mutation; source collection includes official docs, primary projects, community practice, runtime evidence, and reviewable AI coding experience/skillization signals.
- For governance hub reuse and controlled evolution, `GAP-130` is complete as the scope rebaseline, `GAP-131` is complete as the capability portfolio classifier baseline, `GAP-132` is complete as the control-pack execution contract baseline, `GAP-133` is complete as the inheritance override baseline, `GAP-134` is complete as the target-repo reuse effect feedback baseline, `GAP-135` is complete as the knowledge-memory lifecycle baseline, `GAP-136` is complete as the promotion lifecycle baseline, `GAP-137` is complete as the repo-map context artifact baseline, `GAP-138` is complete as the policy/tool/credential audit boundary baseline, `GAP-139` is complete as the governance hub certification baseline, `GAP-140` is complete as the bounded host-capability defer baseline, `GAP-141` is complete as the historical problem-trace closure policy baseline, `GAP-142` is complete as the degraded fresh-evidence next-work guard, and `GAP-143` is complete as the evidence recovery posture contract. They clarify that Codex and Claude Code are primary cooperation hosts, that Claude Code is used locally through third-party Anthropic-compatible providers such as GLM or DeepSeek rather than assumed official subscription state, and that Hermes/OpenHands/SWE-agent/Letta/Mem0/Aider-style mechanisms can be selectively absorbed only when they become executable controls with evidence, rollback, and effect metrics.
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
- `Near-Term Gap Horizon Queue / GAP-080` through `GAP-089` are complete on the current branch baseline (`GAP-080` through `GAP-084` verified on 2026-04-21; `GAP-085` through `GAP-089` verified on 2026-04-22).
- `Long-Term Gap Trigger Audit Queue / GAP-090` through `GAP-092` is complete; all `LTP-01..05` packages remain deferred pending future trigger evidence.
- `Optimized Hybrid Long-Term Implementation Queue / GAP-093` through `GAP-103` is complete on the current branch baseline. No `LTP-01..06` package was selected or implemented; each remains trigger-based until fresh scope-fence evidence exists.
- `Complete Hybrid Final-State Realization Queue / GAP-104` through `GAP-111` is complete and remains evidence-certified by the `GAP-111` evidence batch.
- `Post-Certification Guard Queue / GAP-112` is complete and enforced through `verify-repo.ps1 -Check Docs`.
- `Post-Certification Promotion Queue / GAP-113` is complete and enforced through `verify-repo.ps1 -Check Docs`.
- `Post-Certification Selection Queue / GAP-114` is complete and enforced through `verify-repo.ps1 -Check Docs`.
- `Dual First-Class Host Entrypoint Queue / GAP-115` through `GAP-119` is complete as owner-directed bounded scope for Codex plus Claude Code; latest native tier parity evidence is in `docs/change-evidence/20260427-claude-code-native-attach-tier-parity.md`.
- `Runtime Evolution Review Queue / GAP-120` through `GAP-129` has dry-run `EvolutionReview` and `ExperienceReview` operator actions plus controlled `EvolutionMaterialize` file output. `ExperienceReview` now writes knowledge candidates, memory records, controlled proposals, and disabled skill candidates; `EvolutionMaterialize` now also writes a promotion lifecycle manifest that keeps gate evidence, effect metrics, and rollback refs attached before any enablement. Automatic policy apply, skill enablement, target repo sync, push, and merge remain disabled.
- `Governance Hub Reuse And Controlled Evolution Queue / GAP-130` is complete as the scope rebaseline, `GAP-131` is complete as the capability portfolio classifier baseline, `GAP-132` is complete as the control-pack execution contract baseline, `GAP-133` is complete as the inheritance override baseline, `GAP-134` is complete as the target-repo reuse effect feedback baseline, `GAP-135` is complete as the knowledge-memory lifecycle baseline, `GAP-136` is complete as the promotion lifecycle baseline, `GAP-137` is complete as the repo-map context artifact baseline, `GAP-138` is complete as the policy/tool/credential audit boundary baseline, `GAP-139` is complete as the governance hub certification baseline, `GAP-140` is complete as the bounded host-capability defer baseline, `GAP-141` is complete as the historical problem-trace closure policy baseline, `GAP-142` is complete as the degraded fresh-evidence next-work guard, and `GAP-143` is complete as the evidence recovery posture contract. Their completion standard requires real target-repo effect feedback, not only plan files, and does not authorize automatic host replacement, policy mutation, skill enablement, push, or merge. Self-evolution must evaluate the existing capability portfolio too: add, keep, improve, merge, deprecate, retire, or delete only rollbackable candidates based on evidence.
- New LTP implementation queue items beyond this bounded host-support queue must use later ids and must pass the autonomous or owner-directed promotion scope fence.
- Active verification for this repo remains `build -> test -> contract/invariant -> doctor`, with docs and script checks still included in `verify-repo -Check All`.
- `docs/change-evidence/` remains historical evidence and planning trace, not the primary user-facing product surface.

## Project Entry
- [Root README](../README.md)
- [中文 README](../README.zh-CN.md)
- [English README](../README.en.md)
- [Project AGENTS](../AGENTS.md)

## Main Entrypoints
- Repository-root shortcut: `run.ps1`
  - source of truth: delegates to `scripts/operator.ps1`
  - typical uses: `.\run.ps1`, `.\run.ps1 readiness -OpenUi`, `.\run.ps1 ui`, `.\run.ps1 daily -Mode quick`, `.\run.ps1 rules-check`, `.\run.ps1 feedback`
  - purpose: first-use and daily-use convenience so operators do not need to remember long PowerShell invocations
- Operator aggregate entrypoint: `scripts/operator.ps1`
  - source of truth: existing runtime, rule-sync, target-flow, and operator UI scripts
  - typical uses: `-Action Help`, `-Action Readiness`, `-Action RulesDryRun`, `-Action DailyAll`, `-Action OperatorUi -OpenUi`
  - UI default language: `zh-CN`; use `-UiLanguage en` for English
  - UI purpose: localhost interactive control console for allowlisted operator actions, runtime summary, maintenance policy refs, attachment posture, task/run evidence refs, evidence file preview, and local Codex/Claude config status
- Core-principle change candidate entrypoint: `scripts/operator.ps1 -Action CorePrincipleMaterialize`
  - default behavior is dry-run reporting only
  - after explicit permission, add `-ConfirmCorePrincipleProposalWrite` to write reviewable proposal/manifest files under `docs/change-evidence/core-principle-change-*`
  - for audit-only persistence, add `-WriteCorePrincipleDryRunReport` to write only a dry-run report under `docs/change-evidence/core-principle-change-reports/`
  - does not directly change active core-principles policy, specs, verifiers, target repositories, push, or merge
- Codex local optimizer: `scripts/Optimize-CodexLocal.ps1`
  - default mode is dry-run; use `-Apply` to write the current recommended user-level Codex config and install `codex-account`
  - the stable policy is still `efficiency first`; the current default combo is only the present implementation under that rule
  - account switching preserves user-owned ChatGPT auth files and never prints tokens
  - usage limits are surfaced as `unknown` unless a stable official local source is available
- Claude Code local optimizer: `scripts/Optimize-ClaudeLocal.ps1`
  - default mode is dry-run; use `-Apply` to write recommended user-level Claude Code settings for third-party Anthropic-compatible providers and install `claude-provider`
  - provider profiles include BigModel GLM and DeepSeek without storing API keys in the repository
  - provider switching fails closed when the required credential env is missing
- Target-repo daily/batch entrypoint: `scripts/runtime-flow-preset.ps1`
  - source of truth: `docs/targets/target-repos-catalog.json`
  - typical uses: `-ListTargets`, `-Target <id> -FlowMode daily`, `-AllTargets -ApplyGovernanceBaselineOnly`, `-AllTargets -ApplyAllFeatures`
- Agent-rule sync entrypoint: `scripts/sync-agent-rules.ps1`
  - source of truth: `rules/manifest.json`
  - typical uses: `-Scope All -FailOnChange` for drift check, `-Scope All -Apply` for one-command sync
- Self-repo verification entrypoint: `scripts/verify-repo.ps1 -Check All`
  - validates runtime code, docs, schemas, catalog, scripts, and target-repo consistency gates

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
.\run.ps1 readiness -OpenUi
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File ../scripts/verify-repo.ps1 -Check All
```

From the repository root, install the repo-local hooks before running full verification:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/install-repo-hooks.ps1
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
.\run.ps1
```

```powershell
.\run.ps1 ui
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action Help
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action OperatorUi -OpenUi
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator-ui-service.ps1 -Action Status
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action OperatorUi -OpenUi -UiLanguage en
```

```powershell
python scripts/serve-operator-ui.py
```

```powershell
python scripts/serve-operator-ui.py --serve --open
```

The interactive UI supports all-target or single-target execution, dry-run, browser-local execution history, and bounded repo-local evidence/artifact/verification file preview.

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
- [Codex / Claude Host Feedback Loop](./product/host-feedback-loop.md)
- [Codex / Claude 功能反馈闭环](./product/host-feedback-loop.zh-CN.md)
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
- [Optimized Hybrid Final-State Long-Term Roadmap](./roadmap/optimized-hybrid-final-state-long-term-roadmap.md)
- [Optimized Hybrid Final-State Long-Term Implementation Plan](./plans/optimized-hybrid-final-state-long-term-implementation-plan.md)
- [Claude Code First-Class Entrypoint Plan](./plans/claude-code-first-class-entrypoint-plan.md)
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
