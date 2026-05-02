# Issue-Ready Backlog

## Parent Initiative
Governed AI Coding Runtime MVP

## Assumptions
- solo-developer or very small-team MVP
- control-plane-first remains the guiding decision
- single-agent baseline remains the first executable loop
- no multi-repo distribution in MVP
- reuse is proven through compatible repo profiles, not mirrored source trees

## Current Baseline
- PRD, architecture, ADRs, roadmap docs, schema drafts, and `scripts/github/create-roadmap-issues.ps1` already exist.
- The governance-kernel contract family is landed; the next backlog should complete executable reference assets, control packs, validators, and reuse proof before broad platform buildout.

## Seeds

### GAP-001 Governance Kernel Boundary And Doc Realignment
- Type: AFK
- Blocked by: None
- User stories: 1, 18, 31
- What to build:
  - capture the kernel-first boundary in ADRs and active planning docs
  - remove generic agent-platform implications from the immediate backlog
- Acceptance criteria:
  - [ ] an ADR captures the kernel-first decision
  - [ ] roadmap and backlog align with the ADR
  - [ ] the issue seeding script uses the same MVP boundary

### GAP-002 Governance Contract Family Completion
- Type: AFK
- Blocked by: GAP-001
- User stories: 1, 21, 24, 31, 32
- What to build:
  - add contract families for hooks, skill manifests, knowledge sources, waivers, provenance, and repo maps
- Acceptance criteria:
  - [ ] every missing contract family has a named spec and target schema path
  - [ ] contract minimums distinguish kernel-owned fields from repo-owned fields
  - [ ] contract docs are linked from the active planning baseline

### GAP-003 Control Registry Maturity And Waiver Model
- Type: AFK
- Blocked by: GAP-002
- User stories: 7, 25, 26, 29, 32
- What to build:
  - control maturity states
  - waiver references and expiry semantics
  - rollback metadata for progressive controls
- Acceptance criteria:
  - [ ] controls can express advisory, observe, and enforce modes
  - [ ] waiver records require owner, expiry, and recovery plan
  - [ ] progressive controls point to rollback references

### GAP-004 Sample Repo Profiles And Control Packs
- Type: AFK
- Blocked by: GAP-002
- User stories: 2, 18, 19, 37, 38
- What to build:
  - at least two sample repo profiles
  - at least one sample control pack
- Acceptance criteria:
  - [ ] sample profiles cover commands, tools, and path policies
  - [ ] sample control pack has version, owner, and scope metadata
  - [ ] samples illustrate inheritance vs stricter override

### GAP-005 Compatibility Validator And Repo Admission Checks
- Type: AFK
- Blocked by: GAP-002, GAP-004
- User stories: 2, 11, 12, 16, 36
- What to build:
  - validator for repo profiles and control packs
  - repo admission checks before governed execution
- Acceptance criteria:
  - [ ] invalid profiles fail closed
  - [ ] invalid control packs fail closed
  - [ ] repo admission output explains why a repo cannot enter execution

### GAP-006 Monorepo And Dev Bootstrap Around Governance Kernel
- Type: AFK
- Blocked by: GAP-003, GAP-005
- User stories: 1, 18, 38
- What to build:
  - create `apps/`, `packages/`, `infra/`, and `tests/`
  - add local and CI verification entrypoints around the kernel contracts
- Acceptance criteria:
  - [ ] implementation skeleton exists and is documented
  - [ ] local verification entrypoint is defined
  - [ ] CI can run schema, docs, and script integrity checks

### GAP-007 Quick And Full Verification Runner
- Type: AFK
- Blocked by: GAP-004, GAP-005, GAP-006
- User stories: 2, 11, 12, 16, 36
- What to build:
  - quick gate path
  - full gate path
  - escalation and artifact output
- Acceptance criteria:
  - [ ] canonical order is enforced
  - [ ] escalation conditions are explicit
  - [ ] verification output attaches to evidence

### GAP-008 Repo Map And Context Shaper
- Type: AFK
- Blocked by: GAP-004, GAP-005, GAP-006
- User stories: 4, 18, 37, 38
- What to build:
  - bounded repo map generation
  - context shaping rules from repo profiles
- Acceptance criteria:
  - [ ] repo map includes the highest-value symbols or files
  - [ ] token budget is bounded explicitly
  - [ ] repo-specific hints do not bypass kernel policy

