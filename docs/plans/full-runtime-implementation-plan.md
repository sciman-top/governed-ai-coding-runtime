# Full Runtime Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Execute `GAP-024` through `GAP-028` so the Foundation runtime substrate becomes a real governed runtime path with worker execution, managed workspaces, persisted artifacts, operational verification, replay data, and a CLI-first operator surface that can later support a UI.

**Architecture:** Build on the existing Python contract substrate rather than replacing it. Keep the first Full Runtime slice single-machine and file-backed: a local runtime package owns task execution, workspace allocation, artifact persistence, verification orchestration, replay metadata, and a stable read model for operators. Deliver a CLI-first operator surface in this stage and defer a richer UI shell until a later stage, after runtime read models and query surfaces stabilize.

**Tech Stack:** Python 3.x standard library and dataclass models under `packages/contracts/`, local filesystem persistence under repo-owned runtime directories, PowerShell 7+ verification and doctor entrypoints under `scripts/`, Markdown specs/evidence under `docs/`, JSON Schema draft 2020-12 under `schemas/jsonschema/`.

---

## Source Inputs
- Product scope:
  - `docs/prd/governed-ai-coding-runtime-prd.md`
- Active lifecycle roadmap:
  - `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- Active backlog:
  - `docs/backlog/issue-ready-backlog.md`
  - `docs/backlog/full-lifecycle-backlog-seeds.md`
- Foundation closeout:
  - `docs/change-evidence/20260417-foundation-execution-plan.md`
- Existing runtime baseline:
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/task_store.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/workflow.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/verification_runner.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/delivery_handoff.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/evidence.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/approval.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/workspace.py`
- Repo rules:
  - `AGENTS.md`

## Current Starting Point
- `Foundation / GAP-020` through `GAP-023` are complete and merged to `main`.
- The repo already has:
  - clarification policy contracts
  - repo/adapter compatibility helpers
  - live `build` and `doctor` gate commands
  - file-backed task persistence primitives
  - workflow transition helpers
  - evidence completeness and control-health helpers
- The repo still lacks:
  - a real execution worker
  - managed runtime workspaces tied to stored task runs
  - an artifact store and replay persistence
  - an operational quick/full verification runner over executed runs
  - a stable operator-facing runtime status or task query surface

## Full Runtime Boundaries

### Always do
- Preserve gate order `build -> test -> contract/invariant -> hotspot`.
- Keep the first Full Runtime slice single-machine and local-first.
- Reuse Foundation contracts as the domain boundary; extend them with runtime orchestration rather than parallel ad hoc objects.
- Persist runtime outputs as repo-local artifacts with stable task/run identifiers.
- Add runtime tests for every new orchestration component and every new persisted artifact shape.
- Record each completed slice in `docs/change-evidence/`.

### Ask first
- Introducing a network service boundary that cannot run locally on one machine.
- Introducing non-stdlib Python dependencies.
- Introducing a database, queue, or object store that replaces the current file-backed persistence in this stage.
- Expanding into public release packaging, deployment automation, or multi-tenant design.

### Never do
- Do not bypass approval, rollback, or evidence semantics just to get a worker running.
- Do not let the operator surface become an IDE replacement.
- Do not make replay depend on raw transcripts alone.
- Do not split runtime truth across multiple incompatible local stores.

## Planned File Structure

### Create
- `packages/contracts/src/governed_ai_coding_runtime_contracts/execution_runtime.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/worker.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/artifact_store.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/replay.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/runtime_status.py`
- `docs/specs/runtime-operator-surface-spec.md`
- `schemas/jsonschema/runtime-operator-surface.schema.json`
- `scripts/run-governed-task.py`
- `tests/runtime/test_execution_runtime.py`
- `tests/runtime/test_worker.py`
- `tests/runtime/test_artifact_store.py`
- `tests/runtime/test_replay.py`
- `tests/runtime/test_runtime_status.py`
- `docs/change-evidence/<date>-full-runtime-execution-plan.md`

### Modify
- `docs/plans/README.md`
- `docs/README.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- `docs/specs/task-lifecycle-and-state-machine-spec.md`
- `docs/specs/evidence-bundle-spec.md`
- `docs/specs/runtime-operator-surface-spec.md`
- `docs/specs/verification-gates-spec.md`
- `docs/specs/repo-profile-spec.md`
- `docs/specs/agent-adapter-contract-spec.md`
- `schemas/jsonschema/task-lifecycle.schema.json`
- `schemas/jsonschema/evidence-bundle.schema.json`
- `schemas/jsonschema/runtime-operator-surface.schema.json`
- `schemas/jsonschema/verification-gates.schema.json`
- `schemas/jsonschema/repo-profile.schema.json`
- `schemas/jsonschema/agent-adapter-contract.schema.json`
- `schemas/catalog/schema-catalog.yaml`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/task_store.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/workflow.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/verification_runner.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/delivery_handoff.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/evidence.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/workspace.py`
- `scripts/build-runtime.ps1`
- `scripts/doctor-runtime.ps1`
- `scripts/verify-repo.ps1`
- `README.md`
- `README.zh-CN.md`
- `README.en.md`

