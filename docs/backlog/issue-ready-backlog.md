# Issue-Ready Backlog

## Parent Initiative
Governed AI Coding Runtime Full Functional Lifecycle

## Assumptions
- `Phase 0` through `Phase 4` remain complete through `GAP-017`
- this is a personal free open-source project, so the plan stays function-first and intentionally light on non-functional operations
- the local single-machine runtime through `GAP-034` is baseline, not final completion
- the target product is a generic, portable, interactive governed runtime with repo-local light packs and machine-wide runtime state
- internal runtime boundaries remain service-shaped even though the default delivery shape is attach-first rather than service-first
- Codex compatibility remains the first direct adapter priority, but final product completeness cannot be Codex-only
- non-goals remain non-goals: no enterprise org model, no marketplace, no default multi-agent orchestration, no memory-first product identity
- the active future-facing queue is the direct-to-hybrid-final-state mainline through `GAP-045` onward, while older lifecycle `GAP` entries remain completion history

## Current Baseline
- PRD, architecture, ADRs, specs, runtime contract primitives, repo verifier entrypoints, sample repo profiles, and a runtime-consumable control pack already exist.
- The MVP governance-kernel backlog is complete through `GAP-017`.
- `Vision / GAP-018` and `GAP-019` are complete through lifecycle planning alignment and capability freeze.
- `Foundation / GAP-020` through `GAP-023` are now complete on the current branch baseline.
- `Full Runtime / GAP-024` through `GAP-028` are now complete on the current branch baseline.
- `Public Usable Release / GAP-029` through `GAP-032` are now complete on the current branch baseline.
- `Maintenance Baseline / GAP-033` through `GAP-034` are now complete on the current branch baseline.
- `Strategy Alignment Gates / GAP-040` through `GAP-044` are now complete on the current branch baseline.
- `Interactive Session Productization / GAP-035` through `GAP-039` are complete on the current branch baseline.
- `Direct-To-Hybrid-Final-State Mainline / GAP-045` through `GAP-060` is the active future-facing queue.

## Direct-To-Hybrid-Final-State Mainline

The entries below are the active queue for complete hybrid final-state closure. The historical lifecycle backlog remains below as completion history and dependency context.

### Phase 0: Canonical Re-Baseline

### GAP-045 Phase 0 Planning Sync And Mainline Backlog Alignment
- Type: AFK
- Blocked by: GAP-039, GAP-044
- User stories: 1, 23, 29, 31
- Status: active in direct-to-final-state mainline
- What to build:
  - align backlog, issue seeds, and seeding script to the direct-to-final-state roadmap and implementation plan
  - keep historical lifecycle GAP entries as completion history while promoting `Phase 0` through `Phase 5` as the active queue
  - record planning-sync evidence and validation outputs
- Acceptance criteria:
  - [ ] backlog groups active work by `Phase 0` through `Phase 5`
  - [ ] issue seeds render the new mainline without colliding with historical GAP ids
  - [ ] plans index, backlog, issue seeds, and seeding script agree on the active future-facing queue

### Phase 1: Governed Execution Surface

### GAP-046 Session Bridge Execution Bus Upgrade
- Type: AFK
- Blocked by: GAP-045
- User stories: 1, 5, 41, 43
- Status: active in direct-to-final-state mainline
- What to build:
  - expand the session bridge from posture and planning probe into a governed execution bus
  - add command coverage for write request, write approve, write execute, write status, gate execution, evidence inspection, and handoff inspection
  - return stable execution ids and continuation ids for execution-like paths
- Acceptance criteria:
  - [ ] session bridge commands cover the runtime-owned execution surface needed by attached repos
  - [ ] execution-like results carry stable execution identifiers rather than plan-only output
  - [ ] unsupported capabilities still degrade explicitly instead of implying execution

