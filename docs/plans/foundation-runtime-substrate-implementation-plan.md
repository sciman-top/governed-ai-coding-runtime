# Foundation Runtime Substrate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Execute `GAP-020` through `GAP-023` so the current contracts-first MVP can evolve into a durable single-machine runtime substrate with live gates, deterministic lifecycle persistence, and machine-checkable control maturity.

**Architecture:** Foundation should extend the existing Python contract primitives instead of replacing them. Keep the deployment model single-machine and conservative: use local file-backed persistence, runtime-visible metadata, and verifier-integrated build/doctor entrypoints now; defer multi-service orchestration, databases, workers, and UI to `Full Runtime`.

**Tech Stack:** Python 3.x standard library and dataclass domain models under `packages/contracts/`, PowerShell 7+ repository and runtime gate scripts under `scripts/`, JSON Schema draft 2020-12 under `schemas/jsonschema/`, Markdown specs and evidence under `docs/`.

---

## Source Inputs
- Product scope: `docs/prd/governed-ai-coding-runtime-prd.md`
- Active lifecycle roadmap: `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- Active backlog: `docs/backlog/issue-ready-backlog.md`
- Full lifecycle seeds: `docs/backlog/full-lifecycle-backlog-seeds.md`
- Existing MVP execution baseline: `docs/roadmap/governed-ai-coding-runtime-90-day-plan.md`
- Existing implementation baseline: `docs/plans/phase-0-runnable-baseline-implementation-plan.md`
- Repo rules: `AGENTS.md`
- Relevant specs:
  - `docs/specs/task-lifecycle-and-state-machine-spec.md`
  - `docs/specs/control-registry-spec.md`
  - `docs/specs/evidence-bundle-spec.md`
  - `docs/specs/agent-adapter-contract-spec.md`
  - `docs/specs/verification-gates-spec.md`
  - `docs/specs/repo-profile-spec.md`

## Current Starting Point
- The repository already has Python contract primitives and runtime tests for task intake, approvals, write governance, verification planning, evidence timeline, delivery handoff, and minimal operator console behavior.
- `build` and `hotspot` still rely on `gate_na`; `test` and `contract/invariant` already use live verification commands.
- The active product planning baseline has frozen the final product shape and capability boundary through `Vision / GAP-018` and `GAP-019`.
- The next executable queue is `Foundation / GAP-020` through `GAP-023`.

## Foundation Boundaries

### Always do
- Preserve gate order `build -> test -> contract/invariant -> hotspot`.
- Prefer additive spec/schema evolution over semantic rewrites.
- Keep the first durable runtime substrate single-machine and file-backed.
- Add or update runtime tests for every new contract module or lifecycle rule.
- Record each completed slice in `docs/change-evidence/`.

### Ask first
- Introducing a database, queue, Temporal, Redis, or HTTP service boundary.
- Introducing non-stdlib Python dependencies.
- Renaming existing lifecycle states or approval semantics.
- Expanding scope into worker execution, artifact store, or UI work reserved for `Full Runtime`.

### Never do
- Do not skip the existing Python contract layer and jump directly to a service scaffold.
- Do not claim `build` or `hotspot` are live until concrete commands are runnable in this repo.
- Do not add compatibility semantics that silently weaken approval, gate order, or evidence requirements.
- Do not couple the first task store to cloud-only infrastructure.

## Planned File Structure

### Create
- `docs/specs/clarification-protocol-spec.md`: formal clarification trigger and evidence semantics.
- `schemas/jsonschema/clarification-protocol.schema.json`: machine-readable clarification policy shape.
- `schemas/examples/clarification-protocol/default-runtime.example.json`: baseline clarification policy instance.
- `packages/contracts/src/governed_ai_coding_runtime_contracts/clarification.py`: clarification policy evaluation primitives.
- `packages/contracts/src/governed_ai_coding_runtime_contracts/compatibility.py`: repo and adapter compatibility signal helpers.
- `packages/contracts/src/governed_ai_coding_runtime_contracts/task_store.py`: local durable task persistence primitives.
- `packages/contracts/src/governed_ai_coding_runtime_contracts/workflow.py`: deterministic workflow transition helpers on top of stored task state.
- `packages/contracts/src/governed_ai_coding_runtime_contracts/control_registry.py`: lifecycle-aware control metadata helpers.
- `scripts/build-runtime.ps1`: first real build command for current Python runtime substrate.
- `scripts/doctor-runtime.ps1`: first real doctor or hotspot command for current runtime substrate.
- `tests/runtime/test_clarification.py`
- `tests/runtime/test_compatibility.py`
- `tests/runtime/test_task_store.py`
- `tests/runtime/test_workflow.py`
- `tests/runtime/test_control_registry.py`
- `tests/runtime/test_runtime_doctor.py`
- `docs/change-evidence/<date>-foundation-execution-plan.md`

### Modify
- `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/full-lifecycle-backlog-seeds.md`
- `docs/backlog/README.md`
- `docs/plans/README.md`
- `docs/README.md`
- `README.md`
- `README.zh-CN.md`
- `README.en.md`
- `docs/change-evidence/README.md`
- `AGENTS.md`: only after live `build` and `hotspot` commands exist.
- `scripts/verify-repo.ps1`: add build and doctor entrypoints only after they are real.
- `packages/contracts/README.md`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/task_intake.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_profile.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/evidence.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/verification_runner.py`
- `docs/specs/task-lifecycle-and-state-machine-spec.md`
- `docs/specs/control-registry-spec.md`
- `docs/specs/evidence-bundle-spec.md`
- `docs/specs/agent-adapter-contract-spec.md`
- `docs/specs/verification-gates-spec.md`
- `docs/specs/repo-profile-spec.md`
- `schemas/jsonschema/task-lifecycle.schema.json`
- `schemas/jsonschema/control-registry.schema.json`
- `schemas/jsonschema/evidence-bundle.schema.json`
- `schemas/jsonschema/agent-adapter-contract.schema.json`
- `schemas/jsonschema/verification-gates.schema.json`
- `schemas/jsonschema/repo-profile.schema.json`
- `schemas/catalog/schema-catalog.yaml`

