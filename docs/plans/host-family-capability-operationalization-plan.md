# Host-Family Capability Operationalization Plan

## Status
- conditional owner-directed follow-up plan created on `2026-06-07`
- do not treat this plan as the current active queue while `docs/architecture/planning-status.json` still reports `current_decision_gate = wait_for_host_capability_recovery`

## Goal
Turn the refreshed best-end-state definition, host-family posture, and capability-first blueprint into a bounded executable queue that can start only after current gate conditions permit promotion.

## Fixed Boundaries
- `docs/architecture/planning-status.json` remains the single source of current active queue, current decision gate, and current live posture.
- Historical certification does not activate this queue by itself.
- This plan must not claim recovered Codex `native_attach` until fresh evidence proves recovery.
- Host support continues to be modeled as host families plus capability declarations, not product-name-specific kernel branches.
- Canonical verification order remains `build -> test -> contract/invariant -> hotspot`.

## Activation Trigger
Promote this plan only when all of the following are true:
1. the owner explicitly chooses to promote it, or the status file is updated to a new non-blocking next action that permits bounded follow-on planning work
2. `GAP-159..164` no longer needs to be treated as the current active queue reference
3. fresh evidence exists for the live-host posture that justifies stronger operationalization work instead of continued bounded defer
4. the promotion decision is written as evidence with rollback

## Task List

### Task 1: Freeze Host-Family Operationalization Scope Fence
**Maps to:** `GAP-165`

**Description:** Define the exact scope of post-`GAP-164` host-family operationalization without reopening the current active queue or weakening the live-posture gate.

**Acceptance criteria:**
- [ ] The queue is explicitly documented as conditional follow-up rather than current active work.
- [ ] The queue explains why host-family/capability-first operationalization is separate from historical certification.
- [ ] Activation requires explicit promotion evidence and rollback.

**Verification:**
- [ ] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
- [ ] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`

**Dependencies:** None  
**Files likely touched:** `docs/plans/*`, `docs/backlog/*`, `docs/change-evidence/*`  
**Estimated scope:** S

### Task 2: Capability Declaration And Claim Surface Contract
**Maps to:** `GAP-166`

**Description:** Define the canonical fields that future operator, claim, adapter, and verification surfaces must expose when the runtime talks about host capability.

**Acceptance criteria:**
- [ ] Canonical fields include `host_family`, `surface_class`, `attach_mode`, `adapter_tier`, `degrade_reason`, `verification_refs`, and `evidence_refs`.
- [ ] The contract distinguishes host family from adapter tier so product identity and live posture are not conflated.
- [ ] Fail-closed expectations are documented for missing required host-capability fields.

**Verification:**
- [ ] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
- [ ] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- [ ] manual review against `docs/strategy/current-best-end-state-blueprint.md` and `docs/architecture/host-family-capability-surface-blueprint.md`

**Dependencies:** Task 1  
**Files likely touched:** `docs/specs/*`, `docs/product/*`, `docs/architecture/*`, `docs/change-evidence/*`  
**Estimated scope:** M

### Task 3: Post-Recovery Activation Trigger And Claim Upgrade Gate
**Maps to:** `GAP-167`

**Description:** Define the exact evidence required to upgrade host claims after recovery and the decision rule that distinguishes wording refreshes from backlog-worthy changes.

**Acceptance criteria:**
- [ ] The promotion rule requires fresh evidence and cannot be satisfied by historical certification alone.
- [ ] The trigger names the minimum recovery evidence needed before Codex can move from degraded `process_bridge` to stronger live-host claims.
- [ ] The rule distinguishes wording-only refreshes from true queue-opening changes.

**Verification:**
- [ ] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
- [ ] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- [ ] manual review against `docs/architecture/planning-status.json`

**Dependencies:** Task 2  
**Files likely touched:** `docs/architecture/*`, `docs/product/*`, `docs/strategy/*`, `docs/change-evidence/*`  
**Estimated scope:** M

### Task 4: Conditional Queue Closeout And Promotion Handoff
**Maps to:** `GAP-168`

**Description:** Close the planning package so future promotion into an active queue is auditable, renderable, and rollbackable.

**Acceptance criteria:**
- [ ] Plan, backlog, issue seeds, and index entrypoints all describe the same queue and conditional posture.
- [ ] The issue-rendering script accepts the new `GAP-165..168` range.
- [ ] The queue still does not mutate `planning-status.json` without a separate explicit promotion step.

**Verification:**
- [ ] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
- [ ] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- [ ] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`

**Dependencies:** Task 3  
**Files likely touched:** `docs/plans/*`, `docs/backlog/*`, `scripts/github/create-roadmap-issues.ps1`, `docs/change-evidence/*`  
**Estimated scope:** S

## Immediate Rule
Use this plan as a prepared follow-on queue, not as permission to start new implementation work while the current decision gate still waits for host capability recovery.
