# Governed AI Coding Runtime 90-Day Plan

## Execution Inputs

This plan assumes the following documents are the active design inputs:
- PRD:
  - `docs/prd/governed-ai-coding-runtime-prd.md`
- MVP loop:
  - `docs/architecture/minimum-viable-governance-loop.md`
- Boundary classification:
  - `docs/architecture/governance-boundary-matrix.md`
- ADRs:
  - `docs/adrs/0001-control-plane-first.md`
  - `docs/adrs/0002-no-multi-repo-distribution-in-mvp.md`
  - `docs/adrs/0003-single-agent-baseline-first.md`
  - `docs/adrs/0005-governance-kernel-and-control-packs-before-platform-breadth.md`
- Specs:
  - `docs/specs/control-registry-spec.md`
  - `docs/specs/repo-profile-spec.md`
  - `docs/specs/tool-contract-spec.md`
  - `docs/specs/risk-tier-and-approval-spec.md`
  - `docs/specs/task-lifecycle-and-state-machine-spec.md`
  - `docs/specs/evidence-bundle-spec.md`
  - `docs/specs/verification-gates-spec.md`
  - `docs/specs/eval-and-trace-grading-spec.md`
- Backlog seeds:
  - `docs/backlog/mvp-backlog-seeds.md`

## Current Baseline
- `docs/`, `schemas/`, and `scripts/github/create-roadmap-issues.ps1` already exist.
- Root `README.md` and project `AGENTS.md` already exist as repo entry contracts.
- The repository is still `docs-first / contracts-first`; `apps/`, `packages/`, `infra/`, and `tests/` have not been bootstrapped yet.
- The kernel contract family, schema examples, and two sample repo profiles are now landed; sample control packs and validators are not.
- The next 90 days should therefore validate a governance kernel plus bounded multi-repo reuse, not just generate a broader platform diagram.

## Goal
- Deliver an MVP governance kernel for governed AI coding in 90 days.
- Prove that one kernel can govern multiple repository profiles without becoming a distribution hub.
- Keep the first executable loop auditable, replayable, approval-aware, and rollbackable.

## MVP Definition
A 90-day MVP is successful only if it can do all of the following:
- validate kernel contracts and control packs locally
- load at least one repo profile and run a governed read-only task end-to-end
- require approval before high-risk writes
- emit evidence, decision logs, and required trace fields
- run a minimum eval and trace-grading baseline
- prove compatibility on a second target repository without forking kernel semantics

## Scope

### In Scope
- governance kernel contracts and schemas
- control packs for policy, gates, hooks, skills, evals, and knowledge controls
- repo profiles and repo admission validation
- deterministic task lifecycle
- governed tool execution and approval semantics
- evidence, trace, and replay-oriented output
- second-repo reuse pilot

### Out of Scope
- multi-repo distribution hub behavior
- default multi-agent orchestration
- memory-first personalization platform
- skill marketplace or promotion workflow
- broad deployment automation as the platform identity
- org-scale enterprise tenancy and RBAC complexity

## Roadmap Principles
- Build the smallest executable governance loop before adding platform width.
- Borrow mechanisms from external projects, not their product identity.
- Keep `task / approval / gate / evidence / trace / rollback` deterministic.
- Treat repo reuse as `same kernel, different profiles`, not as source mirroring.
- Only allow repo overrides that tighten or extend governance.

## What To Add / What To Weaken / What To Defer

### Add now
- sample control packs
- compatibility validator and repo admission checks
- schema example validation and repo-profile admission validation
- golden task set for eval and trace grading

### Weaken intentionally
- console breadth before kernel completion
- A2A or federation positioning in MVP materials
- deployment automation as a default path
- generalized agent platform framing

### Defer explicitly
- memory-first architecture
- multi-agent orchestration by default
- skill marketplace and promotion lifecycle
- multi-repo distribution and backflow sync
- enterprise-grade organization model

## Phases

### Phase 0: Kernel Alignment (Week 1-2)
- ratify the governance-kernel boundary
- convert the kernel contracts into executable examples and sample assets
- align roadmap, backlog, and seeding artifacts with the narrowed MVP

**Expected benefit**
- prevents the repository from drifting into a generic agent-platform backlog before the kernel is executable

**Primary risk**
- spending too long on documentation without converting it into executable validators and samples