## Task List

### Task 0: Advance The Planning Baseline From Vision To Foundation

**Files:**
- Modify: `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- Modify: `docs/backlog/issue-ready-backlog.md`
- Modify: `docs/backlog/full-lifecycle-backlog-seeds.md`
- Modify: `docs/backlog/README.md`
- Modify: `docs/plans/README.md`
- Modify: `docs/README.md`
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `README.en.md`
- Evidence: `docs/change-evidence/<date>-foundation-execution-plan.md`

**Purpose:** Move the repository's active execution posture from approved lifecycle definition to Foundation implementation work.

**Acceptance criteria:**
- Active docs say `Vision` is complete through planning alignment and capability freeze.
- Active next-step queue starts at `Foundation / GAP-020`.
- `docs/plans/` exposes this plan as the current execution entrypoint.

**Steps:**
- [ ] Record `Vision / GAP-018` and `GAP-019` as complete in the active roadmap and backlog without deleting them from planning history.
- [ ] Update root and docs index files so the active queue starts at `Foundation / GAP-020`.
- [ ] Add this plan to `docs/plans/README.md` as the current authoritative execution plan.
- [ ] Create or update evidence that links the lifecycle planning baseline to this Foundation plan.

### Task 1: Land GAP-020 Clarification, Rollout, Compatibility, And Evidence Maturity

**Files:**
- Create: `docs/specs/clarification-protocol-spec.md`
- Create: `schemas/jsonschema/clarification-protocol.schema.json`
- Create: `schemas/examples/clarification-protocol/default-runtime.example.json`
- Create: `packages/contracts/src/governed_ai_coding_runtime_contracts/clarification.py`
- Create: `packages/contracts/src/governed_ai_coding_runtime_contracts/compatibility.py`
- Create: `tests/runtime/test_clarification.py`
- Create: `tests/runtime/test_compatibility.py`
- Modify: `docs/specs/evidence-bundle-spec.md`
- Modify: `docs/specs/agent-adapter-contract-spec.md`
- Modify: `docs/specs/repo-profile-spec.md`
- Modify: `schemas/jsonschema/evidence-bundle.schema.json`
- Modify: `schemas/jsonschema/agent-adapter-contract.schema.json`
- Modify: `schemas/jsonschema/repo-profile.schema.json`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/evidence.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_profile.py`
- Modify: `schemas/catalog/schema-catalog.yaml`

**Purpose:** Turn clarification, rollout mode, compatibility posture, and evidence quality into explicit runtime inputs instead of informal planning intent.

**Acceptance criteria:**
- Clarification triggers, state, and audit fields are formally specified and example-backed.
- Repo profiles and adapter contracts can express `observe`, `advisory`, and `enforced` posture.
- Compatibility helpers can distinguish full support, partial support, and explicit degrade behavior.
- Evidence models can distinguish missing mandatory evidence from weak or advisory outcomes.

