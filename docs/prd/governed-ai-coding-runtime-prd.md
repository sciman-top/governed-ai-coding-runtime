# Governed AI Coding Runtime PRD

## Document Map

- Product:
  - `docs/product/interaction-model.md`
- Architecture:
  - `docs/architecture/governed-ai-coding-runtime-target-architecture.md`
  - `docs/architecture/minimum-viable-governance-loop.md`
  - `docs/architecture/governance-boundary-matrix.md`
- Roadmap:
  - `docs/roadmap/governed-ai-coding-runtime-90-day-plan.md`
  - `docs/backlog/mvp-backlog-seeds.md`
- ADRs:
  - `docs/adrs/0001-control-plane-first.md`
  - `docs/adrs/0002-no-multi-repo-distribution-in-mvp.md`
  - `docs/adrs/0003-single-agent-baseline-first.md`
  - `docs/adrs/0004-rename-project-to-governed-ai-coding-runtime.md`
  - `docs/adrs/0005-governance-kernel-and-control-packs-before-platform-breadth.md`
- Specs:
  - `docs/specs/control-registry-spec.md`
  - `docs/specs/control-pack-spec.md`
  - `docs/specs/repo-profile-spec.md`
  - `docs/specs/tool-contract-spec.md`
  - `docs/specs/hook-contract-spec.md`
  - `docs/specs/skill-manifest-spec.md`
  - `docs/specs/knowledge-source-spec.md`
  - `docs/specs/waiver-and-exception-spec.md`
  - `docs/specs/provenance-and-attestation-spec.md`
  - `docs/specs/repo-map-context-shaping-spec.md`
  - `docs/specs/risk-tier-and-approval-spec.md`
  - `docs/specs/task-lifecycle-and-state-machine-spec.md`
  - `docs/specs/evidence-bundle-spec.md`
  - `docs/specs/verification-gates-spec.md`
  - `docs/specs/eval-and-trace-grading-spec.md`
- Research:
  - `docs/research/benchmark-and-borrowing-notes.md`
  - `docs/research/repo-governance-hub-borrowing-review.md`

## Problem Statement

AI coding tools are already good at reading code, drafting changes, and suggesting fixes, but they are still weak at governed execution. In real coding work, the hard part is not just "can the model write code" but "can the whole system execute coding tasks safely, consistently, and recoverably across real repositories."

From the user's perspective, the current pain points are:

- AI coding sessions are usually ephemeral and poorly governed.
- There is no strong boundary between "low-risk reasoning" and "high-risk real-world action."
- Tool access is often too broad, too implicit, or too loosely audited.
- Long-running tasks break when the session ends, the model drifts, or a human needs to intervene.
- Build, test, lint, contract, and repository-specific validation are not consistently enforced as part of one task state machine.
- High-risk actions such as mass edits, CI changes, branch pushes, dependency upgrades, secret-adjacent changes, and deploy-adjacent commands need approvals, but most AI coding tools do not model approvals as a first-class runtime concern.
- There is rarely a complete evidence trail that ties together task intent, context snapshot, commands run, files changed, validation outcomes, approvals, and rollback points.
- When AI-generated changes fail, the human often has to manually reconstruct what happened instead of replaying the task or resuming from a known state.

The problem to solve is therefore:

Create a governed execution platform for AI coding that allows developers to use their preferred coding agents while placing those agents inside a deterministic runtime shell that controls scope, permissions, approvals, validation, auditing, and rollback.

## Solution

The solution is a governed runtime platform for AI coding sessions.

From the user's perspective, the platform works like this:

- A developer creates or receives a coding task against a target repository.
- The platform converts that request into a governed task with scope, acceptance criteria, risk level, and execution budget.
- The platform loads the repository profile, allowed tools, verification gates, and approval rules for that repository.
- The developer starts an AI coding session through the platform using a supported agent.
- The AI can inspect code, draft a plan, edit files, and run safe commands inside a governed execution environment.
- Before any high-risk action, the platform pauses execution and requires explicit approval.
- The platform records every important action and validation result as evidence.
- At the end of the task, the platform produces a validated output package: summary, changed files, verification results, open risks, and rollback information.
- If the task fails or is interrupted, the platform can pause, resume, rerun, compensate, or hand off to a human instead of losing execution state.

