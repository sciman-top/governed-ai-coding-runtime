# Direct-To-Hybrid Final-State Roadmap

## Status
- This is the canonical future-facing roadmap from the current branch baseline to the complete hybrid final state.
- It complements:
  - `docs/architecture/hybrid-final-state-master-outline.md`
  - `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
  - `docs/plans/direct-to-hybrid-final-state-implementation-plan.md`
  - aligned backlog and issue seeds
- If a future-sequencing conflict exists between this file and the lifecycle history file, this roadmap is the active mainline and the lifecycle file remains the history record.

## Execution Inputs
- `docs/architecture/hybrid-final-state-master-outline.md`
- `docs/reviews/2026-04-19-hybrid-final-state-executable-gap-audit.md`
- `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- `docs/architecture/local-baseline-to-hybrid-final-state-migration-matrix.md`
- `docs/prd/governed-ai-coding-runtime-prd.md`
- `docs/architecture/governed-ai-coding-runtime-target-architecture.md`

## Goal
Define the dependency-ordered path from the current validated baseline to the complete hybrid final state without confusing:
- landed proof slices
- transition implementation slices
- full end-state closure

## What This Roadmap Owns
This roadmap owns:
- the active future sequence
- the milestone order
- the dependency logic between phases
- the claim discipline for what the repository can say after each phase

This roadmap does not own:
- historical stage narration
- sprint-level execution detail
- file-by-file implementation steps
- issue decomposition

Those belong to:
- lifecycle history
- implementation plan
- backlog and issue seeds

## Current Starting Point
The current branch baseline already includes:
- docs-first and contracts-first source-of-truth structure
- local durable task, evidence, replay, and handoff primitives
- local verification and doctor entrypoints
- target-repo attachment binding and light-pack boundary
- first attachment-aware verification execution
- first attached write governance and execution loop
- session-bridge contract and local CLI entrypoint
- Codex adapter posture and smoke-trial surface
- profile-based multi-repo trial model
- the planning closeout needed for `Phase 0`: master outline, direct roadmap, direct implementation plan, aligned plans index, aligned backlog, aligned issue seeds, and validated issue seeding script rendering

The executable gaps from the 2026-04-19 audit are now implemented through `GAP-060` on the current branch baseline.

Claim discipline remains explicit:
- complete hybrid final-state closure should only be claimed with fresh executable evidence
- the closeout evidence source is `docs/change-evidence/20260420-direct-to-hybrid-final-state-closeout.md`
- if that evidence no longer reflects runtime reality, the claim must be downgraded until re-verified

## Roadmap Principles
1. Runtime-owned execution before platform width.
2. Attach-first reality before launch-second hardening.
3. Machine-local durable state before service sprawl.
4. Same-contract parity across local runtime, CI, session bridge, and adapters.
5. Incremental re-baseline instead of clean-sheet discard.
6. Evidence-backed phase completion; no stage claim without executable proof.

## Phase Dependency Line
`Phase 0 -> Phase 1 -> Phase 2 -> Phase 3 -> Phase 4 -> Phase 5`

Interpretation:
- `Phase 0` creates the canonical planning baseline.
- `Phase 1` closes the first real governed execution surface and is the prerequisite for meaningful live adapter work.
- `Phase 2` closes live host adapter reality and is the prerequisite for honest multi-repo onboarding claims.
- `Phase 3` makes real external-repo trial loops and machine-local sidecar placement default.
- `Phase 4` extracts stable service-shaped runtime boundaries only after the execution and adapter truths are no longer hypothetical.
- `Phase 5` hardens the operating baseline and is the only phase that should unlock a complete final-state claim.

## Milestone Overview
| milestone | phase | closes | outcome |
|---|---|---|---|
| `M0` | `Phase 0` | planning ambiguity | canonical planning baseline exists |
| `M1` | `Phase 1` | `HFG-001` `HFG-002` `HFG-006` | first complete governed execution surface exists |
| `M2` | `Phase 2` | `HFG-003` `HFG-005` | at least one live adapter path is real |
| `M3` | `Phase 3` | `HFG-004` `HFG-007` | multi-repo and machine-local sidecar claims become honest |
| `M4` | `Phase 4` | service-boundary debt | local runtime can run in a service-shaped deployment |
| `M5` | `Phase 5` | `HFG-H1` `HFG-H2` `HFG-H3` | complete hybrid final-state closure is defensible |

## Phase 0: Canonical Re-Baseline

### Status
- complete on the current branch baseline after the canonical planning package, backlog truth, issue seeds, and GitHub seeding script were aligned and re-validated on `2026-04-19`

### Goal
Turn the repository's final-state definition and forward sequence into one canonical planning baseline.

### Why This Comes First
The repository currently has enough landed surface to move forward, but not enough single-threaded planning to prevent drift between:
- lifecycle history
- future roadmap
- implementation planning
- backlog seeding

