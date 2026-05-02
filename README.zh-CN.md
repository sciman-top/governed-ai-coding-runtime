# Governed AI Coding Runtime 中文使用说明

## 最短使用路径
如果只想知道“现在该执行什么”，先从根目录短入口开始：

```powershell
.\run.ps1
```

AI 推荐的日常入口：

```powershell
.\run.ps1 readiness -OpenUi
```

它会按本仓硬门禁顺序执行 `build -> test -> contract/invariant -> hotspot`，然后打开默认中文 operator UI。`run.ps1` 只是便捷层，真实实现仍在 `scripts/operator.ps1`；需要完整动作说明时运行：

```powershell
.\run.ps1 operator-help
```

## 当前状态
`Foundation / GAP-020` 到 `GAP-023`、`Full Runtime / GAP-024` 到 `GAP-028`、`Public Usable Release / GAP-029` 到 `GAP-032`、`Maintenance Baseline / GAP-033` 到 `GAP-034`、`Interactive Session Productization / GAP-035` 到 `GAP-039` 已完成。

这表示“混合最终形态的第一版产品化边界”已经落地，但不表示“所有上游宿主都已经接入完整 runtime-owned 真实执行能力”。

当前仓库现在应该理解为一个已经完成产品化第一版落地的本地 governed runtime；`Strategy Alignment Gates / GAP-040..044` 已在当前分支基线上完成，并作为这条产品化结果的硬化依赖保留下来。

定位与非目标：

- 定位：AI coding agents 的治理/运行时层，而不是新的执行宿主。
- 非目标：不做另一个宿主壳层，不做 wrapper-first 编排产品，也不做 generation guardrail 产品。
- 策略入口：[Positioning And Competitive Layering](docs/strategy/positioning-and-competitive-layering.md)
- 借鉴矩阵：[Runtime Governance Borrowing Matrix](docs/research/runtime-governance-borrowing-matrix.md)
- 边界 ADR：[ADR-0007 Source-Of-Truth And Runtime Contract Bundle](docs/adrs/0007-source-of-truth-and-runtime-contract-bundle.md)

本项目现在可以使用，但要按正确边界理解：

- 可以用作“治理运行时契约层”。
- 可以运行仓库验证和 runtime contract tests。
- 可以运行本地 build 与 doctor 门禁。
- 可以运行第一个只读 trial 脚本（read-only 基线）。
- 可以在 runtime status/doctor 中看到 Codex capability readiness（adapter tier、flow kind、degrade 原因、remediation hint）。
- 可以通过 session-bridge 执行 runtime-managed gate 流（`run_quick_gate` / `run_full_gate`，支持 `plan_only`）。
- 可以通过 session-bridge 执行 attached write 治理闭环（`write_request` / `write_approve` / `write_execute` / `write_status`），并保留 approval/evidence/handoff/replay refs。
- 可以运行一个 safe-mode 的 Codex adapter smoke trial，并检查 task / binding / evidence / verification 线路是否连通。
- 可以运行一个基于 repo-profile 的 multi-repo trial runner，并输出每个 repo 的 posture、adapter tier、verification/evidence refs 和 follow-ups。
- 可以把外部仓库（例如 `..\ClassroomToolkit`）attach 到本运行时，生成 `.governed-ai` 轻量接入包，并通过 status / doctor / session-bridge 使用这些能力。
- 可以运行 CLI-first governed runtime smoke task，得到本地 artifact、verification、evidence、handoff 与 runtime status。
- 可以直接查看 compatibility/upgrade/deprecation/retirement policy，并在 runtime status 与 operator UI 中看到维护状态。

完整混合终态认证口径：

- `GAP-104..111` 已在当前分支基线上完成；完整混合终态闭环由 `docs/change-evidence/20260427-gap-111-complete-hybrid-final-state-certification.md` 记录。
- 认证含义是 repo-local contract bundle、machine-local durable governance kernel、attach-first host adapters、same-contract verification/delivery plane 已由当前 runtime、docs、tests、all-target workload 和 evidence gate 共同证明。
- 这不表示本项目接管上游 Codex 宿主 UI；上游认证仍保持 user-owned，`native_attach` 仍会按宿主能力显式降级到 `process_bridge` / `manual_handoff`。
- 不宣称所有未来外部仓、所有未来高风险流程都已被无条件接管；新增 LTP implementation queue 必须使用 `GAP-111` 之后的新 id，并由 scope fence 重新选择。
- `LTP-01..06` 仍是触发式候选：当前 certification 将部分能力用 transition-stack 方式落地或覆盖，但未引入 Temporal/OPA/event bus/object store/full ops/signing 等重型包。

