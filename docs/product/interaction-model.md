# Governed AI Coding Runtime Interaction Model

## Purpose
Define the product goal, user-facing capabilities, working model, and the minimum interaction surfaces required for `governed-ai-coding-runtime`.

## Product Thesis
`governed-ai-coding-runtime` is not another IDE copilot and not a generic enterprise agent platform.

It is a governed runtime around AI coding agents that makes coding execution:
- scoped
- approval-aware
- verifiable
- evidence-backed
- replayable

The product's job is to wrap agent execution in deterministic control-plane rules rather than to replace the agent itself.

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

## Core Product Capabilities
- task intake with goal, scope, acceptance criteria, and budgets
- repo profile resolution
- control pack selection and admission checks
- governed workspace or worktree startup
- tool policy enforcement
- risk classification and approval interruption
- ordered verification gates
- evidence bundle and handoff bundle generation
- failure replay and rollback reference capture

## Canonical Workflow

### 1. Create task
The user submits a coding task with goal, scope, acceptance criteria, and target repository.

### 2. Load repo policy
The runtime resolves the repository profile: tool allowlist, path scope, gate commands, risk defaults, and handoff format.

### 3. Start governed session
The system creates an isolated workspace, sets budgets, injects context, and starts the selected agent behind the governed tool runner.

### 4. Plan and bounded execution
The agent inspects code, proposes or follows a plan, and requests tools through policy-checked interfaces.

### 5. Approval interruption
High-risk actions pause the workflow until a human approves, rejects, cancels, or lets the request expire.

### 6. Verification
The runtime executes quick or full gates in canonical order and persists outputs into evidence.

### 7. Delivery handoff
The user receives a final bundle containing changed files, commands run, verification state, approvals, rollback reference, and open questions.

## Interaction Surfaces

### Required
- API: task lifecycle, approvals, evidence retrieval, replay, and registry operations
- CLI or scripted entrypoint: useful for early operator workflows and automation
- Minimal web console: approvals, task detail, evidence, and failed-run inspection

### Not Required As Product Core
- full IDE experience
- chat-first interface as the primary surface
- autonomous multi-agent orchestration UI

## UI Position
The UI is necessary, but it is a control-plane console rather than the core product identity.

The minimum useful UI should cover:
- task list
- task detail
- pending approvals
- verification results
- evidence and audit timeline
- failed run inspection
- replay / handoff entrypoints

Without this UI, approval and audit workflows become operationally awkward. With too much UI, the product risks drifting toward an IDE shell instead of a governed runtime.

## Delivery Model
- API-first for integration
- console-backed for human approval and inspection
- agent-agnostic at the execution boundary
- repo-aware at task startup and verification time

## Product Boundaries

### In scope
- governed AI coding execution
- repository-aware controls
- approvals, verification, evidence, replay, rollback references

### Out of scope for MVP
- generic enterprise automation
- memory-first personalization platform
- default multi-agent orchestration
- deployment automation as the default completion step

## Success Signals
- users can start from a task instead of a chat
- risky actions pause reliably
- task completion and validated completion are not conflated
- reviewers can understand AI work from evidence without reconstructing the session
- interrupted work can resume or replay from durable state
