# Governed AI Coding Runtime Full Lifecycle Plan

## Historical Design Inputs

This file preserves the historical inputs that shaped the lifecycle baseline and the landed `Stage 7` / `Stage 8` boundary:
- PRD:
  - `docs/prd/governed-ai-coding-runtime-prd.md`
- Architecture:
  - `docs/architecture/governed-ai-coding-runtime-target-architecture.md`
  - `docs/architecture/generic-target-repo-attachment-blueprint.md`
  - `docs/architecture/minimum-viable-governance-loop.md`
  - `docs/architecture/governance-boundary-matrix.md`
- Plans:
  - `docs/plans/interactive-session-productization-implementation-plan.md`
  - `docs/plans/interactive-session-productization-plan.md`
  - `docs/plans/governance-runtime-strategy-alignment-plan.md`
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

## Current Planning Package

The current future-facing closure and follow-on planning package is:
- direct-to-hybrid closure mainline:
  - `docs/roadmap/direct-to-hybrid-final-state-roadmap.md`
  - `docs/plans/direct-to-hybrid-final-state-implementation-plan.md`
  - `docs/backlog/issue-ready-backlog.md`
  - `docs/backlog/issue-seeds.yaml`
- governance follow-on lane after `GAP-060`:
  - `docs/roadmap/governance-optimization-lane-roadmap.md`
  - `docs/plans/governance-optimization-lane-implementation-plan.md`

## Goal
- Define the final product shape for this personal free open-source project.
- Keep the plan focused on functional completeness, not business, community, or org-scale operations.
- Turn the repository's current local runtime baseline into a generic, attach-first, interactive governed AI coding runtime that can be reused across many target repositories and many upstream AI coding tools.

## Interpretation Guardrail
- This file is the lifecycle history and current-posture record for the repository.
- `Stage 7` and `Stage 8` being complete means the first landed hybrid product boundary and its strategy hardening are present on the current branch baseline.
- `Stage 7` and `Stage 8` complete do **not** mean complete hybrid final-state closure.
- The active future-facing queue for complete closure is `docs/roadmap/direct-to-hybrid-final-state-roadmap.md` plus `docs/plans/direct-to-hybrid-final-state-implementation-plan.md`.
- The governance follow-on lane after closure is `docs/roadmap/governance-optimization-lane-roadmap.md` plus `docs/plans/governance-optimization-lane-implementation-plan.md`, and this lane is complete on the current branch baseline (verified on 2026-04-20).

## Product Shape

### Final Product Shape
- generic and portable across repositories
- interactive AI-session first
- attach-first, launch-second
- repo-local declarative light pack plus machine-wide runtime sidecar
- hybrid by design: repo-local declarations, machine-local durable kernel, host adapters, and same-contract local/CI verification
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
- bounded and dry-run-first command surface for shell/git/package paths; no silent broadening to arbitrary mutation commands
- deterministic policy before execution through `PolicyDecision`
- user-facing `safe / approval-required / blocked` buckets normalize to `allow / escalate / deny`
- legacy local-baseline `allowed` / `paused` / fail-closed outcomes must not leak past the session-bridge or adapter boundary
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
- complete on the current branch baseline through `GAP-035` to `GAP-039`

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

Interpretation note: satisfying `Stage 7` establishes the first landed hybrid product boundary; it does not establish complete hybrid final-state closure.

### Stage 8: Strategy Alignment Gates
**Status**
- complete on the current branch baseline through `GAP-040` to `GAP-044`

**Purpose**
- fuse the governance-runtime positioning work into the active productization queue without replacing `GAP-035` through `GAP-039`
- although numbered after `GAP-039` for issue continuity, this is a cross-cutting gate track; its dependencies constrain selected `GAP-035` through `GAP-039` work before those outputs harden

**Required outputs**
- borrowing matrix for governance/runtime/gateway/adapter/guardrail references
- ADR for source-of-truth versus runtime contract bundle boundaries
- repo-native contract bundle architecture that clarifies the `GAP-035` light-pack shape
- PolicyDecision contract before deeper session bridge and Codex adapter work
- local/CI same-contract verification and issue-seed reconciliation before broad adapter expansion

**Exit check**
- `Strategy Alignment Gate A` is complete before `GAP-035` implementation hardens the light-pack shape
- `Strategy Alignment Gate B` is complete before `GAP-036` and `GAP-037` depend on policy decisions
- local/CI same-contract verification is complete before `GAP-038` broadens adapter compatibility
- backlog, issue seeds, and seeding script render the alignment work without changing the meaning of `GAP-035` through `GAP-039`

Interpretation note: satisfying `Stage 8` hardens the landed hybrid boundary and future planning discipline; it still does not establish complete hybrid final-state closure.

## Active Issue Grouping
- `Vision`: `GAP-018` to `GAP-019`
- `Foundation`: `GAP-020` to `GAP-023`
- `Full Runtime`: `GAP-024` to `GAP-028`
- `Public Usable Release`: `GAP-029` to `GAP-032`
- `Maintenance Baseline`: `GAP-033` to `GAP-034`
- `Interactive Session Productization`: `GAP-035` to `GAP-039`
- `Strategy Alignment Gates`: `GAP-040` to `GAP-044`

## Current Execution Posture
- `Vision / GAP-018` and `GAP-019` are complete through lifecycle planning alignment and capability freeze.
- `Foundation / GAP-020` through `GAP-023` are complete through clarification policy contracts, live `build` and `doctor` gates, a file-backed task store and workflow skeleton, and control-health or evidence-completeness helpers.
- `Full Runtime / GAP-024` through `GAP-028` are complete through a local execution runtime, managed workspaces, artifact persistence, replay references, gate-backed verification, a CLI-first operator surface, and doctor/status integration.
- `Public Usable Release / GAP-029` through `GAP-032` are complete through a bootstrap path, richer local operator surface, package bundle, explicit release criteria, sample/demo profiles, and adapter degrade visibility.
- `Maintenance Baseline / GAP-033` through `GAP-034` are complete through explicit compatibility and upgrade policy, maintenance and retirement policy docs, runtime maintenance status visibility, and doctor enforcement for those policy surfaces.
- `Interactive Session Productization / GAP-035` through `GAP-039` are complete on the current branch baseline and now define the landed hybrid final-state product boundary.
- `Strategy Alignment Gates / GAP-040` through `GAP-044` are complete on the current branch baseline and remain encoded as satisfied dependencies around `GAP-035` through `GAP-039`; `issue-seeds.yaml` still carries those constraints so future seeding stays honest.
- `Stage 7` plus `Stage 8` complete should be read as "landed hybrid boundary + hardening dependencies complete", not as "complete hybrid final-state closure".
- The active closure queue after that landed boundary is `GAP-045` onward in the direct-to-hybrid-final-state roadmap and implementation plan.
- `GAP-061` through `GAP-068` were the governance-only follow-on lane after `GAP-060` and are now complete; they still do not replace or retroactively redefine the closure queue.
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
- `docs/plans/interactive-session-productization-implementation-plan.md`
- `docs/plans/interactive-session-productization-plan.md`
- `docs/plans/governance-runtime-strategy-alignment-plan.md`
