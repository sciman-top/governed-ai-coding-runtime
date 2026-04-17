# Governed AI Coding Runtime Full Lifecycle Plan

## Execution Inputs

This plan assumes the following documents remain the active design inputs:
- PRD:
  - `docs/prd/governed-ai-coding-runtime-prd.md`
- Architecture:
  - `docs/architecture/governed-ai-coding-runtime-target-architecture.md`
  - `docs/architecture/minimum-viable-governance-loop.md`
  - `docs/architecture/governance-boundary-matrix.md`
- ADRs:
  - `docs/adrs/0001-control-plane-first.md`
  - `docs/adrs/0002-no-multi-repo-distribution-in-mvp.md`
  - `docs/adrs/0003-single-agent-baseline-first.md`
  - `docs/adrs/0005-governance-kernel-and-control-packs-before-platform-breadth.md`
  - `docs/adrs/0006-final-state-best-practice-agent-compatibility.md`
- Current MVP baseline:
  - `docs/roadmap/governed-ai-coding-runtime-90-day-plan.md`
  - `docs/backlog/mvp-backlog-seeds.md`
  - `docs/change-evidence/20260417-mvp-backlog-closeout-handoff.md`

## Goal
- Define the final product shape for this personal free open-source project.
- Keep the plan focused on functional completeness, not business, community, or org-scale operations.
- Turn the repository's current "governance kernel plus verifier" baseline into a complete, strong, single-machine self-hosted governed AI coding runtime.

## Product Shape

### Final Product Shape
- single-machine self-hosted first
- complete governed AI coding runtime
- internal boundaries remain service-shaped:
  - control plane
  - workflow/runtime
  - execution worker
  - persistence and artifact store
  - verification runner
  - operator UI

### Non-Goals
- commercial packaging
- enterprise org model
- multi-tenant platform design
- marketplace or promotion workflow
- default multi-agent orchestration
- memory-first product identity
- deployment automation as the default completion path

## Core Pain Points To Solve
- AI coding sessions are not durable enough for long-running work.
- High-risk writes are not consistently approval-aware or rollback-aware.
- `build -> test -> contract/invariant -> hotspot` is not orchestrated as one governed runtime path.
- Evidence, replay, and handoff are still too easy to lose or reconstruct manually.
- Repo reuse and adapter compatibility still require too much implicit knowledge.
- When governed runs fail, it is still too hard to diagnose, replay, and recover.

## Final Product Capability Boundary

The final product is considered functionally complete only when all of the following capability groups exist together:

### 1. Task And Lifecycle
- durable task object with `goal`, `scope`, `acceptance`, `repo`, and budgets
- task state machine with pause, resume, timeout, retry, cancel, fail, and complete semantics

### 2. Repo Admission And Profile
- repo profile loading
- repo admission checks
- path scope, tool policy, gate commands, and repo defaults

### 3. Governed Execution
- governed shell, file, git, package-manager, and helper-tool execution
- deterministic policy before execution
- explicit `safe`, `approval-required`, and `blocked` behavior
- managed workspace or worktree execution

### 4. Approval And Policy
- approval interruption for risky actions
- approval lifecycle with create, approve, reject, revoke, and expire
- rollout modes such as `observe`, `advisory`, and `enforced`
- clarification protocol as formal runtime policy

### 5. Durable Runtime
- task persistence
- workflow orchestration
- execution worker
- artifact store

### 6. Verification And Delivery
- canonical gate order: `build -> test -> contract/invariant -> hotspot`
- quick and full verification
- delivery handoff with validation and risk state

### 7. Evidence / Replay / Rollback
- evidence bundle
- approval trace
- command and tool trace
- replay references and failure signatures
- rollback references

### 8. Operator Surface
- minimal UI for tasks, approvals, evidence, replay, verification, and health
- control-plane surface only, not an IDE replacement

### 9. Adapter Compatibility
- Codex-first but not Codex-only
- typed adapter contract
- explicit degrade or fallback behavior for unsupported capability surfaces

## Lifecycle Stages

### Stage 1: Vision
**Purpose**
- freeze the final product definition and capability boundary

**Required outputs**
- final product shape
- lifecycle stage definitions
- final capability boundary
- non-goal boundary

