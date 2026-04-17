# Governed AI Coding Runtime 90-Day Plan

## Execution Inputs

This plan assumes the following documents are the active design inputs:
- PRD:
  - `docs/prd/governed-ai-coding-runtime-prd.md`
- Interaction model:
  - `docs/product/interaction-model.md`
- MVP loop:
  - `docs/architecture/minimum-viable-governance-loop.md`
- Boundary classification:
  - `docs/architecture/governance-boundary-matrix.md`
- ADRs:
  - `docs/adrs/0001-control-plane-first.md`
  - `docs/adrs/0002-no-multi-repo-distribution-in-mvp.md`
  - `docs/adrs/0003-single-agent-baseline-first.md`
  - `docs/adrs/0004-rename-project-to-governed-ai-coding-runtime.md`
  - `docs/adrs/0005-governance-kernel-and-control-packs-before-platform-breadth.md`
  - `docs/adrs/0006-final-state-best-practice-agent-compatibility.md`
- Specs:
  - `docs/specs/control-registry-spec.md`
  - `docs/specs/control-pack-spec.md`
  - `docs/specs/repo-profile-spec.md`
  - `docs/specs/tool-contract-spec.md`
  - `docs/specs/agent-adapter-contract-spec.md`
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
- Backlog seeds:
  - `docs/backlog/mvp-backlog-seeds.md`

## Current Baseline
- `docs/`, `schemas/`, and `scripts/github/create-roadmap-issues.ps1` already exist.
- Root `README.md` and project `AGENTS.md` already exist as repo entry contracts.
- The repository is still `docs-first / contracts-first`; `apps/`, `packages/`, `infra/`, and `tests/` have not been bootstrapped yet.
- The governance-kernel contract family, schema examples, sample control-pack metadata, and two sample repo profiles are landed.
- Executable sample control packs, compatibility validators, executable services, local verification entrypoints, and CI are not landed yet.

## Goal
- Deliver an MVP governance kernel for final-state-best-practice governed AI coding in 90 days.
- Put a first trialable governed loop in operator hands within 2-3 weeks.
- Keep the first executable loop auditable, replayable, approval-aware, and rollbackable.
- Make Codex CLI/App compatible operation the first adapter proof while keeping the kernel agent-agnostic.

## Trial-First Definition

### 2-3 week trial slice
A first trial is successful only if it can do all of the following:
- load one repo profile and minimum control inputs
- create a durable task with goal, scope, acceptance criteria, and budgets
- start a governed read-only session through a CLI or scripted entrypoint
- support a Codex CLI/App compatible operator path without taking ownership of upstream Codex authentication
- execute bounded read-only tools against one target repository
- emit evidence and decision logs for the session
- let the operator inspect what happened without reconstructing raw logs manually

### 90-day MVP
A 90-day MVP is successful only if it can do all of the following:
- preserve the trial slice above
- require approval before high-risk writes
- run quick and full verification in canonical order
- emit evidence, decision logs, rollback references, and required trace fields
- generate a delivery handoff bundle
- prove compatibility on a second target repository without forking kernel semantics
- prove that at least one additional agent product shape can be represented by the same adapter capability contract, even if it only runs in observe-only or manual-handoff mode

## Scope

### In Scope
- governance kernel contracts and schemas
- repo profiles and repo admission validation
- deterministic task lifecycle
- governed read-only and write-side tool execution
- approval interruption and rollback references
- evidence, trace, and replay-oriented output
- CLI or scripted operator flow for early trials
- second-repo reuse proof
- Codex CLI/App compatible first adapter path
- generic agent adapter capability contract

### Out of Scope
- multi-repo distribution hub behavior
- default multi-agent orchestration
- memory-first personalization platform
- skill marketplace or promotion workflow
- broad deployment automation as the platform identity
- org-scale enterprise tenancy and RBAC complexity
- replacing upstream agent UX or authentication
- deep integrations with every new AI coding product before a stable capability surface exists