## 当前受控演进口径
`GAP-120..129` 已把 30 天自我演进 review、AI 编码经验沉淀、低风险 proposal/disabled skill materialization 纳入受控流程；但仍不自动改 policy、不自动启用 skill、不自动同步目标仓、不自动 push/merge。

`GAP-130` 已完成范围重基线，`GAP-131` 已完成可机器校验的 capability portfolio classifier 基线，`GAP-132` 已完成 executable control-pack contract 基线，`GAP-133` 已完成 inheritance override verifier 基线，`GAP-134` 已完成 target-repo reuse effect feedback 基线，`GAP-135` 已完成 governed knowledge-memory lifecycle 基线，`GAP-136` 已完成 promotion lifecycle 基线，`GAP-137` 已完成 repo-map context artifact 基线，`GAP-138` 已完成 policy tool credential audit boundary 基线，`GAP-139` 已完成 governance hub certification with effect metrics 基线，`GAP-140` 已完成 bounded host-capability defer 基线，`GAP-141` 已完成 historical problem-trace closure policy 基线，`GAP-142` 已完成 degraded fresh-evidence next-work guard 基线，`GAP-143` 已完成 evidence recovery posture contract 基线。Codex 和 Claude Code 作为日常合作宿主，不与其竞争；本项目里的 Claude Code 默认按本机接入 GLM/DeepSeek 等第三方 Anthropic-compatible provider 处理，不假定官方订阅或官方账号权益；Hermes/OpenHands/SWE-agent/Letta/Mem0/Aider 等作为可选择吸收的机制来源。完成标准必须包含真实 target-repo effect feedback，而不只是新增文档或候选文件。自我演进必须评估现有功能组合，能按证据执行 `add/keep/improve/merge/deprecate/retire/delete_candidate`，而不是只会新增；fresh target-run evidence 如果仍是 degraded/process_bridge，下一步必须先刷新或修复证据 posture。

最佳工程终态已固化为 `Governance Hub + Reusable Contract + Controlled Evolution loop + outer AI intelligent review/generation capability`，即治理中枢、可复用控制契约、受控演进闭环和外层 AI 智能评审/生成能力，而不是新的宿主产品。

核心原则已收敛为 5 条人类可读口径，机器细则仍以 `docs/architecture/core-principles-policy.json` 的 enforced principles 为准：

- `Efficiency first, safety bounded`：综合效率优先，安全边界约束；少打扰、自动连续执行、节省 token / 成本、保留必要解释、高效率；模型、provider、推理档位、context window、compact 阈值和交互入口只是阶段性实现；效率优化不得绕过既有安全、证据、回滚、review 和门禁约束。
- `Automation-first, outer-AI-assisted, gate-controlled evolution`：确定性治理工作应自动化；外层 AI 可自动生成 review、知识、候选和建议，但有效变更必须先成为结构化候选并通过风险分级、机器门禁、证据、回滚和必要 review。
- `Governance hub, reusable contract, host-compatible execution`：本项目是治理中枢和可复用契约，不竞争或替代 Codex / Claude Code 等宿主；外部 agent 项目只作为机制来源。
- `Context budget, instruction minimalism, least privilege`：`context_budget_and_instruction_minimalism` 与 `least_privilege_tool_credential_boundary` 是同一执行边界；根规则保持短而硬，工具输出必须保持高信号、可裁剪、可复用；工具权限、凭据、sandbox、mount、network、provider secret 和 MCP/tool identity 必须可审计并尽量由确定性控制执行。
- `Measured effect over claims`：`measured_effect_feedback_over_claims` 要求完成声明必须有 fresh target-run evidence、eval trace、trace/replay/trajectory refs、effect feedback、verification command 与 rollback；文档、代码存在或候选文件本身不等于完成。

## 现在能否用于其他项目
可以，但要按当前边界理解。

对 `..\ClassroomToolkit` 这类仓库，你现在已经可以：