### GAP-047 Runtime-Owned Attached Write Chain
- Type: HITL
- Blocked by: GAP-046
- User stories: 8, 10, 27, 43
- Status: active in direct-to-final-state mainline
- What to build:
  - route attached write governance and execution through the session bridge
  - bind task id, adapter or session identity, approval ref, artifact refs, handoff ref, and replay ref for each real write
  - make CLI write paths wrappers around the same runtime-owned flow instead of parallel logic
- Acceptance criteria:
  - [ ] one write request can be initiated, escalated, approved, resumed, and executed through the runtime-owned session surface
  - [ ] high-risk writes fail closed when approval state is absent or stale
  - [ ] attached write evidence stays on one task model from request through replay

### GAP-048 Governed Shell, Git, And Package Execution Coverage
- Type: AFK
- Blocked by: GAP-047
- User stories: 8, 10, 17, 31
- Status: active in direct-to-final-state mainline
- What to build:
  - extend governed execution beyond file writes to shell, git, and selected package-manager actions
  - keep allow, escalate, and deny semantics on one evidence and rollback model
  - start with bounded happy-path and fail-closed allowlist coverage rather than broad command support
- Acceptance criteria:
  - [ ] shell, git, and at least one package-manager dry-run path use the same governance model as file writes
  - [ ] allow, escalate, and deny paths emit consistent evidence and rollback metadata
  - [ ] the execution surface remains explicitly bounded and does not silently broaden

### GAP-049 Attached-Repo End-To-End Governed Loop
- Type: HITL
- Blocked by: GAP-048
- User stories: 14, 38, 42, 46
- Status: active in direct-to-final-state mainline
- What to build:
  - prove one attached repo can complete `attach -> request write -> approve -> execute -> verify -> handoff -> replay`
  - keep the output on the same runtime-owned task model as local runtime work
  - record exact command sequence and resulting refs as evidence
- Acceptance criteria:
  - [ ] one attached repo can complete the governed medium-risk loop end to end
  - [ ] the end-to-end output distinguishes real execution from smoke or fallback paths
  - [ ] evidence shows the exact attached-repo command chain and refs

### Phase 2: Live Host Adapter Reality

### GAP-050 Live Codex Handshake And Continuation Identity
- Type: HITL
- Blocked by: GAP-049
- User stories: 2, 11, 31, 41, 43
- Status: active in direct-to-final-state mainline
- What to build:
  - move the direct Codex adapter from declared posture to a real handshake or probe path
  - preserve session id, resume id, and continuation identity in the runtime task model
  - keep live attach, process bridge, and manual handoff explicitly distinguishable
- Acceptance criteria:
  - [ ] the adapter can probe or handshake with a real Codex surface instead of relying only on manual flags
  - [ ] live session and continuation identity are preserved in the runtime-owned task model
  - [ ] unavailable live attach remains explicit posture rather than implied support

### GAP-051 Real Adapter Event Ingestion And Evidence Export
- Type: AFK
- Blocked by: GAP-050
- User stories: 13, 14, 15, 31, 43
- Status: active in direct-to-final-state mainline
- What to build:
  - ingest real tool, diff, gate, approval, and handoff events from the adapter path
  - export richer evidence into the runtime-owned task, evidence, and delivery model
  - keep manual-handoff and live-ingestion evidence distinguishable
- Acceptance criteria:
  - [ ] tool calls, diffs, gate runs, and approval interruptions can be linked back to one runtime-owned task
  - [ ] unsupported or partial events are recorded explicitly rather than dropped
  - [ ] delivery handoff and replay readers can consume the richer evidence shape

### GAP-052 Executable Adapter Registry And Multi-Host Selection
- Type: AFK
- Blocked by: GAP-051
- User stories: 20, 31, 37, 44
- Status: active in direct-to-final-state mainline
- What to build:
  - turn adapter selection, discovery, probing, and delegation into executable runtime behavior
  - support `native_attach`, `process_bridge`, and `manual_handoff` tiers through one registry interface
  - keep Codex first without making the runtime Codex-only