### Phase 1: Kernel Foundation (Week 3-5)
- establish repo profiles, control packs, validators, and bootstrap skeleton
- make control maturity, waivers, and repo admission rules executable

**Expected benefit**
- turns the current schema layer into a reusable governance substrate instead of a static design archive

**Primary risk**
- bootstrapping runtime code before profile and control-pack boundaries are stable

### Phase 2: Governed Execution (Week 6-9)
- implement lifecycle, gates, repo map, evidence, tool governance, approval, and governed session bootstrap

**Expected benefit**
- proves that AI coding can run inside a controlled shell instead of remaining a design hypothesis

**Primary risk**
- shipping execution without enough decision logging, replay references, or gate evidence

### Phase 3: Assurance And Reuse Proof (Week 10-13)
- add evals, trace grading, handoff, second-repo pilot, and minimum console or hardening surfaces

**Expected benefit**
- validates that the kernel is reusable and observable rather than only functional in one curated path

**Primary risk**
- pulling in too much product surface area and diluting the second-repo proof

## Weekly Plan

### Week 1
**Goal**
- lock the governance-kernel boundary and executable contract asset baseline

**Tasks**
- add `ADR-0005`
- add executable examples for `hook`, `skill manifest`, `knowledge source`, `waiver`, `provenance`, and `repo-map`
- align roadmap and backlog around kernel-first execution

**Acceptance**
- kernel boundary is explicit and accepted
- example instances exist for the kernel contract family
- roadmap and backlog no longer imply a generic platform-first build

### Week 2
**Goal**
- define reuse inputs before runtime bootstrap

**Tasks**
- land and document at least two sample repo profiles
- add at least one sample control pack
- define repo admission and compatibility checks
- define control maturity and waiver expectations

**Acceptance**
- sample profiles cover commands, tools, and path policy
- sample control pack has version, owner, and scope
- repo admission rules are explicit

### Week 3
**Goal**
- bootstrap repository skeleton and local verification foundation

**Tasks**
- create `apps/`, `packages/`, `infra/`, and `tests/`
- define local verification entrypoints
- add CI for schema checks, doc integrity, and script parsing

**Acceptance**
- implementation skeleton exists
- local verification entrypoint is documented
- CI can run the minimum repository checks

### Week 4
**Goal**
- establish deterministic kernel state and registry semantics

**Tasks**
- implement task store skeleton
- implement deterministic lifecycle validation
- add control registry maturity and waiver support

**Acceptance**
- illegal transitions fail closed
- control status can express `advisory`, `observe`, and `enforce`
- state changes can emit evidence references

### Week 5
**Goal**
- make repository context and verification executable

**Tasks**
- implement quick and full gate runner
- implement repo map and context shaper
- enforce repo admission before governed sessions start

**Acceptance**
- gate order is canonical and recorded
- repo map stays within a bounded token budget
- invalid repo profile cannot enter execution

### Week 6
**Goal**
- establish decision logging and evidence writing

**Tasks**
- implement policy decision log
- implement evidence bundle writer
- capture rollback and replay references

**Acceptance**
- allow, block, and approve decisions are recorded structurally
- task evidence includes commands, decisions, and rollback refs
- evidence is queryable by task id

### Week 7
**Goal**
- make tool governance executable

**Tasks**
- implement governed tool request path
- enforce tool contract validation
- wire approval defaults into tool execution

**Acceptance**
- blocked tools fail closed
- approval-required tools pause before execution
- write-side tools declare rollback guidance

### Week 8
**Goal**
- establish approval semantics and interruptions

**Tasks**
- implement approval request state machine
- document or decide the medium-tier default
- connect approval results to task state changes

**Acceptance**
- approval supports create, approve, reject, revoke, and timeout
- medium-tier default is explicit
- approval results are auditable and deterministic

### Week 9
**Goal**
- start governed sessions in isolated workspaces

**Tasks**
- implement isolated workspace or worktree allocation
- assemble repo-aware context and budgets
- connect lifecycle, tool runner, and gates into a governed session shell

**Acceptance**
- one governed session can run a read-only task end-to-end
- context, budgets, and path policies are injected from the repo profile
- full gate escalation conditions are explicit

### Week 10
**Goal**
- establish assurance baseline

