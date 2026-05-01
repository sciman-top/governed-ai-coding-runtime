# Runtime Governance Borrowing Matrix

## Purpose
Record what this project should borrow from adjacent products without inheriting their product identity.

## Boundary Rule
- `governed-ai-coding-runtime` remains a governance/runtime layer for AI coding agents.
- External references are mechanism inputs, not product identities.
- Codex and Claude Code are primary cooperation hosts for the user's daily AI coding environment. The project should integrate, govern, and verify their use, but should not compete with their UI, model loop, built-in tool calling, or host-owned memory UX.
- Hermes Agent, OpenHands, SWE-agent, Letta, Mem0, LangGraph, Aider, Cline, and similar projects are external mechanism sources. Their mechanisms may be absorbed more freely than Codex/Claude host behavior, but only as governed contracts with evidence, rollback, and effect feedback.
- Claims below use official documentation, official product pages, or primary repositories only.
- Confidence legend:
  - `high`: stable fit with direct relevance to the target boundary
  - `medium`: useful mechanism with material product-boundary differences
  - `low`: useful signal, but too product-specific to standardize as a repo-native default

## Layer Legend
- `governance control plane`
- `policy engine`
- `identity/scope`
- `gateway`
- `adapter protocol`
- `host cooperation surface`
- `execution host`
- `wrapper/orchestration`
- `memory/knowledge lifecycle`
- `context shaping`
- `eval and skill testing`
- `generation guardrail`

