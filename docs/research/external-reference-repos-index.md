# External Reference Repo Index

## Purpose / 目的
- Record the local external reference set that this repository uses as official and community mechanism inputs.
- 给本项目保留一个项目内索引，避免“参考仓都在本机，但入口只存在于对话记忆里”。

## Boundary / 边界
- This repository remains the source of truth for what is actually adopted.
- 外部参考仓是机制输入，不是本项目规则、代码、规格或 claims 的替代品。
- Any mechanism borrowed from external repos still needs a local landing point, verification command, evidence link, and rollback posture before it becomes part of the governed runtime.

## Local Reference Root / 本地参考根目录
- Local root: `D:\CODE\external\ai-coding-runtime-references`
- External index README: `D:\CODE\external\ai-coding-runtime-references\README.md`
- Clone results: `D:\CODE\external\ai-coding-runtime-references\clone-results.json`

## Recommended Reading Order / 推荐查阅顺序
1. `openai-codex`, `openai-agents-python`, `openai-agents-js`, `mcp-specification`, `mcp-typescript-sdk`, `mcp-python-sdk`, `a2aproject-A2A`
   Host semantics, AGENTS/config/sandbox/approval, official agent-runtime patterns, MCP boundaries, and A2A protocol boundaries.
2. `github-mcp-server`, `mcp-servers`, `microsoft-playwright-cli`, `microsoft-playwright-mcp`, `google-antigravity-cli`, `google-gemini-cli`, `anthropic-claude-code`, `anthropic-claude-code-action`, `github-copilot-cli`
   Official or near-official implementation surfaces for tools, adapters, browser automation, host-family transitions, main host products, and multi-host compatibility.
3. `aider`, `swe-agent`, `continue`, `openhands`, `opencode`, `goose`
   Community coding-agent execution loops, repo grounding, permission posture, and UX.
4. `hermes-agent`, `langgraph`, `semantic-kernel`
   Skills, memory, gateway, multi-backend runtime, scheduling, durable state, and enterprise orchestration ideas.
5. `anthropic-claude-code-monitoring-guide`, `microsoft-ai-agents-for-beginners`
   ROI/telemetry/onboarding material and teaching-grade agent practices.

## Official And Primary Reference Set / 官方与主要参考集
| Local Repo | Source | Why It Matters |
| --- | --- | --- |
| `openai-codex` | <https://github.com/openai/codex> | Codex CLI host semantics, AGENTS loading, config, sandbox, approval, and tool/plugin behavior. |
| `openai-agents-python` | <https://github.com/openai/openai-agents-python> | OpenAI official Python agent-runtime framework for handoffs, guardrails, sessions, tracing, and sandbox-agent execution patterns. |
| `openai-agents-js` | <https://github.com/openai/openai-agents-js> | OpenAI official JS/TS agent-runtime framework for multi-agent workflows, tool orchestration, and realtime/voice-capable agent surfaces. |
| `mcp-specification` | <https://github.com/modelcontextprotocol/modelcontextprotocol> | MCP protocol vocabulary, transport, authorization, tools/resources/prompts boundaries. |
| `mcp-typescript-sdk` | <https://github.com/modelcontextprotocol/typescript-sdk> | TypeScript MCP server/client API shapes and schema patterns. |
| `mcp-python-sdk` | <https://github.com/modelcontextprotocol/python-sdk> | Python MCP server/client patterns and typing/test organization. |
| `mcp-servers` | <https://github.com/modelcontextprotocol/servers> | Official MCP server examples and packaging patterns. |
| `github-mcp-server` | <https://github.com/github/github-mcp-server> | Real external-service MCP server boundary in production-oriented form. |
| `a2aproject-A2A` | <https://github.com/a2aproject/A2A> | Linux Foundation-hosted A2A protocol source for agent discovery, long-running collaboration, modality negotiation, and A2A-vs-MCP boundary clarity. |
| `microsoft-playwright-cli` | <https://github.com/microsoft/playwright-cli> | Official browser CLI+skills path optimized for coding agents that need token-efficient browser automation. |
| `microsoft-playwright-mcp` | <https://github.com/microsoft/playwright-mcp> | Official browser MCP path optimized for persistent browser context, rich introspection, and MCP-based automation. |
| `google-antigravity-cli` | <https://github.com/google-antigravity/antigravity-cli> | Google's current host-family primary terminal surface, shared-engine direction with Antigravity 2.0, and migration anchor away from Gemini CLI. |
| `google-gemini-cli` | <https://github.com/google-gemini/gemini-cli> | Legacy Google CLI host behavior and migration/enterprise compatibility reference; no longer the preferred long-term Google host surface. |
| `anthropic-claude-code` | <https://github.com/anthropics/claude-code> | Claude Code official main host repository; useful for the terminal/IDE/GitHub product surface and plugin/runtime boundary itself, not only CI/action packaging. |
| `anthropic-claude-code-action` | <https://github.com/anthropics/claude-code-action> | Claude Code automation boundary in CI/action form. |
| `anthropic-claude-code-monitoring-guide` | <https://github.com/anthropics/claude-code-monitoring-guide> | Official measurement/ROI guide for telemetry, spend, productivity metrics, and rollout framing; useful as an operational guide, not a host-semantics source. |
| `github-copilot-cli` | <https://github.com/github/copilot-cli> | GitHub official terminal entry for Copilot coding agent; useful for cross-host comparison of approvals, MCP default posture, and GitHub-native context integration. |

