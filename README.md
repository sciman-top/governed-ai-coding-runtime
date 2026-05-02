# Governed AI Coding Runtime

## Language / 语言
- 中文说明: [README.zh-CN.md](README.zh-CN.md)
- English guide: [README.en.md](README.en.md)
- Documentation index / 文档索引: [docs/README.md](docs/README.md)

## Fastest Path / 最短使用路径
如果只想知道“现在该执行什么”，先从根目录短入口开始：

```powershell
.\run.ps1
```

AI 推荐的日常入口：

```powershell
.\run.ps1 fast
```

AI 推荐的交付前 readiness：

```powershell
.\run.ps1 readiness -OpenUi
```

`fast` 执行 `build + quick feedback tests`，用于日常编码快速反馈；`readiness` 会按本仓硬门禁顺序执行 `build -> test -> contract/invariant -> hotspot`，然后打开默认中文 operator UI。`run.ps1` 只是便捷层，真实实现仍在 `scripts/operator.ps1`；需要完整动作说明时运行：

```powershell
.\run.ps1 operator-help
```

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

当前完整混合终态认证口径：
- `GAP-104..111` 已在当前分支基线上完成，完整混合终态闭环由 `docs/change-evidence/20260427-gap-111-complete-hybrid-final-state-certification.md` 记录。
- 认证含义是：repo-local contract bundle、machine-local durable governance kernel、attach-first host adapters、same-contract verification/delivery plane 已由当前仓库的 runtime、docs、tests、all-target workload 和 evidence gate 共同证明。
- 这不表示本项目接管上游宿主 UI；上游认证仍保持 user-owned，`native_attach` 仍按宿主能力显式降级到 `process_bridge` / `manual_handoff`。
- 不宣称所有未来外部仓、所有未来高风险流程都已被无条件接管；新增 LTP implementation queue 必须使用 `GAP-111` 之后的新 id，并由 scope fence 重新选择。
- `LTP-01..06` 仍是触发式候选：当前 certification 将部分能力用 transition-stack 方式落地或覆盖，但未引入 Temporal/OPA/event bus/object store/full ops/signing 等重型包。

当前受控演进口径：
- `GAP-120..129` 已把 30 天自我演进 review、AI 编码经验沉淀、低风险 proposal/disabled skill materialization 纳入受控流程；但仍不自动改 policy、不自动启用 skill、不自动同步目标仓、不自动 push/merge。
- `GAP-130` 已完成范围重基线，`GAP-131` 已完成可机器校验的 capability portfolio classifier 基线，`GAP-132` 已完成 executable control-pack contract 基线，`GAP-133` 已完成 inheritance override verifier 基线，`GAP-134` 已完成 target-repo reuse effect feedback 基线，`GAP-135` 已完成 governed knowledge-memory lifecycle 基线，`GAP-136` 已完成 promotion lifecycle 基线，`GAP-137` 已完成 repo-map context artifact 基线，`GAP-138` 已完成 policy tool credential audit boundary 基线，`GAP-139` 已完成 governance hub certification with effect metrics 基线，`GAP-140` 已完成 bounded host-capability defer 基线，`GAP-141` 已完成 historical problem-trace closure policy 基线，`GAP-142` 已完成 degraded fresh-evidence next-work guard 基线，`GAP-143` 已完成 evidence recovery posture contract 基线。Codex 和 Claude Code 作为日常合作宿主，不与其竞争；本项目里的 Claude Code 默认按本机接入 GLM/DeepSeek 等第三方 Anthropic-compatible provider 处理，不假定官方订阅或官方账号权益；Hermes/OpenHands/SWE-agent/Letta/Mem0/Aider 等作为可选择吸收的机制来源。完成标准必须包含真实 target-repo effect feedback，而不只是新增文档或候选文件。自我演进必须评估现有功能组合，能按证据执行 `add/keep/improve/merge/deprecate/retire/delete_candidate`，而不是只会新增；fresh target-run evidence 如果仍是 degraded/process_bridge，下一步必须先刷新或修复证据 posture。
- 最佳工程终态已固化为 `Governance Hub + Reusable Contract + Controlled Evolution loop + outer AI intelligent review/generation capability`，即治理中枢、可复用控制契约、受控演进闭环和外层 AI 智能评审/生成能力，而不是新的宿主产品。
- 核心原则已收敛为 5 条人类可读口径，机器细则仍以 `docs/architecture/core-principles-policy.json` 的 enforced principles 为准：
  - `Efficiency first, safety bounded`：综合效率优先，安全边界约束；少打扰、自动连续执行、节省 token / 成本、保留必要解释、高效率；模型、provider、推理档位、context window、compact 阈值和交互入口只是阶段性实现；效率优化不得绕过既有安全、证据、回滚、review 和门禁约束。
  - `Automation-first, outer-AI-assisted, gate-controlled evolution`：确定性治理工作应自动化；外层 AI 可自动生成 review、知识、候选和建议，但有效变更必须先成为结构化候选并通过风险分级、机器门禁、证据、回滚和必要 review。
  - `Governance hub, reusable contract, host-compatible execution`：本项目是治理中枢和可复用契约，不竞争或替代 Codex / Claude Code 等宿主；外部 agent 项目只作为机制来源。
  - `Context budget, instruction minimalism, least privilege`：`context_budget_and_instruction_minimalism` 与 `least_privilege_tool_credential_boundary` 是同一执行边界；根规则保持短而硬，工具输出必须保持高信号、可裁剪、可复用；工具权限、凭据、sandbox、mount、network、provider secret 和 MCP/tool identity 必须可审计并尽量由确定性控制执行。
  - `Measured effect over claims`：`measured_effect_feedback_over_claims` 要求完成声明必须有 fresh target-run evidence、eval trace、trace/replay/trajectory refs、effect feedback、verification command 与 rollback；文档、代码存在或候选文件本身不等于完成。