## Matrix
| Reference | Layer | Borrow | Avoid | Impact | Confidence | Source |
|---|---|---|---|---|---|---|
| OpenAI Codex | host cooperation surface | `AGENTS.md` rule loading semantics, coding-agent project guidance, CLI/app host integration expectations, task-to-PR workflow assumptions | replacing Codex UI, model loop, approval surface, or host-owned session behavior | Confirms the project should provide repo instructions, gates, evidence, and adapter conformance around Codex instead of becoming a Codex clone. | high | [OpenAI Codex AGENTS.md Docs](https://github.com/openai/codex/blob/main/docs/agents_md.md), [OpenAI Codex](https://openai.com/index/introducing-codex/) |
| Claude Code | host cooperation surface | memory file conventions, settings governance, hooks, subagent/settings surfaces, managed local configuration vocabulary, third-party Anthropic-compatible provider profiles | duplicating Claude Code's native memory UX, hook runtime, interactive assistant shell, or assuming official subscription/account entitlement as a required baseline | Confirms Claude Code should be treated as a first-class local host with governed settings, hooks, and GLM/DeepSeek-style provider profiles, not as functionality to reimplement. | high | [Claude Code Memory](https://docs.anthropic.com/en/docs/claude-code/memory), [Claude Code Hooks](https://docs.anthropic.com/en/docs/claude-code/hooks), [Claude Code Settings](https://docs.anthropic.com/en/docs/claude-code/settings) |
| Microsoft Agent Governance Toolkit | governance control plane | framework-agnostic action interception, auditability, policy hooks, runtime governance concepts that sit around existing agent frameworks | adopting the full seven-package enterprise breadth as near-term product scope | Reinforces that the project should govern existing hosts instead of replacing them. | medium | [Microsoft Open Source Blog](https://opensource.microsoft.com/blog/2026/04/02/introducing-the-agent-governance-toolkit-open-source-runtime-security-for-ai-agents/) |
| Open Policy Agent | policy engine | structured policy inputs, explicit allow/deny defaults, auditable decision evaluation over JSON-shaped inputs | binding the project to Rego or an OPA runtime before the local `PolicyDecision` interface settles | Directly informs the separation between host adapters and a stable policy-decision boundary. | high | [OPA Policy Language Docs](https://www.openpolicyagent.org/docs/policy-language) |
| Keycard for Coding Agents | identity/scope | agent identity, task-scoped credentials, policy-scoped resource access, per-action logging vocabulary | turning this project into a standalone IAM or credential-broker product | Clarifies what future approval and authorization outputs should be able to express without expanding into an identity platform. | medium | [Keycard Product](https://www.keycard.ai/), [Keycard Docs](https://docs.keycard.ai/) |
| Coder AI Governance | gateway | centralized audit trails, MCP administration, agent firewall posture, org-level gateway framing | making the local-first governed runtime depend on a centralized enterprise gateway shape | Useful as an outer deployment pattern, but intentionally outside the repo-native core product boundary. | medium | [Coder AI Governance Docs](https://coder.com/docs/ai-coder/ai-governance) |
| MCP / MCP-aligned gateway ecosystem | adapter protocol | host-client-server separation, capability negotiation, tools/resources/prompts as adapter surfaces, security-boundary clarity | treating MCP as the governance kernel or as the only enforcement point | Confirms MCP belongs at the adapter boundary, not at the policy or verification kernel. | high | [Model Context Protocol Architecture](https://modelcontextprotocol.io/specification/2025-06-18/architecture) |
| GAAI-framework-style repo files | wrapper/orchestration | repo-local declarative pack ideas, one canonical pack plus thin tool adapters, install-time attachment posture | adopting `.gaai/` conventions as a de facto standard or inheriting its Claude-first autonomous delivery daemon shape | Strong input for attachment-pack ergonomics, but not a standard to copy verbatim into this repository. | medium | [Fr-e-d/GAAI-framework](https://github.com/Fr-e-d/GAAI-framework) |
| LangGraph | wrapper/orchestration | durable state, interruptible flows, human-in-the-loop checkpoints, replayable graph execution vocabulary | turning this project into a graph-framework application or making LangGraph a required runtime dependency before local contracts need it | Useful for future workflow and replay vocabulary, but the near-term implementation should keep local contracts framework-neutral. | medium | [LangGraph Persistence](https://docs.langchain.com/oss/python/langgraph/persistence), [LangGraph Human-In-The-Loop](https://docs.langchain.com/oss/python/langgraph/human-in-the-loop) |
| OpenHands | execution host | sandbox-provider separation, explicit execution environment vocabulary, strong isolation as the default path | becoming another managed execution host or cloud coding platform | Sharpens the runtime boundary: this project governs execution and verification, but does not become the host itself. | high | [OpenHands Sandbox Overview](https://docs.openhands.dev/openhands/usage/sandboxes/overview) |
| SWE-agent | execution host | issue-to-task loop discipline, repository-grounded repair framing, benchmark-friendly verification mindset | making benchmark-first autonomous search the product identity | Useful for task closure semantics and repair loops, but not for product positioning. | high | [SWE-agent Repository](https://github.com/SWE-agent/SWE-agent) |
| Hermes Agent | execution host | isolated profiles, multi-backend runtime expectations, optional tool-use enforcement, host-side skills, memory, and self-improvement surfaces | absorbing messaging gateway, long-lived assistant identity, or autonomous social/communication behavior as the center of gravity | Strong source for governed skill and memory lifecycle ideas because it is not a daily user host, but its product identity should not be copied. | medium | [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) |
| Letta | memory/knowledge lifecycle | memory block structure, explicit agent state, persistence boundaries, memory editing vocabulary | becoming a memory-first agent platform or requiring a database-backed memory service before local evidence proves need | Useful for modeling durable knowledge records with scope, provenance, and editability. | medium | [Letta Memory Docs](https://docs.letta.com/guides/agents/memory) |
| Mem0 | memory/knowledge lifecycle | memory extraction, retrieval, update, and deletion lifecycle vocabulary for agent memory | importing memory automation without provenance, expiry, evaluation, or rollback | Useful as an external signal for turning AI coding experience into governed memory candidates. | medium | [Mem0 Docs](https://docs.mem0.ai/overview) |
| Aider repo map | context shaping | concise repository map, context selection, token-aware codebase orientation | replacing host context management or trusting repo maps without freshness and accuracy checks | Strong input for a governed repo-map artifact with measurable token and clarification impact. | high | [Aider Repo Map](https://aider.chat/docs/repomap.html) |
| Cline | host cooperation surface | human-supervised tool execution, IDE/CLI/browser action expectations, explicit approval posture | becoming another IDE agent or autonomous coding assistant | Useful to keep adapter tiers honest for permissioned tool use, but not a target product identity. | medium | [Cline Repository](https://github.com/cline/cline) |
| OpenAI Cookbook Evals | eval and skill testing | eval-driven skill improvement, repeatable scoring, regression checks for agent skills and workflows | treating cookbook examples as policy authority or replacing local target-repo gates | Direct input for testing skills and evolution candidates before promotion. | high | [OpenAI Cookbook Evals](https://cookbook.openai.com/topic/evals) |
| oh-my-codex | wrapper/orchestration | Codex-native hooks, setup ergonomics, skills and AGENTS scaffolding, wrapper-level UX expectations | letting wrapper-specific tmux or hook flows become the project's core runtime contract | Useful for adapter ergonomics and user expectations around Codex-first integration. | medium | [Yeachan-Heo/oh-my-codex](https://github.com/Yeachan-Heo/oh-my-codex) |
| oh-my-claudecode | wrapper/orchestration | team orchestration vocabulary, parallel worker UX, staged wrapper flows that external adapters may expect | competing as another orchestration-wrapper product | Helps bound external wrapper compatibility work without pulling the project into wrapper identity. | medium | [Yeachan-Heo/oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) |
| NVIDIA NeMo Guardrails | generation guardrail | dialog safety and security rails as adjacent controls, clear separation between generation filtering and execution control | repositioning the project as a conversation guardrail or output-filtering layer | Reinforces that generation guardrails are adjacent, not a substitute for runtime/action governance. | high | [NVIDIA NeMo Guardrails](https://developer.nvidia.com/topics/ai/generative-ai) |
| Guardrails AI | generation guardrail | structured-output validation, validator ecosystems, JSON/schema-oriented output enforcement | collapsing runtime governance into structured-output validation alone | Useful at model-output boundaries and evidence validation edges, but not as the runtime kernel identity. | high | [Guardrails AI Validators](https://guardrailsai.com/guardrails/docs/concepts/validators), [Guardrails AI Structured Data Guide](https://guardrailsai.com/guardrails/docs/how-to-guides/generate_structured_data) |

## Consolidated Conclusions
- Borrow governance mechanisms, not vendor, host, or wrapper identities.
- Codex and Claude Code are cooperation hosts. The project should make their use safer, more repeatable, and more auditable, not compete with their native agent surfaces.
- Claude Code support in this project is local third-party-provider support first. It should not require official Claude subscription state or official account entitlements to satisfy the baseline.
- Hermes/OpenHands/SWE-agent/Letta/Mem0/LangGraph/Aider/Cline-style systems are selective mechanism sources. They may justify new contracts, checks, skills, memory lifecycle, context artifacts, or effect metrics, but not a product identity change.
- Keep `PolicyDecision` local and stable before plugging in any external policy runtime.
- Treat repo-local packs as attachment surfaces, not as a second handwritten source of truth.
- Keep execution hosts, wrapper/orchestration tools, and generation guardrails explicitly outside the core product identity.
- Every absorbed mechanism needs an adoption class, expected effect, verification command, evidence reference, and rollback or retirement path.
- Controlled evolution must classify existing project capabilities too. The correct portfolio outcomes are `add`, `keep`, `improve`, `merge`, `deprecate`, `retire`, and `delete_candidate`, with deletion limited to bounded, proposal-backed, rollbackable candidates rather than reviewed assets or evidence history.
- Preserve one target shorthand for the final shape:
  - `Governance Kernel + Reusable Control Packs + Host Adapters + Inheritance/Override Verifier + Effect Feedback + Controlled Evolution`

## Representative Source Set
- Microsoft Agent Governance Toolkit: <https://opensource.microsoft.com/blog/2026/04/02/introducing-the-agent-governance-toolkit-open-source-runtime-security-for-ai-agents/>
- OpenAI Codex: <https://github.com/openai/codex/blob/main/docs/agents_md.md>, <https://openai.com/index/introducing-codex/>
- Claude Code: <https://docs.anthropic.com/en/docs/claude-code/memory>, <https://docs.anthropic.com/en/docs/claude-code/hooks>, <https://docs.anthropic.com/en/docs/claude-code/settings>
- Open Policy Agent: <https://www.openpolicyagent.org/docs/policy-language>
- Keycard: <https://www.keycard.ai/>, <https://docs.keycard.ai/>
- Coder AI Governance: <https://coder.com/docs/ai-coder/ai-governance>
- MCP: <https://modelcontextprotocol.io/specification/2025-06-18/architecture>
- GAAI framework: <https://github.com/Fr-e-d/GAAI-framework>
- LangGraph: <https://docs.langchain.com/oss/python/langgraph/persistence>, <https://docs.langchain.com/oss/python/langgraph/human-in-the-loop>
- OpenHands: <https://docs.openhands.dev/openhands/usage/sandboxes/overview>
- SWE-agent: <https://github.com/SWE-agent/SWE-agent>
- Hermes Agent: <https://github.com/NousResearch/hermes-agent>
- Letta: <https://docs.letta.com/guides/agents/memory>
- Mem0: <https://docs.mem0.ai/overview>
- Aider repo map: <https://aider.chat/docs/repomap.html>
- Cline: <https://github.com/cline/cline>
- OpenAI Cookbook Evals: <https://cookbook.openai.com/topic/evals>
- oh-my-codex: <https://github.com/Yeachan-Heo/oh-my-codex>
- oh-my-claudecode: <https://github.com/Yeachan-Heo/oh-my-claudecode>
- NVIDIA NeMo Guardrails: <https://developer.nvidia.com/topics/ai/generative-ai>
- Guardrails AI: <https://guardrailsai.com/guardrails/docs/concepts/validators>
