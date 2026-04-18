# Runtime Governance Borrowing Matrix

## Purpose
Record what this project should borrow from adjacent products without inheriting their product identity.

## Boundary Rule
- `governed-ai-coding-runtime` remains a governance/runtime layer for AI coding agents.
- External references are mechanism inputs, not product identities.
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
- `execution host`
- `wrapper/orchestration`
- `generation guardrail`

## Matrix
| Reference | Layer | Borrow | Avoid | Impact | Confidence | Source |
|---|---|---|---|---|---|---|
| Microsoft Agent Governance Toolkit | governance control plane | framework-agnostic action interception, auditability, policy hooks, runtime governance concepts that sit around existing agent frameworks | adopting the full seven-package enterprise breadth as near-term product scope | Reinforces that the project should govern existing hosts instead of replacing them. | medium | [Microsoft Open Source Blog](https://opensource.microsoft.com/blog/2026/04/02/introducing-the-agent-governance-toolkit-open-source-runtime-security-for-ai-agents/) |
| Open Policy Agent | policy engine | structured policy inputs, explicit allow/deny defaults, auditable decision evaluation over JSON-shaped inputs | binding the project to Rego or an OPA runtime before the local `PolicyDecision` interface settles | Directly informs the separation between host adapters and a stable policy-decision boundary. | high | [OPA Policy Language Docs](https://www.openpolicyagent.org/docs/policy-language) |
| Keycard for Coding Agents | identity/scope | agent identity, task-scoped credentials, policy-scoped resource access, per-action logging vocabulary | turning this project into a standalone IAM or credential-broker product | Clarifies what future approval and authorization outputs should be able to express without expanding into an identity platform. | medium | [Keycard Product](https://www.keycard.ai/), [Keycard Docs](https://docs.keycard.ai/) |
| Coder AI Governance | gateway | centralized audit trails, MCP administration, agent firewall posture, org-level gateway framing | making the local-first governed runtime depend on a centralized enterprise gateway shape | Useful as an outer deployment pattern, but intentionally outside the repo-native core product boundary. | medium | [Coder AI Governance Docs](https://coder.com/docs/ai-coder/ai-governance) |
| MCP / MCP-aligned gateway ecosystem | adapter protocol | host-client-server separation, capability negotiation, tools/resources/prompts as adapter surfaces, security-boundary clarity | treating MCP as the governance kernel or as the only enforcement point | Confirms MCP belongs at the adapter boundary, not at the policy or verification kernel. | high | [Model Context Protocol Architecture](https://modelcontextprotocol.io/specification/2025-06-18/architecture) |
| GAAI-framework-style repo files | wrapper/orchestration | repo-local declarative pack ideas, one canonical pack plus thin tool adapters, install-time attachment posture | adopting `.gaai/` conventions as a de facto standard or inheriting its Claude-first autonomous delivery daemon shape | Strong input for attachment-pack ergonomics, but not a standard to copy verbatim into this repository. | medium | [Fr-e-d/GAAI-framework](https://github.com/Fr-e-d/GAAI-framework) |
| OpenHands | execution host | sandbox-provider separation, explicit execution environment vocabulary, strong isolation as the default path | becoming another managed execution host or cloud coding platform | Sharpens the runtime boundary: this project governs execution and verification, but does not become the host itself. | high | [OpenHands Sandbox Overview](https://docs.openhands.dev/openhands/usage/sandboxes/overview) |
| SWE-agent | execution host | issue-to-task loop discipline, repository-grounded repair framing, benchmark-friendly verification mindset | making benchmark-first autonomous search the product identity | Useful for task closure semantics and repair loops, but not for product positioning. | high | [SWE-agent Repository](https://github.com/SWE-agent/SWE-agent) |
| Hermes Agent | execution host | isolated profiles, multi-backend runtime expectations, optional tool-use enforcement, host-side skills and messaging surfaces | absorbing self-improving memory, messaging gateway, or long-lived assistant identity as the center of gravity | Good reminder that hosts may grow richer lifecycle surfaces; governance should stay host-agnostic. | medium | [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) |
| oh-my-codex | wrapper/orchestration | Codex-native hooks, setup ergonomics, skills and AGENTS scaffolding, wrapper-level UX expectations | letting wrapper-specific tmux or hook flows become the project's core runtime contract | Useful for adapter ergonomics and user expectations around Codex-first integration. | medium | [Yeachan-Heo/oh-my-codex](https://github.com/Yeachan-Heo/oh-my-codex) |
| oh-my-claudecode | wrapper/orchestration | team orchestration vocabulary, parallel worker UX, staged wrapper flows that external adapters may expect | competing as another orchestration-wrapper product | Helps bound external wrapper compatibility work without pulling the project into wrapper identity. | medium | [Yeachan-Heo/oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) |
| NVIDIA NeMo Guardrails | generation guardrail | dialog safety and security rails as adjacent controls, clear separation between generation filtering and execution control | repositioning the project as a conversation guardrail or output-filtering layer | Reinforces that generation guardrails are adjacent, not a substitute for runtime/action governance. | high | [NVIDIA NeMo Guardrails](https://developer.nvidia.com/topics/ai/generative-ai) |
| Guardrails AI | generation guardrail | structured-output validation, validator ecosystems, JSON/schema-oriented output enforcement | collapsing runtime governance into structured-output validation alone | Useful at model-output boundaries and evidence validation edges, but not as the runtime kernel identity. | high | [Guardrails AI Validators](https://guardrailsai.com/guardrails/docs/concepts/validators), [Guardrails AI Structured Data Guide](https://guardrailsai.com/guardrails/docs/how-to-guides/generate_structured_data) |

## Consolidated Conclusions
- Borrow governance mechanisms, not vendor or wrapper identities.
- Keep `PolicyDecision` local and stable before plugging in any external policy runtime.
- Treat repo-local packs as attachment surfaces, not as a second handwritten source of truth.
- Keep execution hosts, wrapper/orchestration tools, and generation guardrails explicitly outside the core product identity.
- Preserve one target shorthand for the final shape:
  - `Repo-native Contract Bundle + Host Adapters + Policy Decision Interface + Verification and Delivery Plane`

## Representative Source Set
- Microsoft Agent Governance Toolkit: <https://opensource.microsoft.com/blog/2026/04/02/introducing-the-agent-governance-toolkit-open-source-runtime-security-for-ai-agents/>
- Open Policy Agent: <https://www.openpolicyagent.org/docs/policy-language>
- Keycard: <https://www.keycard.ai/>, <https://docs.keycard.ai/>
- Coder AI Governance: <https://coder.com/docs/ai-coder/ai-governance>
- MCP: <https://modelcontextprotocol.io/specification/2025-06-18/architecture>
- GAAI framework: <https://github.com/Fr-e-d/GAAI-framework>
- OpenHands: <https://docs.openhands.dev/openhands/usage/sandboxes/overview>
- SWE-agent: <https://github.com/SWE-agent/SWE-agent>
- Hermes Agent: <https://github.com/NousResearch/hermes-agent>
- oh-my-codex: <https://github.com/Yeachan-Heo/oh-my-codex>
- oh-my-claudecode: <https://github.com/Yeachan-Heo/oh-my-claudecode>
- NVIDIA NeMo Guardrails: <https://developer.nvidia.com/topics/ai/generative-ai>
- Guardrails AI: <https://guardrailsai.com/guardrails/docs/concepts/validators>