## Task List

### Task 0: Advance The Planning Baseline From Foundation To Full Runtime

**Files:**
- Modify: `docs/plans/README.md`
- Modify: `docs/README.md`
- Modify: `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- Modify: `docs/backlog/issue-ready-backlog.md`
- Evidence: `docs/change-evidence/<date>-full-runtime-execution-plan.md`

**Purpose:** Make the active next-step queue explicit and point execution at a dedicated Full Runtime plan instead of the completed Foundation plan.

**Acceptance criteria:**
- Active docs say `Foundation` is complete and `Full Runtime / GAP-024` is the current queue.
- `docs/plans/` exposes this plan as the active execution checklist.
- Evidence links the Foundation closeout to the Full Runtime start.

**Steps:**
- [ ] Record the completed Foundation closeout as the prior stage input rather than the active plan.
- [ ] Add this plan to `docs/plans/README.md` as the current authoritative execution plan.
- [ ] Update docs indexes so the next executable queue clearly starts at `GAP-024`.
- [ ] Create or update evidence that records the transition from Foundation closeout to Full Runtime execution.

### Task 1: Land GAP-024 Execution Worker And Managed Workspace Runtime

**Files:**
- Create: `packages/contracts/src/governed_ai_coding_runtime_contracts/execution_runtime.py`
- Create: `packages/contracts/src/governed_ai_coding_runtime_contracts/worker.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/task_store.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/workflow.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/workspace.py`
- Test: `tests/runtime/test_execution_runtime.py`
- Test: `tests/runtime/test_worker.py`

**Purpose:** Turn stored task state into a real local execution path with lifecycle-bound workspaces and deterministic worker behavior.

**Acceptance criteria:**
- A stored task can be loaded, executed, and transitioned by a worker rather than only by isolated helpers.
- Workspaces are allocated per run and tied back to task/run metadata.
- Worker execution preserves approval and rollback references.

**Steps:**
- [ ] Extend task records with run metadata needed for execution, workspace ownership, and current attempt identity.
- [ ] Implement a runtime coordinator that loads a task, allocates a workspace, dispatches execution, and records transitions.
- [ ] Implement a local worker interface that can execute one governed run synchronously on one machine.
- [ ] Add tests for task-to-run initialization, workspace binding, interrupted execution, and illegal worker state transitions.
- [ ] Keep execution local and synchronous in this stage; do not introduce queue-backed worker dispatch.

### Task 2: Land GAP-025 Artifact Store, Evidence Persistence, And Replay Data

**Files:**
- Create: `packages/contracts/src/governed_ai_coding_runtime_contracts/artifact_store.py`
- Create: `packages/contracts/src/governed_ai_coding_runtime_contracts/replay.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/evidence.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/delivery_handoff.py`
- Modify: `docs/specs/evidence-bundle-spec.md`
- Modify: `schemas/jsonschema/evidence-bundle.schema.json`
- Test: `tests/runtime/test_artifact_store.py`
- Test: `tests/runtime/test_replay.py`

**Purpose:** Persist artifacts, replay references, and failure signatures outside transcript-only outputs.

**Acceptance criteria:**
- Executed runs write artifacts to a stable local store keyed by task/run identity.
- Evidence bundles can point to persisted artifacts and replay references.
- Failed runs leave replay-oriented metadata sufficient for diagnosis.

**Steps:**
- [ ] Define a local artifact directory layout and stable artifact reference shape.
- [ ] Implement artifact persistence helpers for command outputs, verification outputs, and handoff bundles.
- [ ] Implement replay reference generation with failure signatures and artifact links.
- [ ] Update evidence and delivery helpers to emit artifact-backed references instead of transcript-only fields.
- [ ] Add tests for artifact persistence, replay reference generation, and failure-path evidence completeness.

### Task 3: Land GAP-026 Operational Quick And Full Gate Runner

**Files:**
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/verification_runner.py`
- Modify: `scripts/verify-repo.ps1`
- Modify: `scripts/build-runtime.ps1`
- Modify: `scripts/doctor-runtime.ps1`
- Modify: `docs/specs/verification-gates-spec.md`
- Modify: `schemas/jsonschema/verification-gates.schema.json`
- Test: `tests/runtime/test_verification_runner.py`

**Purpose:** Run quick/full verification against real task executions and persist gate outputs as run artifacts.

**Acceptance criteria:**
- Quick/full plans can attach to executed task runs rather than only planning objects.
- Gate outputs are persisted and queryable through artifact references.
- Risky output classes can be surfaced in delivery state.