**Steps:**
- [ ] Add a standalone clarification spec and schema covering trigger threshold, clarification mode, question cap, evidence fields, and reset semantics from `AGENTS.md`.
- [ ] Extend repo and adapter contract specs/schemas with rollout posture and compatibility signal fields needed for mechanical checks.
- [ ] Extend evidence bundle spec/schema so required evidence absence can fail validation independently from task outcome quality.
- [ ] Add Python contract helpers and tests for clarification policy evaluation and compatibility posture resolution.
- [ ] Update schema catalog and examples so the new clarification asset family participates in repo verification.

### Task 2: Land GAP-021 Real Build And Doctor Gates

**Files:**
- Create: `scripts/build-runtime.ps1`
- Create: `scripts/doctor-runtime.ps1`
- Create: `tests/runtime/test_runtime_doctor.py`
- Modify: `scripts/verify-repo.ps1`
- Modify: `AGENTS.md`
- Modify: `docs/specs/verification-gates-spec.md`
- Modify: `schemas/jsonschema/verification-gates.schema.json`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/verification_runner.py`
- Modify: `packages/contracts/README.md`
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `README.en.md`

**Purpose:** Replace the remaining `gate_na` placeholders with the first live build and doctor commands that are honest for the current Python runtime substrate.

**Acceptance criteria:**
- `scripts/build-runtime.ps1` is a real command and exits non-zero on build failures.
- `scripts/doctor-runtime.ps1` is a real command and exits non-zero on runtime readiness failures.
- `scripts/verify-repo.ps1` can route build and doctor checks through those live commands.
- `AGENTS.md` stops classifying `build` and `hotspot` as `gate_na`.

**Steps:**
- [ ] Define the narrow meaning of "build" for Foundation: validate importability and byte-compilation of the current Python runtime substrate, not future product packaging.
- [ ] Define the narrow meaning of "doctor" for Foundation: verify runtime prerequisites such as `python`, expected directories, schema/catalog visibility, and the presence of active build/test/contract commands.
- [ ] Update verification gate spec/schema and contract helpers so quick/full plans reference live build and doctor gate ids consistently.
- [ ] Wire `scripts/verify-repo.ps1` to expose dedicated `Build` and `Doctor` checks while preserving gate order in `-Check All`.
- [ ] Update docs and AGENTS gate table only after the commands exist and pass locally.

### Task 3: Land GAP-022 Durable Task Store And Workflow Skeleton

**Files:**
- Create: `packages/contracts/src/governed_ai_coding_runtime_contracts/task_store.py`
- Create: `packages/contracts/src/governed_ai_coding_runtime_contracts/workflow.py`
- Create: `tests/runtime/test_task_store.py`
- Create: `tests/runtime/test_workflow.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/task_intake.py`
- Modify: `docs/specs/task-lifecycle-and-state-machine-spec.md`
- Modify: `schemas/jsonschema/task-lifecycle.schema.json`
- Modify: `schemas/examples/repo-profile/python-service.example.json`
- Modify: `schemas/examples/repo-profile/typescript-webapp.example.json`

**Purpose:** Give task lifecycle state a durable single-machine home and deterministic transition engine before worker execution exists.

**Acceptance criteria:**
- Task state survives process boundaries through a local persisted store.
- Stored lifecycle records can represent pause, resume, timeout, retry, cancel, fail, and completion metadata.
- Workflow helpers enforce legal transitions and produce deterministic transition events.
- Repo examples and lifecycle schema stay aligned with the new durable metadata requirements.

**Steps:**
- [ ] Extend the task lifecycle spec and schema to include persistent task ids, transition history, timeout or retry metadata, and pause or resume semantics required by the final product boundary.
- [ ] Implement a file-backed task store using repo-local JSON artifacts or append-only event files; do not introduce a database in Foundation.
- [ ] Implement deterministic workflow helpers that build on the existing transition validation rather than replacing it.
- [ ] Add tests covering store round-trips, illegal transition rejection, resume after reload, and timeout or retry state persistence.
- [ ] Keep the workflow scope at orchestration skeleton level; do not add worker dispatch in this stage.

### Task 4: Land GAP-023 Control Registry Lifecycle And Evidence Completeness Checks

**Files:**
- Create: `packages/contracts/src/governed_ai_coding_runtime_contracts/control_registry.py`
- Create: `tests/runtime/test_control_registry.py`
- Modify: `docs/specs/control-registry-spec.md`
- Modify: `docs/specs/evidence-bundle-spec.md`
- Modify: `schemas/jsonschema/control-registry.schema.json`
- Modify: `schemas/jsonschema/evidence-bundle.schema.json`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/evidence.py`
- Modify: `schemas/catalog/schema-catalog.yaml`