The product is not a new IDE and not a generic chatbot. It is the governed runtime and control layer around AI coding agents.

Its core user value is:

- safer AI coding
- repeatable AI coding
- auditable AI coding
- recoverable AI coding
- repository-aware AI coding

## Product Goals

### Primary Goals
- Make AI coding tasks governable without forcing users to abandon their preferred coding agents.
- Turn repository-aware AI coding into a stateful, validated workflow rather than a one-shot chat interaction.
- Make approvals, evidence, validation, replay, and rollback first-class runtime behaviors.

### Secondary Goals
- Allow the same governed runtime model to work across multiple repositories through repository profiles.
- Enable gradual rollout from solo usage to small-team usage without redesigning the core control model.

### Non-Goals
- Building a new IDE.
- Replacing all coding agents with one proprietary interface.
- Making fully autonomous multi-agent behavior the default.
- Turning the MVP into a generic enterprise automation platform.

## MVP Capability Boundary

The MVP must support the following end-to-end coding loop:

1. Task intake
2. Repository profile loading
3. Governed AI coding session startup
4. Tool-governed reasoning and execution
5. Approval interruption for risky actions
6. Build / test / lint / typecheck / contract-style verification
7. Evidence bundle generation
8. Handoff output for commit / PR preparation

### MVP Functional Requirements
- The platform must model a coding task as a durable object with goal, scope, acceptance criteria, target repository, budgets, approvals, validations, and evidence.
- The platform must support repository profiles that declare build, test, lint, typecheck, contract, and invariant commands.
- The platform must support a governed tool layer for shell, file mutation, git, browser, package manager, and repository-aware helper tools.
- The platform must classify actions into at least three governance buckets: safe, approval-required, and blocked.
- The platform must support explicit pause and resume across long-running tasks.
- The platform must persist validation outcomes as task-level evidence.
- The platform must support isolated execution workspaces or worktrees.
- The platform must emit a structured handoff package at task completion.

### Explicitly Deferred From MVP
- Full A2A federation
- Distributed multi-agent collaboration by default
- Memory-first personalization stack
- Automatic policy promotion
- Automatic rule modification
- Deployment automation as a default completion step

## Governance Ownership Model

This product needs a strict ownership split between platform-level governance and repository-level customization.

### Unified Governance
- task model and lifecycle
- approval semantics
- risk taxonomy
- tool contract and execution semantics
- evidence and audit schema
- replay / rollback model
- eval categories and minimum quality gates

### Repository Inheritance
- build / test / lint / typecheck commands
- contract / invariant commands
- repository path scope
- repository-specific validation commands
- repository-specific handoff hints

### Repository Override
- additional risky command patterns
- repo-specific blocked paths
- repo-specific approval escalation rules
- repo-specific context shaping hints
- repo-specific verification augmentations

### Not Owned By The Platform
- repository business logic
- application-specific product policy
- full release governance for all deployment types in MVP
- long-term autonomous memory optimization

Reference:
- `docs/architecture/governance-boundary-matrix.md`

## Benchmark and Borrowing Principles

The product should explicitly borrow mechanisms, not whole product identities.

- Borrow from `LangGraph`: durable execution, interrupt-based human review, resumable state.
- Borrow from `OpenHands`: runtime isolation and sandbox-centered coding execution.
- Borrow from `SWE-agent`: issue-to-task execution loop and repository-grounded repair flow.
- Borrow from `Aider repo map`: compact repository context shaping rather than naive full-repo stuffing.
- Borrow from `Cline`: fine-grained tool approval ergonomics and explicit permission surfaces.
- Borrow from `OpenAI Cookbook` and official docs: structured outputs, tool use patterns, evals, safety, conversation state concepts.
- Borrow selectively from `Mem0` and `Letta`: memory layering concepts, but not a memory-first product architecture in MVP.

The product should not:
- become graph-first because LangGraph is graph-first
- become IDE-first because OpenHands or Cline present a strong UX shell
- become benchmark-first because SWE-agent performs well on coding benchmarks
- become memory-first because Letta or Mem0 emphasize persistent memory

