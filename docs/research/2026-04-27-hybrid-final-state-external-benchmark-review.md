# Hybrid Final-State External Benchmark Review

## Purpose
Review the repository's hybrid final-state posture against current official documentation, mature community coding-agent projects, and security/supply-chain best practices.

This review answers one question:

Is the current hybrid end state the best engineering target, or should the master outline, roadmap, and plan be adjusted?

## Reviewed Sources
- OpenAI Codex AGENTS.md guidance: https://developers.openai.com/codex/guides/agents-md
- OpenAI Agents SDK sandbox agents: https://developers.openai.com/api/docs/guides/agents/sandboxes
- OpenAI harness engineering notes: https://openai.com/index/harness-engineering/
- OpenAI Agents SDK guardrails and tracing docs: https://openai.github.io/openai-agents-python/guardrails/
- MCP roots and authorization specs: https://modelcontextprotocol.io/specification/2025-06-18/client/roots and https://modelcontextprotocol.io/specification/2025-03-26/basic/authorization
- A2A protocol specification, latest released version 1.0.0: https://a2a-protocol.org/latest/specification/
- LangGraph durable execution docs: https://docs.langchain.com/oss/python/langgraph/durable-execution
- Temporal durable execution docs: https://docs.temporal.io/temporal
- OPA policy-as-code docs: https://www.openpolicyagent.org/docs
- OpenTelemetry docs: https://opentelemetry.io/docs/
- FastAPI features and OpenAPI/Pydantic boundary docs: https://fastapi.tiangolo.com/features/
- OpenHands runtime architecture: https://docs.openhands.dev/openhands/usage/architecture/runtime
- SWE-agent architecture: https://swe-agent.com/0.7/background/architecture/
- GitHub Copilot repository custom instructions: https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions
- OWASP GenAI Security Project: https://owasp.org/www-project-top-10-for-large-language-model-applications/
- SLSA supply-chain framework, current provenance docs: https://slsa.dev/spec/v1.2/provenance

## Current Source Refresh
The 2026-04-27 refresh did not find a reason to replace the hybrid target shape. It did tighten the source interpretation:
- Codex AGENTS.md guidance still favors short, layered, repository-local instructions with project-specific overrides and fresh-run validation.
- OpenAI sandbox guidance separates harness state from sandbox execution state; this supports a runtime-owned control kernel plus sandbox/process containment rather than putting all orchestration inside the execution workspace.
- OpenAI Agents SDK guardrails do not cover every hosted or built-in execution tool path, so guardrails remain defense-in-depth and cannot replace runtime-owned approval, containment, evidence, and rollback.
- MCP roots define filesystem boundaries and require client validation, but servers are only expected to respect those roots; roots are not a sufficient enforcement boundary for this runtime.
- A2A has moved to a 1.0.0 latest release with version negotiation, AgentCard/security metadata, in-task authorization, and protocol-binding requirements. That strengthens the adapter-conformance requirement, but it still does not move task lifecycle, approval, rollback, or evidence ownership out of the kernel.
- SLSA v1.2 keeps provenance as the current supply-chain track; generated runtime packages, light packs, and control packs need provenance-or-waiver evidence before external consumption claims.

## Findings
### 1. Current Hybrid Shape Is Still Correct
The repository's final product shape remains the right target:

`repo-local contract bundle + machine-local durable governance kernel + attach-first host adapters + same-contract verification/delivery plane`

This aligns with the reviewed material:
- agent-readable repo-local docs and instructions improve first-pass agent effectiveness
- host products evolve quickly, so the stable boundary should be a capability adapter contract
- durable task state, approval, evidence, replay, and rollback should stay outside prompt text and outside one host product
- target repos should stay light and declarative

### 2. The Plan Needs A Stronger Execution-Containment Floor
OpenHands and SWE-agent both treat sandbox or environment management as central to software-agent execution. The current repository already has governed tool-runner concepts, but the final-state wording should make containment explicit for every broadened executable family:
- shell
- git
- package manager
- browser/computer use
- MCP tools

Required minimum:
- workspace roots
- path scope
- permission tier
- timeout and resource budget
- evidence reference
- rollback posture

### 3. Protocols Should Stay Below Kernel Semantics
MCP is useful for tools, resources, prompts, roots, and transport auth. A2A is useful for agent cards, tasks, messages, artifacts, streaming, and discovery. Neither should own local governance policy, approval, verification, rollback, or evidence semantics.

