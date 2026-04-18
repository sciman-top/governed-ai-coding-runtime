# Public Usable Release Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Execute `GAP-029` through `GAP-032` so the existing Full Runtime can be cloned, bootstrapped, run, inspected, packaged, and explained by someone other than the author on one machine.

**Architecture:** Build on the landed local runtime instead of replacing it. Keep the release slice single-machine and file-backed: add a documented bootstrap path, one richer local operator surface on top of the existing read model, sample/demo profiles that exercise the full path, packaging metadata for local distribution, and explicit adapter compatibility or degrade behavior.

**Tech Stack:** Python 3.x standard library, `packages/contracts/` domain models, local filesystem persistence under `.runtime/`, PowerShell entrypoints under `scripts/`, Markdown docs under `docs/`, JSON Schema under `schemas/jsonschema/`.

---

## Source Inputs
- `docs/backlog/issue-ready-backlog.md`
- `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- `docs/change-evidence/20260418-full-runtime-execution-plan.md`
- `scripts/run-governed-task.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/runtime_status.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_profile.py`

## Planned File Structure

### Create
- `docs/quickstart/single-machine-runtime-quickstart.md`
- `docs/product/public-usable-release-criteria.md`
- `docs/product/adapter-degrade-policy.md`
- `docs/change-evidence/20260418-public-usable-release-execution-plan.md`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py`
- `scripts/serve-operator-ui.py`
- `scripts/bootstrap-runtime.ps1`
- `scripts/package-runtime.ps1`
- `schemas/examples/repo-profile/governed-ai-coding-runtime.example.json`
- `schemas/examples/runtime-operator-surface/status-snapshot.example.json`
- `tests/runtime/test_operator_ui.py`
- `tests/runtime/test_bootstrap_runtime.py`
- `tests/runtime/test_package_runtime.py`

### Modify
- `README.md`
- `README.zh-CN.md`
- `README.en.md`
- `docs/README.md`
- `docs/backlog/README.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/full-lifecycle-backlog-seeds.md`
- `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- `docs/plans/README.md`
- `packages/contracts/README.md`
- `tests/README.md`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/runtime_status.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_profile.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/compatibility.py`
- `scripts/doctor-runtime.ps1`
- `scripts/verify-repo.ps1`
- `schemas/jsonschema/repo-profile.schema.json`
- `schemas/jsonschema/runtime-operator-surface.schema.json`
- `schemas/catalog/schema-catalog.yaml`

## Task List

### Task 1: Land GAP-029 Single-Machine Deployment And Quickstart

**Files:**
- Create: `scripts/bootstrap-runtime.ps1`
- Create: `docs/quickstart/single-machine-runtime-quickstart.md`
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `README.en.md`
- Modify: `docs/README.md`
- Test: `tests/runtime/test_bootstrap_runtime.py`

**Purpose:** Give a new user one documented local bootstrap path that creates required runtime directories, validates prerequisites, and points them at the first successful governed run.

**Steps:**
- [ ] Add a failing bootstrap smoke test that expects a script entrypoint and successful status output.
- [ ] Implement `scripts/bootstrap-runtime.ps1` to create `.runtime/tasks`, `.runtime/artifacts`, `.runtime/replay`, validate `python` and `pwsh`, and call `scripts/run-governed-task.py status --json`.
- [ ] Add a quickstart doc that covers bootstrap, create/run/status, artifact inspection, and rollback cleanup.
- [ ] Update root/docs entry files to point to the quickstart as the active operator path.
- [ ] Run the new bootstrap test and existing doctor/status checks.

### Task 2: Land GAP-029/030 Richer Local Operator Surface And Demo Profile