现在能否用于其他项目？
- 可以，**但边界是“治理 sidecar / attach-first metadata + runtime-managed gate/write flows + explicit degrade semantics”**。
- 对 `..\ClassroomToolkit` 这类仓库，已经可以生成或校验 `.governed-ai`、挂到 machine-local runtime state、跑 status/doctor、执行 gate 流、执行受治理写流并保留证据链。
- 仍不能宣称“Codex CLI 在所有外部仓、所有环境下已经被本项目完整接管用于真实高风险编码写入”。

当前总入口与一键应用：
- 根目录短入口：`run.ps1`。它把常用动作压成场景化短命令，例如 `.\run.ps1 fast`、`.\run.ps1 readiness -OpenUi`、`.\run.ps1 daily -Mode quick`、`.\run.ps1 rules-check`、`.\run.ps1 feedback`；底层仍转交 `scripts/operator.ps1`。
- 操作者聚合入口：`scripts/operator.ps1`。它把 readiness、自检、规则漂移/同步、目标仓批量流和 operator UI 生成收成同一个入口；默认 `-Action Help`，适合日常少记长命令。
- 宿主反馈汇总入口：`scripts/operator.ps1 -Action FeedbackReport`。它统一汇总 `Codex/Claude` 本机状态、规则同步面、parity 文档面和最新 target-run evidence。
- Codex 本机优化入口：`scripts/Optimize-CodexLocal.ps1`。默认 dry-run；加 `-Apply` 后会备份并写入本项目当前推荐的 Codex 单默认配置。长期优先级是“综合效率优先，安全边界约束”：少打扰、自动连续执行、节省 token / 成本、保留必要解释、高效率；当前暂行实现是 `cli_auth_credentials_store = "file"`、`model = "gpt-5.4"`、`model_reasoning_effort = "medium"`、`approval_policy = "never"`、`model_context_window = 272000`、`model_auto_compact_token_limit = 220000`。以后如果模型、参数或技术栈更迭，应先保持这个原则；既有安全、门禁、证据和回滚约束仍照常生效。脚本同时会安装 `codex-account` 账号切换入口，并把当前仓加入 trusted project。
- Claude Code 本机优化入口：`scripts/Optimize-ClaudeLocal.ps1`。默认 dry-run；加 `-Apply` 后会备份并写入第三方 Anthropic-compatible provider 推荐配置、安装 `claude-provider` 切换入口；密钥只保留在用户本机 settings/env，不写入仓库 profile。
- 核心原则变更候选入口：`scripts/operator.ps1 -Action CorePrincipleMaterialize`。默认只 dry-run 报告候选；得到明确允许后加 `-ConfirmCorePrincipleProposalWrite` 才写 reviewable proposal/manifest；如只需审计留痕，加 `-WriteCorePrincipleDryRunReport` 只写 dry-run report。以上路径仍不直接改 active core-principles policy、spec、verifier 或目标仓。
- 目标仓日常运行/批量下发总入口：`scripts/runtime-flow-preset.ps1`。它读取 `docs/targets/target-repos-catalog.json`，可以对单个 target 或所有 active targets 执行 attach、daily gate、治理基线同步、特性基线同步和里程碑提交。
- AI 规则文件同步入口：`scripts/sync-agent-rules.ps1`。它读取 `rules/manifest.json`，把全局与项目级 `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` 同步到用户目录和目标仓；默认同 hash 跳过，内容漂移按脚本策略阻断或要求 `-Force`。
- 本仓自检入口：`scripts/verify-repo.ps1 -Check All`。它用于验证当前 runtime、文档、schema、catalog、脚本和目标仓一致性门禁。