- Acceptance criteria:
  - [ ] adapter selection is a runtime decision based on repo and host capability, not only static projection
  - [ ] Codex and at least one non-Codex fixture share the same registry interface
  - [ ] degrade behavior is part of the runtime interface rather than documentation only

### Phase 3: Real Multi-Repo And Machine-Local Sidecar Reality

### GAP-053 Attached Multi-Repo Trial Runner
- Type: HITL
- Blocked by: GAP-052
- User stories: 14, 37, 38, 39, 45
- Status: active in direct-to-final-state mainline
- What to build:
  - convert the multi-repo runner from profile summary into an attached-repo execution loop
  - run attach, doctor or status, gate request, attachment verification, optional write probe, and evidence aggregation per repo
  - capture differentiated onboarding friction and follow-up actions from real repo runs
- Acceptance criteria:
  - [ ] the trial runner can accept attached repo roots or bindings instead of only repo profile paths
  - [ ] at least two attached external repos can run without kernel rewrites
  - [ ] trial outputs capture real gate failures, approval friction, replay quality, and follow-up items

### GAP-054 Machine-Local Runtime Roots And Migration
- Type: AFK
- Blocked by: GAP-053
- User stories: 1, 17, 29, 38
- Status: active in direct-to-final-state mainline
- What to build:
  - normalize task, artifact, replay, and workspace placement around one machine-local runtime-root model
  - keep repo-root `.runtime/` as compatibility mode rather than primary posture
  - document and test migration plus rollback behavior
- Acceptance criteria:
  - [ ] machine-local runtime roots become the default posture for self-runtime and attached-runtime flows
  - [ ] repo-root defaults remain available only as compatibility mode
  - [ ] migration and rollback behavior are documented and testable

### Phase 4: Service-Shaped Runtime Extraction

### GAP-055 Service-Shaped Control And Session API Boundary
- Type: AFK
- Blocked by: GAP-054
- User stories: 1, 11, 13, 14, 17, 39
- Status: active in direct-to-final-state mainline
- What to build:
  - extract a service-shaped API boundary for session operations and operator reads
  - make CLI entrypoints wrappers or clients rather than the only control surface
  - introduce tracing hooks at the new boundary without breaking contract parity
- Acceptance criteria:
  - [ ] session operations and operator reads are exposed through a service API boundary
  - [ ] CLI and API paths preserve contract parity
  - [ ] observability hooks exist at the new runtime boundary

### GAP-056 Service-Shaped Persistence And Local Deployment Scaffold
- Type: AFK
- Blocked by: GAP-055
- User stories: 1, 5, 24, 29, 30, 39
- Status: active in direct-to-final-state mainline
- What to build:
  - add local service deployment scaffolding for control-plane and worker boundaries
  - move durable metadata and artifact handling behind stable persistence abstractions
  - introduce transition-stack dependencies only where the service boundary requires them
- Acceptance criteria:
  - [ ] local service deployment can run the extracted runtime stack with durable metadata storage
  - [ ] filesystem artifact handling remains supported through an abstraction layer
  - [ ] the existing contract bundle and evidence model stay consumable after the persistence split

### Phase 5: Hardening And Closeout

### GAP-057 Attachment-Scoped Operator Query Surfaces
- Type: AFK
- Blocked by: GAP-056
- User stories: 14, 27, 34, 40
- Status: active in direct-to-final-state mainline
- What to build:
  - add attachment-scoped queries for approvals, evidence, handoff, replay, and posture
  - stop degrading `inspect_evidence` for the primary attached path
  - keep operator surfaces read-only unless explicit escalation is required elsewhere
- Acceptance criteria:
  - [ ] attachment-scoped queries can list approvals, evidence refs, handoff refs, replay refs, and posture summary
  - [ ] `inspect_evidence` works on the primary attached path without default degradation
  - [ ] operator read surfaces remain stable enough for later console reuse

