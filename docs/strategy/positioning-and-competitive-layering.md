# Positioning And Competitive Layering

## One-Line Position
`governed-ai-coding-runtime` is a governance/runtime layer for AI coding agents. It is not a host replacement, not a wrapper-first product identity, and not a generation-guardrail product.

## Current Phase
- Local single-machine baseline is complete through `Maintenance Baseline / GAP-034`.
- `Strategy Alignment Gates / GAP-040` through `GAP-044` are complete on the current branch baseline.
- The active next-step implementation queue remains `Interactive Session Productization / GAP-035` through `GAP-039`.

## Final-State Shorthand
The target product shape remains:

`Repo-native Contract Bundle + Host Adapters + Policy Decision Interface + Verification and Delivery Plane`

This shorthand names the external product surfaces, not the entire internal runtime. The hybrid final state underneath those surfaces is:
- repo-local contract bundle or light pack in the target repository
- machine-local durable governance kernel for task, approval, evidence, artifact, replay, and rollback state
- attach-first host-adapter layer with explicit launch-second fallback
- same-contract verification and delivery plane shared by local execution and CI

In practice that means:
- repo-local declarations stay lightweight and versioned
- host adapters integrate Codex-first flows without becoming Codex-only
- policy decisions are explicit and auditable
- local and CI consume the same contract inputs
- evidence, handoff, replay, and rollback stay first-class

## Non-Goals
- another AI coding host, IDE shell, or terminal shell
- another multi-agent orchestration wrapper as the product center
- an enterprise gateway platform as the default deployment shape
- an execution-host platform that competes directly with OpenHands, SWE-agent, or Hermes
- a generation-guardrail or output-filtering product

## Competitive Layering

### 1. Execution Hosts
Examples: Codex, Claude Code, Cursor, Windsurf, OpenHands, SWE-agent, Hermes.

These products execute work, own the main interaction loop, and increasingly absorb UX, tooling, and automation features. This repository should integrate with them, not compete with them on host experience.

### 2. Wrapper And Orchestration Tools
Examples: oh-my-codex, oh-my-claudecode, GAAI-style repo packs.

These tools improve setup, hooks, teams, skills, or wrapper ergonomics around hosts. They are useful input for adapter expectations and repo-local pack ergonomics, but they should not redefine the product identity here.

### 3. Governance And Control-Plane Systems
Examples: Microsoft Agent Governance Toolkit, Keycard, Coder AI Governance, OPA-backed policy systems.

This is the closest adjacent layer. The useful borrowing target is explicit policy boundaries, auditability, scoped authorization, and gateway deployment patterns. The project still stays local-first and repo-native by default.

### 4. Generation Guardrails
Examples: NVIDIA NeMo Guardrails, Guardrails AI.

These products focus on what the model says or emits. This repository focuses on what the agent is allowed to do, how it is verified, and how the result is handed off and rolled back. The distinction must stay explicit.

## Why This Boundary Is Better
- Host features move quickly and are increasingly commoditized.
- Governance, verification, evidence, and rollback stay valuable across hosts.
- Repo-native declarations give the project portability and reviewability.
- Keeping policy decisions separate from adapters lowers future integration risk.
- CI using the same contract as local execution reduces drift and makes bypasses less dangerous.

## How External References Are Used
- The borrowing matrix controls mechanism intake and prevents identity drift: [Runtime Governance Borrowing Matrix](../research/runtime-governance-borrowing-matrix.md).
- Historical local-baseline code is interpreted through the migration bridge, not treated as the final boundary: [Local Baseline To Hybrid Final-State Migration Matrix](../architecture/local-baseline-to-hybrid-final-state-migration-matrix.md).
- Repo-local bundle work is constrained by the source-of-truth decision and bundle architecture, not by wrapper conventions alone.

## Working Rule
Do not compete with the host. Govern the host.