**Exit check**
- planning docs stop describing the project as only a contracts/tooling repo
- planning docs also stop drifting into a generic agent platform

### Stage 2: MVP
**Status**
- already complete through `GAP-017`

**Purpose**
- preserve the historical validated governance-kernel baseline

**Required outputs**
- historical roadmap
- historical evidence
- runtime contract tests
- first governed loop primitives

**Exit check**
- MVP remains a stable input baseline for later stages rather than being rewritten

### Stage 3: Foundation
**Status**
- complete through `GAP-020` to `GAP-023`

**Purpose**
- make the MVP capable of supporting the full product

**Required outputs**
- clarification, rollout, compatibility, and evidence maturity
- real `build` and `doctor|hotspot` gates
- durable task store skeleton
- workflow skeleton
- control lifecycle metadata

**Exit check**
- key runtime controls are no longer documentation-only
- task state is no longer trapped in in-memory primitives
- repo and adapter compatibility can be checked mechanically

### Stage 4: Full Runtime
**Purpose**
- land the complete runtime path

**Required outputs**
- execution worker
- managed workspace runtime
- artifact store
- operational quick/full gate runner
- replay pipeline
- minimal operator surface with CLI-first delivery and stable read models for a later UI
- runtime health and status query surface

**Exit check**
- one real governed task can run end-to-end with approval, verification, evidence, and replay

### Stage 5: Public Usable Release
**Purpose**
- make the complete runtime understandable and runnable by someone other than the author

**Required outputs**
- single-machine deployment path
- quickstart
- sample repo profiles
- end-to-end demo flow
- richer operator UI shell on top of the Full Runtime control surface
- packaging and release criteria
- adapter baseline and degrade behavior

**Exit check**
- a user can clone the repo, follow docs, and run a real governed task without author-specific guidance

### Stage 6: Maintenance
**Purpose**
- keep the product alive with minimal but explicit maintenance rules

**Required outputs**
- compatibility and upgrade policy
- maintenance and triage rules
- deprecation and retirement policy

**Exit check**
- changes can continue without breaking the final product capability boundary silently

## Active Issue Grouping
- `Vision`: `GAP-018` to `GAP-019`
- `Foundation`: `GAP-020` to `GAP-023`
- `Full Runtime`: `GAP-024` to `GAP-028`
- `Public Usable Release`: `GAP-029` to `GAP-032`
- `Maintenance`: `GAP-033` to `GAP-034`

## Current Execution Posture
- `Vision / GAP-018` and `GAP-019` are complete through the active lifecycle roadmap, backlog, issue seeds, seeding script, and entry-doc alignment.
- `Foundation / GAP-020` through `GAP-023` are complete through clarification policy contracts, live `build` and `doctor` gates, a file-backed task store and workflow skeleton, and control-health or evidence-completeness helpers.
- The active next-step queue now starts at `Full Runtime / GAP-024`.
- `docs/plans/foundation-runtime-substrate-implementation-plan.md` is now execution history for the completed Foundation stage, not the active next-step checklist.
- The current `Full Runtime` intent remains conservative about sequence:
  - land worker execution and managed workspace runtime before adding package or release concerns
  - add artifact persistence, replay plumbing, and operator surfaces on top of the Foundation substrate
  - keep single-machine self-hosted operation as the first completion target

## Lifecycle Completion Criteria
- the repository can run the complete governed runtime on one machine
- the final product capability boundary exists as working software, not only as contracts
- a real governed task can be created, executed, approved, verified, handed off, replayed, and recovered
- a second repo can be onboarded through profiles without kernel drift
- at least one non-Codex adapter path has explicit compatibility or degrade behavior
- a new user can run the product from docs without private context
- maintenance and deprecation are documented enough for the project to evolve without confusion

## Supporting Documents
- `docs/prd/governed-ai-coding-runtime-prd.md`
- `docs/architecture/governed-ai-coding-runtime-target-architecture.md`
- `docs/architecture/governance-boundary-matrix.md`
- `docs/architecture/minimum-viable-governance-loop.md`
- `docs/roadmap/governed-ai-coding-runtime-90-day-plan.md`
- `docs/backlog/full-lifecycle-backlog-seeds.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/issue-seeds.yaml`
- `docs/plans/foundation-runtime-substrate-implementation-plan.md`
