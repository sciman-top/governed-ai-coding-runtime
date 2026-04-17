# Change Evidence Index

## Purpose
This directory stores dated evidence for planning, schema, script, and documentation changes.

## Current Evidence Baseline
- [20260418 Full Runtime CLI-First Planning Realignment](./20260418-full-runtime-cli-first-planning-realignment.md)
  - evidence companion for changing `GAP-027` to a CLI-first operator surface and moving the richer UI shell to `Public Usable Release`
- [20260417 Foundation Execution Plan](./20260417-foundation-execution-plan.md)
  - evidence companion for advancing the active queue from `Vision` to `Foundation` and adding the executable Foundation plan
- [20260417 Full Lifecycle Functional Planning](./20260417-full-lifecycle-functional-planning.md)
  - evidence companion for the new active full-lifecycle roadmap, backlog, issue seeds, and seeding script alignment
- [20260417 Phase 0 Runnable Baseline](./20260417-phase-0-runnable-baseline.md)
  - historical evidence companion for the Phase 0 runnable-baseline execution branch that was later superseded by the mainline runtime substrate
- [20260417 MVP Backlog Closeout Handoff](./20260417-mvp-backlog-closeout-handoff.md)
  - final closeout evidence for the current Phase 0-4 backlog execution chain
- [20260417 Phase 1 Waiver Recovery And Control Rollback Runbooks](./20260417-phase-1-waiver-recovery-control-rollback-runbooks.md)
  - evidence companion for operator recovery runbooks
- [20260417 Phase 1 Minimal Approval And Evidence Console](./20260417-phase-1-minimal-approval-evidence-console.md)
  - evidence companion for the control-plane approval and evidence console facade
- [20260417 Phase 1 Second-Repo Reuse Pilot](./20260417-phase-1-second-repo-reuse-pilot.md)
  - evidence companion for the second repo profile reuse pilot and generic process adapter gap record
- [20260417 Phase 1 Eval And Trace Baseline](./20260417-phase-1-eval-trace-baseline.md)
  - evidence companion for eval baseline and trace grading primitives
- [20260417 Phase 1 Delivery Handoff](./20260417-phase-1-delivery-handoff.md)
  - evidence companion for delivery handoff packages and replay references
- [20260417 Phase 1 Verification Runner](./20260417-phase-1-verification-runner.md)
  - evidence companion for quick/full verification runner plans and artifacts
- [20260417 Phase 1 Write-Side Tool Governance](./20260417-phase-1-write-side-tool-governance.md)
  - evidence companion for write-side governance decisions and rollback references
- [20260417 Phase 1 Approval Flow](./20260417-phase-1-approval-flow.md)
  - evidence companion for the approval state and interruption contract slice
- [20260417 Phase 1 Write Policy Defaults](./20260417-phase-1-write-policy-defaults.md)
  - evidence companion for the conservative write policy default decision
- [20260417 Phase 1 Workspace Allocation](./20260417-phase-1-workspace-allocation.md)
  - evidence companion for the first isolated workspace allocation contract slice
- [20260417 Phase 1 Scripted Trial Entrypoint](./20260417-phase-1-scripted-trial-entrypoint.md)
  - evidence companion for the first documented read-only trial entrypoint
- [20260417 Phase 1 Evidence Timeline](./20260417-phase-1-evidence-timeline.md)
  - evidence companion for the first evidence timeline contract slice
- [20260417 Phase 1 Read-Only Tool Runner](./20260417-phase-1-readonly-tool-runner.md)
  - evidence companion for the first read-only tool runner contract slice
- [20260417 Phase 1 Task Intake And Repo Resolution](./20260417-phase-1-task-intake-repo-resolution.md)
  - evidence companion for the first Phase 1 runtime contract slice
- [20260417 Pre-Implementation Deep Audit And Doc Refresh](./20260417-pre-implementation-deep-audit-and-doc-refresh.md)
  - current evidence companion for the latest implementation handoff review
- [20260417 Phase 0 Plan Evidence](./20260417-phase-0-plan.md)
  - evidence companion for the current executable plan

## Directory Semantics
- dated `.md` files:
  - change basis, rule landing, commands, gate results, risks, and rollback notes
- `snapshots/`:
  - optional rollback and audit copies for selected file states
- `rename-cleanup.log`:
  - utility artifact from rename cleanup
  - not part of the active product-surface documentation baseline

## Verification Boundary Note
- Evidence files may be linked from active docs as operator references.
- Historical paths, command snippets, and preserved old names inside this directory are not the active docs/spec/schema baseline and should not be treated as live product documentation.
