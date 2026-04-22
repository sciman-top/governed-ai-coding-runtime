# Governed AI Coding Runtime

## Language / 语言
- 中文说明: [README.zh-CN.md](README.zh-CN.md)
- English guide: [README.en.md](README.en.md)
- Documentation index / 文档索引: [docs/README.md](docs/README.md)

## 中文快速结论
本项目已经完成 `Foundation / GAP-020` 到 `GAP-023`、`Full Runtime / GAP-024` 到 `GAP-028`、`Public Usable Release / GAP-029` 到 `GAP-032`、`Maintenance Baseline / GAP-033` 到 `GAP-034`，以及 `Interactive Session Productization / GAP-035` 到 `GAP-039`。这表示“混合最终形态的第一版产品化边界”已经落地，但仍不等于“已经拥有完整 runtime-owned 的所有宿主真实执行能力”。

当前仓库的正确理解是：
- 已完成一个可运行、可验证、可留痕的本地治理运行时基线
- 已完成 repo-local light pack、session bridge、Codex smoke-trial、generic adapter tiers、multi-repo trial runner 这些产品化切片
- `Strategy Alignment Gates / GAP-040..044` 已在当前分支基线上完成，并作为 `GAP-035..039` 的已满足硬化依赖保留下来
- 终态目标是“通用、可迁移、交互式会话优先、attach-first”的 governed AI coding runtime

定位与非目标：
- 定位：AI coding agents 的治理/运行时层，而不是新的执行宿主
- 非目标：不做另一个宿主壳层、不做 wrapper-first 编排产品、不做 generation guardrail 产品
- 策略入口：[Positioning And Competitive Layering](docs/strategy/positioning-and-competitive-layering.md)
- 借鉴矩阵：[Runtime Governance Borrowing Matrix](docs/research/runtime-governance-borrowing-matrix.md)
- 边界 ADR：[ADR-0007 Source-Of-Truth And Runtime Contract Bundle](docs/adrs/0007-source-of-truth-and-runtime-contract-bundle.md)

当前可用能力：
- 运行仓库完整验证：文档、Schema、Catalog、脚本、runtime contract tests
- 运行本地 baseline 的 `build` 与 `doctor` 门禁
- 运行第一个只读 trial 脚本（read-only 基线）
- 运行 Codex capability live probe/readiness，并在 `status`/`doctor` 暴露 adapter tier、flow kind、degrade 原因与 remediation hint
- 通过 session bridge 运行 runtime-managed gate 执行（`run_quick_gate` / `run_full_gate`，支持 `plan_only`）
- 通过 session bridge 运行 attached write 治理闭环（`write_request` / `write_approve` / `write_execute` / `write_status`），并产出 approval/evidence/handoff/replay refs
- 运行 safe-mode Codex adapter smoke trial，并输出 task/binding/evidence/verification wiring
- 运行一个基于 repo-profile 的 multi-repo trial runner，并输出每个 repo 的 posture、adapter tier、verification/evidence refs 和 follow-ups
- 把外部仓库（例如 `..\ClassroomToolkit`）attach 到本运行时，生成 `.governed-ai/` 轻量接入包，并通过 status/doctor/session-bridge 查看 posture
- 运行 CLI-first runtime smoke path：创建任务、执行本地 worker、跑 `build -> test -> contract -> doctor`、写 evidence/handoff/replay、查询 runtime status
- 在 Python 中复用 `packages/contracts` 下的任务、repo profile、审批、执行运行时、artifact/replay、验证、handoff、eval/trace 等契约原语

当前仍在实现中的终态能力：
- 仍未实现“替代上游宿主 UI”的全托管 Codex 运行形态（上游认证保持 user-owned）
- `native_attach` 不是所有环境都可用，运行时会按能力面显式降级到 `process_bridge` / `manual_handoff`
- 不应宣称“所有外部仓、所有高风险流程都已被 runtime 全量接管”
- attach-first 已有 contract 与本地 entrypoint，但还不是“替代上游宿主 UI”的最终交互体验
- `GAP-045..060` 是直达完整混合终态的主线且已完成；`GAP-061..068` 是 `GAP-060` 之后的治理优化 follow-on lane，现也已完成（2026-04-20），且不回写成终态闭环证明的一部分