### GAP-058 Runtime Reader And CI Same-Contract Parity
- Type: AFK
- Blocked by: GAP-057
- User stories: 11, 12, 22, 36, 44
- Status: active in direct-to-final-state mainline
- What to build:
  - extend same-contract parity beyond verifier boundaries to runtime readers, adapters, and attachment consumers
  - add CI coverage for session bridge, runtime status, adapter, and attachment reader paths
  - fail loudly on incompatible contract shapes instead of silently defaulting
- Acceptance criteria:
  - [ ] runtime readers fail loudly on missing or incompatible contract fields
  - [ ] CI coverage proves session bridge, adapter, and attachment readers consume the declared contract shape
  - [ ] parity is demonstrable beyond verifier-only scope

### GAP-059 Remediation-Capable Attachment Doctor
- Type: AFK
- Blocked by: GAP-058
- User stories: 11, 12, 16, 24, 39
- Status: active in direct-to-final-state mainline
- What to build:
  - add guided remediation and fail-closed enforcement for missing, invalid, and stale attachment posture
  - map remediation steps back to exact commands or documents
  - keep remediation evidence-backed and rollback-aware
- Acceptance criteria:
  - [ ] missing, invalid, and stale bindings each have an explicit remediation path
  - [ ] fail-closed posture is used when execution should not continue
  - [ ] remediation actions are evidence-backed and rollback-aware

### GAP-060 Final-State Closeout And Claim Discipline
- Type: HITL
- Blocked by: GAP-059
- User stories: 18, 29, 37, 44, 46
- Status: active in direct-to-final-state mainline
- What to build:
  - sync backlog, roadmap, master outline, issue seeds, and closeout evidence to only verified completed work
  - record final commands, outputs, residual risks, and rollback notes
  - make final-state claims depend on executable proof rather than narrative alone
- Acceptance criteria:
  - [ ] roadmap, master outline, backlog, issue seeds, evidence, and gate results agree on what is complete
  - [ ] final-state claims are made only when exit criteria are actually met
  - [ ] closeout evidence records commands, outputs, residual risks, and rollback paths

## Vision

### GAP-018 Final Product Lifecycle Alignment
- Type: AFK
- Blocked by: None
- User stories: 1, 23, 29
- Status: complete in planning baseline
- What to build:
  - align roadmap, backlog, issue seeds, script, and entry docs around a full functional lifecycle
  - freeze the final product shape around a governed runtime target without collapsing it into repo-local scripts only
- Acceptance criteria:
  - [x] active planning docs describe the same lifecycle stages
  - [x] the project is described as a complete governed runtime target, not only as contracts/tooling
  - [x] the active queue was re-based away from MVP closure without re-opening MVP semantics

### GAP-019 Final Product Capability Boundary Freeze
- Type: HITL
- Blocked by: GAP-018
- User stories: 18, 29, 37
- Status: complete in planning baseline
- What to build:
  - freeze the final product capability boundary and explicit non-goals
  - define what counts as final product completeness
- Acceptance criteria:
  - [x] the final capability boundary is explicit and stable
  - [x] non-goals are explicit and remain outside the active queue
  - [x] final product completeness can be judged without ad hoc interpretation

## Foundation

### GAP-020 Clarification, Rollout, Compatibility, And Evidence Maturity
- Type: AFK
- Blocked by: GAP-019
- User stories: 4, 7, 23, 39
- Status: complete in Foundation runtime substrate
- What to build:
  - clarification protocol
  - rollout and promotion policy
  - compatibility signals
  - evidence maturity semantics
- Acceptance criteria:
  - [x] clarification is formal runtime policy rather than conversational convention
  - [x] rollout state supports `observe`, `advisory`, and `enforced`
  - [x] repo and adapter compatibility can be checked mechanically
  - [x] evidence quality can distinguish missing evidence from weak outcomes