### Scope
- create the master outline
- create the direct-to-final-state roadmap
- create the direct implementation plan
- align backlog and issue seeds to the new mainline
- mark the lifecycle plan as historical posture plus completion criteria, not the only future roadmap

### Out Of Scope
- no runtime behavior changes
- no adapter feature additions
- no service extraction yet

### Exit Criteria
- canonical master outline exists
- direct roadmap exists
- direct implementation plan exists
- aligned backlog/task list exists
- future readers can tell the difference between landed baseline and final-state closure without reconstructing it themselves

### Claim Allowed After Phase 0
The repository can claim that the hybrid final state now has a canonical planning baseline.

## Phase 1: Close The Governed Execution Surface

### Goal
Turn the already-landed session-bridge write or read surface into the first live-host-ready governed execution surface.

### Primary Gaps Closed
- `HFG-001`
- `HFG-002`
- `HFG-006`

### Scope
- promote quick/full gate paths from plan-only responses to runtime-managed execution lifecycle
- consolidate the existing session-bridge write, approval, status, evidence, and handoff paths around one stable execution model
- bind adapter or session or continuation identity into the attached write flow instead of stopping at local-only command ids
- extend governed execution coverage beyond file writes to shell, git, and selected package-manager actions

### Required Outputs
- stable execution identifiers and continuation identifiers across gate, write, approval, evidence, and handoff paths
- one runtime-owned medium-risk write loop inside an attached repository
- same task-level linkage across approval, execution, evidence, handoff, and replay
- end-to-end tests for `attach -> request -> approve -> execute -> verify -> handoff -> replay`

### Exit Criteria
- one attached repository can complete a governed medium-risk write loop entirely through the runtime-owned session surface
- session bridge no longer stops at plan-only gate requests or local-only session identity for the primary governed path
- shell, git, and file execution all use the same governance and evidence model

### Claim Allowed After Phase 1
The repository can claim that it has a real runtime-owned governed execution surface for an attached repository.

## Phase 2: Close Live Host Adapter Reality

### Goal
Move adapters from posture declarations and smoke trials to live runtime integration.

### Primary Gaps Closed
- `HFG-003`
- `HFG-005`

### Scope
- add live host capability probing or handshake
- bind real session identity and continuation identity
- ingest real adapter events instead of deterministic placeholder refs
- export evidence from live sessions into the runtime-owned task model
- turn the adapter registry from classification helper into runtime selection and delegation surface

### Required Outputs
- at least one live Codex path
- at least one shared runtime adapter interface covering selection, execution, event capture, and degrade behavior
- live adapter fixtures or end-to-end tests that prove the evidence timeline is sourced from a real session path

### Exit Criteria
- at least one real Codex path produces task, approval, execution, evidence, and handoff linkage from a live session
- adapter selection is a runtime decision, not only a doc or fixture projection
- adapter runtime behavior is governed by one stable interface instead of ad hoc trial code

### Claim Allowed After Phase 2
The repository can claim that at least one live host adapter path is real, runtime-owned, and evidence-linked.

## Phase 3: Close Real Multi-Repo And Machine-Local Sidecar Reality

### Goal
Make multi-repo onboarding and machine-local runtime placement real, repeatable, and external-repo proven.

### Primary Gaps Closed
- `HFG-004`
- `HFG-007`

### Scope
- turn the multi-repo runner from profile summary into real attached-repo execution
- make machine-local runtime root the default for task, artifact, replay, and workspace placement
- support migration from repo-root defaults to machine-local state roots
- capture differentiated onboarding friction and follow-up evidence from real repositories

### Required Outputs
- at least two real attached external repositories
- real onboarding or trial records sourced from attached execution, not only sample profiles
- migration and rollback handling for runtime-root placement
- test coverage for repo-root compatibility, machine-local configuration, and migration rollback

### Exit Criteria
- at least two real attached external repositories can complete the onboarding or trial loop without kernel rewrites
- durable state and workspace placement are machine-local by default
- multi-repo trial evidence is sourced from real attached repositories

### Claim Allowed After Phase 3
The repository can claim honest attach-first multi-repo onboarding and machine-local sidecar reality.

## Phase 4: Extract Service-Shaped Runtime

### Goal
Move the runtime from script-heavy local harnesses to stable service-shaped boundaries without breaking the proven contract model.

### Scope
- extract runtime API boundaries for control, session, execution, and operator reads
- preserve contract parity while replacing script-only orchestration with service-shaped surfaces
- introduce clearer physical layout under `apps/`, `packages/`, `infra/`, and `tests/`
- move persistence behind stable abstractions suitable for local and future hosted deployment

### Non-Goals
- do not broaden platform width before keeping contract parity
- do not introduce service decomposition solely for appearance

### Required Outputs
- service-shaped local deployment path
- runtime APIs for session, execution, and operator reads
- preserved compatibility with the existing contract bundle and evidence model

