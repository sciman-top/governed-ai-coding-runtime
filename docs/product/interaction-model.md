# Governed AI Coding Runtime Interaction Model

## Purpose
Define the product goal, user-facing capabilities, working model, and the minimum interaction surfaces required for `governed-ai-coding-runtime`.

## Product Thesis
`governed-ai-coding-runtime` is not another IDE copilot, not a generic enterprise agent platform, and not a replacement chat shell for upstream AI tools.

It is a governed runtime layer around AI coding sessions that makes coding execution:
- scoped
- approval-aware
- verifiable
- evidence-backed
- replayable
- portable across repositories
- compatible across agent product shapes

The product's job is to wrap agent execution in deterministic control-plane rules rather than to replace the agent itself.

Final-state best practice means risk-proportional governance, not maximum friction. Low-risk exploration and local iteration should stay fast. Medium and high-risk actions should receive the approval, verification, evidence, and rollback controls that real engineering work requires.

## Current Baseline
The repository has already landed a local runtime baseline through `GAP-034`:

- local task and evidence runtime
- local verification and doctor gates
- local operator surface
- local packaging and quickstart
- explicit compatibility, maintenance, and degrade policy

That baseline is a prerequisite, not the final product boundary. The next active product queue is generic, interactive, attach-first session productization.

## Primary Users

### Solo developer
Needs a controlled way to let an AI inspect, plan, edit, verify, and hand off repository work without losing traceability.

### Repository owner or maintainer
Needs repository-specific rules, approval posture, and delivery evidence so AI-generated work can be reviewed like normal engineering work.

### Reviewer
Needs a concise handoff package: what changed, what was run, what passed, what was approved, and what remains risky.

## Core User Goals
- Start work from a durable task rather than an ad hoc chat.
- Attach repository-specific rules automatically.
- Prevent risky actions from executing silently.
- Preserve a complete execution trail.
- Resume or replay interrupted work.
- Distinguish "agent produced output" from "validated delivery."
- Keep using preferred agent products without making governance dependent on one vendor or UI shape.
- Reuse the same runtime across many repositories without copying the kernel into each one.

## Core Product Capabilities
- task intake with goal, scope, acceptance criteria, and budgets
- repo profile resolution
- repo-local light pack generation or validation
- machine-local runtime binding
- attach-first session bridge with governed in-session commands
- launch-second fallback for weaker upstream tools
- tool policy enforcement
- risk classification and approval interruption
- graduated governance modes: observe-only, advisory, enforced, and strict
- agent adapter contract for native attach, process bridge, and manual-handoff shapes
- ordered verification gates
- evidence bundle and handoff bundle generation
- failure replay, rollback reference capture, and trial feedback capture

## Canonical Workflow

### 1. Attach repository
The user selects a target repository. The runtime validates or creates the repo-local light pack and binds the repo to machine-local runtime state.

### 2. Bind governed task
The user or session creates a coding task with goal, scope, acceptance criteria, budgets, and adapter posture.

### 3. Attach governed session
The runtime attaches to the active AI coding session when possible. If attach is unavailable, it falls back to launch mode.

### 4. Plan and bounded execution
The agent inspects code, proposes or follows a plan, and requests tools through policy-checked interfaces.

### 5. Approval interruption
High-risk actions pause the workflow until a human approves, rejects, cancels, or lets the request expire.

### 6. Verification
The runtime executes quick or full gates in canonical order and persists outputs into evidence.

### 7. Delivery handoff and trial feedback
The user receives a final bundle containing changed files, commands run, verification state, approvals, rollback reference, open questions, and any onboarding or adapter gaps surfaced during execution.

## Interaction Surfaces

### Required
- Session bridge: governed actions callable inside an active AI coding session
- API: task lifecycle, approvals, evidence retrieval, replay, and registry operations
- Minimal web or local console: approvals, task detail, evidence, and failed-run inspection
- CLI or scripted entrypoint: useful for automation, replay, recovery, and fallback launch mode
- Agent adapter contract: maps product-specific execution frontends into stable runtime capabilities

### Not Required As Product Core
- full IDE experience
- a replacement chat UI as the primary surface
- autonomous multi-agent orchestration UI
- ownership of upstream agent authentication

## UI Position
The UI is necessary, but it is a control-plane console rather than the core product identity.

The minimum useful console should cover:
- task list
- task detail
- pending approvals
- verification results
- evidence and audit timeline
- failed run inspection
- replay and handoff entrypoints

The higher-priority interactive surface is the session bridge inside the active AI coding workflow. The console remains essential for inspection, approvals, and recovery.

## Delivery Model
- attach-first for existing AI coding sessions
- launch-second when attach is unavailable
- API-first for integration
- console-backed for human approval and inspection
- agent-agnostic at the execution boundary
- Codex CLI/App as the first direct adapter priority
- repo-aware at task startup and verification time

## Agent Compatibility Position
The runtime should treat AI coding products as replaceable execution frontends. The kernel should not know whether the active frontend is Codex CLI/App, Claude Code, an IDE plugin, a cloud coding worker, browser automation, or a future agent product.

Adapters should declare capabilities:
- invocation mode
- authentication ownership
- workspace control
- tool and event visibility
- mutation model
- continuation or resume model
- evidence export model
- attach strength or compatibility tier

If an agent product exposes enough structure, the runtime can enforce policy before or during execution. If it exposes limited structure, the runtime should degrade to observe-only, advisory, or manual-handoff mode while still running repository gates and capturing delivery evidence.

## Product Boundaries

### In scope
- governed AI coding execution
- repository-aware controls
- approvals, verification, evidence, replay, rollback references
- repo-local light packs plus machine-local runtime state
- agent adapter contracts and risk-proportional governance modes
- multi-repo trial feedback loops

### Out of scope for MVP and baseline stages
- generic enterprise automation
- memory-first personalization platform
- default multi-agent orchestration
- deployment automation as the default completion step
- building a replacement UX for upstream AI coding products

## Success Signals
- users can start from a task instead of a chat
- risky actions pause reliably
- task completion and validated completion are not conflated
- reviewers can understand AI work from evidence without reconstructing the session
- interrupted work can resume or replay from durable state
- governance reduces high-risk ambiguity without slowing down ordinary low-risk coding flow
- new repositories can attach through light packs without kernel rewrites
- new agent products can be integrated by capability mapping instead of kernel rewrites
