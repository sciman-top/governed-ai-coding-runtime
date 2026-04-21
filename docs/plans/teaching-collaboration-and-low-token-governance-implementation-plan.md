# Teaching Collaboration And Low-Token Governance Implementation Plan

> **For agentic workers:** Execute this plan in narrow slices. Keep each slice evidence-backed, gate-verified, and compatible with the existing governed task, evidence, and trace model.

**Goal:** Turn the approved top-level design for teaching-style collaboration and low-token governance into a bounded implementation lane that lands formal specs, schemas, examples, evidence integration, trace inputs, and minimal read-model projection without creating a parallel runtime or changing canonical gate semantics.

**Architecture:** Preserve the current source-of-truth split: `docs/` for design and execution rationale, `schemas/` for machine-readable contract families, `packages/contracts/` for executable primitives, and existing evidence/trace/operator surfaces as the integration points. Land the interaction model in dependency order: first formalize reviewable contracts, then wire those contracts into evidence and trace semantics, then add task/runtime defaults and minimal read-model projection, and only then add repo-profile defaults and follow-on metrics wiring.

**Tech Stack:** Markdown under `docs/`, JSON Schema draft 2020-12 under `schemas/jsonschema/`, schema examples under `schemas/examples/`, Python standard-library contract primitives under `packages/contracts/`, PowerShell verification entrypoints under `scripts/`, and existing runtime/evidence tests under `tests/runtime/`.

---

## Status

- This is a new bounded follow-on implementation plan derived from the approved design document:
  - `docs/superpowers/specs/2026-04-22-teaching-collaboration-and-low-token-governance-design.md`
- It does not replace the completed direct-to-hybrid or governance-optimization implementation histories.
- It defines a narrow post-design execution lane for interaction governance only.

## Current Baseline

- The repository already has:
  - clarification protocol policy shape and Python primitives
  - task intake with `goal / scope / acceptance / budgets`
  - evidence bundle and trace grading contracts
  - repo-map token-budget semantics
  - repo profile summary and handoff template hooks
- The repository does not yet have:
  - formal contracts for interaction signals, response policy, teaching budget, or interaction evidence
  - explicit interaction posture projection in runtime/operator read models
  - postmortem-ready interaction failure classifications
  - repo-profile-level defaults for teaching/cost trade-offs

## Source Inputs

- `docs/superpowers/specs/2026-04-22-teaching-collaboration-and-low-token-governance-design.md`
- `docs/specs/clarification-protocol-spec.md`
- `docs/specs/evidence-bundle-spec.md`
- `docs/specs/eval-and-trace-grading-spec.md`
- `docs/specs/repo-map-context-shaping-spec.md`
- `docs/specs/repo-profile-spec.md`
- `docs/specs/runtime-operator-surface-spec.md`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/task_intake.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/clarification.py`
- `tests/runtime/`

## Dependency Graph

```text
Task 1 interaction core contracts
  -> Task 2 examples and schema catalog integration
       -> Task 3 Python contract primitives
            -> Task 4 evidence bundle interaction_trace integration
                 -> Task 5 trace/postmortem interaction signals
                      -> Task 6 task intake and runtime defaults
                           -> Task 7 operator read-model projection
                                -> Task 8 repo-profile defaults and rollout docs
                                     -> Task 9 metrics baseline and closeout evidence
```

## Planned File Structure

### Planned Create

- `docs/specs/interaction-signal-spec.md`
- `docs/specs/response-policy-spec.md`
- `docs/specs/teaching-budget-spec.md`
- `docs/specs/interaction-evidence-spec.md`
- `docs/specs/learning-efficiency-metrics-spec.md`
- `schemas/jsonschema/interaction-signal.schema.json`
- `schemas/jsonschema/response-policy.schema.json`
- `schemas/jsonschema/teaching-budget.schema.json`
- `schemas/jsonschema/interaction-evidence.schema.json`
- `schemas/jsonschema/learning-efficiency-metrics.schema.json`
- `schemas/examples/interaction-signal/default-bugfix-gap.example.json`
- `schemas/examples/response-policy/guided-clarify.example.json`
- `schemas/examples/teaching-budget/default-runtime.example.json`
- `schemas/examples/interaction-evidence/checklist-first-bugfix.example.json`
- `schemas/examples/learning-efficiency-metrics/baseline.example.json`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/interaction_governance.py`
- `tests/runtime/test_interaction_governance.py`
- `docs/change-evidence/<date>-teaching-collaboration-low-token-implementation-plan.md`

### Planned Modify