### GAP-009 Task Store And Deterministic Lifecycle
- Type: AFK
- Blocked by: GAP-003, GAP-006
- User stories: 1, 5, 23, 24, 39
- What to build:
  - durable task object
  - deterministic lifecycle transitions
  - illegal transition rejection
- Acceptance criteria:
  - [ ] task lifecycle supports required states
  - [ ] illegal transitions fail
  - [ ] state changes emit evidence references

### GAP-010 Policy Decision Log And Evidence Bundle Writer
- Type: AFK
- Blocked by: GAP-003, GAP-007, GAP-009
- User stories: 10, 13, 14, 27, 39
- What to build:
  - policy decision log
  - evidence bundle writer
  - rollback and replay references
- Acceptance criteria:
  - [ ] allow, block, and approve decisions are logged structurally
  - [ ] task produces an evidence bundle
  - [ ] rollback and replay references are attached where applicable

### GAP-011 Governed Tool Runner And Contract Enforcement
- Type: AFK
- Blocked by: GAP-003, GAP-004, GAP-006, GAP-007
- User stories: 3, 8, 25, 26, 31, 37
- What to build:
  - tool contract validator
  - governed tool request path
  - allow, approve, and block decision flow
- Acceptance criteria:
  - [ ] tool requests validate against contract
  - [ ] blocked tools fail closed
  - [ ] approval-required tools pause before execution

### GAP-012 Medium-Tier Approval Default Decision
- Type: HITL
- Blocked by: GAP-003
- User stories: 20, 28, 40
- What to build:
  - explicit decision on whether medium-tier repo writes require approval in Phase 2
  - ADR or policy record capturing the choice
- Acceptance criteria:
  - [ ] decision documented
  - [ ] policy default updated consistently
  - [ ] downstream issues can implement against the chosen default

### GAP-013 Risk Tier And Approval Service
- Type: AFK
- Blocked by: GAP-011, GAP-009, GAP-012
- User stories: 7, 9, 20, 27, 28, 40
- What to build:
  - risk classifier
  - approval request object and state handling
  - approval interruption interface
- Acceptance criteria:
  - [ ] high-risk actions require explicit approval
  - [ ] approval status is persisted
  - [ ] audit trail includes approval decisions

### GAP-014 Single-Agent Session Bootstrap With Isolated Workspace
- Type: AFK
- Blocked by: GAP-007, GAP-008, GAP-009, GAP-011
- User stories: 4, 5, 6, 17, 18, 37, 39
- What to build:
  - governed session bootstrap
  - isolated worktree or workspace allocation
  - repo-aware context, budgets, and guardrails
- Acceptance criteria:
  - [ ] task can start in isolated workspace
  - [ ] agent receives repo-aware context and budgets
  - [ ] large changes can escalate to plan-first execution

### GAP-015 Eval And Trace Baseline With Golden Tasks
- Type: AFK
- Blocked by: GAP-010, GAP-014
- User stories: 15, 33
- What to build:
  - baseline eval recording
  - required trace field emission
  - minimum golden task set and trace grading
- Acceptance criteria:
  - [ ] required eval suites are recorded
  - [ ] required trace fields are emitted
  - [ ] trace grading can distinguish missing evidence from poor outcome quality

### GAP-016 Delivery Handoff Bundle And Replay References
- Type: AFK
- Blocked by: GAP-010, GAP-014, GAP-015
- User stories: 14, 35, 36
- What to build:
  - final summary bundle
  - changed files list
  - validation status, risk notes, and replay references
- Acceptance criteria:
  - [ ] handoff package is generated per completed task
  - [ ] package distinguishes fully validated vs partially validated
  - [ ] replay info is included for failed or interrupted paths

### GAP-017 Second-Repo Reuse Pilot
- Type: AFK
- Blocked by: GAP-004, GAP-005, GAP-014, GAP-015
- User stories: 2, 18, 37, 38
- What to build:
  - register a second target repository
  - validate compatibility and run the minimum governed loop
- Acceptance criteria:
  - [ ] second repo uses the same kernel semantics
  - [ ] only repo-profile values or stricter overrides differ
  - [ ] no kernel fork is required for the pilot

### GAP-018 Task Review And Approval Console
- Type: AFK
- Blocked by: GAP-013, GAP-016
- User stories: 27, 34, 40
- What to build:
  - minimal console for task list, approvals, evidence, and replay-oriented inspection
- Acceptance criteria:
  - [ ] user can approve or reject pending steps
  - [ ] user can inspect evidence by task
  - [ ] failed task path is reviewable from the console
