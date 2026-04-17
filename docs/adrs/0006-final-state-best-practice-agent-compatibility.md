# ADR-0006: Final-State Best Practice And Agent Compatibility

## Status
Accepted

## Date
2026-04-17

## Context
The project is intentionally focused on governed AI coding execution rather than building another coding assistant, IDE, or generic agent platform.

Upstream AI coding products such as Codex CLI/App, Claude Code, OpenClaw, Hermes, and future agent products will continue to improve quickly. If this project competes with them on model capability, chat UX, autonomous coding breadth, or IDE surface area, it will become redundant or burdensome.

At the same time, stronger upstream agents do not remove the need for repository-owned governance. Real engineering work still needs durable tasks, scoped execution, approval semantics, evidence, verification, auditability, and rollback references that remain stable across tools and product generations.

## Decision
Use final-state best practice as the long-term product target.

This means the project should aim for the best governed AI coding runtime design we can define, not merely a short-lived MVP wrapper. The final state should be:
- agent-agnostic
- product-shape tolerant
- governance-kernel centered
- evidence-first
- low-friction for low-risk work
- strict only where risk justifies it
- compatible with current Codex CLI/App usage
- adaptable to future agent products through contracts rather than product-specific assumptions

Final-state best practice does not mean implementing the full target stack in the first slice. The MVP remains a tracer bullet that proves the smallest governed loop while preserving the architecture needed for the final state.

## Governance Friction Model
Governance must not become a blanket slowdown layer.

The runtime should support graduated enforcement modes:
- `observe_only`: record activity and evidence without blocking agent work.
- `advisory`: warn, classify risk, and recommend gates without mandatory interruption.
- `enforced`: require approval, verification, and rollback references for medium/high-risk actions.
- `strict`: require stronger controls for production-adjacent, dependency, CI, release, secrets-adjacent, or broad write operations.

The default target is minimum necessary friction:
- low-risk read, search, plan, local edit, and verification paths should stay fast
- high-risk writes should pause predictably
- repeated approvals should be avoided when one scoped approval safely covers a bounded action set
- upstream sandbox and approval mechanisms should be reused where they are sufficient, not duplicated for ceremony

## Agent Compatibility Model
Compatibility should be based on declared capabilities rather than product identity.

The kernel should define an agent adapter contract that can describe:
- invocation mode: interactive, non-interactive, MCP, app server, IDE bridge, browser/UI automation, or manual handoff
- authentication ownership: user-owned upstream auth, service-owned auth, or unsupported
- workspace control: external workspace, managed worktree, sandbox, or read-only inspection
- tool visibility: structured tool events, JSONL events, logs only, or no event stream
- mutation model: direct writes, patch output, git diff, pull request, or handoff-only
- continuation model: resume, fork, session id, stateless, or manual
- evidence model: structured trace, command log, transcript, diff, or external artifact

The first-class early adapter should support the user's current Codex CLI/App workflow without taking ownership of Codex authentication. The governed runtime should create or select the workspace, inject repo profile context, run Codex through supported entrypoints where possible, collect output and diffs, run gates, and produce evidence.

Future products such as OpenClaw, Hermes, IDE plugins, cloud agents, and unknown agent forms should integrate by mapping their capabilities into the same adapter contract. Products that cannot expose enough control should degrade to observe-only, advisory, or manual-handoff modes rather than forcing a fragile deep integration.

## Consequences
- The PRD and architecture should describe final-state best practice as the north star.
- MVP planning must still prioritize the smallest governed loop and avoid platform breadth before proof.
- Compatibility work should start with Codex CLI/App but must not hardcode Codex semantics into the governance kernel.
- The project should treat agent products as replaceable execution frontends.
- The project should treat task lifecycle, policy, approval, evidence, verification, and rollback semantics as durable kernel contracts.
- Governance should be measured by risk reduction and delivery confidence, not by number of interruptions.
- Any future deep integration with a specific agent product must remain an adapter, not a kernel dependency.

## Alternatives Considered

### Keep MVP-only positioning
- Pros: lower near-term scope and less documentation churn
- Cons: under-specifies long-term compatibility and makes it easier to build a disposable wrapper
- Rejected: the project needs a clear final-state target to avoid early architectural dead ends

### Build a strict governance wrapper around every agent action
- Pros: maximum control and audit detail
- Cons: high friction, poor user experience, and likely to suppress stronger upstream agent capabilities
- Rejected: governance must be risk-proportional

### Optimize only for Codex CLI/App
- Pros: best near-term fit for the user's current workflow
- Cons: creates product lock-in and weakens compatibility with future agent shapes
- Rejected as kernel strategy; accepted only as the first adapter priority

### Build a new IDE or agent app
- Pros: full UX control
- Cons: competes directly with upstream tools and expands scope away from governance
- Rejected: the product identity remains a governed runtime and control layer