**Tasks**
- add minimum eval suites and golden tasks
- emit required trace fields
- add trace grading baseline

**Acceptance**
- smoke, regression, adversarial, and cost eval placeholders exist
- required trace fields are emitted
- trace grading can distinguish missing evidence from low-quality outcomes

### Week 11
**Goal**
- complete delivery and replay outputs

**Tasks**
- add delivery handoff bundle
- attach validation status and risk notes
- add replay-oriented references to failed tasks

**Acceptance**
- completed tasks always produce a handoff package
- partial validation is distinguishable from full validation
- replay references are present for failures

### Week 12
**Goal**
- prove reuse on a second target repository

**Tasks**
- register a second repo profile
- run compatibility validation
- run the minimum governed task loop on the second repo

**Acceptance**
- second repo uses the same kernel contracts
- only repo-profile values or stricter overrides differ
- no kernel fork is needed to support the second repo

### Week 13
**Goal**
- harden only what the kernel proof requires

**Tasks**
- add minimum review or approval console surface if still needed
- add control rollout and rollback notes
- add basic runbooks for waiver recovery and control rollback

**Acceptance**
- operator can inspect approvals and evidence without terminal for the key path
- rollout and rollback behavior for progressive controls is documented
- minimum runbooks cover failed rollout and expired waiver handling

## Suggested Initial Backlog

### First 8 tasks
1. Add example instances for hook, skill manifest, knowledge source, waiver, provenance, and repo-map contracts
2. Add sample repo profiles and sample control packs
3. Add compatibility validator and repo admission checks
4. Initialize implementation skeleton and shared tooling
5. Implement task store and control registry maturity model
6. Implement quick/full gate runner and repo map/context shaper
7. Implement policy decision log and evidence bundle writer
8. Implement governed tool runner and approval defaults

Seed backlog document:
- `docs/backlog/mvp-backlog-seeds.md`

## Phase Decision Matrix

| Phase | Strengthen | Keep minimal | Defer | Exit check |
|---|---|---|---|---|
| Phase 0 | kernel boundary, contract family completion, backlog alignment | architecture breadth | memory, multi-agent, marketplace | docs and backlog reflect kernel-first execution |
| Phase 1 | repo profiles, control packs, validators, bootstrap | UI work | federation, distribution | invalid repos fail admission; samples validate |
| Phase 2 | lifecycle, gates, evidence, tool governance, approval, governed session | advanced automation | broad product surfaces | one repo runs the governed loop end-to-end |
| Phase 3 | evals, trace grading, handoff, second-repo proof, minimal hardening | console polish | enterprise breadth | second repo runs without kernel semantic drift |

## Release Criteria
- kernel contracts, example instances, and sample control packs validate
- at least one repo can run a governed read-only task end-to-end
- high-risk writes require approval
- required trace fields and evidence bundle fields are emitted
- minimum eval and trace grading baseline can run
- a second repo compatibility pilot passes without a kernel fork
- rollback and waiver recovery notes exist for progressive controls

## Supporting Documents
- `docs/prd/governed-ai-coding-runtime-prd.md`
- `docs/architecture/governed-ai-coding-runtime-target-architecture.md`
- `docs/architecture/governance-boundary-matrix.md`
- `docs/architecture/minimum-viable-governance-loop.md`
- `docs/adrs/0001-control-plane-first.md`
- `docs/adrs/0002-no-multi-repo-distribution-in-mvp.md`
- `docs/adrs/0003-single-agent-baseline-first.md`
- `docs/adrs/0005-governance-kernel-and-control-packs-before-platform-breadth.md`
- `docs/specs/control-registry-spec.md`
- `docs/specs/repo-profile-spec.md`
- `docs/specs/tool-contract-spec.md`
- `docs/specs/risk-tier-and-approval-spec.md`
- `docs/specs/task-lifecycle-and-state-machine-spec.md`
- `docs/specs/evidence-bundle-spec.md`
- `docs/specs/verification-gates-spec.md`
- `docs/specs/eval-and-trace-grading-spec.md`
- `docs/backlog/mvp-backlog-seeds.md`

## References
- `docs/architecture/governed-ai-coding-runtime-target-architecture.md`
- `docs/research/benchmark-and-borrowing-notes.md`
- `scripts/github/create-roadmap-issues.ps1`
- `docs/FinalStateBestPractices.md`
