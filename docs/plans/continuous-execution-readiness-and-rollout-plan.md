# Continuous Execution Readiness And Rollout Plan

## Status
- active kickoff plan on `2026-04-23`
- execution mode: small closed loops (`implement -> verify -> evidence -> rollback`)
- `Task 1` is complete by `docs/change-evidence/20260614-continuous-execution-readiness-reassessment.md`
- `Task 2` is complete by `docs/change-evidence/20260614-continuous-execution-task-board-template.md`
- `Task 3` is complete by `docs/change-evidence/20260614-continuous-execution-output-envelope.md`
- `Task 4` is complete by the already-landed runtime/evidence path anchored in:
  - `docs/change-evidence/20260422-interaction-profile-runtime-enforcement.md`
  - `docs/change-evidence/20260422-interaction-evidence-trace-and-runtime-projection.md`
  - revalidated by `docs/change-evidence/20260614-continuous-execution-phase2-misalignment-metrics.md`
- `Task 5` is complete by `docs/change-evidence/20260614-continuous-execution-phase2-misalignment-metrics.md`
- `Task 6` is complete by `docs/change-evidence/20260614-continuous-execution-teaching-yield-guardrail.md`
- `Task 7` is complete by `docs/change-evidence/20260614-continuous-execution-two-repo-trials.md`
- `Task 8` is complete by `docs/change-evidence/20260615-continuous-execution-active-loop-reconciliation.md`

## Goal
Turn the approved interaction-governance direction into continuously executable work across target repos, while keeping hard governance boundaries unchanged and token usage bounded.

## Fixed Boundaries
- canonical gate order remains `build -> test -> contract/invariant -> hotspot`
- clarification cap remains `max_questions <= 3`
- hard budget stop and explicit degrade semantics remain non-overridable
- repo-level interaction defaults may tune phrasing, but may not weaken approvals, gate order, or rollback/evidence requirements

## Readiness Trigger (Start Continuous Rollout)
Continuous rollout starts only when all conditions are met:
1. two consecutive full gate passes on current mainline baseline
2. runtime consumes repo-profile interaction defaults with hard-cap enforcement
3. minimum learning-efficiency metrics output is stable and persisted
4. at least two low-risk target repos complete attached trial with evidence and rollback refs

## Architecture Decisions
- Keep interaction-governance changes task-scoped and evidence-backed; no transcript-only hidden behavior.
- Prefer trigger-based restatement and checklist-first guidance over per-turn verbose teaching.
- Enforce token efficiency through posture downgrade (`teaching -> guided -> terse`) and explicit budget-stop behavior.
- Land cross-repo rollout through profile/baseline templates first, then runtime enforcement and telemetry hardening.

## Task List

### Phase 1: Readiness Baseline

## Task 1: Freeze Continuous-Execution Trigger Contract
**Description:** Codify the startup trigger as an execution checklist to prevent drift between plan, runtime decisions, and operator expectations.

**Acceptance criteria:**
- [x] Trigger conditions are documented in one plan source and one evidence source.
- [x] Trigger wording is aligned with existing clarification/budget hard boundaries.
- [x] Trigger can be verified from local artifacts and gate outputs.

**Verification:**
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- [x] Manual check: trigger terms are consistent with `docs/specs/clarification-protocol-spec.md` and `docs/specs/teaching-budget-spec.md`.

**Dependencies:** None  
**Files likely touched:** `docs/plans/*`, `docs/change-evidence/*`  
**Estimated scope:** S

## Task 2: Add Continuous-Execution Task Board Skeleton
**Description:** Define the minimum fields for every loop item so each run is auditable and rollback-ready.

**Acceptance criteria:**
- [x] Each task template includes `goal/scope/acceptance/verification/evidence/rollback`.
- [x] Each task template includes interaction fields (`signal`, `policy`, `budget snapshot`).
- [x] Template is compatible with existing evidence bundle semantics.

**Verification:**
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- [x] Manual check: template does not conflict with `docs/specs/evidence-bundle-spec.md`.

**Dependencies:** Task 1  
**Files likely touched:** `docs/plans/*`, `docs/templates/*`  
**Estimated scope:** S

## Task 3: Define Token-Efficient Teaching Output Envelope
**Description:** Make response-shape limits explicit so teaching remains short, actionable, and bounded.

**Acceptance criteria:**
- [x] Envelope includes: one-line task anchor, `1..3` questions, `3..5` observation checklist items, at most one term explanation.
- [x] Envelope includes downgrade rules for `near_limit` and `exhausted`.
- [x] Envelope references existing response-policy and teaching-budget invariants.

**Verification:**
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- [x] Manual check: no rule exceeds clarification cap or hard budget stop semantics.