## Roadmap Principles
- Ship the smallest runnable governed slice before adding platform width.
- Bias toward real trial feedback over plan completeness.
- Keep `task / approval / gate / evidence / trace / rollback` deterministic.
- Treat repo reuse as `same kernel, different profiles`, not as source mirroring.
- Only allow repo overrides that tighten or extend governance.
- Add UI only when it removes operator pain from approval, evidence, or replay.
- Treat final-state best practice as the north star, not as permission to front-load all target-state infrastructure.
- Treat new agent products as adapters; do not let the first adapter redefine kernel semantics.
- Keep governance friction proportional to risk.

## What To Add / What To Weaken / What To Defer

### Add now
- implementation skeleton and local verification entrypoints
- runtime-consumable sample control pack and repo admission baseline
- durable task intake and repo profile resolution
- read-only governed session shell and evidence timeline
- CLI or scripted operator entrypoint for the first trial
- Codex CLI/App compatible first operator path
- draft agent adapter capability contract

### Weaken intentionally
- contract-family expansion work that is already completed
- console breadth before the first runnable slice exists
- A2A or federation positioning in MVP materials
- deployment automation as a default path
- strict enforcement for low-risk exploratory work

### Defer explicitly
- memory-first architecture
- multi-agent orchestration by default
- skill marketplace and promotion lifecycle
- multi-repo distribution and backflow sync
- enterprise-grade organization model
- deep IDE replacement UX
- broad product-specific adapter catalog

## Phases

### Phase 0: Runnable Baseline (Week 1)
- bootstrap `apps/`, `packages/`, `infra/`, and `tests/`
- define local verification entrypoints and CI minimums
- promote the sample control-pack metadata into a runtime-consumable sample control pack plus repo admission minimums
- define the initial agent adapter capability contract and Codex CLI/App compatibility assumptions
- keep roadmap, backlog, issue seeds, and seeding script aligned with the trial-first plan

**Expected benefit**
- removes the gap between a docs-only repo and a repo that can start a real operator trial

**Primary risk**
- spending another cycle refining planning assets without creating a runnable entrypoint

### Phase 1: First Trial Slice (Week 2-3)
- implement deterministic task intake and repo profile resolution
- implement a governed read-only tool path
- implement evidence timeline and task result output
- add a CLI or scripted entrypoint for one Codex-compatible operator-driven trial path

**Expected benefit**
- validates the product thesis with a real governed session before write-side complexity arrives

**Primary risk**
- proving only backend internals without giving an operator a usable way to run the slice

### Phase 2: Controlled Write Slice (Week 4-6)
- implement isolated workspace or worktree allocation
- make medium/high-risk write policy explicit
- implement approval interruption and write-side rollback references
- route write-side tool requests through governed policy checks
- add quick verification gate execution

**Expected benefit**
- turns the read-only trial into a real controlled coding workflow

**Primary risk**
- adding write capability without a clear approval default or rollback reference model

### Phase 3: Delivery Assurance Slice (Week 7-9)
- add full verification and escalation rules
- add delivery handoff bundle and replay references
- add required trace fields and minimum eval baseline
- make evidence queryable enough for repeated trial review

**Expected benefit**
- lets reviewers judge trial output as delivery, not just as raw execution

**Primary risk**
- confusing “task finished” with “validated delivery”

### Phase 4: Reuse And Operator Hardening (Week 10-13)
- prove the same kernel on a second target repository
- add minimum approval/evidence console surfaces only where needed
- add waiver recovery, control rollback, and operator runbooks

**Expected benefit**
- proves the kernel is reusable and operable, not only runnable in one curated repo

**Primary risk**
- pulling in too much admin UI or enterprise breadth before the reuse proof is complete

## Weekly Plan

### Week 1
**Goal**
- create the minimum runnable repository baseline for trials

**Tasks**
- create `apps/`, `packages/`, `infra/`, and `tests/`
- add a local verification entrypoint for schema, docs, and script integrity
- add CI for schema checks, doc integrity, and script parsing
- promote at least one sample control-pack metadata record into a runtime-consumable pack and document repo admission minimums
- document the first agent adapter contract and Codex CLI/App compatibility posture