- `docs/plans/README.md`
- `docs/change-evidence/README.md`
- `docs/specs/evidence-bundle-spec.md`
- `docs/specs/eval-and-trace-grading-spec.md`
- `docs/specs/repo-profile-spec.md`
- `docs/specs/runtime-operator-surface-spec.md`
- `schemas/jsonschema/evidence-bundle.schema.json`
- `schemas/jsonschema/eval-trace-policy.schema.json`
- `schemas/jsonschema/repo-profile.schema.json`
- `schemas/jsonschema/runtime-operator-surface.schema.json`
- `schemas/catalog/schema-catalog.yaml`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/__init__.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/task_intake.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/runtime_status.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/evidence.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_queries.py`
- `tests/runtime/test_task_intake.py`
- `tests/runtime/test_runtime_status.py`
- `tests/runtime/test_evidence.py`
- `tests/runtime/test_operator_queries.py`

## Task List

**Cross-task evidence rule:**
- Any task that modifies specs, schemas, examples, Python contracts, or operator/runtime read models must add one new `docs/change-evidence/<date>-<slug>.md` entry recording commands, key outputs, risks, and rollback notes.

### Task 1: Define Interaction Core Specs

**Purpose:** Turn the approved design into reviewable contract families before any runtime wiring starts.

**Files:**
- Create: `docs/specs/interaction-signal-spec.md`
- Create: `docs/specs/response-policy-spec.md`
- Create: `docs/specs/teaching-budget-spec.md`
- Create: `docs/specs/interaction-evidence-spec.md`
- Create: `docs/specs/learning-efficiency-metrics-spec.md`

**Acceptance criteria:**
- [x] Each spec defines purpose, required fields, optional fields, and invariants.
- [x] Specs use “observable signals” language rather than psychological inference language.
- [x] `ResponsePolicy` states posture limits and degrade behavior explicitly.
- [x] `TeachingBudget` distinguishes explanation, clarification, and compaction budgets.
- [x] `InteractionEvidence` and `LearningEfficiencyMetrics` align with existing evidence/trace semantics instead of inventing a new storage model.

**Verification:**
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`.

**Dependencies:** None.

**Estimated scope:** Medium.

### Task 2: Add JSON Schemas, Examples, And Catalog Wiring

**Purpose:** Make the new interaction-governance assets machine-readable and enforceable by the existing contract gate.

**Files:**
- Create: `schemas/jsonschema/interaction-signal.schema.json`
- Create: `schemas/jsonschema/response-policy.schema.json`
- Create: `schemas/jsonschema/teaching-budget.schema.json`
- Create: `schemas/jsonschema/interaction-evidence.schema.json`
- Create: `schemas/jsonschema/learning-efficiency-metrics.schema.json`
- Create: `schemas/examples/interaction-signal/default-bugfix-gap.example.json`
- Create: `schemas/examples/response-policy/guided-clarify.example.json`
- Create: `schemas/examples/teaching-budget/default-runtime.example.json`
- Create: `schemas/examples/interaction-evidence/checklist-first-bugfix.example.json`
- Create: `schemas/examples/learning-efficiency-metrics/baseline.example.json`
- Modify: `schemas/catalog/schema-catalog.yaml`

**Acceptance criteria:**
- [x] Each new spec has one schema and one example.
- [x] Schema enums and required fields match the specs exactly.
- [x] New assets participate in existing schema parse, example validation, and catalog pairing gates.
- [x] Example records demonstrate bugfix/checklist-first and budget-pressure scenarios.

**Verification:**
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`.

**Dependencies:** Task 1.

**Estimated scope:** Medium.

### Task 3: Add Python Interaction Governance Primitives

**Purpose:** Provide executable contract helpers that normalize signals, derive policy posture, and validate budget/status transitions.

**Files:**
- Create: `packages/contracts/src/governed_ai_coding_runtime_contracts/interaction_governance.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/__init__.py`
- Create: `tests/runtime/test_interaction_governance.py`

**Acceptance criteria:**
- [x] Helpers can represent signals, policy posture, and budget state without requiring a service boundary.
- [x] Helpers fail closed on invalid signal kinds, posture values, or budget status names.
- [x] Clarification integration remains compatible with the existing clarification primitives instead of replacing them.
- [x] Tests cover task-created, repeated-failure, observation-gap, term-confusion, and budget-pressure cases.

**Verification:**
- [x] Run `python -m unittest tests.runtime.test_interaction_governance -v`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`.

**Dependencies:** Task 2.

**Estimated scope:** Medium.

### Task 4: Extend Evidence Bundle With Interaction Trace

**Purpose:** Persist why the runtime chose to restate, clarify, teach, compress, degrade, or stop.

**Files:**
- Modify: `docs/specs/evidence-bundle-spec.md`
- Modify: `schemas/jsonschema/evidence-bundle.schema.json`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/evidence.py`
- Modify: `tests/runtime/test_evidence.py`

**Acceptance criteria:**
- [ ] `interaction_trace` is modeled as an optional structured extension of the evidence bundle.
- [ ] The extension records signals, applied policies, restatements, clarification rounds, checklists, terms explained, compression actions, budget snapshots, and stop/degrade reasons.
- [ ] Existing evidence consumers remain compatible when `interaction_trace` is absent.
- [ ] The extension does not create a parallel evidence store.

**Verification:**
- [ ] Run `python -m unittest tests.runtime.test_evidence -v`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`.

**Dependencies:** Task 3.

**Estimated scope:** Medium.

### Task 5: Extend Trace Grading And Postmortem Inputs For Interaction Quality

