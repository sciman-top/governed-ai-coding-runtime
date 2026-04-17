# Issue-Ready Backlog

## Parent Initiative
Governed AI Coding Runtime Full Functional Lifecycle

## Assumptions
- `Phase 0` through `Phase 4` remain complete through `GAP-017`
- this is a personal free open-source project, so the plan stays function-first and intentionally light on non-functional operations
- the target product is a single-machine self-hosted complete governed runtime
- internal runtime boundaries remain service-shaped even though deployment stays single-machine first
- Codex compatibility remains the first adapter priority, but final product completeness cannot be Codex-only
- non-goals remain non-goals: no enterprise org model, no marketplace, no default multi-agent orchestration, no memory-first product identity

## Current Baseline
- PRD, architecture, ADRs, specs, runtime contract primitives, repo verifier entrypoints, sample repo profiles, and a runtime-consumable control pack already exist.
- The MVP governance-kernel backlog is complete through `GAP-017`.
- `Vision / GAP-018` and `GAP-019` are complete through lifecycle planning alignment and capability freeze.
- `Foundation / GAP-020` through `GAP-023` are now complete on the current branch baseline.
- The active gap is now `Full Runtime / GAP-024` through `GAP-028`, followed by `Public Usable Release` and `Maintenance`.

## Vision

### GAP-018 Final Product Lifecycle Alignment
- Type: AFK
- Blocked by: None
- User stories: 1, 23, 29
- Status: complete in planning baseline
- What to build:
  - align roadmap, backlog, issue seeds, script, and entry docs around a full functional lifecycle
  - freeze the final product shape as a single-machine self-hosted complete runtime
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
- What to build:
  - execution worker
  - managed workspace or worktree runtime
  - governed task execution path on real runtime state
- Acceptance criteria:
  - [ ] governed tasks can execute through a worker rather than only through contract objects
  - [ ] workspaces are lifecycle-bound and policy-aware
  - [ ] worker execution preserves approval and rollback semantics

### GAP-025 Artifact Store, Evidence Bundle, And Replay Pipeline
- Type: AFK
- Blocked by: GAP-024
- User stories: 13, 14, 15, 27, 34, 39
- What to build:
  - artifact store
  - persisted evidence bundles
  - replay references and failure signatures
- Acceptance criteria:
  - [ ] artifacts persist outside stdout or transcript-only output
  - [ ] evidence bundles can reference real artifacts and replay cases
  - [ ] failed tasks leave enough persisted data for replay-oriented diagnosis

### GAP-026 Operational Quick And Full Gate Runner
- Type: AFK
- Blocked by: GAP-024, GAP-025
- User stories: 11, 12, 22, 36
- What to build:
  - operational quick/full gate runner
  - artifact classification for risky outputs such as dependency, CI, and release-adjacent changes
- Acceptance criteria:
  - [ ] quick and full gates run against real task executions
  - [ ] gate artifacts are persisted and queryable
  - [ ] risky files or artifacts are surfaced distinctly in delivery state

### GAP-027 Operator UI For Task, Approval, Evidence, And Replay
- Type: AFK
- Blocked by: GAP-025, GAP-026
- User stories: 14, 27, 34, 40
- What to build:
  - minimal operator UI
  - task list
  - approval queue
  - evidence and replay views
- Acceptance criteria:
  - [ ] operators can inspect tasks, approvals, evidence, and replay without raw log digging
  - [ ] the UI remains control-plane focused
  - [ ] a failed task can be inspected from the UI without reconstructing history manually

### GAP-028 Health, Status, And Runtime Query Surface
- Type: AFK
- Blocked by: GAP-024, GAP-025
- User stories: 1, 11, 13, 14, 17, 39
- What to build:
  - runtime health/status surface
  - task query surface
  - runtime-level visibility for current and past governed runs
- Acceptance criteria:
  - [ ] the runtime exposes health or doctor results through a stable surface
  - [ ] task state and query history are inspectable without direct database access
  - [ ] operators can tell whether the runtime is healthy enough to accept new tasks

## Public Usable Release

### GAP-029 Single-Machine Deployment And Quickstart
- Type: AFK
- Blocked by: GAP-026, GAP-027, GAP-028
- User stories: 14, 27, 34, 40
- What to build:
  - single-machine deployment path
  - quickstart instructions
  - bootstrapping path for the complete runtime
- Acceptance criteria:
  - [ ] the complete runtime can be started on one machine with a documented path
  - [ ] quickstart covers task creation, execution, approval, verification, and evidence inspection
  - [ ] the setup path does not depend on private maintainer knowledge

### GAP-030 Sample Repo Profiles And End-To-End Demo Flow
- Type: AFK
- Blocked by: GAP-029
- User stories: 2, 18, 37, 38
- What to build:
  - sample repo profiles
  - end-to-end demo flow for a real governed coding task
  - sample operator path for second-repo onboarding
- Acceptance criteria:
  - [ ] at least one sample repo profile can run the documented quickstart
  - [ ] the demo flow exercises the complete runtime path rather than only contracts
  - [ ] second-repo onboarding follows profile inputs instead of kernel changes

### GAP-031 Public Usable Release Criteria And Packaging
- Type: AFK
- Blocked by: GAP-029, GAP-030
- User stories: 18, 31, 37, 38
- What to build:
  - public usable release criteria
  - package or distribution layout for the single-machine runtime
  - release-readiness checklist for the full runtime
- Acceptance criteria:
  - [ ] public usable release criteria are explicit
  - [ ] packaging or distribution layout matches the documented quickstart
  - [ ] the release checklist covers the full product capability boundary

### GAP-032 Adapter Baseline And Fallback Or Degrade Behavior
- Type: AFK
- Blocked by: GAP-029, GAP-030
- User stories: 20, 27, 35
- What to build:
  - adapter baseline for the full runtime
  - explicit fallback or degrade behavior when adapter capabilities are weak
  - operator-visible compatibility posture
- Acceptance criteria:
  - [ ] Codex-first compatibility remains explicit
  - [ ] unsupported adapter capabilities degrade or fail closed explicitly
  - [ ] compatibility posture is visible in docs and runtime outputs

## Maintenance

### GAP-033 Compatibility And Upgrade Policy
- Type: AFK
- Blocked by: GAP-031, GAP-032
- User stories: 21, 31, 37, 38
- What to build:
  - compatibility policy
  - upgrade policy for adapters, repo profiles, and persisted runtime state
- Acceptance criteria:
  - [ ] upgrade expectations are explicit
  - [ ] compatibility-breaking changes require an explicit note or migration path
  - [ ] adapter and repo profile evolution does not silently break the full runtime

### GAP-034 Maintenance, Deprecation, And Retirement Policy
- Type: AFK
- Blocked by: GAP-033
- User stories: 21, 22, 27, 40
- What to build:
  - maintenance boundary
  - deprecation policy
  - retirement or removal policy for outdated capabilities
- Acceptance criteria:
  - [ ] maintenance expectations are documented
  - [ ] deprecated capabilities include replacement or migration guidance
  - [ ] retired capabilities do not disappear without traceability