**Acceptance**
- implementation skeleton exists
- local verification entrypoint is documented
- CI can run the minimum repository checks
- repo admission minimums are explicit
- Codex-compatible operation is described as an adapter, not as kernel behavior

### Week 2
**Goal**
- make trial intake and repo resolution executable

**Tasks**
- implement task store skeleton
- implement deterministic lifecycle validation for intake and startup states
- implement repo profile resolution and admission checks
- define the first operator-facing CLI or scripted entrypoint contract
- define observe-only/advisory/enforced/strict friction modes for trial use

**Acceptance**
- a task can be created with required fields
- illegal intake transitions fail closed
- invalid repo profile cannot enter startup
- operator entrypoint contract is explicit
- low-risk trial paths are not forced through high-friction approval behavior

### Week 3
**Goal**
- complete the first read-only governed trial slice

**Tasks**
- implement governed read-only tool request path
- implement evidence timeline and task result output
- run one repo through a read-only governed session end-to-end
- capture operator feedback from the first trial
- capture which adapter capabilities were available from the selected agent frontend

**Acceptance**
- one governed session can run a read-only task end-to-end
- evidence captures task, decisions, commands, and outputs
- operator can inspect trial output without digging through raw logs
- first-trial feedback is recorded for backlog reprioritization
- adapter gaps are recorded as compatibility work, not kernel drift

### Week 4
**Goal**
- establish write-side execution boundaries

**Tasks**
- implement isolated workspace or worktree allocation
- define medium-tier and high-tier write policy defaults
- require rollback references for write-side tools

**Acceptance**
- write-side execution does not target arbitrary live directories
- write policy defaults are explicit
- write-side tools declare rollback guidance

### Week 5
**Goal**
- make approval interruption executable

**Tasks**
- implement approval request object and state machine
- connect approval results to task state changes
- ensure blocked and approval-required actions fail closed

**Acceptance**
- approval supports create, approve, reject, revoke, and timeout
- approval results are auditable and deterministic
- high-risk writes cannot execute without an explicit path

### Week 6
**Goal**
- add quick verification to the write slice

**Tasks**
- implement quick gate runner
- connect quick-gate output to evidence
- require quick verification before write-side delivery claims

**Acceptance**
- canonical quick-gate order is enforced
- verification output is attached to evidence
- write-side tasks cannot claim delivery without quick-gate state

### Week 7
**Goal**
- add full verification and escalation rules

**Tasks**
- implement full gate runner
- define escalation from quick to full verification
- persist full-gate artifacts into evidence

**Acceptance**
- full-gate order is explicit and recorded
- escalation conditions are explicit
- verification state distinguishes quick vs full completion

### Week 8
**Goal**
- complete delivery handoff and replay references

**Tasks**
- add delivery handoff bundle
- attach changed files, validation state, risk notes, and replay refs
- ensure failed tasks retain enough evidence for replay-oriented debugging

**Acceptance**
- completed tasks always produce a handoff bundle
- partial validation is distinguishable from full validation
- failed tasks include replay-oriented references

### Week 9
**Goal**
- establish assurance baseline around trials

**Tasks**
- add minimum eval suites and golden tasks
- emit required trace fields
- add trace grading baseline for trial runs

**Acceptance**
- smoke, regression, adversarial, and cost eval placeholders exist
- required trace fields are emitted
- trace grading can distinguish missing evidence from weak outcomes

### Week 10
**Goal**
- start second-repo compatibility proof

**Tasks**
- register a second repo profile
- run compatibility validation on the second repo
- compare reuse gaps against the first trial repo

**Acceptance**
- second repo passes admission and compatibility validation
- reuse gaps are captured as profile or adapter work, not kernel drift

### Week 11
**Goal**
- run the minimum governed loop on a second repo

**Tasks**
- run the read-only trial slice on the second repo
- run the write-side governed path where safe
- confirm that only profile values or stricter overrides differ

**Acceptance**
- second repo uses the same kernel semantics
- no kernel fork is required
- differences are explained through repo profile or adapter inputs