**Files:**
- Create: `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py`
- Create: `scripts/serve-operator-ui.py`
- Create: `schemas/examples/repo-profile/governed-ai-coding-runtime.example.json`
- Create: `schemas/examples/runtime-operator-surface/status-snapshot.example.json`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/runtime_status.py`
- Modify: `schemas/jsonschema/repo-profile.schema.json`
- Modify: `schemas/jsonschema/runtime-operator-surface.schema.json`
- Modify: `schemas/catalog/schema-catalog.yaml`
- Test: `tests/runtime/test_operator_ui.py`

**Purpose:** Add a richer local operator surface than plain CLI output and ship at least one sample repo profile and status snapshot that exercises the documented runtime path.

**Steps:**
- [ ] Add failing tests for HTML operator rendering and empty/non-empty runtime snapshots.
- [ ] Implement `operator_ui.py` to turn runtime snapshots into a local standalone HTML page.
- [ ] Implement `scripts/serve-operator-ui.py` to write the HTML artifact and print the local file path.
- [ ] Add a governed-ai-coding-runtime sample repo profile that points at this repo’s bootstrap and gate entrypoints.
- [ ] Add a runtime-operator-surface example JSON snapshot and keep schema/catalog pairings valid.
- [ ] Run operator UI tests plus contract validation.

### Task 3: Land GAP-030/031 End-To-End Demo Flow, Packaging, And Release Criteria

**Files:**
- Create: `scripts/package-runtime.ps1`
- Create: `docs/product/public-usable-release-criteria.md`
- Modify: `packages/contracts/README.md`
- Modify: `tests/README.md`
- Modify: `docs/backlog/issue-ready-backlog.md`
- Modify: `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- Test: `tests/runtime/test_package_runtime.py`

**Purpose:** Make the runtime distributable as a local artifact bundle and define what “public usable release” means in concrete, testable terms.

**Steps:**
- [ ] Add a failing packaging test that expects a package script and a generated local distribution directory.
- [ ] Implement `scripts/package-runtime.ps1` to assemble docs, scripts, schemas, package sources, and sample profiles into `.runtime/dist/public-usable-release/`.
- [ ] Write release criteria covering bootstrap, task run, verification, evidence inspection, operator UI, and demo profile usage.
- [ ] Update package/test docs to describe the packaged layout and how it maps to the quickstart.
- [ ] Run packaging tests and one real package build.

### Task 4: Land GAP-032 Adapter Baseline And Explicit Degrade Behavior

**Files:**
- Create: `docs/product/adapter-degrade-policy.md`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/compatibility.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_profile.py`
- Modify: `scripts/doctor-runtime.ps1`
- Modify: `scripts/verify-repo.ps1`
- Modify: `docs/backlog/README.md`
- Modify: `docs/plans/README.md`

**Purpose:** Make Codex-first compatibility explicit, define honest fallback/degrade behavior, and surface that posture through docs and runtime verification.

**Steps:**
- [ ] Add a failing compatibility test for unsupported or partial adapter capability behavior.
- [ ] Extend compatibility helpers so adapter posture can resolve to `enforced`, `advisory`, `observe`, or fail-closed with an explicit reason.
- [ ] Document the adapter degrade policy and reference it from entry docs.
- [ ] Extend doctor/verify output to report adapter posture visibility in addition to runtime readiness.
- [ ] Update planning docs so `Public Usable Release` is complete only after the packaging/demo/degrade path is verified.

### Task 5: Close Public Usable Release With Evidence

**Files:**
- Create: `docs/change-evidence/20260418-public-usable-release-execution-plan.md`
- Modify: `docs/backlog/issue-ready-backlog.md`
- Modify: `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- Modify: `docs/README.md`

**Purpose:** Record exact commands, artifacts, risks, and rollback notes after the public usable release slice passes all gates.

**Steps:**
- [ ] Run bootstrap, quickstart, operator UI, package, and one demo governed task end to end.
- [ ] Run `build -> test -> contract/invariant -> hotspot`.
- [ ] Record exact commands, exit codes, artifact locations, residual risks, and rollback notes.
- [ ] Mark `GAP-029` through `GAP-032` complete only after verification passes.

## Checkpoints
- After Task 1: a new user can bootstrap and query runtime status locally.
- After Task 2: a richer local operator surface and sample/demo profile exist.
- After Task 3: a local release bundle and explicit release criteria exist.
- After Task 4: adapter posture and degrade behavior are explicit and visible.
- After Task 5: docs and evidence agree on whether `Public Usable Release` is complete.