Detailed comparison notes live in:
- `docs/research/benchmark-and-borrowing-notes.md`

## User Stories

1. As a solo developer, I want to submit a coding task against a repository, so that the AI starts from a scoped, trackable unit of work rather than an ad hoc chat.
2. As a solo developer, I want the platform to attach the repository's build, test, and verification commands automatically, so that the AI uses the correct engineering gates without me repeating them every time.
3. As a solo developer, I want the platform to limit the AI to an approved tool set, so that the agent cannot freely execute unsafe commands.
4. As a solo developer, I want to see the exact task scope before execution begins, so that I can catch goal drift early.
5. As a solo developer, I want the platform to create a resumable task state, so that I can continue a long coding session after interruption.
6. As a solo developer, I want the AI to propose a plan before making large changes, so that I can decide whether to proceed.
7. As a solo developer, I want the platform to classify actions by risk, so that low-risk work flows quickly while high-risk work is gated.
8. As a solo developer, I want file writes, shell commands, git actions, and package manager operations to be policy-checked, so that the AI coding workflow is governed consistently.
9. As a solo developer, I want large or destructive edits to require explicit approval, so that I stay in control of risky changes.
10. As a solo developer, I want the platform to register rollback points before risky writes, so that failed changes can be undone safely.
11. As a solo developer, I want the AI to run build and test commands through the platform, so that validation results are attached to the task automatically.
12. As a solo developer, I want repository-specific contract and invariant checks to run as part of task completion, so that "AI passed unit tests" is not mistaken for "change is safe."
13. As a solo developer, I want every coding task to produce an evidence bundle, so that I can review what happened without reconstructing it manually.
14. As a solo developer, I want a clear summary of changed files, commands run, validations passed, and open risks, so that review is fast.
15. As a solo developer, I want failed tasks to be replayable, so that I can debug the failure path instead of starting from zero.
16. As a solo developer, I want the platform to stop execution when token, time, or cost budgets are exceeded, so that the AI does not drift indefinitely.
17. As a solo developer, I want the platform to support isolated workspaces or worktrees, so that AI-generated changes do not pollute my main working directory.
18. As a solo developer, I want the AI to be repository-aware, so that it uses the right commands, conventions, and review gates for each repo.
19. As a repository owner, I want repository profiles to define allowed tools and required gates, so that governance is consistent per repo.
20. As a repository owner, I want to mark certain commands or operations as approval-required, so that dangerous actions cannot run unattended.
21. As a repository owner, I want to version policies and prompt/tool registries, so that changes to runtime behavior are traceable.
22. As a repository owner, I want to know which tasks changed CI, package dependencies, workflow files, secrets-adjacent configuration, or release logic, so that I can review these with more scrutiny.
23. As a repository owner, I want the platform to capture task intent and acceptance criteria, so that I can judge whether the AI solved the right problem.
24. As a repository owner, I want task state transitions to be deterministic, so that "completed" always means validation and gating actually happened.
25. As a security-minded user, I want the platform to treat tool governance as a first-class system concern, so that AI tool use is not governed only by prompt wording.
26. As a security-minded user, I want the platform to deny unauthorized writes by default, so that the safe path is the default path.
27. As a security-minded user, I want approval decisions and policy results to be auditable, so that post-incident review is possible.
28. As a security-minded user, I want high-risk actions to be explicitly categorized, so that I can tune review burden without hand-curating every task.
29. As a platform maintainer, I want a clear separation between control plane and execution plane, so that governance does not get entangled with agent implementation details.
30. As a platform maintainer, I want durable workflows to model pause, resume, timeout, retry, and compensation, so that long coding tasks behave predictably.
31. As a platform maintainer, I want tool adapters to use typed contracts, so that tool validation and execution stay stable across agents.
32. As a platform maintainer, I want a registry of repository profiles, tools, prompts, and policies, so that runtime behavior is configurable and inspectable.
33. As a platform maintainer, I want eval and regression checks to run against the platform, so that runtime changes do not silently degrade coding outcomes.
34. As a platform maintainer, I want task replay and audit visualization in a console, so that failures can be analyzed without digging through raw logs.
35. As a developer reviewing AI-generated changes, I want a generated handoff package for commit or PR preparation, so that AI work integrates into standard engineering workflows.
36. As a developer reviewing AI-generated changes, I want to see whether the change was fully validated or only partially validated, so that I can decide whether more manual review is needed.
37. As a developer using different agents, I want the platform to work with multiple AI coding front-ends, so that I am not locked into one model or one interface.
38. As a developer using local and remote repos, I want repository onboarding to be simple and repeatable, so that new repos can adopt governed AI coding incrementally.
39. As a developer with interrupted work, I want the platform to preserve task context, evidence, and validation state, so that I do not lose progress when the agent session ends.
40. As a future team user, I want the platform to support approvals, traceability, and consistent repository policies, so that it can scale from solo usage to collaborative governance later.

