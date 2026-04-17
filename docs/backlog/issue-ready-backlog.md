# Issue-Ready Backlog

## Parent Initiative
Governed AI Coding Runtime MVP

## Assumptions
- solo-developer or very small-team MVP
- control-plane-first remains the guiding decision
- single-agent baseline remains the first executable loop
- no multi-repo distribution in MVP
- reuse is proven through compatible repo profiles, not mirrored source trees
- the first 2-3 weeks should produce a runnable governed trial slice
- final-state best practice is the north star, while the MVP remains a narrow tracer bullet
- Codex CLI/App compatibility is the first adapter priority, but kernel semantics remain agent-agnostic

## Current Baseline
- PRD, architecture, ADRs, roadmap docs, schema drafts, and `scripts/github/create-roadmap-issues.ps1` already exist.
- The governance-kernel contract family, schema examples, sample control-pack metadata, runtime-consumable control-pack asset, sample repo profiles, local verifier, CI wiring, and runtime contract layer are landed.
- Current backlog execution has reached the `GAP-017` endpoint; the next step is closeout review or a new post-MVP backlog.

## Seeds

### GAP-001 Final-State And Trial-First Planning Alignment
- Type: AFK
- Blocked by: None
- User stories: 1, 18, 31
- What to build:
  - align PRD, ADRs, architecture, roadmap, backlog, issue seeds, and seeding script around final-state best practice as the north star
  - align roadmap, backlog, issue seeds, and seeding script around a 2-3 week first trial slice
  - keep planning assets tied to the existing PRD and ADR boundary
- Acceptance criteria:
  - [x] final-state best practice is positioned as a long-term quality target, not as first-slice infrastructure scope
  - [x] roadmap, backlog, issue seeds, and seeding script describe the same trial-first order
  - [x] first runnable slice is explicit
  - [x] 90-day MVP criteria still preserve approval, evidence, verification, and reuse goals
  - [x] Codex-first compatibility and generic agent adapter contracts are represented consistently

### GAP-002 Runnable Skeleton And Verification Bootstrap
- Type: AFK
- Blocked by: GAP-001
- User stories: 1, 18, 38
- What to build:
  - create `apps/`, `packages/`, `infra/`, and `tests/`
  - add local and CI verification entrypoints around schemas, docs, and scripts
- Acceptance criteria:
  - [x] implementation skeleton exists and is documented
  - [x] local verification entrypoint is defined
  - [x] CI can run schema, docs, and script integrity checks

### GAP-003 Sample Control Pack And Repo Admission Minimums
- Type: AFK
- Blocked by: GAP-001
- User stories: 2, 18, 19, 38
- What to build:
  - a runtime-consumable sample control pack derived from the control-pack metadata contract
  - minimum repo admission checks for the first runnable slice
- Acceptance criteria:
  - [x] control pack metadata validates against `schemas/jsonschema/control-pack.schema.json`
  - [x] sample control pack has version, owner, and scope metadata
  - [x] runtime-consumable pack references controls/hooks/gates without weakening kernel semantics
  - [x] admission minimums cover commands, tools, and path policy
  - [x] invalid repos fail before session startup

### GAP-004 Deterministic Task Intake And Repo Resolution
- Type: AFK
- Blocked by: GAP-002, GAP-003
- User stories: 1, 2, 23, 24, 39
- What to build:
  - durable task intake object
  - deterministic startup-state validation
  - repo profile resolution
- Acceptance criteria:
  - [x] task intake requires goal, scope, acceptance, repo, and budgets
  - [x] illegal startup transitions fail closed
  - [x] repo resolution attaches the correct profile inputs

### GAP-005 Read-Only Governed Tool Runner
- Type: AFK
- Blocked by: GAP-004
- User stories: 3, 8, 18, 25, 31
- What to build:
  - read-only governed tool request path
  - tool contract validation for the first trial slice
- Acceptance criteria:
  - [x] read-only tools validate against contract
  - [x] blocked tools fail closed
  - [x] one repo can execute a bounded read-only session

### GAP-006 Evidence Timeline And Task Output
- Type: AFK
- Blocked by: GAP-004, GAP-005
- User stories: 13, 14, 27, 39
- What to build:
  - evidence timeline for task creation, decisions, commands, and outputs
  - task result output for operator review
- Acceptance criteria:
  - [x] evidence captures task, decisions, commands, and outputs structurally
  - [x] task output is reviewable without reconstructing raw logs
  - [x] evidence is queryable by task id

### GAP-007 Codex-Compatible CLI Or Scripted Trial Entrypoint
- Type: AFK
- Blocked by: GAP-004, GAP-005, GAP-006
- User stories: 1, 5, 18, 37, 39
- What to build:
  - a Codex CLI/App compatible CLI or scripted entrypoint for the first trial slice
  - an agent adapter capability declaration for invocation mode, auth ownership, workspace control, event visibility, mutation model, continuation model, and evidence model
  - first-run operator flow documentation