现在能否用于其他项目？
- 可以，**但边界是“治理 sidecar / attach-first metadata + runtime-managed gate/write flows + explicit degrade semantics”**。
- 对 `..\ClassroomToolkit` 这类仓库，已经可以生成或校验 `.governed-ai`、挂到 machine-local runtime state、跑 status/doctor、执行 gate 流、执行受治理写流并保留证据链。
- 仍不能宣称“Codex CLI 在所有外部仓、所有环境下已经被本项目完整接管用于真实高风险编码写入”。

如何快速使用（推荐三条路径）：
- 路径 A（治理侧车，阻力最低）：继续在 Codex/Claude Code 编码，同时运行 `bootstrap + doctor + verify-repo -Check All + status` 做 readiness、门禁和证据检查。
- 路径 B（外部仓 attach-first，推荐）：先 `attach-target-repo`，再运行 `runtime-flow.ps1 -FlowMode daily`，让目标仓按统一治理链执行。
- 路径 C（中高风险写入）：通过 `govern-attachment-write -> decide-attachment-write -> execute-attachment-write` 走审批与回滚引用闭环。

对 AI 编码的具体辅助作用：
- 会话前能力探测：在执行前显示 adapter tier、flow kind、degrade reason，减少“以为可执行、实际降级”的误判。
- 统一验收链：把 `build -> test -> contract/invariant -> hotspot` 固化到 runtime-managed gate 流，降低“只跑了部分检查”的漏检风险。
- 高风险写入拦截：对 medium/high 请求触发审批或 fail-closed，避免无审批直写。
- 证据与交付留痕：每次治理执行可关联 approval/evidence/handoff/replay refs，便于交接、审计和回滚。
- 多仓复用：通过 `.governed-ai` light-pack 和 preset flow，在不同仓库复用同一治理协议。
- 与宿主解耦演进：保持 user-owned 上游认证，不锁死在单一宿主或单一接入方式。

最常用命令：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/bootstrap-runtime.ps1
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
```

```powershell
python scripts/run-governed-task.py status --json
```

```powershell
python scripts/run-governed-task.py run --json
```

```powershell
python scripts/run-codex-adapter-trial.py --repo-id "python-service" --task-id "task-codex-trial" --binding-id "binding-python-service"
```

```powershell
python scripts/run-multi-repo-trial.py
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-check.ps1 `
  -AttachmentRoot "..\ClassroomToolkit" `
  -AttachmentRuntimeStateRoot ".runtime\attachments\classroomtoolkit" `
  -Mode "quick"
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow.ps1 `
  -FlowMode "daily" `
  -AttachmentRoot "..\ClassroomToolkit" `
  -AttachmentRuntimeStateRoot ".runtime\attachments\classroomtoolkit" `
  -Mode "quick"
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-classroomtoolkit.ps1 -FlowMode "daily"
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target "self-runtime" -FlowMode "daily" -SkipVerifyAttachment
```

