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

## Current Baseline
- PRD, architecture, ADRs, roadmap docs, schema drafts, and `scripts/github/create-roadmap-issues.ps1` already exist.
- The governance-kernel contract family, schema examples, and sample repo profiles are landed.
- The next backlog should bootstrap a runnable trial loop before broad platform buildout.

## Seeds

### GAP-001 Trial-First Planning Alignment
- Type: AFK
- Blocked by: None
- User stories: 1, 18, 31
- What to build:
  - align roadmap, backlog, issue seeds, and seeding script around a 2-3 week first trial slice
  - keep planning assets tied to the existing PRD and ADR boundary
- Acceptance criteria:
  - [ ] roadmap, backlog, issue seeds, and seeding script describe the same trial-first order
  - [ ] first runnable slice is explicit
  - [ ] 90-day MVP criteria still preserve approval, evidence, verification, and reuse goals

### GAP-002 Runnable Skeleton And Verification Bootstrap
- Type: AFK
- Blocked by: GAP-001
- User stories: 1, 18, 38
- What to build:
  - create `apps/`, `packages/`, `infra/`, and `tests/`
  - add local and CI verification entrypoints around schemas, docs, and scripts
- Acceptance criteria:
  - [ ] implementation skeleton exists and is documented
  - [ ] local verification entrypoint is defined
  - [ ] CI can run schema, docs, and script integrity checks

### GAP-003 Sample Control Pack And Repo Admission Minimums
- Type: AFK
- Blocked by: GAP-001
- User stories: 2, 18, 19, 38
- What to build:
  - at least one sample control pack
  - minimum repo admission checks for the first runnable slice
- Acceptance criteria:
  - [ ] sample control pack has version, owner, and scope metadata
  - [ ] admission minimums cover commands, tools, and path policy
  - [ ] invalid repos fail before session startup

### GAP-004 Deterministic Task Intake And Repo Resolution
- Type: AFK
- Blocked by: GAP-002, GAP-003
- User stories: 1, 2, 23, 24, 39
- What to build:
  - durable task intake object
  - deterministic startup-state validation
  - repo profile resolution
- Acceptance criteria:
  - [ ] task intake requires goal, scope, acceptance, repo, and budgets
  - [ ] illegal startup transitions fail closed
  - [ ] repo resolution attaches the correct profile inputs

### GAP-005 Read-Only Governed Tool Runner
- Type: AFK
- Blocked by: GAP-004
- User stories: 3, 8, 18, 25, 31
- What to build:
  - read-only governed tool request path
  - tool contract validation for the first trial slice
- Acceptance criteria:
  - [ ] read-only tools validate against contract
  - [ ] blocked tools fail closed
  - [ ] one repo can execute a bounded read-only session

### GAP-006 Evidence Timeline And Task Output
- Type: AFK
- Blocked by: GAP-004, GAP-005
- User stories: 13, 14, 27, 39
- What to build:
  - evidence timeline for task creation, decisions, commands, and outputs
  - task result output for operator review
- Acceptance criteria:
  - [ ] evidence captures task, decisions, commands, and outputs structurally
  - [ ] task output is reviewable without reconstructing raw logs
  - [ ] evidence is queryable by task id

### GAP-007 CLI Or Scripted Trial Entrypoint
- Type: AFK
- Blocked by: GAP-004, GAP-005, GAP-006
- User stories: 1, 5, 18, 37, 39
- What to build:
  - a CLI or scripted entrypoint for the first trial slice
  - first-run operator flow documentation
- Acceptance criteria:
  - [ ] an operator can start the first trial through one documented entrypoint
  - [ ] entrypoint attaches repo profile and budgets
  - [ ] one read-only governed task runs end-to-end

### GAP-008 Isolated Workspace Allocation
- Type: AFK
- Blocked by: GAP-007
- User stories: 17, 18, 37, 39
- What to build:
  - isolated workspace or worktree allocation
  - path-scope enforcement for write-side preparation
