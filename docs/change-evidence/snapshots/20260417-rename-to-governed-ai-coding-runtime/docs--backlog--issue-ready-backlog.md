# Issue-Ready Backlog

## Parent Initiative
Governed Agent Platform MVP

## Assumptions
- Solo-developer MVP
- Single-agent baseline first
- No multi-repo distribution in MVP
- Control-plane-first remains the guiding decision

## Current Baseline
- PRD, architecture, ADRs, roadmap, backlog docs, schema drafts, and `scripts/github/create-roadmap-issues.ps1` already exist.
- `GAP-001` should bootstrap the missing implementation skeleton and repo entry contracts around those assets, not recreate the documentation baseline.

## Seeds

### GAP-001 Monorepo And Dev Bootstrap
- Type: AFK
- Blocked by: None
- User stories: 1, 18, 38
- What to build:
  - create `apps/`, `packages/`, `infra/`, and `tests/` while preserving the existing docs/spec/schema baseline
  - keep root `README.md` and project `AGENTS.md` synchronized as the repo entry contract
  - standardize local bootstrap and verification commands
- Acceptance criteria:
  - [ ] implementation skeleton exists and is documented
  - [ ] root `README.md` points to the active docs index
  - [ ] project `AGENTS.md` still maps current repo gates and evidence paths
  - [ ] local bootstrap or verification command is defined

### GAP-002 Contracts Package And Schema Baseline
- Type: AFK
- Blocked by: GAP-001
- User stories: 1, 21, 24, 31, 32
- What to build:
  - turn existing task, repo profile, tool contract, risk, evidence, and gates definitions into a contracts package
  - wire JSON schemas into validation workflow
- Acceptance criteria:
  - [ ] contract package exists
  - [ ] schema validation can run locally
  - [ ] core contract docs point to machine-readable schemas

### GAP-003 Repository Profile Registry And Loader
- Type: AFK
- Blocked by: GAP-002
- User stories: 2, 18, 19, 37, 38
- What to build:
  - repo profile registry
  - loader and validator
  - one sample repo profile
- Acceptance criteria:
  - [ ] platform can load a repo profile by repo id
  - [ ] invalid profile fails closed
  - [ ] sample repo profile covers commands, tools, and path policies

### GAP-004 Control Registry And Policy Resolution
- Type: AFK
- Blocked by: GAP-002
- User stories: 7, 25, 26, 29, 32
- What to build:
  - control registry model
  - policy resolution layer
  - runtime lookup for active controls
- Acceptance criteria:
  - [ ] control registry parses and validates
  - [ ] controls are queryable by plane
  - [ ] progressive controls carry observe-to-enforce metadata

### GAP-005 Task Store And Deterministic Lifecycle
- Type: AFK
- Blocked by: GAP-002
- User stories: 1, 5, 23, 24, 39
- What to build:
  - durable task object
  - deterministic lifecycle transitions
  - illegal transition rejection
- Acceptance criteria:
  - [ ] task lifecycle supports required states
  - [ ] illegal transitions fail
  - [ ] state changes emit evidence refs

### GAP-006 Medium-Tier Approval Default Decision
- Type: HITL
- Blocked by: GAP-002
- User stories: 20, 28, 40
- What to build:
  - explicit decision on whether medium-tier repo writes require approval in Phase 1
  - ADR or policy record capturing the choice
- Acceptance criteria:
  - [ ] decision documented
  - [ ] policy default updated consistently
  - [ ] downstream issues can implement against the chosen default

### GAP-007 Risk Tier And Approval Service
- Type: AFK
- Blocked by: GAP-004, GAP-005, GAP-006
- User stories: 7, 9, 20, 27, 28, 40
- What to build:
  - risk classifier
  - approval request object and status handling
  - approval interruption interface
- Acceptance criteria:
  - [ ] high-risk actions require explicit approval
  - [ ] approval status is persisted
  - [ ] audit trail includes approval decisions

### GAP-008 Governed Tool Runner And Contract Enforcement
- Type: AFK
- Blocked by: GAP-003, GAP-004, GAP-007
- User stories: 3, 8, 25, 26, 31, 37
- What to build:
  - tool contract validator
  - governed tool request path
  - allow / approve / block decision flow
- Acceptance criteria:
  - [ ] tool requests validate against contract
  - [ ] blocked tools fail closed
  - [ ] approval-required tools pause before execution

### GAP-009 Evidence Bundle And Audit Event Store
- Type: AFK
- Blocked by: GAP-005, GAP-007, GAP-008
- User stories: 10, 13, 14, 27, 39
- What to build:
  - evidence bundle writer
  - append-oriented audit events
  - rollback reference capture
- Acceptance criteria:
  - [ ] task produces evidence bundle
  - [ ] high-risk actions include approval and rollback refs
  - [ ] audit events are queryable by task id

### GAP-010 Quick And Full Verification Runner
- Type: AFK
- Blocked by: GAP-003, GAP-004, GAP-008
- User stories: 2, 11, 12, 16, 36
- What to build:
  - quick gate path
  - full gate path
  - escalation logic
- Acceptance criteria:
  - [ ] canonical order is enforced
  - [ ] escalation conditions are explicit
  - [ ] verification output attaches to evidence

### GAP-011 Single-Agent Session Bootstrap With Isolated Workspace
- Type: AFK
- Blocked by: GAP-003, GAP-005, GAP-008, GAP-010
- User stories: 4, 5, 6, 17, 18, 37, 39
- What to build:
  - governed session bootstrap
  - isolated worktree or workspace allocation
  - plan-before-large-change flow
- Acceptance criteria:
  - [ ] task can start in isolated workspace
  - [ ] agent receives repo-aware context and budgets
  - [ ] large change flow can request plan first

### GAP-012 Delivery Handoff Bundle
- Type: AFK
- Blocked by: GAP-009, GAP-010, GAP-011
- User stories: 14, 35, 36
- What to build:
  - final summary bundle
  - changed files list
  - validation status and risk notes
- Acceptance criteria:
  - [ ] handoff package is generated per completed task
  - [ ] package distinguishes fully validated vs partially validated
  - [ ] rollback info is included when applicable

### GAP-013 Task Review And Approval Console
- Type: AFK
- Blocked by: GAP-007, GAP-009, GAP-011, GAP-012
- User stories: 27, 34, 40
- What to build:
  - minimal console for task list, approvals, evidence, replay-oriented inspection
- Acceptance criteria:
  - [ ] user can approve or reject pending steps
  - [ ] user can inspect evidence by task
  - [ ] failed task path is reviewable from the console

### GAP-014 Eval And Trace Emission Baseline
- Type: AFK
- Blocked by: GAP-009, GAP-010, GAP-011
- User stories: 15, 33
- What to build:
  - baseline eval recording
  - required trace field emission
  - trace grading placeholders
- Acceptance criteria:
  - [ ] required eval suites are recorded
  - [ ] required trace fields are emitted
  - [ ] platform can distinguish emit-only vs graded phases