- 生成或校验 `.governed-ai/repo-profile.json` 和 `.governed-ai/light-pack.json`
- 把 repo-local 声明绑定到 machine-local runtime state
- 用 `status` / `doctor` 看 attachment posture
- 用 `session-bridge` 执行 runtime-managed gate 流
- 用 `session-bridge` 执行受治理写流并保留 approval/evidence/handoff/replay 链路
- 用 Codex smoke-trial 与 multi-repo trial 验证 adapter / evidence / verification wiring

你现在还不能把它表述成：

- 不应声称本项目已经在所有环境下完全接管 Codex 宿主执行
- 所有外部仓和所有高风险流程都已统一实现 runtime-owned 全闭环

## 快速使用路径（推荐）
- 路径 A（治理侧车，阻力最低）：继续用 Codex/Claude Code 编码，同时运行 `bootstrap + doctor + verify-repo -Check All + status` 做 readiness 与门禁检查。
- 路径 B（外部仓 attach-first，推荐）：先 `attach-target-repo`，再跑 `runtime-flow.ps1 -FlowMode daily` 作为日常治理链。
- 路径 C（中高风险写入）：用 `govern-attachment-write -> decide-attachment-write -> execute-attachment-write` 走审批与回滚引用闭环。

## 当前总入口与一键应用
- 根目录短入口：`run.ps1`。它把常用动作压成场景化短命令，例如 `.\run.ps1 readiness -OpenUi`、`.\run.ps1 daily -Mode quick`、`.\run.ps1 rules-check`、`.\run.ps1 feedback`；底层仍转交 `scripts/operator.ps1`。
- 操作者聚合入口：`scripts/operator.ps1`。它把 readiness、自检、规则漂移/同步、目标仓批量流和 operator UI 生成收成同一个入口；默认 `-Action Help`。
- Codex 本机优化入口：`scripts/Optimize-CodexLocal.ps1`。默认 dry-run；加 `-Apply` 后会备份并写入本项目当前推荐的 Codex 单默认配置。长期优先级是“综合效率优先，安全边界约束”：少打扰、自动连续执行、节省 token / 成本、保留必要解释、高效率；当前暂行实现是 `cli_auth_credentials_store = "file"`、`model = "gpt-5.4"`、`model_reasoning_effort = "medium"`、`approval_policy = "never"`、`model_context_window = 272000`、`model_auto_compact_token_limit = 220000`。以后如果模型、参数或技术栈更迭，应先保持这个原则；既有安全、门禁、证据和回滚约束仍照常生效。脚本同时会安装 `codex-account` 账号切换入口，并把当前仓加入 trusted project。
- Claude Code 本机优化入口：`scripts/Optimize-ClaudeLocal.ps1`。默认 dry-run；加 `-Apply` 后会备份并写入第三方 Anthropic-compatible provider 推荐配置、安装 `claude-provider` 切换入口；密钥只保留在用户本机 settings/env，不写入仓库 profile。
- 核心原则变更候选入口：`scripts/operator.ps1 -Action CorePrincipleMaterialize`。默认只 dry-run 报告候选；得到明确允许后加 `-ConfirmCorePrincipleProposalWrite` 才写 reviewable proposal/manifest；如只需审计留痕，加 `-WriteCorePrincipleDryRunReport` 只写 dry-run report。以上路径仍不直接改 active core-principles policy、spec、verifier 或目标仓。
- 目标仓日常运行/批量下发总入口：`scripts/runtime-flow-preset.ps1`。它读取 `docs/targets/target-repos-catalog.json`，支持单 target 或所有 active targets。
- AI 规则文件同步入口：`scripts/sync-agent-rules.ps1`。它读取 `rules/manifest.json`，同步全局与项目级 `AGENTS.md` / `CLAUDE.md` / `GEMINI.md`。
- 本仓自检入口：`scripts/verify-repo.ps1 -Check All`。它验证 runtime、docs、schema、catalog、脚本和目标仓一致性门禁。

先看操作者入口和 AI 推荐路径：

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

打开本地交互 operator UI（默认中文，会启动 localhost 服务）：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action OperatorUi -OpenUi
```

打开英文版交互 UI：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action OperatorUi -OpenUi -UiLanguage en
```