### Exit Criteria
- the runtime can run as a service-shaped local deployment without losing current contract parity
- script entrypoints become wrappers or operator conveniences instead of the only runtime boundary
- the repository physical shape reflects the service-shaped runtime rather than only the tracer-bullet harness

### Claim Allowed After Phase 4
The repository can claim that the runtime deployment boundary is now service-shaped rather than hypothetical.

## Phase 5: Hardening And Operational Completion

### Goal
Close the final gap between a functioning hybrid runtime and a stable, auditable, repeatable operating baseline.

### Primary Gaps Closed
- `HFG-H1`
- `HFG-H2`
- `HFG-H3`

### Scope
- add attachment-scoped evidence, approval, handoff, and replay operator queries
- extend same-contract parity beyond verifier boundaries to runtime readers and adapters
- add remediation-capable doctor and posture enforcement
- harden observability, policy, and operational failure handling
- align local and CI contract consumers across the runtime surface

### Required Outputs
- operator or control-plane surfaces for approvals, evidence, handoff, replay, and attachment posture
- CI coverage that proves runtime readers consume the declared contract shape
- remediation and rollback paths for invalid or stale attachment posture

### Exit Criteria
- runtime, adapters, CI, and operator surfaces all consume the same declared contract model
- failures are remediable and evidence-backed
- hybrid final-state claims are backed by real attached execution, live adapter behavior, machine-local runtime placement, and service-shaped runtime boundaries

### Claim Allowed After Phase 5
The repository can claim complete hybrid final-state closure only while the closeout evidence remains current and reproducible.

## Claim Discipline
The repository should not claim complete hybrid final-state closure before `Phase 5` exits.

The repository may claim narrower truths after earlier phases:
1. After `Phase 0`: canonical planning baseline exists.
2. After `Phase 1`: real governed execution surface exists for an attached repo.
3. After `Phase 2`: at least one live adapter path is real.
4. After `Phase 3`: attach-first multi-repo onboarding and machine-local sidecar posture are real.
5. After `Phase 4`: service-shaped runtime deployment is real.

## Near-Term Gap Lanes (Execution Horizon)
These lanes define the current actionable gap set for reaching an optimized hybrid best-state.

| lane id | mapped phases | gap statement | done when |
|---|---|---|---|
| `NT-01` | Phase 1 -> Phase 2 | Live host execution closure is not yet proven end-to-end for real sessions. | one live attached path preserves session identity and continuation across request, approval, execute, verify, handoff, and replay with runtime-owned evidence. |
| `NT-02` | Phase 2 | Non-Codex path guarantees are weaker than Codex path guarantees. | at least one non-Codex adapter passes the same conformance gate set and emits equivalent runtime evidence linkage. |
| `NT-03` | Phase 3 | Multi-repo onboarding still depends on partial synthetic or profile-driven evidence in some flows. | two or more attached external repos run reproducible trial loops with differentiated runtime-sourced outcomes. |
| `NT-04` | Phase 4 | Service-shaped runtime is landed but still vulnerable to API/CLI drift over time. | API/CLI parity stays green for execution-like commands and CLI is only a wrapper surface for the same execution bus. |
| `NT-05` | Phase 5 | Claim discipline is still mostly human-governed and can drift under rapid iteration. | CI enforces claim-to-evidence consistency and fails when roadmap/plan completion labels outrun executable evidence. |

## Long-Term Gap Lanes (North-Star Hardening Horizon)
These lanes are intentionally deferred until near-term lanes are stable.

| lane id | trigger to start | deferred capabilities |
|---|---|---|
| `LT-01` | execution pause/resume/compensation graph becomes hard to manage in local runtime flow code | workflow orchestration depth (`Temporal`-class capability) |
| `LT-02` | policy cardinality and compliance audit burden exceed local policy decision surfaces | externalized policy runtime depth (`OPA/Rego`-class capability) |
| `LT-03` | event throughput and replay retention pressure exceed current persistence path | data-plane expansion (event stream, indexed evidence, retention tiers) |
| `LT-04` | non-Codex conformance parity is stable and multi-host demand is product-critical | first-class multi-host adapter productization beyond Codex |
| `LT-05` | transition runtime is stable under sustained real workloads | production-grade SLO/error-budget/failover and operations hardening stack |

## Companion Deliverables
This roadmap is paired with:
1. a direct implementation plan
2. an aligned backlog and task list
3. backlog or issue-seed synchronization

Those companion deliverables now exist and should continue translating this dependency order into:
- executable work batches
- acceptance criteria
- verification commands
- rollback notes

## Source References
- `docs/architecture/hybrid-final-state-master-outline.md`
- `docs/reviews/2026-04-19-hybrid-final-state-executable-gap-audit.md`
- `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- `docs/architecture/local-baseline-to-hybrid-final-state-migration-matrix.md`
- `docs/prd/governed-ai-coding-runtime-prd.md`
- `docs/architecture/governed-ai-coding-runtime-target-architecture.md`