## Acceptance Metrics

The MVP should define success using operational metrics, not just feature completion.

### Core Product Metrics
- task completion rate
- validated completion rate
- approval interruption rate
- replay success rate
- rollback success rate
- evidence completeness rate
- verification pass rate
- human handoff quality rate

### Failure Metrics
- unauthorized action block rate
- false-positive approval rate
- task timeout rate
- tool execution failure rate
- partial-validation completion rate

### Quality Metrics
- percentage of tasks with full evidence bundle
- percentage of tasks with repository-specific gates executed
- percentage of high-risk actions correctly intercepted
- regression pass rate on runtime changes
- safety eval pass rate

## Implementation Decisions

Implementation should follow the adopted decision chain:
- `ADR-0001`: control-plane-first
- `ADR-0002`: no multi-repo distribution in MVP
- `ADR-0003`: single-agent baseline first
- `ADR-0005`: governance kernel and control packs before platform breadth

The active naming decision is captured by:
- `ADR-0004`: rename project to Governed AI Coding Runtime

Implementation contracts should be taken from:
- `docs/specs/control-registry-spec.md`
- `docs/specs/control-pack-spec.md`
- `docs/specs/repo-profile-spec.md`
- `docs/specs/tool-contract-spec.md`
- `docs/specs/hook-contract-spec.md`
- `docs/specs/skill-manifest-spec.md`
- `docs/specs/knowledge-source-spec.md`
- `docs/specs/waiver-and-exception-spec.md`
- `docs/specs/provenance-and-attestation-spec.md`
- `docs/specs/repo-map-context-shaping-spec.md`
- `docs/specs/risk-tier-and-approval-spec.md`
- `docs/specs/task-lifecycle-and-state-machine-spec.md`
- `docs/specs/evidence-bundle-spec.md`
- `docs/specs/verification-gates-spec.md`

- The product will target AI coding first, not generic enterprise automation. This keeps the MVP focused on repository-bound engineering tasks.
- The primary architecture will be control-plane-first with durable workflows for task execution and deterministic policy enforcement for governance-critical decisions.
- The initial product model will be "single-agent baseline inside a governed shell," not multi-agent by default.
- The platform will define a task object as the core execution unit. A task will carry goal, scope, acceptance criteria, repo target, risk level, execution budgets, approvals, evidence, and validation outcomes.
- Repository onboarding will be based on repository profiles that define the repository's commands, allowed tools, approval rules, and required gates.
- High-risk actions will be modeled explicitly, not inferred only through prompt behavior. Risk classes will drive approval and execution behavior.
- Tool execution will be separated from agent reasoning. The agent can request tool use, but a deterministic tool governance layer must validate the request before execution.
- The system will distinguish between safe tools, approval-required tools, and blocked tools.
- The platform will support isolated execution environments for AI coding tasks so that repository mutations happen in controlled workspaces rather than arbitrary live directories.
- Build, test, lint, typecheck, and repository-specific contract/invariant checks will be modeled as part of task lifecycle completion, not optional post-processing.
- Approval will be a first-class runtime concept. High-risk task steps will pause the workflow until approval is granted, rejected, revoked, or timed out.
- Rollback points will be registered for risky write operations so that execution failure can transition into compensation or recovery paths.
- Evidence capture will include task definition, context snapshot, commands run, tool calls, changed files, validation outputs, approval events, and final outcome.
- Audit and evidence will be append-oriented and queryable from a console so that the user can replay or inspect task history.
- The console will focus on task review, approvals, evidence inspection, validation outcomes, and failure analysis before it expands into broader admin features.
- The platform must support multiple AI coding agents as execution front-ends, but the governance model must remain stable regardless of which agent is used.
- Policy, prompt, tool, and repository-profile definitions will be versioned so that runtime behavior changes can be traced and evaluated.
- Evaluation will include final outcome quality, trajectory quality, regression, and safety checks. The platform must be testable as a governed runtime, not only as a coding assistant.
- The MVP will optimize for a solo developer using one or a few repositories, while leaving room to scale toward team usage later.
- Repository profiles will be a first-class product concept, not an implementation detail. They will define inherited defaults and bounded override points.
- Hooks and gates will be treated differently: hooks may be repository-local integration points, but gates remain platform-governed completion criteria.
- Long-term memory will not be a first-class MVP dependency. The MVP will prefer task-local evidence, replayability, and repository profiles over self-evolving memory.
- Repository context shaping should be explicit and compact. The platform should support a repo map or symbol graph style abstraction rather than forcing full-repository prompt stuffing.