UI 使用方式：`-OpenUi` 会启动 `127.0.0.1` 本地常驻交互控制台并打开浏览器；后续可直接访问 `http://127.0.0.1:8770/?lang=zh-CN`。状态/停止/重启使用 `scripts/operator-ui-service.ps1 -Action Status|Stop|Restart`；登录自动启动可用 `-Action EnableAutoStart|DisableAutoStart|AutoStartStatus` 管理。页面可执行 allowlist 内的本仓 readiness、目标仓列表、规则漂移检查、规则同步、治理基线下发、daily、全部功能应用、一键清理退役治理文件和一键卸载治理；可选择全部目标仓、单个目标仓或勾选多个目标仓进行批量卸载，可调整语言、验证模式、并发、fail-fast、只预演、真实删除开关与里程碑标签；执行结果会写入输出区和本地浏览器执行历史；可点击 evidence/artifact/verification refs 查看文件内容。`Codex` 页签展示本机账号、额度和配置健康，并把“综合效率优先”单独标成长期核心原则，明确目标是少打扰、自动连续执行、节省 token / 成本、保留必要解释、高效率；`gpt-5.4 + medium + never` 仅作为当前暂行实现展示，`model_auto_compact_token_limit = 220000` 仍作为配套压缩阈值。以后如有新模型/新参数/新技术栈进入默认方案，也应优先保持这个原则，而不是固化当前组合。`Claude` 页签集中展示第三方 provider 状态，并内置 provider 切换、推荐配置预演/应用，以及 `settings.json`、`provider-profiles.json`、切换脚本的本机预览入口。若不加 `-OpenUi`，脚本只生成只读快照 `.runtime/artifacts/operator-ui/index.html` 并在 JSON 输出里给出 `file_url`。

先查看当前可用 target：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -ListTargets
```

只同步目标仓治理基线（低噪音的一键应用）：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 `
  -AllTargets `
  -ApplyGovernanceBaselineOnly `
  -Json
```

一键执行全部当前目标仓功能（daily flow + 特性基线 + 里程碑提交）：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 `
  -AllTargets `
  -ApplyAllFeatures `
  -FlowMode "daily" `
  -MilestoneTag "milestone" `
  -Json
```

同步 Codex/Claude/Gemini 全局与项目规则：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -Apply
```

只检查规则漂移、不落盘：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -FailOnChange
```

## 统一入口建议
- 如果你要“一键日常使用”或“批量应用到目标仓”，优先走 `runtime-flow-preset.ps1`
- 如果你只操作一个临时外部仓、还不想写入 target catalog，可走 `runtime-flow.ps1`
- 如果你要先观察绕过统一入口的情况，把 `required_entrypoint_policy.current_mode` 设为 `advisory`
- 如果你要拦截 direct gate/write 入口、但保留只读状态查询，把它设为 `targeted_enforced`
- 如果你要在仓级范围强制 canonical entrypoint，把它设为 `repo_wide_enforced`
- 可直接复制的配置和命令见：
  - [Use With An Existing Repo](docs/quickstart/use-with-existing-repo.md)
  - [在现有仓库中使用](docs/quickstart/use-with-existing-repo.zh-CN.md)

## 对 AI 编码的具体辅助作用
- 会话前能力可见：在执行前就能看到 `adapter_tier`、`flow_kind`、`degrade_reason`，避免运行中才发现能力降级。
- 验收链统一执行：`build -> test -> contract/invariant -> hotspot` 由 runtime-managed gate 流统一执行，降低漏检。
- 规则稳定下发：用 `rules/manifest.json` 管理全局/项目级 agent 规则，减少 Codex、Claude、Gemini 在不同仓读到不同规则。
- 反复问题前置防护：把 Windows 进程环境、canonical entrypoint、low-token 交互、里程碑提交、fast/full gate 等策略同步到目标仓，而不是只靠聊天提醒。
- 高风险写入防护：medium/high 写入会触发审批或 fail-closed，避免无审批直写。
- 交付可追溯：approval/evidence/handoff/replay refs 与 task/run 绑定，方便审计、交接和回滚。
- 多仓复用：通过 `.governed-ai` light-pack 与 preset flow，把同一治理协议复用到多个目标仓。
- 与宿主解耦：保持 user-owned 上游认证，不把治理能力绑定到单一宿主实现。

## 你可以怎样使用

### 1. 验证仓库是否健康
在仓库根目录执行：

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

这个命令会执行：

- runtime contract tests
- JSON Schema 解析
- schema example validation
- schema catalog 配对检查
- active Markdown links 检查
- backlog / YAML ID drift 检查
- PowerShell 脚本解析检查

对应 quickstart：
- [Single-Machine Runtime Quickstart](docs/quickstart/single-machine-runtime-quickstart.md)
- [单机 Runtime 快速开始](docs/quickstart/single-machine-runtime-quickstart.zh-CN.md)
- [AI Coding Usage Guide](docs/quickstart/ai-coding-usage-guide.md)
- [AI 编码使用指南](docs/quickstart/ai-coding-usage-guide.zh-CN.md)

只运行 runtime contract tests：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
```