快速上手文档：
- [Single-Machine Runtime Quickstart](docs/quickstart/single-machine-runtime-quickstart.md)
- [单机 Runtime 快速开始](docs/quickstart/single-machine-runtime-quickstart.zh-CN.md)
- [AI Coding Usage Guide](docs/quickstart/ai-coding-usage-guide.md)
- [AI 编码使用指南](docs/quickstart/ai-coding-usage-guide.zh-CN.md)
- [Use With An Existing Repo](docs/quickstart/use-with-existing-repo.md)
- [在现有仓库中使用](docs/quickstart/use-with-existing-repo.zh-CN.md)
- [Multi-Repo Trial Quickstart](docs/quickstart/multi-repo-trial-quickstart.md)
- [多仓试运行快速开始](docs/quickstart/multi-repo-trial-quickstart.zh-CN.md)
- [Codex CLI/App Integration Guide](docs/product/codex-cli-app-integration-guide.md)
- [Codex CLI/App 集成指南](docs/product/codex-cli-app-integration-guide.zh-CN.md)
- [Codex Direct Adapter](docs/product/codex-direct-adapter.md)
- [Multi-Repo Trial Loop](docs/product/multi-repo-trial-loop.md)
- [Positioning And Competitive Layering](docs/strategy/positioning-and-competitive-layering.md)
- [Generic Target-Repo Attachment Blueprint](docs/architecture/generic-target-repo-attachment-blueprint.md)
- [Repo-Native Contract Bundle](docs/architecture/repo-native-contract-bundle.md)
- [Hybrid Final-State Master Outline](docs/architecture/hybrid-final-state-master-outline.md)
- [Direct-To-Hybrid Final-State Roadmap](docs/roadmap/direct-to-hybrid-final-state-roadmap.md)
- [Direct-To-Hybrid Final-State Implementation Plan](docs/plans/direct-to-hybrid-final-state-implementation-plan.md)
- [Governance Optimization Lane Roadmap](docs/roadmap/governance-optimization-lane-roadmap.md)
- [Governance Optimization Lane Implementation Plan](docs/plans/governance-optimization-lane-implementation-plan.md)
- [Local Baseline To Hybrid Final-State Migration Matrix](docs/architecture/local-baseline-to-hybrid-final-state-migration-matrix.md)
- [Interactive Session Productization Implementation Plan](docs/plans/interactive-session-productization-implementation-plan.md)
- [Interactive Session Productization Plan](docs/plans/interactive-session-productization-plan.md)
- [Governance Runtime Strategy Alignment Plan](docs/plans/governance-runtime-strategy-alignment-plan.md)

## English Quick Answer
`Foundation / GAP-020` through `GAP-023`, `Full Runtime / GAP-024` through `GAP-028`, `Public Usable Release / GAP-029` through `GAP-032`, `Maintenance Baseline / GAP-033` through `GAP-034`, and `Interactive Session Productization / GAP-035` through `GAP-039` are complete. That means the first landed hybrid productization boundary is present. It does not mean every upstream host already has a full runtime-owned real-write execution path.

`Strategy Alignment Gates / GAP-040..044` are complete on the current branch baseline and remain encoded as satisfied dependencies around that landed slice.

Positioning and non-goals:
- governance/runtime layer for AI coding agents, not another execution host
- not a wrapper-first orchestration product
- not a generation-guardrail product
- strategy doc: [Positioning And Competitive Layering](docs/strategy/positioning-and-competitive-layering.md)
- borrowing matrix: [Runtime Governance Borrowing Matrix](docs/research/runtime-governance-borrowing-matrix.md)
- boundary ADR: [ADR-0007 Source-Of-Truth And Runtime Contract Bundle](docs/adrs/0007-source-of-truth-and-runtime-contract-bundle.md)

Available now:
- Full repository verification over docs, schemas, catalog, scripts, and runtime contract tests
- Local baseline `build` and `doctor` gates
- The first read-only scripted trial baseline
- Codex capability readiness surfaced in runtime status/doctor, including tier/flow/degrade metadata
- Runtime-managed gate execution through session bridge (`run_quick_gate` / `run_full_gate`, with optional `plan_only`)
- Runtime-managed attached write governance flow through session bridge (`write_request` / `write_approve` / `write_execute` / `write_status`) with approval/evidence/handoff/replay refs
- External target-repo attachment for repos such as `..\ClassroomToolkit`
- A CLI-first governed runtime smoke path with persisted evidence, handoff, replay, and runtime status
- Python contract primitives under `packages/contracts`