- Acceptance criteria:
  - [ ] write-side work does not target arbitrary live directories
  - [ ] workspace allocation is tied to task lifecycle
  - [ ] path policy is injected from the repo profile

### GAP-009 Write Policy Defaults And Approval Decision
- Type: HITL
- Blocked by: GAP-003, GAP-008
- User stories: 20, 28, 40
- What to build:
  - explicit decision on medium-tier and high-tier write defaults
  - policy record for downstream implementation
- Acceptance criteria:
  - [ ] medium-tier behavior is documented
  - [ ] high-tier behavior remains explicit approval
  - [ ] downstream issues can implement against the chosen default

### GAP-010 Approval Service And Interruption Flow
- Type: AFK
- Blocked by: GAP-008, GAP-009
- User stories: 7, 9, 20, 27, 28, 40
- What to build:
  - approval request object and state handling
  - approval interruption interface wired into task state
- Acceptance criteria:
  - [ ] approval supports create, approve, reject, revoke, and timeout
  - [ ] approval results are persisted
  - [ ] audit trail includes approval decisions

### GAP-011 Write-Side Tool Governance And Rollback References
- Type: AFK
- Blocked by: GAP-008, GAP-009, GAP-010
- User stories: 8, 9, 10, 25, 26, 31
- What to build:
  - write-side governed tool path
  - rollback references for risky writes
- Acceptance criteria:
  - [ ] approval-required writes pause before execution
  - [ ] blocked writes fail closed
  - [ ] risky writes carry rollback references

### GAP-012 Quick And Full Verification Runner
- Type: AFK
- Blocked by: GAP-011
- User stories: 2, 11, 12, 16, 36
- What to build:
  - quick gate path
  - full gate path
  - escalation rules and artifact output
- Acceptance criteria:
  - [ ] canonical order is enforced
  - [ ] escalation conditions are explicit
  - [ ] verification output attaches to evidence

### GAP-013 Delivery Handoff And Replay References
- Type: AFK
- Blocked by: GAP-006, GAP-011, GAP-012
- User stories: 14, 35, 36
- What to build:
  - final summary bundle
  - changed files list
  - validation status, risk notes, and replay references
- Acceptance criteria:
  - [ ] handoff package is generated per completed task
  - [ ] package distinguishes fully validated vs partially validated
  - [ ] replay info is included for failed or interrupted paths

### GAP-014 Eval And Trace Baseline
- Type: AFK
- Blocked by: GAP-006, GAP-012, GAP-013
- User stories: 15, 33
- What to build:
  - baseline eval recording
  - required trace field emission
  - minimum golden task set and trace grading
- Acceptance criteria:
  - [ ] required eval suites are recorded
  - [ ] required trace fields are emitted
  - [ ] trace grading distinguishes missing evidence from poor outcome quality

### GAP-015 Second-Repo Reuse Pilot
- Type: AFK
- Blocked by: GAP-003, GAP-007, GAP-012, GAP-014
- User stories: 2, 18, 37, 38
- What to build:
  - register a second target repository
  - validate compatibility and run the minimum governed loop
- Acceptance criteria:
  - [ ] second repo uses the same kernel semantics
  - [ ] only repo-profile values or stricter overrides differ
  - [ ] no kernel fork is required for the pilot

### GAP-016 Minimal Approval And Evidence Console
- Type: AFK
- Blocked by: GAP-010, GAP-013
- User stories: 27, 34, 40
- What to build:
  - minimal console for task list, approvals, evidence, and replay-oriented inspection
- Acceptance criteria:
  - [ ] user can approve or reject pending steps
  - [ ] user can inspect evidence by task
  - [ ] console scope stays control-plane focused

### GAP-017 Waiver Recovery And Control Rollback Runbooks
- Type: AFK
- Blocked by: GAP-014, GAP-015, GAP-016
- User stories: 27, 29, 40
- What to build:
  - runbooks for failed rollout, expired waiver handling, and control rollback
- Acceptance criteria:
  - [ ] minimum operator runbooks exist
  - [ ] progressive controls point to rollback behavior
  - [ ] repeated trial operation has documented recovery paths
