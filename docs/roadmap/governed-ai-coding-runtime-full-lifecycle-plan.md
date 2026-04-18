# Governed AI Coding Runtime Full Lifecycle Plan

## Execution Inputs

This plan assumes the following documents remain the active design inputs:
- PRD:
  - `docs/prd/governed-ai-coding-runtime-prd.md`
- Architecture:
  - `docs/architecture/governed-ai-coding-runtime-target-architecture.md`
  - `docs/architecture/generic-target-repo-attachment-blueprint.md`
  - `docs/architecture/minimum-viable-governance-loop.md`
  - `docs/architecture/governance-boundary-matrix.md`
- ADRs:
  - `docs/adrs/0001-control-plane-first.md`
  - `docs/adrs/0002-no-multi-repo-distribution-in-mvp.md`
  - `docs/adrs/0003-single-agent-baseline-first.md`
  - `docs/adrs/0005-governance-kernel-and-control-packs-before-platform-breadth.md`
  - `docs/adrs/0006-final-state-best-practice-agent-compatibility.md`
- Historical MVP baseline:
  - `docs/roadmap/governed-ai-coding-runtime-90-day-plan.md`
  - `docs/backlog/mvp-backlog-seeds.md`
  - `docs/change-evidence/20260417-mvp-backlog-closeout-handoff.md`

## Goal
- Define the final product shape for this personal free open-source project.
- Keep the plan focused on functional completeness, not business, community, or org-scale operations.
- Turn the repository's current local runtime baseline into a generic, attach-first, interactive governed AI coding runtime that can be reused across many target repositories and many upstream AI coding tools.

## Product Shape

### Final Product Shape
- generic and portable across repositories
- interactive AI-session first
- attach-first, launch-second
- repo-local declarative light pack plus machine-wide runtime sidecar
- Codex-first, but not Codex-only
- rapid multi-repo trial and feedback driven
- internal boundaries remain service-shaped:
  - control plane
  - workflow/runtime
  - execution worker
  - persistence and artifact store
  - verification runner
  - operator and session bridge surfaces

### Local Baseline Already Landed
The current branch has already completed the local single-machine runtime baseline through `GAP-034`. That baseline is necessary, but it is no longer the final lifecycle endpoint by itself.

### Non-Goals
- commercial packaging
- enterprise org model
- multi-tenant platform design
- marketplace or promotion workflow
- default multi-agent orchestration
- memory-first product identity
- replacing upstream AI coding products with a proprietary IDE shell
- deployment automation as the default completion path

## Core Pain Points To Solve
- AI coding sessions are still too ephemeral for long-running governed work.
- High-risk writes are not consistently approval-aware inside interactive AI sessions.
- `build -> test -> contract/invariant -> hotspot` is not yet attached to real upstream coding sessions as one governed path.
- Evidence, replay, and handoff are still too easy to lose or reconstruct manually across repositories.
- New target repositories still require too much manual interpretation to onboard safely.
- Adapter compatibility still lacks a strong attach-first path for real Codex or future agent sessions.
- Fast multi-repo experimentation is still weaker than the desired product feedback loop.

## Final Product Capability Boundary

The final product is considered functionally complete only when all of the following capability groups exist together:

### 1. Task And Lifecycle
- durable task object with `goal`, `scope`, `acceptance`, `repo`, and budgets
- task state machine with pause, resume, timeout, retry, cancel, fail, and complete semantics

### 2. Target-Repo Attachment And Onboarding
- repo-local light pack generation or validation
- repo admission checks
- path scope, tool policy, gate commands, and repo defaults
- machine-local binding that does not require copying the kernel into the target repo

### 3. Interactive Session Bridge
- governed actions callable during an AI coding session
- attach-first path for existing sessions
- launch-second fallback when attach is unavailable
- stable session-to-task binding

### 4. Governed Execution And Approval
- governed shell, file, git, package-manager, and helper-tool execution
- deterministic policy before execution
- explicit `safe`, `approval-required`, and `blocked` behavior
- approval interruption for risky actions inside the runtime path

### 5. Durable Runtime
- task persistence
- workflow orchestration
- execution worker
- artifact store
- machine-local state separation from repo-local declarations

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
- trial feedback capture for target-repo onboarding and adapter evolution

### 8. Operator And Session Surfaces
- minimal operator surface for tasks, approvals, evidence, replay, verification, and health
- session-level governed commands for interactive use
- control-plane surface only, not an IDE replacement

### 9. Adapter Compatibility
- Codex-first but not Codex-only
- typed adapter contract
- capability tiers for native attach, process bridge, and manual handoff
- explicit degrade or fallback behavior for unsupported capability surfaces