**Purpose:** Make interaction failures auditable without replacing the current four primary trace-grading dimensions.

**Files:**
- Modify: `docs/specs/eval-and-trace-grading-spec.md`
- Modify: `schemas/jsonschema/eval-trace-policy.schema.json`

**Acceptance criteria:**
- [ ] Primary grading dimensions remain unchanged.
- [ ] Postmortem-ready interaction failure classifications are added, including:
  - `misalignment_not_caught`
  - `over_explained_under_budget_pressure`
  - `under_explained_with_high_user_confusion`
  - `repeated_question_without_signal_upgrade`
  - `observation_gap_ignored`
  - `compression_without_recoverable_summary`
- [ ] The new interaction inputs point back to evidence refs and affected dimensions.
- [ ] The spec remains explicit that postmortem inputs do not autonomously mutate policy.

**Verification:**
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`.

**Dependencies:** Task 4.

**Estimated scope:** Small.

### Task 6: Add Task Intake Defaults And Budget Overrides

**Purpose:** Bind interaction governance to task creation instead of treating it as an implicit session habit.

**Files:**
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/task_intake.py`
- Modify: `tests/runtime/test_task_intake.py`

**Acceptance criteria:**
- [ ] Task intake can carry optional `interaction_defaults`.
- [ ] Task intake can carry optional `interaction_budget_overrides`.
- [ ] Existing task creation flows remain valid when the new fields are absent.
- [ ] Defaults do not override hard clarification caps or safety boundaries.

**Verification:**
- [ ] Run `python -m unittest tests.runtime.test_task_intake -v`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`.

**Dependencies:** Task 3.

**Estimated scope:** Small.

### Task 7: Project Minimal Interaction Read Model Into Runtime Status And Operator Queries

**Purpose:** Make the interaction state visible to operators without introducing a new console product.

**Files:**
- Modify: `docs/specs/runtime-operator-surface-spec.md`
- Modify: `schemas/jsonschema/runtime-operator-surface.schema.json`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/runtime_status.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_queries.py`
- Modify: `tests/runtime/test_runtime_status.py`
- Modify: `tests/runtime/test_operator_queries.py`

**Acceptance criteria:**
- [ ] Runtime/operator read models can project current interaction posture.
- [ ] Read models can project the latest task restatement, budget status, clarification activity, compression action, and outstanding observation items count.
- [ ] Read models stay read-only and compatible with current operator-surface semantics.
- [ ] The projection is optional when no interaction data exists.

**Verification:**
- [ ] Run `python -m unittest tests.runtime.test_runtime_status tests.runtime.test_operator_queries -v`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`.

**Dependencies:** Tasks 4, 6.

**Estimated scope:** Medium.

### Task 8: Add Repo-Profile Interaction Defaults

**Purpose:** Allow repositories to set default collaboration style without weakening unified governance semantics.

**Files:**
- Modify: `docs/specs/repo-profile-spec.md`
- Modify: `schemas/jsonschema/repo-profile.schema.json`

**Acceptance criteria:**
- [ ] Repo profiles may declare bounded interaction defaults such as:
  - `interaction_profile.default_mode`
  - `interaction_profile.term_explain_style`
  - `interaction_profile.default_checklist_kind`
  - `interaction_profile.compaction_preference`
  - `interaction_profile.summary_template`
  - `interaction_profile.handoff_teaching_notes`
- [ ] Repo profiles may not override hard clarification caps, hard budget stops, explicit degrade semantics, or canonical gate order.
- [ ] Repo-profile examples remain consistent with summary and handoff templates already in use.

**Verification:**
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`.

**Dependencies:** Tasks 2, 7.

**Estimated scope:** Small.

### Task 9: Close The Lane With Minimal Metrics Baseline And Evidence

**Purpose:** Record the first bounded metrics surface and close the documentation-first lane with auditable evidence.

**Files:**
- Modify: `docs/change-evidence/README.md`
- Modify: `docs/plans/README.md`
- Create: `docs/change-evidence/<date>-teaching-collaboration-low-token-implementation-plan.md`

**Acceptance criteria:**
- [ ] The plan index records this implementation plan as a bounded follow-on lane.
- [ ] Change evidence captures the final task chain, verification results, risks, and rollback notes.
- [ ] The baseline metrics set is documented as:
  - `alignment_confirm_rate`
  - `misalignment_detect_rate`
  - `repeated_failure_before_clarify`
  - `observation_gap_prompt_rate`
  - `term_explanation_trigger_rate`
  - `compression_trigger_rate`
  - `explanation_token_share`
  - `handoff_recovery_success_rate`
- [ ] Evidence clearly states which parts are design-and-contract complete versus runtime-behavior complete.

**Verification:**
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`.

**Dependencies:** Tasks 1 through 8.

**Estimated scope:** Small.

## Scope Discipline

The plan intentionally stops short of:
- a memory-first personalization stack
- autonomous user modeling
- a dedicated teaching UI
- provider-specific prompt engines
- runtime mutation based only on metrics

Those items require additional product evidence and should remain follow-on proposals rather than implicit scope creep inside this lane.