Still in progress as the true end-state:
- full runtime-owned replacement of upstream Codex host UX
- environment-independent native-attach availability across all host surfaces
- universal real-write takeover claims across all external repos and high-risk workflows
- fuller attach-first user experience beyond the current local bridge and trial surfaces
- `GAP-045..060` is the direct path to full hybrid final-state closure and is complete; `GAP-061..068` is the governance-only follow-on lane after `GAP-060` and is also complete (2026-04-20), without being back-written into the final-state closure proof itself

Primary docs:
- [Single-Machine Runtime Quickstart](docs/quickstart/single-machine-runtime-quickstart.md)
- [单机 Runtime 快速开始](docs/quickstart/single-machine-runtime-quickstart.zh-CN.md)
- [AI Coding Usage Guide](docs/quickstart/ai-coding-usage-guide.md)
- [AI 编码使用指南](docs/quickstart/ai-coding-usage-guide.zh-CN.md)
- [Codex CLI/App Integration Guide](docs/product/codex-cli-app-integration-guide.md)
- [Positioning And Competitive Layering](docs/strategy/positioning-and-competitive-layering.md)
- [Generic Target-Repo Attachment Blueprint](docs/architecture/generic-target-repo-attachment-blueprint.md)
- [Repo-Native Contract Bundle](docs/architecture/repo-native-contract-bundle.md)
- [Hybrid Final-State Master Outline](docs/architecture/hybrid-final-state-master-outline.md)
- [Direct-To-Hybrid Final-State Roadmap](docs/roadmap/direct-to-hybrid-final-state-roadmap.md)
- [Direct-To-Hybrid Final-State Implementation Plan](docs/plans/direct-to-hybrid-final-state-implementation-plan.md)
- [Governance Optimization Lane Roadmap](docs/roadmap/governance-optimization-lane-roadmap.md)
- [Governance Optimization Lane Implementation Plan](docs/plans/governance-optimization-lane-implementation-plan.md)
- [Local Baseline To Hybrid Final-State Migration Matrix](docs/architecture/local-baseline-to-hybrid-final-state-migration-matrix.md)
- [Interactive Session Productization Implementation Plan](docs/plans/interactive-session-productization-implementation-plan.md)
- [Interactive Session Productization Plan](docs/plans/interactive-session-productization-plan.md)
- [Governance Runtime Strategy Alignment Plan](docs/plans/governance-runtime-strategy-alignment-plan.md)

How to use quickly (recommended paths):
- Path A (governance sidecar, least friction): keep coding in your host tool and run `bootstrap + doctor + verify-repo -Check All + status`.
- Path B (attach-first for external repos): run `attach-target-repo` once, then use `runtime-flow.ps1 -FlowMode daily` as the daily governance chain.
- Path C (risky writes): run `govern-attachment-write -> decide-attachment-write -> execute-attachment-write` for medium/high-risk mutations.

Canonical entrypoint recommendation:
- if you want one-command daily use, prefer `runtime-flow.ps1` or `runtime-flow-preset.ps1`
- if you want to observe drift first, set `required_entrypoint_policy.current_mode` to `advisory`
- if you want to block direct gate/write entrypoints but keep read-only inspection open, set it to `targeted_enforced`
- if you want repo-wide canonical-entrypoint enforcement, set it to `repo_wide_enforced`
- operator-facing copy/paste examples: [Use With An Existing Repo](docs/quickstart/use-with-existing-repo.md) / [在现有仓库中使用](docs/quickstart/use-with-existing-repo.zh-CN.md)

Concrete assistance for AI coding:
- pre-execution capability visibility (tier/flow/degrade) to avoid hidden posture mismatch
- canonical gate chain execution to reduce partial-check drift
- policy and approval enforcement for risky writes
- evidence/handoff/replay linkage for traceable delivery and rollback
- reusable multi-repo governance via light packs and preset flows
- host-decoupled governance layer without replacing upstream auth ownership