**Dependencies:** Task 1  
**Files likely touched:** `docs/specs/*`, `docs/product/*`  
**Estimated scope:** M

### Checkpoint: Phase 1
- [x] docs checks pass
- [x] readiness trigger is explicit and reviewable
- [x] output-envelope limits are bounded and compatible with current contracts

### Phase 2: Runtime Enforcement And Metrics

## Task 4: Enforce Interaction Profile Consumption in Runtime Paths
**Description:** Ensure runtime execution consistently consumes repo-profile interaction defaults and preserves hard caps.

**Acceptance criteria:**
- [x] runtime applies interaction defaults on task creation/run paths
- [x] invalid overrides fail closed
- [x] operator surface projection reflects active interaction posture fields when available

**Verification:**
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- [x] `python -m unittest discover -s tests/runtime -p "test_*.py"`

**Dependencies:** Phase 1 checkpoint  
**Files likely touched:** `packages/contracts/src/*`, `scripts/run-governed-task.py`, `tests/runtime/*`  
**Estimated scope:** M

## Task 5: Add Misalignment False-Positive / False-Negative Metrics
**Description:** Add bounded quality signals so clarification and teaching triggers can be tuned with evidence, not intuition.

**Acceptance criteria:**
- [x] metric definitions are task-scoped and reviewable
- [x] metrics do not auto-mutate runtime behavior
- [x] metrics persist with source evidence links

**Verification:**
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- [x] `python -m unittest tests.runtime.test_learning_efficiency_metrics -v`

**Dependencies:** Task 4  
**Files likely touched:** `docs/specs/*`, `schemas/jsonschema/*`, `packages/contracts/src/*`, `tests/runtime/*`  
**Estimated scope:** M

## Task 6: Add Teaching Yield vs Token Spend Guardrail
**Description:** Introduce a bounded rule that downshifts response mode when explanation spend rises without alignment improvement.

**Acceptance criteria:**
- [x] guardrail thresholds are explicit and machine-reviewable
- [x] downgrade path is deterministic (`teaching -> guided -> terse`)
- [x] stop/handoff behavior remains explicit at exhaustion

**Verification:**
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`

**Dependencies:** Task 5  
**Files likely touched:** `packages/contracts/src/*`, `docs/specs/*`, `tests/runtime/*`  
**Estimated scope:** M

### Checkpoint: Phase 2
- [x] runtime and contract gates pass
- [x] learning-efficiency metrics remain persisted and evidence-linked
- [x] downgrade behavior is deterministic under budget pressure

### Phase 3: Cross-Repo Rollout

## Task 7: Rollout to Two Low-Risk Target Repos
**Description:** Execute attached trials on two low-risk target repos to validate baseline portability.

**Acceptance criteria:**
- [x] each repo has successful attachment posture and gate references
- [x] each repo has evidence and rollback refs
- [x] no hard-boundary override is required

**Verification:**
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target "classroomtoolkit" -FlowMode "daily" -Mode "quick"`
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target "github-toolkit" -FlowMode "daily" -Mode "quick"`

**Dependencies:** Phase 2 checkpoint  
**Files likely touched:** `.runtime/attachments/*`, `docs/change-evidence/*`  
**Estimated scope:** M

## Task 8: Reconcile Active Continuous Loop Truth
**Description:** Once readiness trigger is satisfied and the active queue is promoted, close the remaining truth gap between owner-directed activation and selector-driven defer posture by documenting the bounded active-loop cadence and publishing one gate-backed loop result.

**Acceptance criteria:**
- [x] readiness trigger checklist is fully satisfied
- [x] active-loop cadence is documented and auditable
- [x] one full loop result is published with gate outputs

**Verification:**
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

**Dependencies:** Task 7  
**Files likely touched:** `docs/change-evidence/*`, `docs/plans/*`  
**Estimated scope:** S

### Checkpoint: Phase 3
- [x] two-repo trial proof is present
- [x] readiness trigger is fully met
- [x] continuous loop is active with gate-backed evidence

## Risks and Mitigations
| Risk | Impact | Mitigation |
|---|---|---|
| Over-clarification causes token waste | Medium | force checklist-first when observation gaps persist and cap clarification rounds |
| Under-explanation increases rework | Medium | track alignment metrics and downshift only when yield is low |
| Cross-repo profile drift | High | enforce baseline profile sync before rollout |
| Evidence drift across loops | High | require per-loop evidence entry with rollback refs and gate outputs |

## Immediate Next Slice
1. Keep `Continuous-Execution` active as a bounded selector-backed evidence loop instead of inferring heavy implementation permission.
2. Open the next slice only when fresh evidence shows a real gap inside the active loop or a new owner-directed queue promotion is justified.
3. Preserve `defer_ltp_and_refresh_evidence` until the selector output itself changes with stronger evidence.