直接运行 Python unittest：

```powershell
python -m unittest discover -s tests/runtime -p "test_*.py" -v
```

### 2. 运行第一个只读 trial
当前 trial 是 scripted/read-only，不会调用真实 Codex，也不会写入目标仓库。

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

预期输出是 JSON，包含：

- `repo_id`
- `accepted_count`
- `summary`
- `auth_ownership`
- `unsupported_capability_behavior`

### 3. 运行 Codex adapter smoke trial
这个 trial 默认是 safe-mode，用于验证 direct adapter contract 的最小通路，不代表真实高风险写入已经接通。

```powershell
python scripts/run-codex-adapter-trial.py `
  --repo-id "python-service" `
  --task-id "task-codex-trial" `
  --binding-id "binding-python-service"
```

预期输出是 JSON，包含：

- `adapter_tier`
- `task_id`
- `binding_id`
- `evidence_refs`
- `verification_refs`
- `unsupported_capability_behavior`

### 4. 运行一个完整 governed task
这里的 `run-governed-task.py` 当前应理解为 runtime smoke path，不应理解为“已经直接调用 Codex 完成真实编码”的集成入口。

```powershell
python scripts/run-governed-task.py status --json
```

```powershell
python scripts/run-governed-task.py run --json
```

预期输出会包含：

- `task_id`
- `state`
- `active_run_id`
- `verification_refs`
- `evidence_refs`
- `artifact_refs`

### 5. 运行 multi-repo trial runner
这个 runner 默认使用仓库内置的两个 sample repo-profile，输出多仓 onboarding evidence 汇总。

```powershell
python scripts/run-multi-repo-trial.py
```

预期输出会按 repo 给出：

- `attachment_posture`
- `adapter_tier`
- `verification_refs`
- `evidence_refs`
- `handoff_refs`
- `follow_ups`

### 6. 在现有仓库中使用本项目
如果目标仓是 `..\ClassroomToolkit` 这类外部仓，推荐直接看：

- [Use With An Existing Repo](docs/quickstart/use-with-existing-repo.md)
- [在现有仓库中使用](docs/quickstart/use-with-existing-repo.zh-CN.md)
- [Target Repo Attachment Flow](docs/product/target-repo-attachment-flow.md)
- [Target Repo 接入流程](docs/product/target-repo-attachment-flow.zh-CN.md)

它已经包含实际可执行的 `ClassroomToolkit` attach 命令示例。

日常可以直接用一键检查命令：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-check.ps1 `
  -AttachmentRoot "..\ClassroomToolkit" `
  -AttachmentRuntimeStateRoot ".runtime\attachments\classroomtoolkit" `
  -Mode "quick"
```

双模式一键流（支持首次接入和日常检查）：

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
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target "skills-manager" -FlowMode "daily" -SkipVerifyAttachment
```

### 7. 使用 runtime contract primitives
当前核心代码在：

```text
packages/contracts/src/governed_ai_coding_runtime_contracts/
```

规划入口：
- [Hybrid Final-State Master Outline](docs/architecture/hybrid-final-state-master-outline.md)
- [Direct-To-Hybrid Final-State Roadmap](docs/roadmap/direct-to-hybrid-final-state-roadmap.md)
- [Direct-To-Hybrid Final-State Implementation Plan](docs/plans/direct-to-hybrid-final-state-implementation-plan.md)
- [Governance Optimization Lane Roadmap](docs/roadmap/governance-optimization-lane-roadmap.md)
- [Governance Optimization Lane Implementation Plan](docs/plans/governance-optimization-lane-implementation-plan.md)

主要模块：