**Steps:**
- [ ] Extend verification planning to bind gate runs to task/run identifiers.
- [ ] Persist build/test/contract/hotspot results as artifact-backed verification records.
- [ ] Add risky artifact classification for dependency, CI, release-adjacent, or other operator-relevant outputs.
- [ ] Update tests to cover quick/full execution paths, artifact persistence, and classification behavior.
- [ ] Keep gate execution local and repo-scoped; distributed runners belong to later stages.

### Task 4: Land GAP-027 Minimal Operator Surface (CLI-First)

**Files:**
- Create: `packages/contracts/src/governed_ai_coding_runtime_contracts/runtime_status.py`
- Create: `docs/specs/runtime-operator-surface-spec.md`
- Create: `schemas/jsonschema/runtime-operator-surface.schema.json`
- Create: `scripts/run-governed-task.py`
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `README.en.md`
- Modify: `docs/README.md`
- Test: `tests/runtime/test_runtime_status.py`

**Purpose:** Expose a thin operator-facing control surface for task list, task status, approvals, evidence references, and replay references without committing this stage to a web UI shell.

**Acceptance criteria:**
- Operators can inspect current and recent tasks from a stable local surface.
- The surface can show approvals, verification state, evidence links, and replay links without raw log digging.
- The surface stays control-plane focused and local-first.
- The runtime status/read model is explicit enough to back a later UI without changing task or artifact semantics.

**Steps:**
- [ ] Define a runtime status/read model that projects task, run, approval, verification, and artifact state from persisted records.
- [ ] Add a spec/schema pair for the operator surface read model so future UI work builds on stable runtime-facing structures.
- [ ] Add a minimal CLI entrypoint that can create a task, run it, and print operator-oriented status.
- [ ] Document the operator path in root/docs entry files.
- [ ] Add tests for task query output, empty-state handling, and replay/evidence visibility.
- [ ] Keep the first surface CLI-based; explicitly defer a richer UI shell to `Public Usable Release` after the read model stabilizes.

### Task 5: Land GAP-028 Runtime Health, Status Query Surface, And Full Runtime Handoff

**Files:**
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/runtime_status.py`
- Modify: `scripts/doctor-runtime.ps1`
- Modify: `scripts/verify-repo.ps1`
- Modify: `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- Modify: `docs/backlog/issue-ready-backlog.md`
- Modify: `docs/change-evidence/<date>-full-runtime-execution-plan.md`
- Optional modify: `docs/reviews/<date>-full-runtime-review.md`

**Purpose:** Close the first Full Runtime execution slice with real runtime status signals and a clear handoff into later release work.

**Acceptance criteria:**
- One real governed task can run end-to-end on one machine with execution, verification, evidence, and replay.
- `doctor` can report runtime readiness using real runtime state, not only repository prerequisites.
- Active docs reflect whether `Full Runtime` is complete or which short remainder list is still open.

**Steps:**
- [ ] Extend doctor/status checks to include runtime data locations, recent run visibility, and worker readiness.
- [ ] Run one real governed task through the runtime path and persist its artifacts.
- [ ] Run `build`, `test`, `contract/invariant`, and `hotspot` against the Full Runtime implementation.
- [ ] Update evidence with exact commands, exit codes, artifact locations, residual risks, and rollback notes.
- [ ] Move the active next-step queue only after the end-to-end runtime path is verified.

## Checkpoints

### Checkpoint A: After Task 0
- The active next-step queue points to `Full Runtime / GAP-024`.
- `docs/plans/` exposes a dedicated Full Runtime execution plan.

### Checkpoint B: After Task 1
- Stored task state can drive a real local execution worker.
- Workspaces are lifecycle-bound and linked to runs.

### Checkpoint C: After Tasks 2-3
- Artifacts and replay references persist outside transcripts.
- Quick/full verification attaches to real executed runs.

### Checkpoint D: After Tasks 4-5
- Operators can inspect runtime state through a thin local surface.
- One real governed task can run end-to-end with execution, verification, evidence, and replay.

## Risks And Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Worker execution bypasses governance semantics | High | Reuse approval, rollback, evidence, and verification helpers instead of inventing a parallel runtime path. |
| Artifact persistence fragments across ad hoc directories | High | Define one repo-owned artifact layout keyed by task/run id before persisting anything. |
| The first operator surface expands into a half-built UI stack | Medium | Keep the first surface CLI/read-model based; add web UI only when the read model is stable. |
| Replay references stay too weak for real diagnosis | High | Persist failure signatures, artifact refs, and verification refs together in the same runtime store. |
| Full Runtime drifts into packaging or deployment work too early | Medium | Keep release/quickstart concerns explicitly in `Public Usable Release`. |

## Completion Definition
Full Runtime is complete when:
- a stored task can be executed by a real local worker
- workspaces and runs are lifecycle-bound and queryable
- artifacts and replay metadata persist outside transcripts
- quick/full verification runs against real task executions
- an operator can inspect task, approval, evidence, replay, and runtime health state from a stable local surface
- one governed task can run end-to-end on one machine with approval, verification, evidence, and replay
