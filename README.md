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
- 运行第一个只读 trial 脚本
- 运行一个 safe-mode 的 Codex adapter smoke trial，并输出 task/binding/evidence/verification wiring
- 运行一个基于 repo-profile 的 multi-repo trial runner，并输出每个 repo 的 posture、adapter tier、verification/evidence refs 和 follow-ups
- 把外部仓库（例如 `D:\OneDrive\CODE\ClassroomToolkit`）attach 到本运行时，生成 `.governed-ai/` 轻量接入包，并通过 status/doctor/session-bridge 查看 posture
- 运行 CLI-first runtime smoke path：创建任务、执行本地 worker、跑 `build -> test -> contract -> doctor`、写 evidence/handoff/replay、查询 runtime status
- 在 Python 中复用 `packages/contracts` 下的任务、repo profile、审批、执行运行时、artifact/replay、验证、handoff、eval/trace 等契约原语

当前仍在实现中的终态能力：
- 外部目标仓中的真实高风险写入仍未接成完整 runtime-owned Codex 执行链
- direct Codex adapter 目前是 honest smoke-trial / posture / evidence wiring，不是完整生产级写入控制面
- attach-first 已有 contract 与本地 entrypoint，但还不是“替代上游宿主 UI”的最终交互体验
- `GAP-045..060` 是直达完整混合终态的主线且已完成；`GAP-061..068` 是 `GAP-060` 之后的治理优化 follow-on lane，现也已完成（2026-04-20），且不回写成终态闭环证明的一部分

现在能否用于其他项目？
- 可以，**但边界是“治理 sidecar / attach-first metadata + posture + gate planning + trial surfaces”**。
- 对 `D:\OneDrive\CODE\ClassroomToolkit` 这类仓库，已经可以生成或校验 `.governed-ai`、挂到 machine-local runtime state、跑 status/doctor、请求 gate plan、做 Codex smoke trial。
- 还不能宣称“Codex CLI 在外部仓里已经被本项目完整接管，用于真实高风险编码写入”。

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
  -AttachmentRoot "D:\OneDrive\CODE\ClassroomToolkit" `
  -AttachmentRuntimeStateRoot "D:\OneDrive\CODE\governed-ai-coding-runtime\.runtime\attachments\classroomtoolkit" `
  -Mode "quick"
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow.ps1 `
  -FlowMode "daily" `
  -AttachmentRoot "D:\OneDrive\CODE\ClassroomToolkit" `
  -AttachmentRuntimeStateRoot "D:\OneDrive\CODE\governed-ai-coding-runtime\.runtime\attachments\classroomtoolkit" `
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
- The first read-only scripted trial
- External target-repo attachment for repos such as `D:\OneDrive\CODE\ClassroomToolkit`
- A CLI-first governed runtime smoke path with persisted evidence, handoff, replay, and runtime status
- Python contract primitives under `packages/contracts`

Still in progress as the true end-state:
- production-grade real-write Codex ownership for external repos
- fuller attach-first user experience beyond the current local bridge and trial surfaces
- `GAP-045..060` is the direct path to full hybrid final-state closure and is complete; `GAP-061..068` is the governance-only follow-on lane after `GAP-060` and is also complete (2026-04-20), without being back-written into the final-state closure proof itself

Primary docs:
- [Single-Machine Runtime Quickstart](docs/quickstart/single-machine-runtime-quickstart.md)
- [单机 Runtime 快速开始](docs/quickstart/single-machine-runtime-quickstart.zh-CN.md)
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
