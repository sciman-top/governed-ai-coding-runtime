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
1. `openai-codex`, `mcp-specification`, `mcp-typescript-sdk`, `mcp-python-sdk`
   Host semantics, AGENTS/config/sandbox/approval, and MCP protocol/SDK boundaries.
2. `github-mcp-server`, `mcp-servers`, `google-gemini-cli`, `anthropic-claude-code-action`
   Official or near-official implementation surfaces for tools, adapters, and multi-host compatibility.
3. `aider`, `swe-agent`, `continue`, `openhands`, `opencode`, `goose`
   Community coding-agent execution loops, repo grounding, permission posture, and UX.
4. `hermes-agent`
   Skills, memory, gateway, multi-backend runtime, scheduling, and trajectory-compression ideas.
5. `langgraph`, `semantic-kernel`, `microsoft-ai-agents-for-beginners`
   Orchestration, durable state, enterprise SDK patterns, and teaching-grade agent practices.

## Official And Primary Reference Set / 官方与主要参考集
| Local Repo | Source | Why It Matters |
| --- | --- | --- |
| `openai-codex` | <https://github.com/openai/codex> | Codex CLI host semantics, AGENTS loading, config, sandbox, approval, and tool/plugin behavior. |
| `mcp-specification` | <https://github.com/modelcontextprotocol/modelcontextprotocol> | MCP protocol vocabulary, transport, authorization, tools/resources/prompts boundaries. |
| `mcp-typescript-sdk` | <https://github.com/modelcontextprotocol/typescript-sdk> | TypeScript MCP server/client API shapes and schema patterns. |
| `mcp-python-sdk` | <https://github.com/modelcontextprotocol/python-sdk> | Python MCP server/client patterns and typing/test organization. |
| `mcp-servers` | <https://github.com/modelcontextprotocol/servers> | Official MCP server examples and packaging patterns. |
| `github-mcp-server` | <https://github.com/github/github-mcp-server> | Real external-service MCP server boundary in production-oriented form. |
| `google-gemini-cli` | <https://github.com/google-gemini/gemini-cli> | Gemini CLI host behavior, config layering, and MCP-facing posture. |
| `anthropic-claude-code-action` | <https://github.com/anthropics/claude-code-action> | Claude Code automation boundary in CI/action form. |

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
- External benchmark interpretation: see [Hybrid Final-State External Benchmark Review](./2026-04-27-hybrid-final-state-external-benchmark-review.md).

## Update Note / 更新说明
- The cloned repos live outside this repository so they can be refreshed independently without polluting the control repo history.
- 如果参考集继续扩容，先更新外部索引，再回写本项目索引，保持“外部集合”和“项目内入口”一致。
