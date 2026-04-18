# Maintenance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Execute `GAP-033` through `GAP-034` so the complete single-machine governed runtime has explicit compatibility, upgrade, maintenance, deprecation, and retirement rules that stay visible through docs, runtime read models, and doctor checks.

**Architecture:** Keep the maintenance slice lightweight and local-first. Treat maintenance policy as product metadata, not a new service: land authoritative policy docs, project them into the existing runtime status surface and operator UI, and fail doctor checks if the maintenance policy surface disappears.

**Tech Stack:** Python 3.x standard library, `packages/contracts/` read models, PowerShell gate scripts under `scripts/`, Markdown policy docs under `docs/product/`, runtime examples under `schemas/examples/`, JSON Schema under `schemas/jsonschema/`.

---

## Source Inputs
- `docs/backlog/issue-ready-backlog.md`
- `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- `docs/change-evidence/20260418-public-usable-release-execution-plan.md`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/runtime_status.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py`
- `scripts/doctor-runtime.ps1`

## Planned File Structure

### Create
- `docs/plans/maintenance-implementation-plan.md`
- `docs/product/runtime-compatibility-and-upgrade-policy.md`
- `docs/product/maintenance-deprecation-and-retirement-policy.md`
- `docs/change-evidence/20260418-maintenance-execution-plan.md`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/maintenance_policy.py`
- `tests/runtime/test_maintenance_policy.py`

### Modify
- `README.md`
- `README.zh-CN.md`
- `README.en.md`
- `docs/README.md`
- `docs/backlog/README.md`
- `docs/backlog/full-lifecycle-backlog-seeds.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- `docs/plans/README.md`
- `docs/specs/runtime-operator-surface-spec.md`
- `packages/contracts/README.md`
- `tests/README.md`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/runtime_status.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py`
- `schemas/jsonschema/runtime-operator-surface.schema.json`
- `schemas/examples/runtime-operator-surface/status-snapshot.example.json`
- `schemas/catalog/schema-catalog.yaml`
- `scripts/run-governed-task.py`
- `scripts/serve-operator-ui.py`
- `scripts/doctor-runtime.ps1`
- `scripts/github/create-roadmap-issues.ps1`
- `tests/runtime/test_runtime_status.py`
- `tests/runtime/test_operator_ui.py`
- `tests/runtime/test_package_runtime.py`

## Task List

### Task 1: Land GAP-033 Compatibility And Upgrade Policy

**Files:**
- Create: `docs/product/runtime-compatibility-and-upgrade-policy.md`
- Create: `packages/contracts/src/governed_ai_coding_runtime_contracts/maintenance_policy.py`
- Test: `tests/runtime/test_maintenance_policy.py`

**Purpose:** Make compatibility and upgrade expectations explicit for adapters, repo profiles, and persisted runtime state instead of leaving them implied by historical implementation.

**Steps:**
- [ ] Add a failing unit test for a maintenance policy read model that reports policy document refs and lifecycle stage.
- [ ] Write the compatibility and upgrade policy doc, covering compatibility classes, upgrade expectations, migration notes, and fail-closed behavior for breaking changes.
- [ ] Implement a small read model that surfaces the compatibility and upgrade policy into the runtime status layer.

### Task 2: Land GAP-034 Maintenance, Deprecation, And Retirement Policy

**Files:**
- Create: `docs/product/maintenance-deprecation-and-retirement-policy.md`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/runtime_status.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py`
- Modify: `scripts/run-governed-task.py`
- Modify: `scripts/serve-operator-ui.py`
- Test: `tests/runtime/test_runtime_status.py`
- Test: `tests/runtime/test_operator_ui.py`

**Purpose:** Keep maintenance policy visible in the live operator surface, not only in Markdown docs.

**Steps:**
- [ ] Extend the runtime snapshot with maintenance policy metadata and stable doc references.
- [ ] Show the maintenance surface in CLI status output and the local operator HTML page.
- [ ] Ensure empty-state and non-empty-state tests cover maintenance visibility.

### Task 3: Keep Runtime Contracts And Packaging In Sync

**Files:**
- Modify: `docs/specs/runtime-operator-surface-spec.md`
- Modify: `schemas/jsonschema/runtime-operator-surface.schema.json`
- Modify: `schemas/examples/runtime-operator-surface/status-snapshot.example.json`
- Modify: `schemas/catalog/schema-catalog.yaml`
- Modify: `tests/runtime/test_package_runtime.py`
- Modify: `packages/contracts/README.md`
- Modify: `tests/README.md`

**Purpose:** Preserve the docs/spec/schema/example/package contract now that maintenance metadata is part of the operator surface.

**Steps:**
- [ ] Update the operator-surface spec and schema with maintenance fields.
- [ ] Refresh the sample snapshot example.
- [ ] Ensure package smoke checks include the new policy docs.

### Task 4: Close Maintenance With Doctor, Planning Alignment, And Evidence

**Files:**
- Create: `docs/change-evidence/20260418-maintenance-execution-plan.md`
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `README.en.md`
- Modify: `docs/README.md`
- Modify: `docs/backlog/README.md`
- Modify: `docs/backlog/full-lifecycle-backlog-seeds.md`
- Modify: `docs/backlog/issue-ready-backlog.md`
- Modify: `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- Modify: `docs/plans/README.md`
- Modify: `scripts/doctor-runtime.ps1`
- Modify: `scripts/github/create-roadmap-issues.ps1`

**Purpose:** Mark the lifecycle complete only after maintenance policy is visible through runtime status and gates.

**Steps:**
- [ ] Extend doctor to fail if maintenance policy docs or runtime maintenance metadata are missing.
- [ ] Update roadmap/backlog/readmes/plan index so `GAP-033` and `GAP-034` become completed execution history.
- [ ] Run `build -> test -> contract/invariant -> hotspot`.
- [ ] Record commands, exit codes, artifact paths, risks, and rollback notes in evidence.

## Checkpoints
- After Task 1: compatibility and upgrade policy exists as a runtime-consumable read model.
- After Task 2: maintenance metadata is visible in CLI and operator UI.
- After Task 3: schema/example/package contract matches the new runtime surface.
- After Task 4: lifecycle docs and evidence agree that maintenance is complete.