## Testing Decisions

Testing should evolve in this order:
- Phase 1: validate the minimum governance loop
- Phase 2: validate verification gates and evidence bundle completeness
- Phase 3: add eval freshness, trace grading, and replay readiness checks

Reference specs:
- `docs/specs/verification-gates-spec.md`
- `docs/specs/eval-and-trace-grading-spec.md`
- `docs/specs/evidence-bundle-spec.md`

- A good test proves externally observable behavior, not internal implementation details. The platform should be tested by task outcomes, state transitions, approvals, validation results, evidence integrity, and rollback behavior.
- The task state machine must be tested to ensure only valid transitions occur and that approval, timeout, retry, and failure paths behave correctly.
- The repository profile and policy layer must be tested to ensure the correct tools, commands, and approvals are enforced per repository.
- The tool governance layer must be tested to ensure unauthorized or malformed tool requests fail closed.
- The workflow runtime must be tested for pause, resume, timeout, retry, and compensation behavior.
- The approval flow must be tested for create, approve, reject, revoke, and timeout behavior, including evidence and audit emission.
- The evidence and audit pipeline must be tested to ensure that key events are persisted and replayable.
- The verification pipeline must be tested to ensure required gates run before a task is marked complete.
- The console must be tested against task review workflows, approval workflows, and failed-task inspection flows.
- Evaluation and regression tests must confirm that policy or runtime changes do not silently weaken safety or governance guarantees.
- Prior art inside the target codebase does not exist yet, because the repository is being created greenfield. Early test design should therefore borrow quality patterns from the existing governance ecosystem: deterministic gate checks, contract verification, failure replay readiness, and evidence-oriented validation.
- Repository profile tests should confirm inheritance behavior, bounded overrides, and failure when unsupported overrides attempt to weaken platform guarantees.
- Repo-context tests should confirm that repository context shaping improves task routing without leaking excessive irrelevant context into every task.

## Out of Scope

- Building a new IDE.
- Replacing all existing AI coding tools with a proprietary agent interface.
- Fully autonomous multi-agent collaboration in the MVP.
- Generic enterprise workflow automation beyond coding-focused use cases.
- Automatic self-modifying policy or rule systems.
- Production-grade A2A federation in the MVP.
- Multi-region active-active deployment.
- Full organizational role and tenancy complexity in the MVP.
- Deployment automation as a default AI action path.

## Further Notes

- The product should be positioned as "the governed runtime around AI coding agents," not "another coding copilot."
- The initial user is a solo developer who wants stronger control, replayability, and evidence than today's ad hoc AI coding flows provide.
- The first milestone should prove one complete governed coding loop: create task, start session, run controlled edits, pass through approval if needed, validate, produce evidence, and hand off changes cleanly.
- The MVP should deliberately trade breadth for determinism. A narrower but governed product is more valuable than a wide but weakly controlled platform.
- If the product succeeds, later phases can add stronger repository onboarding, richer approval patterns, more tool adapters, team collaboration, and eventually controlled multi-agent execution.
- The PRD intentionally treats "software engineering governance hub" ideas as inputs, not as the product's primary identity. The product remains centered on governed AI coding execution.


