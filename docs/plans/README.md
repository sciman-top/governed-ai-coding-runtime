# Plans Index

## Purpose
This directory holds executable implementation plans that translate strategy and backlog into ordered work.

## Current Authoritative Plan
- [Direct-To-Hybrid Final-State Implementation Plan](./direct-to-hybrid-final-state-implementation-plan.md)
  - Status: active future-facing implementation mainline
  - Scope: `Phase 0` through `Phase 5`; `Phase 0` planning closeout is complete on the current branch baseline, and the remaining active execution queue covers governed execution closure, live adapter reality, real attached multi-repo trials, machine-local sidecar default, service-shaped runtime extraction, and final hardening or closeout discipline
- [Interactive Session Productization Implementation Plan](./interactive-session-productization-implementation-plan.md)
  - Status: completed execution plan kept as productization history
  - Scope: `GAP-035` through `GAP-039` covering target-repo attachment, session bridge, direct Codex adapter, generic adapter tiers, multi-repo trial loop, and closeout evidence
- [Interactive Session Productization Plan](./interactive-session-productization-plan.md)
  - Status: completed planning realignment kept as history
  - Scope: created the `GAP-035` through `GAP-039` queue and generic attachment blueprint; use the implementation plan above for current execution
- [Governance Runtime Strategy Alignment Plan](./governance-runtime-strategy-alignment-plan.md)
  - Status: completed coordination plan kept as strategy-alignment history and closeout rationale
  - Scope: external mechanism borrowing, source-of-truth versus runtime bundle decision, PolicyDecision contract, local/CI same-contract verification, and backlog/issue-seed alignment
- [Maintenance Implementation Plan](./maintenance-implementation-plan.md)
  - Status: completed execution plan kept as the local baseline maintenance checklist
  - Scope: `GAP-033` through `GAP-034` covering compatibility and upgrade policy, maintenance and triage rules, and deprecation or retirement visibility through runtime status and doctor checks
- [Public Usable Release Implementation Plan](./public-usable-release-implementation-plan.md)
  - Status: completed execution plan kept as the Public Usable Release closeout checklist
  - Scope: `GAP-029` through `GAP-032` covering bootstrap, quickstart, richer local operator surface, sample/demo profiles, packaging, release criteria, and adapter degrade behavior
- [Full Runtime Implementation Plan](./full-runtime-implementation-plan.md)
  - Status: completed execution plan kept as the Full Runtime closeout checklist
  - Scope: `GAP-024` through `GAP-028` covering worker execution, managed workspaces, artifact persistence, operational verification, replay data, and runtime status surfaces
- [Foundation Runtime Substrate Implementation Plan](./foundation-runtime-substrate-implementation-plan.md)
  - Status: completed Foundation execution plan kept as implementation history
  - Scope: `GAP-020` through `GAP-023` covering clarification and compatibility maturity, live build and doctor gates, durable task persistence skeleton, and control lifecycle or evidence completeness checks
- [Phase 0 Runnable Baseline Implementation Plan](./phase-0-runnable-baseline-implementation-plan.md)
  - Status: historical MVP-era implementation plan
  - Scope: repository skeleton, local verifier, CI minimums, runtime-consumable control-pack reference asset, repo admission planning, and gate routing cleanup

## How To Use This Directory
1. Read the latest audit review:
   - [Hybrid Final-State Executable Gap Audit](../reviews/2026-04-19-hybrid-final-state-executable-gap-audit.md)
   - [Hybrid Final-State And Plan Reconciliation](../reviews/2026-04-18-hybrid-final-state-and-plan-reconciliation.md)
2. Read the latest supporting evidence:
   - [20260417 Foundation Execution Plan](../change-evidence/20260417-foundation-execution-plan.md)
   - [20260418 Full Runtime Execution Plan](../change-evidence/20260418-full-runtime-execution-plan.md)
   - [20260418 Public Usable Release Execution Plan](../change-evidence/20260418-public-usable-release-execution-plan.md)
   - [20260418 Maintenance Execution Plan](../change-evidence/20260418-maintenance-execution-plan.md)
   - [20260418 Governance Runtime Strategy Alignment Closeout](../change-evidence/20260418-governance-runtime-strategy-alignment-closeout.md)
   - [20260418 Governance Runtime Strategy Alignment Plan](../change-evidence/20260418-governance-runtime-strategy-alignment-plan.md)
3. Use the roadmap and backlog to understand current posture:
   - the local runtime baseline through `Maintenance Baseline / GAP-034` is complete on the current branch baseline
   - use [Direct-To-Hybrid Final-State Implementation Plan](./direct-to-hybrid-final-state-implementation-plan.md) as the active future-facing execution mainline
   - use [Interactive Session Productization Implementation Plan](./interactive-session-productization-implementation-plan.md) as the completed productization execution history
   - use [Governance Runtime Strategy Alignment Plan](./governance-runtime-strategy-alignment-plan.md) as the completed alignment record for `GAP-040` through `GAP-044`
   - use [Direct-To-Hybrid Final-State Roadmap](../roadmap/direct-to-hybrid-final-state-roadmap.md) for phase order and claim discipline
   - use [Local Baseline To Hybrid Final-State Migration Matrix](../architecture/local-baseline-to-hybrid-final-state-migration-matrix.md) when comparing completed plans or landed baseline code against the new hybrid final-state target
   - use [Maintenance Implementation Plan](./maintenance-implementation-plan.md) as the latest completed baseline closeout history
   - keep future maintenance evidence in `docs/change-evidence/`

## Boundaries
- Plans here should be execution-oriented, not a duplicate of the PRD or architecture docs.
- Roadmap timing stays in `docs/roadmap/`.
- Gap ordering and dependencies stay in `docs/backlog/`.
- Historical plans remain useful evidence. The active future-facing entrypoint is now the direct-to-final-state implementation plan, while completed productization and strategy-alignment plans remain rationale and execution history rather than a second active queue.