## Lifecycle Stages

### Stage 1: Vision
**Status**
- complete through `GAP-018` to `GAP-019`

**Purpose**
- freeze the initial product definition and capability boundary

### Stage 2: MVP
**Status**
- already complete through `GAP-017`

**Purpose**
- preserve the historical validated governance-kernel baseline

### Stage 3: Foundation
**Status**
- complete through `GAP-020` to `GAP-023`

**Purpose**
- make the MVP capable of supporting the local runtime baseline

### Stage 4: Full Runtime
**Status**
- complete through `GAP-024` to `GAP-028`

**Purpose**
- land the complete local runtime path

### Stage 5: Public Usable Release
**Status**
- complete through `GAP-029` to `GAP-032`

**Purpose**
- make the local runtime understandable and runnable by someone other than the author

### Stage 6: Maintenance Baseline
**Status**
- complete through `GAP-033` to `GAP-034`

**Purpose**
- keep the landed local baseline evolvable without silent contract breakage

### Stage 7: Interactive Session Productization
**Status**
- active next-step queue through `GAP-035` to `GAP-039`

**Purpose**
- move from a repo-owned local runtime baseline to a generic, portable, interactive product path

**Required outputs**
- target-repo attachment pack and onboarding flow
- attach-first session bridge and governed interaction surface
- direct Codex adapter and evidence mapping
- capability-tiered multi-agent adapter framework
- multi-repo trial loop and generic onboarding kit

**Exit check**
- at least one real Codex path is direct rather than manual-handoff only
- at least one non-Codex tool is modeled through explicit capability tiers
- multiple target repositories can attach through light packs without kernel drift
- interactive governed actions are usable inside an AI session

## Active Issue Grouping
- `Vision`: `GAP-018` to `GAP-019`
- `Foundation`: `GAP-020` to `GAP-023`
- `Full Runtime`: `GAP-024` to `GAP-028`
- `Public Usable Release`: `GAP-029` to `GAP-032`
- `Maintenance Baseline`: `GAP-033` to `GAP-034`
- `Interactive Session Productization`: `GAP-035` to `GAP-039`

## Current Execution Posture
- `Vision / GAP-018` and `GAP-019` are complete through lifecycle planning alignment and capability freeze.
- `Foundation / GAP-020` through `GAP-023` are complete through clarification policy contracts, live `build` and `doctor` gates, a file-backed task store and workflow skeleton, and control-health or evidence-completeness helpers.
- `Full Runtime / GAP-024` through `GAP-028` are complete through a local execution runtime, managed workspaces, artifact persistence, replay references, gate-backed verification, a CLI-first operator surface, and doctor/status integration.
- `Public Usable Release / GAP-029` through `GAP-032` are complete through a bootstrap path, richer local operator surface, package bundle, explicit release criteria, sample/demo profiles, and adapter degrade visibility.
- `Maintenance Baseline / GAP-033` through `GAP-034` are complete through explicit compatibility and upgrade policy, maintenance and retirement policy docs, runtime maintenance status visibility, and doctor enforcement for those policy surfaces.
- `Interactive Session Productization / GAP-035` through `GAP-039` are the active queue for the true final product boundary.
- `docs/plans/foundation-runtime-substrate-implementation-plan.md`, `docs/plans/full-runtime-implementation-plan.md`, `docs/plans/public-usable-release-implementation-plan.md`, and `docs/plans/maintenance-implementation-plan.md` are execution history for completed local-baseline stages.

## Lifecycle Completion Criteria
- a new target repo can be attached through a repo-local light pack without copying the runtime into it
- the runtime can bind interactive AI sessions to durable governed tasks
- a real governed task can be created, executed, approved, verified, handed off, replayed, and recovered across attached repos
- at least one direct Codex adapter path exists
- at least one non-Codex adapter path has explicit compatibility or degrade behavior
- multi-repo trial evidence can be captured and used to evolve onboarding and adapter contracts
- a new user can run the product from docs without private context
- maintenance and deprecation are documented enough for the project to evolve without confusion

## Supporting Documents
- `docs/prd/governed-ai-coding-runtime-prd.md`
- `docs/architecture/governed-ai-coding-runtime-target-architecture.md`
- `docs/architecture/generic-target-repo-attachment-blueprint.md`
- `docs/architecture/governance-boundary-matrix.md`
- `docs/architecture/minimum-viable-governance-loop.md`
- `docs/roadmap/governed-ai-coding-runtime-90-day-plan.md`
- `docs/backlog/full-lifecycle-backlog-seeds.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/issue-seeds.yaml`
- `docs/plans/interactive-session-productization-plan.md`