常用一键命令：

```powershell
.\run.ps1
```

```powershell
.\run.ps1 readiness -OpenUi
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action Help
```

AI 推荐的本仓日常 readiness：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action Readiness
```

一键生成 `Codex/Claude` 功能反馈汇总：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action FeedbackReport
```

打开本地交互 operator UI（默认中文，会启动 localhost 服务）：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action OperatorUi -OpenUi
```

打开英文版交互 UI：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action OperatorUi -OpenUi -UiLanguage en
```

UI 使用方式：`-OpenUi` 会启动 `127.0.0.1` 本地常驻交互控制台并打开浏览器；后续可直接访问 `http://127.0.0.1:8770/?lang=zh-CN`。状态/停止/重启使用 `scripts/operator-ui-service.ps1 -Action Status|Stop|Restart`；登录自动启动可用 `-Action EnableAutoStart|DisableAutoStart|AutoStartStatus` 管理。页面可执行 allowlist 内的本仓 readiness、目标仓列表、规则漂移检查、规则同步、治理基线下发、daily、全部功能应用（含退役托管文件清理检测）、一键清理退役治理文件和一键卸载治理；可选择全部目标仓、单个目标仓或勾选多个目标仓进行批量卸载，可调整语言、验证模式、并发、fail-fast、只预演、真实删除开关与里程碑标签；执行结果会写入输出区和本地浏览器执行历史；可点击 evidence/artifact/verification refs 查看文件内容。若不加 `-OpenUi`，脚本只生成只读快照 `.runtime/artifacts/operator-ui/index.html` 并在 JSON 输出里给出 `file_url`。
Codex 面板会显示本机 ChatGPT auth profiles、当前登录状态、推荐配置健康、官方 usage dashboard 入口和账号切换按钮；同时会把“综合效率优先，安全边界约束”作为长期核心原则单独展示，明确目标是少打扰、自动连续执行、节省 token / 成本、保留必要解释、高效率，且既有安全、最小权限、门禁、证据和回滚约束仍照常生效，再把 `gpt-5.4 + medium + never` 标为当前暂行实现，并把 `model_auto_compact_token_limit = 220000` 标为配套压缩阈值。以后如有新模型/新参数/新技术栈进入默认方案，也应优先保持这个原则，而不是固化当前组合。5h/7d 额度在缺少稳定官方本地 API 时标为 `unknown`，不伪造估算值。Claude 面板会集中展示第三方 provider 状态，并提供 provider 切换、推荐配置预演/应用，以及 `settings.json`、`provider-profiles.json`、切换脚本的本机预览入口。

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/Optimize-CodexLocal.ps1
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/Optimize-CodexLocal.ps1 -Apply
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -ListTargets
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 `
  -AllTargets `
  -ApplyGovernanceBaselineOnly `
  -Json
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 `
  -AllTargets `
  -ApplyAllFeatures `
  -FlowMode "daily" `
  -MilestoneTag "milestone" `
  -Json
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -Apply
```

如何快速使用（推荐三条路径）：
- 路径 A（治理侧车，阻力最低）：继续在 Codex/Claude Code 编码，同时运行 `bootstrap + doctor + verify-repo -Check All + status` 做 readiness、门禁和证据检查。
- 路径 B（外部仓 attach-first，推荐）：先 `attach-target-repo`，再运行 `runtime-flow.ps1 -FlowMode daily`，让目标仓按统一治理链执行。
- 路径 C（中高风险写入）：通过 `govern-attachment-write -> decide-attachment-write -> execute-attachment-write` 走审批与回滚引用闭环。

对 AI 编码的具体辅助作用：
- 会话前能力探测：在执行前显示 adapter tier、flow kind、degrade reason，减少“以为可执行、实际降级”的误判。
- 统一验收链：把 `build -> test -> contract/invariant -> hotspot` 固化到 runtime-managed gate 流，降低“只跑了部分检查”的漏检风险。
- 规则与提示词稳定下发：把全局/项目级 agent 规则作为 manifest 管理，减少 Codex、Claude、Gemini 在不同仓里读到不一致规则的概率。
- 目标仓防反复问题：把 PowerShell 环境、统一入口、低 token 交互、里程碑提交、fast/full gate 等策略同步进目标仓 profile 和受管文件，不靠聊天提醒。
- 高风险写入拦截：对 medium/high 请求触发审批或 fail-closed，避免无审批直写。
- 证据与交付留痕：每次治理执行可关联 approval/evidence/handoff/replay refs，便于交接、审计和回滚。
- 多仓复用：通过 `.governed-ai` light-pack 和 preset flow，在不同仓库复用同一治理协议。
- 与宿主解耦演进：保持 user-owned 上游认证，不锁死在单一宿主或单一接入方式。

最常用命令：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/bootstrap-runtime.ps1
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/install-repo-hooks.ps1
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
- [Codex / Claude Host Feedback Loop](docs/product/host-feedback-loop.md)
- [Codex / Claude 功能反馈闭环](docs/product/host-feedback-loop.zh-CN.md)
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

Current complete hybrid final-state certification posture:
- `GAP-104..111` are complete on the current branch baseline; the certification evidence is `docs/change-evidence/20260427-gap-111-complete-hybrid-final-state-certification.md`.
- Certification means the repo-local contract bundle, machine-local durable governance kernel, attach-first host adapters, and same-contract verification/delivery plane are backed by current runtime code, docs, tests, all-target workload evidence, and claim-drift gates.
- It does not mean this project takes over upstream host UI ownership. Upstream authentication remains user-owned, and `native_attach` still degrades explicitly to `process_bridge` / `manual_handoff` when host capability is absent.
- It does not claim unconditional takeover of every future external repo or every future high-risk workflow. New LTP implementation queues must use ids beyond `GAP-111` and pass a scope fence.
- `LTP-01..06` remain trigger-based candidates: this certification lands or covers the required transition-stack capabilities without introducing Temporal, OPA, event bus, object store, full operations stack, or external signing as mandatory packages.

Current controlled-evolution posture:
- `GAP-120..129` put 30-day evolution review, AI coding experience capture, and low-risk proposal/disabled-skill materialization under governance. They still do not auto-apply policy, auto-enable skills, sync target repos, push, or merge.
- `GAP-130` is complete as the scope rebaseline, `GAP-131` is complete as the machine-checkable capability portfolio classifier baseline, `GAP-132` is complete as the executable control-pack contract baseline, `GAP-133` is complete as the inheritance override verifier baseline, `GAP-134` is complete as the target-repo reuse effect feedback baseline, `GAP-135` is complete as the governed knowledge-memory lifecycle baseline, `GAP-136` is complete as the promotion lifecycle baseline, `GAP-137` is complete as the repo-map context artifact baseline, `GAP-138` is complete as the policy tool credential audit boundary baseline, `GAP-139` is complete as the governance hub certification with effect metrics baseline, `GAP-140` is complete as the bounded host-capability defer baseline, `GAP-141` is complete as the historical problem-trace closure policy baseline, `GAP-142` is complete as the degraded fresh-evidence next-work guard baseline, and `GAP-143` is complete as the evidence recovery posture contract baseline. Codex and Claude Code are cooperation hosts, not competitors; Claude Code is treated as local use through third-party Anthropic-compatible providers such as GLM or DeepSeek, not as an official subscription dependency; Hermes/OpenHands/SWE-agent/Letta/Mem0/Aider-style projects are selective mechanism sources. Completion requires real target-repo effect feedback, not only new docs or generated candidates. Self-evolution must evaluate the existing capability portfolio and decide `add/keep/improve/merge/deprecate/retire/delete_candidate` from evidence instead of only adding features; fresh target-run evidence that remains degraded/process_bridge must first refresh or repair evidence posture.

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

Current main entrypoints and one-command apply:
- Operator aggregate entrypoint: `scripts/operator.ps1`. It collects readiness checks, rule drift/sync, target-repo batch flows, and operator UI rendering behind one action-oriented entrypoint; default `-Action Help`.
- Target-repo daily/batch entrypoint: `scripts/runtime-flow-preset.ps1`. It reads `docs/targets/target-repos-catalog.json` and can run attach, daily gates, governance baseline sync, feature baseline sync, and milestone commits for one target or all active targets.
- Agent-rule sync entrypoint: `scripts/sync-agent-rules.ps1`. It reads `rules/manifest.json` and syncs global/project `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` files to user directories and target repos.
- Self-repo verification entrypoint: `scripts/verify-repo.ps1 -Check All`.

Common one-command flows:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action Help
```