- `task_intake.py`: 任务输入与生命周期 transition 校验
- `repo_profile.py`: repo profile 加载与 admission minimums
- `tool_runner.py`: 只读工具请求治理
- `workspace.py`: 隔离工作区分配与写路径校验
- `write_policy.py`: medium/high 写入策略默认值
- `approval.py`: approval request 状态与审计
- `write_tool_runner.py`: 写侧工具治理与 rollback reference
- `execution_runtime.py`: 任务到运行实例的本地执行编排
- `worker.py`: 同步单机 worker 接口
- `artifact_store.py`: 本地 artifact 持久化与风险分类
- `replay.py`: 失败签名与 replay 引用
- `verification_runner.py`: quick/full verification plan 与 artifact
- `delivery_handoff.py`: 交付 handoff package
- `eval_trace.py`: eval baseline 与 trace grading
- `second_repo_pilot.py`: 第二 repo profile reuse pilot
- `runtime_status.py`: CLI-first operator read model
- `control_console.py`: 最小 approval/evidence console facade

示例：

```powershell
$env:PYTHONPATH="packages/contracts/src"
python - <<'PY'
from governed_ai_coding_runtime_contracts.repo_profile import load_repo_profile
from governed_ai_coding_runtime_contracts.write_policy import resolve_write_policy

profile = load_repo_profile("schemas/examples/repo-profile/python-service.example.json")
policy = resolve_write_policy(profile)
print(profile.repo_id)
print(policy.approval_mode("high"))
PY
```

### 5. 阅读文档的推荐顺序
如果你只想知道怎么用：

1. [本文档](README.zh-CN.md)
2. [文档索引](docs/README.md)
3. [AI 编码使用指南](docs/quickstart/ai-coding-usage-guide.zh-CN.md)
4. [第一个只读 Trial](docs/product/first-readonly-trial.md)
5. [Use With An Existing Repo](docs/quickstart/use-with-existing-repo.md)
6. [在现有仓库中使用](docs/quickstart/use-with-existing-repo.zh-CN.md)
7. [Codex Direct Adapter](docs/product/codex-direct-adapter.md)
8. [Multi-Repo Trial Loop](docs/product/multi-repo-trial-loop.md)
9. [写入策略默认值](docs/product/write-policy-defaults.md)
10. [审批流程](docs/product/approval-flow.md)
11. [写侧工具治理](docs/product/write-side-tool-governance.md)
12. [Verification Runner](docs/product/verification-runner.md)
13. [交付 Handoff](docs/product/delivery-handoff.md)
14. [Runbooks](docs/runbooks/README.md)

如果你要理解产品规划：

1. [90-Day Plan](docs/roadmap/governed-ai-coding-runtime-90-day-plan.md)
2. [Issue-Ready Backlog](docs/backlog/issue-ready-backlog.md)
3. [PRD](docs/prd/governed-ai-coding-runtime-prd.md)
4. [Target Architecture](docs/architecture/governed-ai-coding-runtime-target-architecture.md)
5. [Positioning And Competitive Layering](docs/strategy/positioning-and-competitive-layering.md)
6. [Generic Target-Repo Attachment Blueprint](docs/architecture/generic-target-repo-attachment-blueprint.md)
7. [Interactive Session Productization Implementation Plan](docs/plans/interactive-session-productization-implementation-plan.md)
8. [Governance Runtime Strategy Alignment Plan](docs/plans/governance-runtime-strategy-alignment-plan.md)

## 当前完成度
当前已完成：

- `Phase 0` 到 `Phase 4` 的 MVP 合约层与验证基线
- `Full Runtime / GAP-024` 到 `GAP-028`
- `Public Usable Release / GAP-029` 到 `GAP-032`
- `Maintenance Baseline / GAP-033` 到 `GAP-034`

当前产品化切片：

- `Interactive Session Productization / GAP-035` 到 `GAP-039` 已在当前分支基线上完成
- `Strategy Alignment Gates / GAP-040` 到 `GAP-044` 已在当前分支基线上完成

当前验证基线：

- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
- `python -m unittest discover -s tests/runtime -p "test_*.py" -v`

## 维护策略
- [Codex CLI/App Integration Guide](docs/product/codex-cli-app-integration-guide.md)
- [Codex CLI/App 集成指南](docs/product/codex-cli-app-integration-guide.zh-CN.md)
- [Runtime Compatibility And Upgrade Policy](docs/product/runtime-compatibility-and-upgrade-policy.md)
- [Maintenance, Deprecation, And Retirement Policy](docs/product/maintenance-deprecation-and-retirement-policy.md)

