# Governance Hub Reuse And Controlled Evolution Plan

## Status
- Created: 2026-05-01.
- Queue: `GAP-130` through `GAP-141`.
- Current state: `GAP-130..139` are complete on the current branch baseline. `GAP-140..141` are the post-certification effect-feedback follow-on queue: first recover or explicitly defer degraded host-capability posture with fresh evidence, then close or formalize the historical problem-trace window. This plan does not enable automatic policy mutation, automatic skill installation, target-repo sync, push, or merge.
- Prior dependency: `GAP-120..129` established runtime evolution review and controlled materialization. This plan turns the clarified product direction into the next implementation queue.

## Goal
Turn the project into the reusable governance center for AI coding work:

- `Governance Hub`: one control plane for risk policy, gates, evidence, rollback, and effect feedback.
- `Reusable Contract`: repo-native control packs that target repositories inherit, validate, and override only through declared rules.
- `Controlled Evolution`: repeatable review, absorption, promotion, retirement, and feedback loops that can improve the runtime without bypassing review gates.

The outcome must be executable and measurable. Every promoted capability needs:

```text
baseline -> proposed change -> gate -> effect metric -> evidence -> rollback
```

## Positioning Correction
Codex and Claude Code are the user's primary AI coding environments. This project must cooperate with them instead of competing with them.

What this means:

- Do not duplicate Codex or Claude Code chat UI, model loop, built-in tool calling, or host-specific memory UX.
- Do govern how Codex and Claude Code sessions attach to target repos, execute gates, use policies, write evidence, and degrade when a host capability is absent.
- Treat Claude Code support in this repository as local Claude Code used with third-party Anthropic-compatible providers such as GLM or DeepSeek. Do not assume official Claude subscription availability, official cloud entitlement, or vendor-hosted account state as a required baseline.
- Treat Hermes Agent, OpenHands, SWE-agent, Letta, Mem0, LangGraph, Aider, Cline, OPA, MCP gateways, Agent Skills, and similar projects as mechanism sources. Since they are not the user's active daily hosts, the project can absorb useful mechanisms more freely, but only as governed contracts and verifiable runtime capabilities.

## Automation And Outer AI Principle
Automation-first, outer-AI-assisted, gate-controlled evolution is a core principle.

The project should automate deterministic governance work inside the repository and may automatically trigger outer AI for high-intelligence evolution assistance:

- collect official docs, primary project sources, community practice, runtime evidence, and AI coding experience signals
- extract knowledge, repeated patterns, failure modes, and skill candidates
- generate structured evolution proposals and disabled candidates
- classify capability portfolio decisions
- analyze target-repo effect feedback

Outer AI output is advisory until it becomes a structured candidate with risk classification, machine gate, evidence ref, rollback ref, and the required review boundary. Automatic triggers do not authorize active policy mutation, skill enablement, target-repo sync, push, merge, reviewed evidence deletion, or active gate deletion.

## Final-State Architecture
The best engineering final state is Governance Hub + Reusable Contract + Controlled Evolution loop + outer AI intelligent review/generation capability. This final state remains a governance-control shape, not a replacement for Codex or Claude Code as day-to-day AI coding hosts.

The target shape is:

```text
Governance Kernel
  + Control Packs
  + Repo Profiles
  + Host Adapters
  + Inheritance And Override Verifier
  + Knowledge And Skill Lifecycle
  + Effect Evaluation Harness
  + Evidence, Replay, And Rollback Plane
  + Controlled Evolution Queue
```

### Governance Kernel
Owns stable decisions and invariants:

- risk taxonomy
- `PolicyDecision`
- gate order and result contract
- evidence schema
- rollback references
- waiver semantics
- promotion and retirement states

### Control Packs
Provide repo-native reusable governance bundles. A control pack is a versioned bundle of:

- `policy`
- `gate`
- `hook`
- `eval`
- `workflow`
- `skill`
- `knowledge`
- `memory`
- `evidence`
- `rollback`

Control packs are not handwritten second sources of truth. They are generated, validated, or checked against repository sources.

### Repo Profiles
Target repositories inherit the control pack, then declare repository facts:

- repo type and gate commands
- allowed target-repo overrides
- domain invariants
- local performance and hotspot checks
- data migration and rollback requirements
- host support posture

### Host Adapters
Adapters connect Codex, Claude Code, and future hosts without moving the project into a host product identity.

Host adapters must report:

- capability tier
- supported actions
- degrade reason
- remediation hint
- evidence mapping
- policy and gate attachment status

### Knowledge And Skill Lifecycle
AI coding experience becomes useful only after it is captured as reviewable evidence and promoted through gates.