### GAP-021 Real Build And Doctor Gates
- Type: AFK
- Blocked by: GAP-020
- User stories: 11, 12, 16, 24
- Status: complete in Foundation runtime substrate
- What to build:
  - real build command
  - real `doctor` or `hotspot_or_health_check` command
  - gate routing that uses live commands instead of `gate_na`
- Acceptance criteria:
  - [x] `build` no longer depends on `gate_na`
  - [x] `hotspot` no longer depends on `gate_na`
  - [x] canonical gate order can execute through live commands

### GAP-022 Durable Task Store And Workflow Skeleton
- Type: AFK
- Blocked by: GAP-020, GAP-021
- User stories: 1, 5, 24, 29, 30, 39
- Status: complete in Foundation runtime substrate
- What to build:
  - durable task persistence skeleton
  - workflow skeleton for pause, resume, timeout, retry, and compensation
- Acceptance criteria:
  - [x] task state survives process boundaries
  - [x] workflow transitions stay deterministic
  - [x] lifecycle data is no longer trapped in in-memory primitives

### GAP-023 Control Registry Lifecycle And Evidence Completeness Checks
- Type: AFK
- Blocked by: GAP-020, GAP-021
- User stories: 13, 21, 27, 33
- Status: complete in Foundation runtime substrate
- What to build:
  - control lifecycle metadata
  - evidence completeness checks
  - recurring review semantics for control health
- Acceptance criteria:
  - [x] controls track lifecycle and review state
  - [x] evidence completeness can fail missing required fields
  - [x] rollback and observability links are explicit per control

## Full Runtime

### GAP-024 Execution Worker And Managed Workspace Runtime
- Type: AFK
- Blocked by: GAP-022, GAP-023
- User stories: 8, 10, 17, 30, 31
- Status: complete in Full Runtime baseline
- What to build:
  - execution worker
  - managed workspace or worktree runtime
  - governed task execution path on real runtime state
- Acceptance criteria:
  - [x] governed tasks can execute through a worker rather than only through contract objects
  - [x] workspaces are lifecycle-bound and policy-aware
  - [x] worker execution preserves approval and rollback semantics

### GAP-025 Artifact Store, Evidence Bundle, And Replay Pipeline
- Type: AFK
- Blocked by: GAP-024
- User stories: 13, 14, 15, 27, 34, 39
- Status: complete in Full Runtime baseline
- What to build:
  - artifact store
  - persisted evidence bundles
  - replay references and failure signatures
- Acceptance criteria:
  - [x] artifacts persist outside stdout or transcript-only output
  - [x] evidence bundles can reference real artifacts and replay cases
  - [x] failed tasks leave enough persisted data for replay-oriented diagnosis

### GAP-026 Operational Quick And Full Gate Runner
- Type: AFK
- Blocked by: GAP-024, GAP-025
- User stories: 11, 12, 22, 36
- Status: complete in Full Runtime baseline
- What to build:
  - operational quick/full gate runner
  - artifact classification for risky outputs such as dependency, CI, and release-adjacent changes
- Acceptance criteria:
  - [x] quick and full gates run against real task executions
  - [x] gate artifacts are persisted and queryable
  - [x] risky files or artifacts are surfaced distinctly in delivery state

### GAP-027 Minimal Operator Surface For Task, Approval, Evidence, And Replay
- Type: AFK
- Blocked by: GAP-025, GAP-026
- User stories: 14, 27, 34, 40
- Status: complete in Full Runtime baseline
- What to build:
  - minimal operator surface
  - task list
  - approval queue
  - evidence and replay views
  - CLI-first operator path backed by stable runtime read models
- Acceptance criteria:
  - [x] operators can inspect tasks, approvals, evidence, and replay without raw log digging
  - [x] the surface remains control-plane focused
  - [x] a failed task can be inspected from the operator surface without reconstructing history manually
  - [x] the first delivery can be CLI-first as long as it preserves a stable read model for a later UI