This supports the existing adapter-first architecture, but the roadmap should explicitly test that protocol capability changes cannot become hidden kernel forks.

The refreshed protocol reading adds two concrete checks:
- MCP roots must be treated as declared scope inputs that the runtime revalidates, not as the runtime's only path guard.
- A2A 1.0.0 integration, if started later, must include version negotiation, authorization scoping, and in-task authorization mapping into the existing runtime approval model.

### 4. Host Guardrails Are Defense-In-Depth, Not The Authority
OpenAI Agents SDK guardrail docs explicitly distinguish which tool paths the guardrail pipeline does and does not cover. This reinforces the repository's runtime-owned policy and approval model. Host or SDK guardrails can reduce risk, but they should not replace deterministic enforcement in the runtime.

### 5. Durable Execution Is A Capability Requirement, Not A Tool Mandate
LangGraph and Temporal-style guidance both emphasize persistence, deterministic replay, idempotency, and side-effect isolation. The repository should preserve its current trigger-based posture:
- prove durable/idempotent runtime behavior first
- introduce Temporal-class infrastructure when pause/resume/compensation complexity exceeds the local runtime path
- do not add orchestration depth solely because it appears in the north-star stack

### 6. Policy-As-Code Should Be Trigger-Based
OPA is a strong long-term fit when policy cardinality and audit pressure grow. It should remain a deferred transition from explicit local policy decisions to an external policy runtime. The near-term requirement is stable structured policy inputs and fail-closed decisions, not immediate Rego adoption.

### 7. Supply-Chain Provenance Is Underrepresented
The repository has provenance/attestation schemas, but the master outline and roadmap should make provenance a final-state acceptance class for:
- packaged runtime artifacts
- generated control packs
- target-repo light packs
- release and rollout evidence

This should be implemented as provenance or explicit waiver, not as narrative assurance.

### 8. The Technology Stack Needs A Staged Ladder
The current target stack is directionally strong, but some documents still read as if all target components should be adopted together. That is not optimal for this repository.

Recommended interpretation:
- keep the current Python/PowerShell/filesystem/SQLite substrate as the verified local baseline
- promote to FastAPI, Pydantic v2, PostgreSQL, object-store abstraction, OpenTelemetry hooks, and sandbox/process containment where service-shaped runtime behavior is real
- keep Temporal, OPA/Rego, event bus, Redis, pgvector, gRPC, A2A gateway, full observability, and web console as trigger-based final-state candidates

This is better than a one-shot platform stack because it preserves local-first usability and prevents infrastructure from outrunning the governed execution loop.

## Decision
Keep the current hybrid final-state product shape.

Improve the planning package by adding:
- execution-containment invariant
- protocol-boundary invariant
- sandbox/provenance near-term package
- supply-chain hardening long-term trigger
- explicit trigger-based component adoption rules
- staged stack ladder for current baseline, direct transition, and final-state candidates
- current-source compatibility guard for A2A/MCP/Codex sandbox and guardrail semantics

Do not:
- rewrite the runtime from scratch
- copy a full community project architecture
- make A2A, MCP, Temporal, OPA, Redis, pgvector, or event streaming mandatory before the runtime-owned loop needs them
- treat host-specific guardrails as the system of record
- treat protocol roots, AgentCards, host approvals, or SDK guardrails as sufficient enforcement without runtime-owned verification

## Projected Changes
- `docs/architecture/hybrid-final-state-master-outline.md`: add benchmark update, execution containment, protocol-boundary truth, and acceptance targets.
- `docs/roadmap/direct-to-hybrid-final-state-roadmap.md`: add external benchmarking adjustments and `NT-06` / `LT-06`.
- `docs/plans/direct-to-hybrid-final-state-implementation-plan.md`: add implementation interpretation rules, `NTP-06`, `LTP-06`, risks, and completion criteria.
- `docs/FinalStateBestPractices.md`: promote the current canonical planning package and distilled principles.
- `docs/architecture/mvp-stack-vs-target-stack.md`: clarify that `Temporal` and other heavy components are trigger-based, not MVP defaults.
- `docs/architecture/governed-ai-coding-runtime-target-architecture.md`: split the recommended stack into current baseline, direct transition, and final-state candidates.
- `docs/change-evidence/20260427-hybrid-final-state-current-source-refresh.md`: record this source refresh, conclusion, verification plan, and rollback.
