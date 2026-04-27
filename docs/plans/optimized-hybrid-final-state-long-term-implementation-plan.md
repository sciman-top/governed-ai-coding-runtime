# Optimized Hybrid Final-State Long-Term Implementation Plan

## Status
- Created from the 2026-04-27 optimized hybrid final-state and stack-staging review.
- Future-facing queue: `GAP-093..103`.
- Current posture: `GAP-093..103` are complete. No long-term package was implemented; `LTP-01..06` remain deferred/watch or not triggered pending fresh scope-fence evidence.

## Goal
Provide an implementation-ready plan for the long-term optimized hybrid final state while preserving the current rule that heavyweight components remain trigger-based.

## Planning Rules
- Keep the current verified baseline unless a task proves a boundary pressure that justifies the transition stack.
- Treat `FastAPI`, `Pydantic v2`, `PostgreSQL`, `OpenTelemetry`, sandbox/process guards, and provenance records as transition-stack tools, not identity changes.
- Treat `Temporal`, `OPA/Rego`, event buses, `Redis`, `pgvector`, `gRPC`, A2A gateway, `Next.js`, and full observability suites as candidates that need trigger evidence.
- Select at most one long-term package for implementation at a time.
- Preserve gate order: `build -> test -> contract/invariant -> hotspot`.

## Task Graph

`GAP-092 -> GAP-093 -> GAP-094 -> GAP-095 -> GAP-096 -> GAP-097 -> GAP-098 -> GAP-099 -> GAP-100 -> GAP-101 -> GAP-102 -> GAP-103`

## GAP-093 Optimized Hybrid Long-Term Planning Baseline

### Type
AFK

### Dependencies
- `GAP-092`

### Scope
- Create the long-term roadmap and implementation plan for the optimized hybrid final state.
- Add `GAP-093..102` to the issue-ready backlog and issue seeds.
- Extend issue-seeding label mapping for the new queue.
- Record evidence for the planning baseline.

### Acceptance Criteria
- [x] roadmap, implementation plan, backlog, issue seeds, plan index, and docs index agree on `GAP-093..102`
- [x] `LTP-01..06` are visible as trigger-based packages, not started work
- [x] issue rendering validates all task bodies without GitHub calls
- [x] evidence records commands, changed files, residual risks, and rollback