### GAP-028 Health, Status, And Runtime Query Surface
- Type: AFK
- Blocked by: GAP-024, GAP-025
- User stories: 1, 11, 13, 14, 17, 39
- Status: complete in Full Runtime baseline
- What to build:
  - runtime health/status surface
  - task query surface
  - runtime-level visibility for current and past governed runs
- Acceptance criteria:
  - [x] the runtime exposes health or doctor results through a stable surface
  - [x] task state and query history are inspectable without direct database access
  - [x] operators can tell whether the runtime is healthy enough to accept new tasks

## Public Usable Release

### GAP-029 Single-Machine Deployment And Quickstart
- Type: AFK
- Blocked by: GAP-026, GAP-027, GAP-028
- User stories: 14, 27, 34, 40
- Status: complete in Public Usable Release baseline
- What to build:
  - single-machine deployment path
  - quickstart instructions
  - bootstrapping path for the complete runtime
  - first richer operator UI shell on top of the Full Runtime read model
- Acceptance criteria:
  - [x] the complete runtime can be started on one machine with a documented path
  - [x] quickstart covers task creation, execution, approval, verification, and evidence inspection
  - [x] the setup path does not depend on private maintainer knowledge
  - [x] operator-facing runtime flows are no longer limited to the CLI-first control surface

### GAP-030 Sample Repo Profiles And End-To-End Demo Flow
- Type: AFK
- Blocked by: GAP-029
- User stories: 2, 18, 37, 38
- Status: complete in Public Usable Release baseline
- What to build:
  - sample repo profiles
  - end-to-end demo flow for a real governed coding task
  - sample operator path for second-repo onboarding
- Acceptance criteria:
  - [x] at least one sample repo profile can run the documented quickstart
  - [x] the demo flow exercises the complete runtime path rather than only contracts
  - [x] second-repo onboarding follows profile inputs instead of kernel changes

### GAP-031 Public Usable Release Criteria And Packaging
- Type: AFK
- Blocked by: GAP-029, GAP-030
- User stories: 18, 31, 37, 38
- Status: complete in Public Usable Release baseline
- What to build:
  - public usable release criteria
  - package or distribution layout for the single-machine runtime
  - release-readiness checklist for the full runtime
- Acceptance criteria:
  - [x] public usable release criteria are explicit
  - [x] packaging or distribution layout matches the documented quickstart
  - [x] the release checklist covers the full product capability boundary

### GAP-032 Adapter Baseline And Fallback Or Degrade Behavior
- Type: AFK
- Blocked by: GAP-029, GAP-030
- User stories: 20, 27, 35
- Status: complete in Public Usable Release baseline
- What to build:
  - adapter baseline for the full runtime
  - explicit fallback or degrade behavior when adapter capabilities are weak
  - operator-visible compatibility posture
- Acceptance criteria:
  - [x] Codex-first compatibility remains explicit
  - [x] unsupported adapter capabilities degrade or fail closed explicitly
  - [x] compatibility posture is visible in docs and runtime outputs

## Maintenance

### GAP-033 Compatibility And Upgrade Policy
- Type: AFK
- Blocked by: GAP-031, GAP-032
- User stories: 21, 31, 37, 38
- Status: complete in Maintenance baseline
- What to build:
  - compatibility policy
  - upgrade policy for adapters, repo profiles, and persisted runtime state
- Acceptance criteria:
  - [x] upgrade expectations are explicit
  - [x] compatibility-breaking changes require an explicit note or migration path
  - [x] adapter and repo profile evolution does not silently break the full runtime

### GAP-034 Maintenance, Deprecation, And Retirement Policy
- Type: AFK
- Blocked by: GAP-033
- User stories: 21, 22, 27, 40
- Status: complete in Maintenance baseline
- What to build:
  - maintenance boundary
  - deprecation policy
  - retirement or removal policy for outdated capabilities