Lifecycle:

```text
experience note -> knowledge candidate -> pattern candidate -> skill/control-pack candidate
  -> eval -> disabled materialization -> reviewed promotion -> inherited use -> effect feedback
  -> retire or keep
```

### Effect Evaluation Harness
The project must measure whether an absorbed mechanism improves real workflows.

Minimum metrics:

- gate pass or fail rate
- repeated failure count
- time to readiness
- time to reviewed proposal
- drift count
- target repo adoption pass count
- token or context size change when measurable
- rollback or retirement count

### Capability Portfolio Lifecycle
Controlled evolution must evaluate the whole capability portfolio, not only external sources or proposed additions.

Each capability should have a machine-readable lifecycle state:

```text
candidate -> disabled -> observe -> enforced -> keep
candidate -> disabled -> reject
enforced -> adjust -> keep
enforced -> deprecate -> retire -> delete_candidate
```

The evaluator must decide one of:

- `add`: introduce a missing capability because evidence shows a real gap.
- `keep`: retain a capability because it is still useful, used, and passing.
- `improve`: keep but change the implementation because effect or drift evidence is weak.
- `merge`: combine redundant capabilities that solve the same problem.
- `deprecate`: stop recommending a capability but keep compatibility and evidence.
- `retire`: remove it from active runtime, control packs, or default flows.
- `delete_candidate`: delete only generated, unreviewed, stale, or rejected candidates after proposal-backed cleanup.

Deletion rules:

- Never delete reviewed policy, enabled skills, active gates, target-repo declarations, or evidence history automatically.
- Cleanup must be proposal-backed, path-bounded, and rollbackable.
- Old features qualify for retirement only with evidence such as low usage, repeated failure, replacement coverage, drift, security risk, maintenance cost, or redundant overlap.

## Boundary Matrix
| Capability | Unified governance | Target repo inheritance | Target repo override | Not in hub |
|---|---|---|---|---|
| Risk taxonomy, gate order, evidence, rollback | Own canonical semantics | Inherit by default | Tighten only | Weaken or skip hard gates |
| Codex and Claude Code host support | Govern adapter conformance and degrade posture | Inherit host config templates and checks | Declare `platform_na` or stricter local gate | Duplicate host UI or agent loop |
| Hermes-like skills and self-evolution | Govern skill lifecycle, promotion, and retirement | Inherit disabled or reviewed skills | Add repo-specific facts with provenance | Long-lived assistant persona as product identity |
| OpenHands-style sandboxing | Govern containment profile and evidence contract | Inherit safe execution constraints | Stricter sandbox or local runner | Become a managed coding host |
| SWE-agent-style repair loops | Govern issue-to-task and verification semantics | Inherit task closure and eval contracts | Add domain-specific evals | Benchmark-first product identity |
| Letta/Mem0-style memory | Govern memory scope, provenance, expiry, and retrieval evidence | Inherit knowledge/memory policy | Repo-specific durable facts with expiry | Memory-first assistant platform |
| Aider-style repo map | Govern context map generation and budget metrics | Inherit repo-map artifact contract | Repo-specific include/exclude rules | Replace host context systems |
| OPA or policy-as-code runtime | Own stable policy input/output contract first | Inherit policy input schemas | Stricter local deny/escalate rules | Require Rego before local contract settles |
| MCP gateway and tool registry | Govern tool identity, scope, and audit contract | Inherit allowed tools/resources/prompts | Repo-specific deny lists | Treat MCP as the governance kernel |
| Guardrails and structured output validation | Govern output validation edge | Inherit schemas and validators | Add repo validators | Substitute for runtime/action governance |

## What To Add
- Executable adoption and portfolio classifier with `add`, `keep`, `improve`, `merge`, `deprecate`, `retire`, and `delete_candidate` outcomes.
- Control-pack execution contract, not only metadata.
- Inheritance and override verifier for target repositories.
- One-target proof that a target repo can inherit, override, run, and report effect metrics.
- Governed knowledge and memory lifecycle.
- Governed skill, hook, gate, eval, policy, and workflow promotion lifecycle.
- Repo-map and context-shaping artifact that can prove context benefit or regressions.
- Policy, tool, and credential boundary audit.
- Certification gate that requires effect evidence, not only successful file generation.

## What To Delete Or Weaken
- Host-like UI ambitions that compete with Codex or Claude Code.
- Wrapper-specific flows that cannot be expressed as host adapter capabilities.
- Memory-first persona or assistant identity as a product center.
- Manual duplicate contract copies that drift from repository sources.
- Community mechanism copying without source, acceptance criteria, rollback, and effect metric.

