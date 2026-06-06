# External Reference Repo One-Page Overview

## Purpose
- 用一页看清当前 `D:\CODE\external\ai-coding-runtime-references` 的参考仓结构、优先级和用途。
- 作为“先看谁、为什么留、哪些只是桥接或观察”的快速入口。

## Reading Rule
- `Tier 1 / Must Read`: 当前宿主战略、协议边界、adapter 能力建模优先看这些。
- `Tier 2 / Keep`: 值得长期保留，但不是每次都要先看。
- `Tier 3 / Legacy Bridge`: 继续保留，仅用于兼容或迁移，不代表长期方向。
- `Tier 4 / Observe`: 补充材料或观察面，优先级最低。

## One-Page Matrix
| Repo | Tier | Class | Primary Use | Why now |
| --- | --- | --- | --- | --- |
| `openai-codex` | Must Read | official host | Codex host semantics, AGENTS/config/sandbox/approval | Codex family 仍是核心主宿主之一 |
| `openai-agents-python` | Must Read | official runtime | Python handoffs/guardrails/sessions/tracing/sandbox agents | 对运行时 contract 和 controlled evolution 很关键 |
| `openai-agents-js` | Must Read | official runtime | JS/TS multi-agent, tools, realtime/voice | 补齐 TypeScript agent-runtime 视角 |
| `anthropic-claude-code` | Must Read | official host | Claude host semantics, plugins, runtime boundary | Claude family 已是 co-equal 主宿主 |
| `google-antigravity-cli` | Must Read | official host | Google current host direction, shared engine/settings/session export | Google 侧长期方向已转向 Antigravity |
| `github-copilot-cli` | Must Read | official host | Copilot CLI, GitHub context, approvals, MCP defaults | 补一条主流第一方宿主对照面 |
| `mcp-specification` | Must Read | protocol | MCP vocabulary, security, transport, boundaries | MCP 是当前 adapter 边界核心协议 |
| `mcp-typescript-sdk` | Must Read | protocol sdk | TS MCP implementation shapes | 设计 TypeScript tool/server 面时最直接 |
| `mcp-python-sdk` | Must Read | protocol sdk | Python MCP implementation shapes | Python runtime 与 tool adapter 参考面 |
| `github-mcp-server` | Must Read | first-party server | Real production MCP server boundary | 看真实外部服务如何暴露工具 |
| `a2aproject-A2A` | Must Read | protocol | Agent-to-agent discovery/collaboration | A2A 是未来多 agent 互操作的正式边界 |
| `microsoft-playwright-cli` | Must Read | first-party browser cli | Token-efficient browser CLI + skills | 很适合 coding agent 的低 token 浏览器路径 |
| `microsoft-playwright-mcp` | Must Read | first-party browser mcp | Persistent browser context, rich introspection | 和 CLI 路径形成直接取舍对照 |
| `mcp-servers` | Keep | official examples | Example MCP servers and packaging | 对比 spec/sdk 后再看更有价值 |
| `anthropic-claude-code-action` | Keep | official ci | Claude CI/action surface | 重要但窄于主宿主本体 |
| `openhands` | Keep | community runtime | Sandbox/execution host vocabulary | 执行环境与宿主隔离参考强 |
| `aider` | Keep | community cli | Repo map, patch/edit loop | repo grounding 和 edit ergonomics 仍然非常强 |
| `swe-agent` | Keep | community repair | issue-to-fix / benchmark-aware closure | 任务闭环和验证心智参考强 |
| `continue` | Keep | community ide/cli | source-controlled checks, IDE/CLI cooperation | 策略化检查与 IDE 协作参考面 |
| `opencode` | Keep | community cli | terminal UX, provider/session abstractions | 宿主抽象和 TUI 取舍参考面 |
| `goose` | Keep | community app/cli | extension surface, desktop/CLI packaging | 桌面/CLI 边界可对照 |
| `hermes-agent` | Keep | community self-improve | skills/memory/scheduling/trajectory | controlled improvement / memory 借鉴面 |
| `langgraph` | Keep | orchestration | durable state, interrupt/resume | orchestration vocabulary 参考面 |
| `semantic-kernel` | Keep | enterprise sdk | plugins/planners/multi-language structure | 企业 SDK 结构化参考面 |
| `google-gemini-cli` | Legacy Bridge | official legacy host | GEMINI.md/tooling/MCP/enterprise bridge | 仍有真实兼容债，但不再是长期方向 |
| `anthropic-claude-code-monitoring-guide` | Observe | official ops guide | telemetry, ROI, rollout framing | 适合运营和度量，不是宿主语义源 |
| `microsoft-ai-agents-for-beginners` | Observe | teaching material | onboarding and examples | 教学价值高，架构直接价值低 |

## Quick Decision
- 现在要研究“宿主怎么建模”：先看 `Codex / Claude / Antigravity / Copilot`
- 现在要研究“协议边界怎么定”：先看 `MCP + A2A`
- 现在要研究“浏览器自动化怎么选”：先看 `playwright-cli` 与 `playwright-mcp`
- 现在要研究“编辑循环/修复闭环怎么借”：先看 `aider`、`swe-agent`、`openhands`

## Keep / Delete Answer
- 立即删除：`none`
- 当前最不影响主线的未来归档候选：
  1. `microsoft-ai-agents-for-beginners`
  2. `anthropic-claude-code-monitoring-guide`
  3. `goose` 或 `opencode` 其中之一，如果后续不再提供新洞见

## Related Docs
- [External Reference Repo Index](./external-reference-repos-index.md)
- [External Reference Repo Tiering](./external-reference-repo-tiering.md)
- [Runtime Governance Borrowing Matrix](./runtime-governance-borrowing-matrix.md)