- Acceptance criteria:
  - [x] maintenance expectations are documented
  - [x] deprecated capabilities include replacement or migration guidance
  - [x] retired capabilities do not disappear without traceability

## Interactive Session Productization

### GAP-035 Generic Target-Repo Attachment Pack And Onboarding Flow
- Type: AFK
- Blocked by: GAP-032, GAP-034, GAP-042
- User stories: 18, 38, 42, 46
- Status: complete on current branch baseline
- What to build:
  - repo-local declarative light pack
  - target-repo bootstrap and attach flow
  - machine-local runtime binding that keeps mutable state out of the target repo
- Acceptance criteria:
  - [x] a new target repo can be attached without copying the runtime into it
  - [x] repo-local light pack contents are explicit, minimal, and portable
  - [x] target-repo onboarding produces a stable runtime binding and doctor-visible posture

### GAP-036 Attach-First Session Bridge And Governed Interaction Surface
- Type: AFK
- Blocked by: GAP-035, GAP-043
- User stories: 1, 5, 41, 43
- Status: complete on current branch baseline
- What to build:
  - attach-first session bridge
  - governed in-session commands for task start, approval, gate runs, and evidence inspection
  - launch-second fallback when live session attach is unavailable
  - PolicyDecision normalization so execution-like session commands expose `allow` / `escalate` / `deny` instead of raw local-baseline `allowed` / `paused` / fail-closed outcomes
- Acceptance criteria:
  - [x] the preferred user flow runs inside an active AI coding session rather than only through batch CLI
  - [x] governed actions are callable without replacing the upstream AI tool UI
  - [x] launch mode remains available as an explicit compatibility fallback
  - [x] execution-like session commands expose `PolicyDecision` outcomes rather than raw legacy write-governance statuses

### GAP-037 Direct Codex Adapter And Evidence Mapping
- Type: HITL
- Blocked by: GAP-035, GAP-036, GAP-043
- User stories: 2, 11, 31, 41, 43
- Status: complete on current branch baseline
- What to build:
  - direct Codex adapter for interactive governed use
  - session-to-task binding and mutation capture
  - evidence mapping for Codex-driven file changes, tool calls, and gate runs
- Acceptance criteria:
  - [x] at least one real Codex path is direct rather than manual-handoff only
  - [x] runtime evidence can attribute Codex-driven changes and verification output to one governed task
  - [x] unsupported Codex capabilities degrade explicitly instead of being implied silently

### GAP-038 Capability-Tiered Adapter Framework For Multiple AI Tools
- Type: AFK
- Blocked by: GAP-035, GAP-036, GAP-044
- User stories: 20, 31, 37, 44
- Status: complete on current branch baseline
- What to build:
  - capability tiers for native attach, process bridge, and manual handoff
  - adapter registry updates for non-Codex tools
  - explicit governance guarantees per capability tier
- Acceptance criteria:
  - [x] adapters can declare attach strength without changing kernel semantics
  - [x] non-Codex tools have an honest compatibility posture
  - [x] degrade and fail-closed behaviors remain explicit and operator-visible

### GAP-039 Multi-Repo Trial Loop And Generic Onboarding Kit
- Type: HITL
- Blocked by: GAP-035, GAP-036, GAP-037, GAP-038, GAP-044
- User stories: 14, 37, 38, 39, 45
- Status: complete on current branch baseline as the first productization slice; full external attached-repo closure is tracked by `GAP-053`
- What to build:
  - reusable onboarding kit for arbitrary target repos
  - multi-repo trial execution and feedback capture
  - evidence-backed iteration path for onboarding friction, adapter gaps, and gate drift
- Acceptance criteria:
  - [x] profile-based multi-repo trial loops can run without kernel rewrites and preserve per-repo structured evidence outputs
  - [x] onboarding, adapter, and gate failures are captured as structured trial evidence
  - [x] the product can evolve from real trial data instead of repo-specific one-off fixes