### Week 12
**Goal**
- add only the operator surfaces needed by trial feedback

**Tasks**
- add minimum review or approval console surface if still needed
- surface task list, approvals, evidence, and replay-oriented inspection
- validate that console scope stays control-plane focused

**Acceptance**
- operator can approve or inspect evidence without raw terminal access for the key path
- console scope does not drift into a full IDE shell
- approval and evidence surfaces cover the main trial pain points

### Week 13
**Goal**
- harden the trial-first MVP for repeated use

**Tasks**
- add rollout, waiver recovery, and control rollback notes
- add basic runbooks for failed rollout and expired waiver handling
- review the first 90-day loop against actual trial feedback

**Acceptance**
- minimum runbooks exist for failed rollout and expired waiver handling
- control rollback behavior is documented
- next-phase priorities are based on observed trial friction, not only planned breadth

## Suggested Initial Backlog

### First 8 tasks
1. Initialize implementation skeleton and local verification entrypoints
2. Promote sample control-pack metadata into a runtime-consumable pack and repo admission minimums
3. Implement task intake and repo profile resolution
4. Implement read-only governed tool runner
5. Implement evidence timeline and first trial output
6. Add CLI or scripted trial entrypoint
7. Implement isolated workspace and write-side policy defaults
8. Implement approval interruption plus quick verification

Seed backlog document:
- `docs/backlog/mvp-backlog-seeds.md`

## Phase Decision Matrix

| Phase | Strengthen | Keep minimal | Defer | Exit check |
|---|---|---|---|---|
| Phase 0 | bootstrap, verification entrypoints, admission minimums | architecture breadth | memory, multi-agent, marketplace | repo can support the first trial slice |
| Phase 1 | task intake, repo resolution, read-only governed loop, evidence | console work | federation, distribution | one repo runs a read-only governed trial end-to-end |
| Phase 2 | workspace isolation, write policy, approval, quick gates | advanced automation | broad product surfaces | high-risk writes are gated and rollback-aware |
| Phase 3 | full gates, handoff, replay, eval, trace | console polish | enterprise breadth | validated delivery is distinct from raw execution |
| Phase 4 | second-repo proof, minimal operator UI, runbooks | admin breadth | org-scale platform concerns | second repo runs without kernel semantic drift |

## Release Criteria
- one repo can run a governed read-only trial end-to-end within the first 2-3 weeks
- high-risk writes require approval and carry rollback references
- quick and full verification states are emitted in canonical order
- evidence bundle and required trace fields are present
- completed tasks produce a delivery handoff bundle
- a second repo compatibility pilot passes without a kernel fork
- waiver recovery and control rollback notes exist for repeated operation

## Supporting Documents
- `docs/prd/governed-ai-coding-runtime-prd.md`
- `docs/product/interaction-model.md`
- `docs/architecture/governed-ai-coding-runtime-target-architecture.md`
- `docs/architecture/governance-boundary-matrix.md`
- `docs/architecture/minimum-viable-governance-loop.md`
- `docs/adrs/0001-control-plane-first.md`
- `docs/adrs/0002-no-multi-repo-distribution-in-mvp.md`
- `docs/adrs/0003-single-agent-baseline-first.md`
- `docs/adrs/0004-rename-project-to-governed-ai-coding-runtime.md`
- `docs/adrs/0005-governance-kernel-and-control-packs-before-platform-breadth.md`
- `docs/adrs/0006-final-state-best-practice-agent-compatibility.md`
- `docs/specs/control-registry-spec.md`
- `docs/specs/control-pack-spec.md`
- `docs/specs/repo-profile-spec.md`
- `docs/specs/tool-contract-spec.md`
- `docs/specs/agent-adapter-contract-spec.md`
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
- `docs/backlog/mvp-backlog-seeds.md`

## References
- `docs/architecture/governed-ai-coding-runtime-target-architecture.md`
- `docs/research/benchmark-and-borrowing-notes.md`
- `scripts/github/create-roadmap-issues.ps1`
- `docs/FinalStateBestPractices.md`