**Purpose:** Make control lifecycle state, recurring review posture, and evidence completeness mechanically checkable.

**Acceptance criteria:**
- Control registry records lifecycle, review cadence, observability, and rollback visibility in a stable machine-readable shape.
- Evidence completeness checks can fail missing required fields independently from task success/failure.
- Runtime tests cover missing rollback refs, missing observability, and incomplete evidence cases.

**Steps:**
- [ ] Extend the control registry spec/schema with lifecycle status, last-reviewed or next-review metadata, and explicit rollback or observability completeness markers.
- [ ] Add contract helpers that evaluate whether a control is healthy enough to participate in enforced mode.
- [ ] Extend evidence helpers so they can calculate completeness state, enumerate missing fields, and fail hard requirements.
- [ ] Add tests for progressive control review drift, missing rollback references, and incomplete evidence bundles.
- [ ] Keep the first implementation repo-local and synchronous; async review orchestration belongs to `Full Runtime`.

### Task 5: Final Foundation Verification And Handoff

**Files:**
- Modify: `docs/change-evidence/<date>-foundation-execution-plan.md`
- Modify: `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- Modify: `docs/backlog/issue-ready-backlog.md`
- Optional modify: `docs/reviews/<date>-foundation-runtime-substrate-review.md`

**Purpose:** Close the planning-to-execution handoff for Foundation with verification evidence and a clear next queue into `Full Runtime`.

**Acceptance criteria:**
- `build`, `test`, `contract/invariant`, and `hotspot` all have live commands or active checks in this repo.
- Runtime tests include the new Foundation slices.
- Active docs reflect whether `Foundation` is complete or still partially open.
- Residual risks are explicit and scoped to `Full Runtime`.

**Steps:**
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`.
- [ ] Run `git diff --check` and record any CRLF-only notices separately from whitespace failures.
- [ ] Update evidence with exact commands, exit codes, gate results, residual risks, and rollback notes.

## Checkpoints

### Checkpoint A: After Tasks 0-1
- Active queue starts at `Foundation / GAP-020`.
- Clarification, compatibility, rollout, and evidence maturity have explicit plan-owned file targets.
- Schema catalog and tests have a clear path for the new policy family.

### Checkpoint B: After Task 2
- `build` and `doctor` are live commands.
- `AGENTS.md` gate table no longer uses `gate_na` for `build` or `hotspot`.
- Verification runner contracts reference the live gate ids consistently.

### Checkpoint C: After Tasks 3-4
- Task lifecycle survives process boundaries through a file-backed store.
- Workflow transitions remain deterministic.
- Control lifecycle and evidence completeness are mechanically checkable.

### Checkpoint D: After Task 5
- Foundation work is either verified complete or reduced to an explicit short remainder list.
- `Full Runtime` becomes the next execution queue with no ambiguity about what Foundation delivered first.

## Risks And Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Foundation drifts into multi-service platform scaffolding | High | Keep persistence file-backed and local; defer worker/service boundaries to `Full Runtime`. |
| "Real build" becomes meaningless | High | Define build as importability and runtime-substrate compilation for actual current Python modules, then document that scope explicitly. |
| Doctor checks overclaim runtime health | Medium | Restrict doctor to readiness checks the repo can actually prove today; do not imply deployment health. |
| Evidence completeness becomes only schema-level and misses runtime semantics | Medium | Add contract helpers plus tests that compute completeness over real bundle objects, not just raw JSON validation. |
| Clarification semantics stay doc-only | High | Add a schema, example, and Python policy helper in the same stage. |

## Completion Definition
Foundation is complete when:
- `Vision` is preserved as planning history and no longer the active queue
- clarification, rollout, compatibility, and evidence maturity exist as specs, schemas, examples, and Python contract helpers
- `build` and `hotspot` use live commands rather than `gate_na`
- task lifecycle state can persist across process boundaries on one machine
- control lifecycle and evidence completeness are mechanically checked
- active docs point the next execution queue at `Full Runtime` only after these conditions are verified