## Community Mechanism Sources / 社区机制参考源
| Local Repo | Source | Why It Matters |
| --- | --- | --- |
| `aider` | <https://github.com/Aider-AI/aider> | Repo map, patch/edit loop, terminal coding-agent ergonomics. |
| `swe-agent` | <https://github.com/SWE-agent/SWE-agent> | Issue-to-fix loop discipline, task closure, and benchmark-aware verification mindset. |
| `continue` | <https://github.com/continuedev/continue> | Source-controlled checks, IDE/CLI cooperation, and policy-shaped coding assistance. |
| `openhands` | <https://github.com/All-Hands-AI/OpenHands> | Execution environment separation, sandbox vocabulary, and long-running coding-agent posture. |
| `opencode` | <https://github.com/sst/opencode> | Terminal-first coding-agent UX and provider/session abstractions. |
| `goose` | <https://github.com/block/goose> | Tool extensibility, desktop/CLI boundary, and agent surface packaging. |
| `hermes-agent` | <https://github.com/NousResearch/hermes-agent> | Skills/memory lifecycle, messaging gateway, multi-backend terminal runtime, scheduling, and trajectory compression. |
| `langgraph` | <https://github.com/langchain-ai/langgraph> | Durable state, checkpoints, interrupt/resume vocabulary, and graph orchestration patterns. |
| `semantic-kernel` | <https://github.com/microsoft/semantic-kernel> | Enterprise agent SDK patterns, plugins, planners, and multi-language structure. |
| `microsoft-ai-agents-for-beginners` | <https://github.com/microsoft/ai-agents-for-beginners> | Teaching-grade agent practices, eval framing, and onboarding-friendly examples. |

## How This Repo Uses Them / 本项目如何使用这些参考源
- Positioning and boundary shaping: see [Positioning And Competitive Layering](../strategy/positioning-and-competitive-layering.md).
- Borrow/do-not-borrow decisions: see [Runtime Governance Borrowing Matrix](./runtime-governance-borrowing-matrix.md).
- One-page entry and reading priority: see [External Reference Repo One-Page Overview](./external-reference-repo-one-page-overview.md).
- Maintenance tiering and archive candidates: see [External Reference Repo Tiering](./external-reference-repo-tiering.md).
- External benchmark interpretation: see [Hybrid Final-State External Benchmark Review](./2026-04-27-hybrid-final-state-external-benchmark-review.md).

## Update Note / 更新说明
- The cloned repos live outside this repository so they can be refreshed independently without polluting the control repo history.
- 如果参考集继续扩容，先更新外部索引，再回写本项目索引，保持“外部集合”和“项目内入口”一致。