## Strategy Alignment Gates

### GAP-040 Runtime Governance Borrowing Matrix
- Type: AFK
- Blocked by: None
- User stories: 29, 31, 37, 44
- Status: complete in Strategy Alignment baseline
- What to build:
  - borrowing matrix for Microsoft Agent Governance Toolkit, OPA, Keycard, Coder AI Governance, MCP, GAAI-style repo files, OpenHands, SWE-agent, Hermes-like agents, oh-my-codex or oh-my-claudecode-style wrappers, NeMo Guardrails, and Guardrails AI
  - product-layer classification for each reference
  - explicit borrow and avoid guidance
- Acceptance criteria:
  - [x] each reference is classified by layer rather than copied as product identity
  - [x] each row includes borrow, avoid, impact, confidence, and official or primary source
  - [x] matrix conclusions preserve the project's runtime/action governance identity

### GAP-041 Source-Of-Truth And Runtime Bundle ADR
- Type: HITL
- Blocked by: GAP-040
- User stories: 18, 21, 29, 38
- Status: complete in Strategy Alignment baseline
- What to build:
  - ADR-0007 for source-of-truth versus runtime contract bundle boundaries
  - decision that `docs/`, `schemas/`, and `packages/contracts/` remain the repository source of truth
  - decision that repo-local light packs or `.governed-ai/`-style bundles are generated or validated runtime-consumable attachment surfaces
- Acceptance criteria:
  - [x] ADR rejects hand-maintaining two competing contract copies
  - [x] ADR links the decision to ADR-0005 and ADR-0006
  - [x] ADR gives GAP-035 a stable boundary for repo-local light packs

### GAP-042 Repo-Native Contract Bundle Architecture
- Type: AFK
- Blocked by: GAP-041
- User stories: 18, 31, 38, 46
- Status: complete in Strategy Alignment baseline
- What to build:
  - architecture document for repo-native contract bundle contents
  - mapping from repo profile, gates, write policy, approval policy, adapter capabilities, PolicyDecision, evidence, handoff, and rollback references to existing source-of-truth docs and schemas
  - state placement rules for repo-local declarations versus machine-local runtime state
- Acceptance criteria:
  - [x] GAP-035 light-pack scope is described as the runtime bundle attachment shape
  - [x] mutable task, run, approval, artifact, and replay state remains machine-local
  - [x] local and CI consumers are described as reading the same contract inputs

### GAP-043 PolicyDecision Contract
- Type: AFK
- Blocked by: GAP-042
- User stories: 7, 8, 20, 27, 31, 43
- Status: complete in Strategy Alignment baseline
- What to build:
  - PolicyDecision spec, JSON Schema, Python contract, and runtime tests
  - `allow`, `escalate`, and `deny` decision statuses
  - decision basis, evidence reference, approval reference, and remediation hint fields
- Acceptance criteria:
  - [x] `allow`, `escalate`, and `deny` are schema-backed and tested
  - [x] `deny` fails closed and does not produce an executable action
  - [x] `escalate` carries approval intent without conflating approval with execution

### GAP-044 Local/CI Same-Contract Verification And Alignment Closeout
- Type: AFK
- Blocked by: GAP-042, GAP-043
- User stories: 11, 12, 22, 36, 44
- Status: complete in Strategy Alignment baseline
- What to build:
  - verification spec update for local and CI same-contract inputs
  - docs/script regression coverage for non-ASCII markdown path collection and ignored worktree docs
  - backlog, issue-seed, and seeding script reconciliation for the strategy alignment gates
- Acceptance criteria:
  - [x] local and CI verification are described as consuming the same repo contract inputs
  - [x] docs verification handles non-ASCII markdown paths and ignored worktree markdown robustly
  - [x] issue seeding renders GAP-040 through GAP-044 without changing GAP-035 through GAP-039 semantics