## What To Accelerate
These items should move earlier than broad long-term infrastructure because they directly serve the user's clarified goal:

- control-pack execution contract
- inheritance and override verifier
- effect feedback harness
- knowledge and skill lifecycle
- repo-map/context shaping
- containment and execution evidence vocabulary
- policy/tool/credential audit boundary

## What To Defer
These remain useful, but should not lead the next implementation batch:

- full OPA runtime adoption
- Temporal or equivalent workflow service
- vector database or graph memory backend
- organization gateway product shape
- standalone credential broker
- full OpenHands-like execution host
- Hermes-like messaging gateway
- default multi-agent orchestration

## Executable Roadmap
### GAP-130 Governance Hub Scope Rebaseline
Clarify product scope after the user's Codex/Claude/Hermes boundary correction. Output must update plan, backlog, evidence, and source matrix.

### GAP-131 Extended Borrowing Matrix And Adoption Classifier
Turn external source review and the current feature portfolio into machine-checkable adoption or retirement classes with effect hypotheses.

### GAP-132 Control Pack Execution Contract Upgrade
Define and validate the executable control-pack shape for policy, gates, hooks, evals, workflows, skills, knowledge, and memory.

### GAP-133 Inheritance Override And Forbidden Override Verifier
Mechanize which control-pack fields are unified, inherited, allowed to override, or forbidden to override.

### GAP-134 Target Repo Reuse Effect Feedback Harness
Run at least one real target repo through inherited controls and collect effect metrics.

### GAP-135 Governed Knowledge Memory Lifecycle
Promote AI coding experience into knowledge candidates, skill candidates, and memory records only through evidence and eval.

### GAP-136 Skill Hook Gate Eval Promotion Lifecycle
Make skill/hook/gate/eval/policy/workflow promotion and retirement executable, staged, and rollbackable.

### GAP-137 Repo Map And Context Shaping Integration
Borrow Aider-style repo-map discipline as a governed context artifact with token/effect metrics.

### GAP-138 Policy Tool Credential Audit Boundary
Complete as the fail-closed audit boundary for tool identity, credential scope, host actions, and target-repo override limits without becoming an IAM platform.

### GAP-139 Governance Hub Certification With Effect Metrics
Complete as the executable certification package proving that the governance hub, reusable contract, and controlled evolution loop produce measurable effect on at least one target repo, can keep or remove capabilities based on evidence, and do not compete with Codex or Claude Code.

### GAP-140 Target Repo Host Capability Recovery Follow-On
Translate the live `target-repo-reuse-host-capability-gap` candidate into bounded remediation or explicit defer evidence. The work must keep host cooperation boundaries explicit and must not claim restored `native_attach` posture until fresh target-run evidence proves it.

### GAP-141 Historical Problem Trace Closure Window
Turn the live `target-repo-reuse-historical-problem-trace` candidate into a governed closure rule for rolling KPI windows and effect reports, separating historical problem visibility from current pass-state claims.

## Verification Standard
Planning completion requires:

- backlog entries for `GAP-130..141`
- machine-readable issue seeds for `GAP-130..141`
- issue-render script support for the new queue
- source matrix update
- evidence entry
- docs and script validation

Implementation completion for later gaps requires:

- runnable command
- checked artifact or schema
- real target repo feedback where applicable
- evidence under `docs/change-evidence/`
- rollback path
- no claim that a planned capability is live before its gate passes

## Refreshed Primary Source Set
- OpenAI Codex AGENTS guidance: <https://github.com/openai/codex/blob/main/docs/agents_md.md>
- Claude Code memory, hooks, and settings: <https://docs.anthropic.com/en/docs/claude-code/memory>, <https://docs.anthropic.com/en/docs/claude-code/hooks>, <https://docs.anthropic.com/en/docs/claude-code/settings>
- Model Context Protocol: <https://modelcontextprotocol.io/>
- OPA policy as code: <https://www.openpolicyagent.org/docs>
- LangGraph persistence and human-in-the-loop: <https://docs.langchain.com/oss/python/langgraph/persistence>, <https://docs.langchain.com/oss/python/langgraph/human-in-the-loop>
- Aider repo map: <https://aider.chat/docs/repomap.html>
- Letta memory: <https://docs.letta.com/guides/agents/memory>
- Mem0 memory: <https://docs.mem0.ai/overview>
- OpenHands: <https://github.com/OpenHands/OpenHands>
- SWE-agent: <https://github.com/SWE-agent/SWE-agent>
- OpenAI Cookbook evals: <https://cookbook.openai.com/topic/evals>