### Verification
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`

### Likely Files
- `docs/roadmap/optimized-hybrid-final-state-long-term-roadmap.md`
- `docs/plans/optimized-hybrid-final-state-long-term-implementation-plan.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/issue-seeds.yaml`
- `docs/README.md`
- `docs/plans/README.md`
- `docs/backlog/README.md`
- `scripts/github/create-roadmap-issues.ps1`
- `docs/change-evidence/*.md`

### Rollback
Revert the planning docs, backlog/seeds, issue-seeding label mapping, and evidence file with git.

## GAP-094 Execution Containment Contract And Tool Coverage Floor

### Type
AFK

### Dependencies
- `GAP-093`

### Scope
- Inventory governed executable tool families: file write, shell, git, package manager, browser automation, and MCP/tool bridges where present.
- Define common containment fields: workspace root, allowed path roots, environment policy, network posture, timeout, approval class, evidence refs, and rollback refs.
- Add fail-closed behavior for unclassified executable tool families.

### Acceptance Criteria
- [x] every governed executable tool family has a declared containment profile
- [x] unclassified executable tools fail closed or require explicit waiver
- [x] execution evidence records containment metadata and rollback metadata
- [x] containment contract has schema/spec/test coverage

### Verification
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

### Likely Files
- `docs/specs/*`
- `schemas/jsonschema/*`
- `packages/contracts/src/*`
- `packages/runtime/src/*`
- `tests/runtime/*`
- `docs/change-evidence/*.md`

### Rollback
Revert the containment contract and runtime enforcement changes. Restore previous executable-tool behavior only if gates prove no fail-open path remains.

## GAP-095 Provenance And Light-Pack Release Evidence Floor

### Type
AFK

### Dependencies
- `GAP-094`

### Scope
- Define provenance records for generated repo-local light packs, control packs, and release-adjacent artifacts.
- Include source ref, generator version, input hash, output hash, target repo binding, and waiver metadata.
- Make doctor/verifier surfaces report missing provenance for generated artifacts that claim release readiness.

### Acceptance Criteria
- [x] generated light packs and control packs can carry provenance metadata
- [x] release-adjacent artifacts have either provenance or an explicit waiver
- [x] verifier/doctor output distinguishes missing provenance from unsupported provenance
- [x] documentation explains rollback and regeneration behavior

### Verification
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Dependency`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Doctor`

### Likely Files
- `docs/specs/*`
- `schemas/jsonschema/*`
- `scripts/governance/*`
- `scripts/verify-repo.ps1`
- `docs/change-evidence/*.md`

### Rollback
Revert provenance schema/verifier changes and remove generated provenance samples if they were created by the task.

## GAP-096 Service-Shaped Transition Stack Convergence Gate

### Type
AFK

### Dependencies
- `GAP-095`

### Scope
- Define when transition-stack dependencies are allowed: API boundary, typed runtime validation, durable metadata, tracing, and containment.
- Keep local single-machine use functional without forcing service infrastructure.
- Add drift checks for API/CLI parity and boundary-owned validation.

### Acceptance Criteria
- [x] `FastAPI` is allowed only for active service API boundaries
- [x] `Pydantic v2` is used at API/runtime validation boundaries, not as a duplicate schema truth
- [x] SQLite/filesystem remain valid for local use; PostgreSQL is scoped to service-shaped metadata pressure
- [x] tracing hooks exist at runtime/API boundaries without requiring a full observability stack
- [x] CLI and API paths share the same contract behavior for execution-like commands

### Verification
- `python scripts/verify-transition-stack-convergence.py`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- targeted API/CLI parity tests for touched surfaces

### Likely Files
- `docs/architecture/mvp-stack-vs-target-stack.md`
- `docs/architecture/governed-ai-coding-runtime-target-architecture.md`
- `docs/specs/*`
- `packages/runtime/src/*`
- `tests/runtime/*`

### Rollback
Revert transition-stack adoption rules and any dependency additions that cannot be tied to an active boundary.

## GAP-097 Orchestration And Policy Trigger Review

### Type
HITL

### Dependencies
- `GAP-096`

### Scope
- Evaluate `LTP-01 orchestration-depth` and `LTP-02 policy-runtime-separation`.
- Use real runtime traces, failure signatures, policy count, waiver count, retry/compensation complexity, and review burden.
- Decide `not_triggered`, `watch`, or `triggered` for each package.

### Acceptance Criteria
- [x] orchestration trigger decision is evidence-backed
- [x] policy trigger decision is evidence-backed
- [x] no workflow engine or external policy runtime is started without a selected scope fence
- [x] decision evidence includes rollback and next review trigger

### Verification
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
- latest representative runtime-flow or target-repo evidence window

### Likely Files
- `docs/change-evidence/*.md`
- `docs/plans/*`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/issue-seeds.yaml`

### Rollback
Revert decision docs if evidence is found stale or misclassified.

## GAP-098 Data Plane And Operations Trigger Review

### Type
HITL

### Dependencies
- `GAP-097`

### Scope
- Evaluate `LTP-03 data-plane-scaling` and `LTP-05 operations-hardening`.
- Use event volume, replay retention, artifact size, query latency, evidence recovery, sustained workload, SLO, and failure-remediation signals.

### Acceptance Criteria
- [x] data-plane trigger decision is evidence-backed
- [x] operations-hardening trigger decision is evidence-backed
- [x] no event bus, semantic store, or full observability suite is introduced without trigger evidence
- [x] decision evidence separates runtime failures from target-repo business failures

### Verification
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
- latest KPI snapshot or target-repo run summary

### Likely Files
- `docs/change-evidence/*.md`
- `docs/runtime-*`
- `docs/architecture/*`
- `docs/backlog/issue-ready-backlog.md`

### Rollback
Revert decision docs if workload or KPI data does not support the classification.

## GAP-099 Multi-Host And Protocol Trigger Review

### Type
HITL

### Dependencies
- `GAP-098`

### Scope
- Evaluate `LTP-04 multi-host-first-class` and protocol boundary depth.
- Check Codex and non-Codex conformance parity, adapter evidence, MCP/A2A boundary pressure, and product demand.
- Preserve kernel-owned task lifecycle, approval, rollback, and evidence semantics.

### Acceptance Criteria
- [x] multi-host trigger decision is evidence-backed
- [x] protocol-boundary decision is evidence-backed
- [x] MCP/A2A are treated as integration protocols, not runtime governance owners
- [x] selected next steps preserve adapter conformance and fail-closed behavior

### Verification
- adapter conformance tests for touched hosts
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`

### Likely Files
- `docs/architecture/*adapter*`
- `docs/specs/*adapter*`
- `packages/runtime/src/*adapter*`
- `tests/runtime/*adapter*`
- `docs/change-evidence/*.md`

### Rollback
Revert decision docs and any protocol-boundary claims if conformance evidence is stale or incomplete.

## GAP-100 Selected LTP Scope Fence And Architecture ADR

### Type
HITL

### Dependencies
- `GAP-097`
- `GAP-098`
- `GAP-099`

### Scope
- Select exactly one `LTP-01..06` package for implementation, or defer all packages with evidence.
- If one package is selected, create an architecture decision, bounded scope, verification floor, rollback plan, and owner/evidence path.
- Update backlog and issue seeds for the selected package without widening unrelated packages.

### Acceptance Criteria
- [x] exactly one package is selected, or all packages are deferred with reasons
- [x] selected package has a bounded vertical slice and explicit non-goals
- [x] selected package has verification, rollback, compatibility, and evidence requirements
- [x] non-selected packages remain visible as deferred/watch, not silently dropped

### Verification
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`

### Likely Files
- `docs/adrs/*`
- `docs/plans/*`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/issue-seeds.yaml`
- `docs/change-evidence/*.md`

### Rollback
Revert selected-package planning docs and restore all packages to deferred/watch if the evidence basis is invalidated.

## GAP-101 Selected LTP Implementation Batch 1

### Type
HITL

### Dependencies
- `GAP-100`

### Scope
- Implement the first vertical slice of the package selected by `GAP-100`.
- Cover contract, runtime behavior, operator/evidence surface, tests, and rollback.
- Keep all other long-term packages out of scope.

### Acceptance Criteria
- [x] implementation touches only the selected package scope
- [x] contract, runtime, evidence, and operator surfaces agree
- [x] fallback or rollback behavior is explicit and tested
- [x] closeout evidence includes commands, outputs, risks, and compatibility notes

### Verification
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
- targeted tests for the selected package
- representative runtime-flow or target-repo trial where the selected package changes behavior

### Likely Files
Depends on selected package. The scope fence from `GAP-100` must name the exact write set before implementation begins.

### Rollback
Use the rollback plan approved in `GAP-100`. If the selected package was deferred instead of implemented, close this task as `deferred-no-implementation` with evidence.

## GAP-102 Sustained Optimized Hybrid Release Readiness Closeout

### Type
HITL

### Dependencies
- `GAP-101`

### Scope
- Run a sustained evidence window against self-runtime and representative target repos.
- Refresh final-state claims, roadmap labels, backlog statuses, issue seeds, and evidence links.
- Confirm that containment, provenance, transition-stack boundaries, and any selected LTP implementation remain reproducible.

### Acceptance Criteria
- [x] fresh gates support every visible optimized final-state claim
- [x] target-repo or representative workload evidence is linked
- [x] claim catalog, roadmap, implementation plan, backlog, issue seeds, and evidence agree
- [x] residual risks and next review triggers are explicit

### Verification
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
- latest all-target or representative runtime-flow evidence window
- `git diff --check`

### Likely Files
- `docs/change-evidence/*.md`
- `docs/README.md`
- `docs/architecture/hybrid-final-state-master-outline.md`
- `docs/roadmap/optimized-hybrid-final-state-long-term-roadmap.md`
- `docs/plans/optimized-hybrid-final-state-long-term-implementation-plan.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/issue-seeds.yaml`

### Rollback
Downgrade final-state claims and revert status labels if fresh evidence cannot reproduce the claimed posture.

## GAP-103 Fresh All-Target Sustained Workload Window

### Type
HITL

### Dependencies
- `GAP-102`

### Scope
- Rerun the all-target daily runtime-flow window after the optimized long-term queue closeout.
- Record target count, failure count, timeout posture, governance sync posture, and per-target flow exit codes.
- Keep `LTP-01..06` deferred unless the fresh window produces trigger evidence.

### Acceptance Criteria
- [x] all configured target repos run through the daily preset with `failure_count=0`
- [x] evidence records command, timing, timeout controls, and per-target exit posture
- [x] final-state wording distinguishes fresh all-target evidence from heavy LTP implementation
- [x] issue rendering, docs/scripts gates, and repo gates agree after the new queue item

### Verification
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -FlowMode daily -Json -BatchTimeoutSeconds 1200 -RuntimeFlowTimeoutSeconds 300`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
- `git diff --check`

### Likely Files
- `docs/change-evidence/20260427-gap-103-fresh-all-target-workload-window.md`
- `docs/README.md`
- `docs/roadmap/optimized-hybrid-final-state-long-term-roadmap.md`
- `docs/plans/optimized-hybrid-final-state-long-term-implementation-plan.md`
- `docs/backlog/README.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/issue-seeds.yaml`
- `scripts/github/create-roadmap-issues.ps1`

### Rollback
Revert `GAP-103` planning/status entries and evidence if the fresh all-target window cannot be reproduced.

## Checkpoints

| checkpoint | after | required decision |
|---|---|---|
| planning checkpoint | `GAP-093` | new roadmap/plan/backlog/seeds are canonical |
| containment checkpoint | `GAP-095` | execution and release claims are not outpacing containment/provenance evidence |
| transition-stack checkpoint | `GAP-096` | dependencies are justified by active boundaries |
| LTP decision checkpoint | `GAP-100` | exactly one package selected or all packages deferred |
| release-readiness checkpoint | `GAP-102` | claims, gates, and workload evidence agree |
| fresh all-target checkpoint | `GAP-103` | all configured target repos still pass the daily flow after closeout |

## Evidence Requirements
Each gap must add or update `docs/change-evidence/*.md` with:
- goal
- scope
- changed files
- commands
- key output
- residual risks
- rollback path