AI recommended local readiness:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action Readiness
```

Open the interactive local operator UI. It defaults to Chinese and starts a localhost service:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action OperatorUi -OpenUi
```

Open the English interactive UI:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action OperatorUi -OpenUi -UiLanguage en
```

How to use the UI: `-OpenUi` starts a persistent local `127.0.0.1` interactive control console and opens the browser; later visits can use `http://127.0.0.1:8770/?lang=en` directly. Use `scripts/operator-ui-service.ps1 -Action Status|Stop|Restart` to inspect or control the service, and `-Action EnableAutoStart|DisableAutoStart|AutoStartStatus` to manage logon autostart. The page can run allowlisted actions for repo readiness, target listing, rule drift checks, rule sync, governance baseline rollout, daily, all-feature apply with retired managed-file cleanup detection, one-click retired-file cleanup, and one-click governance uninstall. It can target all repos, one selected target repo, or multiple checked target repos for batch uninstall, exposes settings for language, mode, parallelism, fail-fast, dry-run, managed-removal apply, and milestone tag, records results in the output panel and local browser history, and refs can be clicked to preview evidence/artifact/verification files. Without `-OpenUi`, the script only writes a read-only `.runtime/artifacts/operator-ui/index.html` snapshot and prints a JSON `file_url`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -ListTargets
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 `
  -AllTargets `
  -ApplyGovernanceBaselineOnly `
  -Json
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 `
  -AllTargets `
  -ApplyAllFeatures `
  -FlowMode "daily" `
  -MilestoneTag "milestone" `
  -Json
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -Apply
```

Canonical entrypoint recommendation:
- if you want one-command daily use or batch apply to target repos, prefer `runtime-flow-preset.ps1`
- if you are working with one temporary external repo that is not in the target catalog, use `runtime-flow.ps1`
- if you want to observe drift first, set `required_entrypoint_policy.current_mode` to `advisory`
- if you want to block direct gate/write entrypoints but keep read-only inspection open, set it to `targeted_enforced`
- if you want repo-wide canonical-entrypoint enforcement, set it to `repo_wide_enforced`
- operator-facing copy/paste examples: [Use With An Existing Repo](docs/quickstart/use-with-existing-repo.md) / [在现有仓库中使用](docs/quickstart/use-with-existing-repo.zh-CN.md)

Concrete assistance for AI coding:
- pre-execution capability visibility (tier/flow/degrade) to avoid hidden posture mismatch
- canonical gate chain execution to reduce partial-check drift
- manifest-backed agent rule distribution across Codex, Claude, and Gemini contexts
- target-repo prevention for repeated Windows process environment, canonical-entrypoint, low-token interaction, milestone commit, and fast/full gate drift
- policy and approval enforcement for risky writes
- evidence/handoff/replay linkage for traceable delivery and rollback
- reusable multi-repo governance via light packs and preset flows
- host-decoupled governance layer without replacing upstream auth ownership

