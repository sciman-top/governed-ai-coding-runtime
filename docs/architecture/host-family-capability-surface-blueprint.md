# Host Family Capability Surface Blueprint

## Purpose
- 把“最佳工程终态”落实成一个稳定的宿主建模蓝图。
- 明确 runtime 应该围绕 `host family + capability surface` 建模，而不是绑定某个单一 CLI 名称。
- 区分当前兼容层、长期主方向和治理内核不可让渡的边界。

## Official Grounding (2026-06-06)
- `OpenAI Codex` 官方仍把 `AGENTS.md`、config layering、sandbox/approval、subagents 作为稳定控制面语义。
- `OpenAI Codex` 官方也已明确把 `Codex App` 做成桌面主表面之一，覆盖 desktop projects、worktrees、automations、in-app browser、artifact viewer、IDE sync、native Windows sandbox、`Computer Use` 与 `Remote connections`。
- `Claude` 官方已不再只是 terminal CLI；`Claude Code` 当前覆盖 terminal、web、desktop、VS Code、JetBrains、Slack、GitHub Actions、GitLab 等表面，且 `Claude Cowork` 已在 `Claude Desktop` 推广为本地隔离 VM + 本地文件/MCP 可达。
- `Google` 官方已把长期终端宿主方向从 `Gemini CLI` 转到 `Antigravity CLI`，并明确 `Antigravity CLI` 与 `Antigravity 2.0` 共享 agent engine、settings 和 session export continuity。

## Final Product Answer
本项目的最佳工程终态不是“做一个更大的 AI coding host”，而是：

`Governance hub + reusable contract + controlled evolution loop + attach-first multi-host adapters`

它应该做到：
- 宿主可替换：Codex、Claude、Antigravity、未来 IDE/cloud/browser agent 都是可替换前端。
- 内核稳定：task、policy、approval、evidence、verification、rollback 语义不跟随宿主产品名漂移。
- 风险可治理：尽量复用上游宿主权限/沙箱能力，但最终以 runtime 的证据、门禁和回滚语义收口。
- 演进可证据化：官方文档变化、target-run 退化、重复 toil、AI coding session lessons 都进入受控演进流程，而不是靠会话记忆隐式漂移。

## Canonical Host Families

| Host family | Current product interpretation | Runtime stance |
| --- | --- | --- |
| `Codex family` | Codex CLI + Codex App + remote/mobile control + Computer Use + related OpenAI coding surfaces | first-class required host family |
| `Claude family` | Claude Code terminal + IDE + Desktop/Cowork + collaboration surfaces | first-class required host family |
| `Antigravity family` | Antigravity CLI + Antigravity 2.0 GUI | supported now, long-term primary Google host family |
| `Gemini legacy bridge` | `GEMINI.md` hierarchy, existing Gemini local settings, remaining enterprise compatibility path | migration-only / best-effort compatibility bridge |

## Capability Surface Contract
宿主适配必须先声明能力，而不是先声明品牌。建议最小能力维度如下：

| Capability field | Meaning | Why runtime cares |
| --- | --- | --- |
| `surface_class` | terminal / desktop / IDE / web / cloud-worker | 决定交互密度、可见性和 orchestration 模式 |
| `attach_mode` | native_attach / process_bridge / manual_handoff / import_only | 决定 continuity、evidence 可信度和退化语义 |
| `tool_visibility` | tool call 是否可结构化观察 | 决定治理能否在 write/tool 前后精确收口 |
| `event_stream_visibility` | 是否有稳定事件流、日志、checkpoints | 决定 replay、trace、operator feedback 深度 |
| `approval_delegateability` | 宿主审批能否被 runtime 借用 | 决定 friction 是复用上游还是 runtime 补强 |
| `sandbox_delegateability` | 宿主隔离能力是否足够可信 | 决定 runtime 是否必须额外 containment |
| `continuation_model` | resume/session export/shared history 是否稳定 | 决定 attach-first 体验与 handoff 模型 |
| `evidence_exportability` | diff/log/transcript/artifacts 是否可导出 | 决定 completion claim 是否可验证 |
| `execution_locality` | local / remote / hybrid | 决定凭据、路径、网络和 rollback 模型 |

## Engineering Boundary
以下边界在最佳终态中不应被打破：
- runtime 不是新的 primary host product。
- runtime 不接管用户宿主账号、provider、历史桶或 GUI 生命周期。
- MCP/A2A/tool SDK 只是协议与接入边界，不是治理事实源。
- 社区优秀项目只能提供结构启发，不能替代官方语义和本机实测。

## Codex Surface Interpretation
对 `Codex family`，当前更准确的官方解释应是：
- `CLI`: shell-first、本地命令与项目内执行面。
- `App`: desktop-first、多项目/多线程/worktree/automation/review/artifact 组织面。
- `Remote`: ChatGPT mobile 或其他 Codex App 设备对同一 host 的跨设备接力与审批面。
- `Computer Use / Browser`: GUI、browser、desktop-app 观察与操作面。

因此，`Codex` 不应再在架构里只被写成 “CLI first tool”。更准确的说法是：
- day-to-day direct coding 入口常常仍从 CLI 开始；
- 但长期宿主建模必须把 `Codex App` 视为正式、多 surface 的 host-family 核心组成部分。

## Target Stack Interpretation
围绕这个蓝图，推荐的终态技术栈/架构解释是：

- Control plane:
  - policy/risk/approval/evidence/rollback 继续由 runtime kernel 拥有
- Execution plane:
  - attach-first session bridge + capability-tiered host adapters
- Data plane:
  - repo-local light pack + machine-local durable runtime state + reviewable evidence artifacts
- Assurance plane:
  - build -> test -> contract/invariant -> hotspot 固定门禁
  - current-source compatibility
  - target-run effect feedback
  - controlled runtime evolution review

实现栈建议：
- 当前直接演进栈仍以 `Python 3.12+`, `FastAPI`, `Pydantic v2`, `SQLite/PostgreSQL`, object-store abstraction, `OpenTelemetry` 为主。
- Host adapters 必须 capability-first，而不是为每个产品重写 kernel。
- 更重的 orchestration / policy / event stack 继续保持 trigger-based promotion，而不是因为“看起来更平台化”就提前引入。

## Google Transition Rule
- 长期 Google 主宿主：`Antigravity family`
- 当前兼容桥：`Gemini legacy bridge`
- 规则同步/目标仓兼容层若仍分发 `GEMINI.md`，这是当前落地兼容事实，不等于长期产品方向仍是 `Gemini CLI`

## Acceptance Questions
- 新宿主接入时，是否先提交 capability declaration，而不是直接写产品特判？
- 当前完成声明，是否能指出 host family、attach mode、degrade reason、verification refs、evidence refs？
- Google 相关文档/策略，是否区分了 `Antigravity` 主方向与 `Gemini` 兼容桥？
- Desktop / IDE / terminal / web surface 的差异，是否通过 capability surface 吸收，而不是污染 kernel 语义？
- `Codex` 相关文档，是否已经把 `Codex App / Remote connections / Computer Use` 作为正式 surface，而不是继续只按 CLI 理解？