- Acceptance criteria:
  - [x] an operator can start the first trial through one documented entrypoint
  - [x] entrypoint attaches repo profile and budgets
  - [x] Codex authentication remains owned by the upstream Codex CLI/App workflow
  - [x] one read-only governed task runs end-to-end
  - [x] unsupported agent capabilities degrade to observe-only, advisory, or manual-handoff mode

### GAP-008 Isolated Workspace Allocation
- Type: AFK
- Blocked by: GAP-007
- User stories: 17, 18, 37, 39
- What to build:
  - isolated workspace or worktree allocation
  - path-scope enforcement for write-side preparation
- Acceptance criteria:
  - [x] write-side work does not target arbitrary live directories
  - [x] workspace allocation is tied to task lifecycle
  - [x] path policy is injected from the repo profile

### GAP-009 Write Policy Defaults And Approval Decision
- Type: HITL
- Blocked by: GAP-003, GAP-008
- User stories: 20, 28, 40
- What to build:
  - explicit decision on medium-tier and high-tier write defaults
  - policy record for downstream implementation
- Acceptance criteria:
  - [x] medium-tier behavior is documented
  - [x] high-tier behavior remains explicit approval
  - [x] downstream issues can implement against the chosen default

### GAP-010 Approval Service And Interruption Flow
- Type: AFK
- Blocked by: GAP-008, GAP-009
- User stories: 7, 9, 20, 27, 28, 40
- What to build:
  - approval request object and state handling
  - approval interruption interface wired into task state
- Acceptance criteria:
  - [x] approval supports create, approve, reject, revoke, and timeout
  - [x] approval results are persisted
  - [x] audit trail includes approval decisions

### GAP-011 Write-Side Tool Governance And Rollback References
- Type: AFK
- Blocked by: GAP-008, GAP-009, GAP-010
- User stories: 8, 9, 10, 25, 26, 31
- What to build:
  - write-side governed tool path
  - rollback references for risky writes
- Acceptance criteria:
  - [x] approval-required writes pause before execution
  - [x] blocked writes fail closed
  - [x] risky writes carry rollback references

### GAP-012 Quick And Full Verification Runner
- Type: AFK
- Blocked by: GAP-011
- User stories: 2, 11, 12, 16, 36
- What to build:
  - quick gate path
  - full gate path
  - escalation rules and artifact output
- Acceptance criteria:
  - [x] canonical order is enforced
  - [x] escalation conditions are explicit
  - [x] verification output attaches to evidence

### GAP-013 Delivery Handoff And Replay References
- Type: AFK
- Blocked by: GAP-006, GAP-011, GAP-012
- User stories: 14, 35, 36
- What to build:
  - final summary bundle
  - changed files list
  - validation status, risk notes, and replay references
- Acceptance criteria:
  - [x] handoff package is generated per completed task
  - [x] package distinguishes fully validated vs partially validated
  - [x] replay info is included for failed or interrupted paths

### GAP-014 Eval And Trace Baseline
- Type: AFK
- Blocked by: GAP-006, GAP-012, GAP-013
- User stories: 15, 33
- What to build:
  - baseline eval recording
  - required trace field emission
  - minimum golden task set and trace grading
- Acceptance criteria:
  - [x] required eval suites are recorded
  - [x] required trace fields are emitted
  - [x] trace grading distinguishes missing evidence from poor outcome quality

### GAP-015 Second-Repo Reuse Pilot
- Type: AFK
- Blocked by: GAP-003, GAP-007, GAP-012, GAP-014
- User stories: 2, 18, 37, 38
- What to build:
  - register a second target repository
  - validate compatibility and run the minimum governed loop
  - represent at least one additional agent product shape through the same adapter capability contract
- Acceptance criteria:
  - [x] second repo uses the same kernel semantics
  - [x] only repo-profile values or stricter overrides differ
  - [x] no kernel fork is required for the pilot
  - [x] future agent compatibility gaps are tracked as adapter work, not governance-kernel rewrites

### GAP-016 Minimal Approval And Evidence Console
- Type: AFK
- Blocked by: GAP-010, GAP-013
- User stories: 27, 34, 40
- What to build:
  - minimal console for task list, approvals, evidence, and replay-oriented inspection
- Acceptance criteria:
  - [x] user can approve or reject pending steps
  - [x] user can inspect evidence by task
  - [x] console scope stays control-plane focused

### GAP-017 Waiver Recovery And Control Rollback Runbooks
- Type: AFK
- Blocked by: GAP-014, GAP-015, GAP-016
- User stories: 27, 29, 40
- What to build:
  - runbooks for failed rollout, expired waiver handling, and control rollback
- Acceptance criteria:
  - [x] minimum operator runbooks exist
  - [x] progressive controls point to rollback behavior
  - [x] repeated trial operation has documented recovery paths
