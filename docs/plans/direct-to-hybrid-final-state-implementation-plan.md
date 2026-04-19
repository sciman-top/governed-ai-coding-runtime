# Direct-To-Hybrid Final-State Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the current hybrid-baseline productization slice into a complete hybrid final state with runtime-owned governed execution, at least one live host adapter path, real attached multi-repo onboarding, machine-local durable state by default, and service-shaped runtime boundaries.

**Architecture:** Preserve the current docs-first, contracts-first kernel as the source of truth and extend it in dependency order. Close the governed execution surface first, then close live adapter reality, then make multi-repo and machine-local sidecar reality honest, then extract service-shaped runtime boundaries, and only then harden operator, CI, and remediation surfaces. Keep target repositories light, runtime state machine-local, and all execution, approval, evidence, replay, rollback, and handoff flows on one contract model.

**Tech Stack:** Current baseline: Python 3.x standard library, `packages/contracts/`, filesystem-backed `.runtime/`, PowerShell verification entrypoints, Markdown, JSON Schema draft 2020-12. Transition stack: Python 3.12+, FastAPI, Pydantic v2, PostgreSQL, object-store abstraction, OpenTelemetry. Deferred north-star hardening only after transition slices are real: Temporal, Redis, pgvector, OPA/Rego, `apps/console-web/` promotion.

---

## Status

- This is the canonical future-facing implementation plan for the repository.
- It complements:
  - `docs/architecture/hybrid-final-state-master-outline.md`
  - `docs/roadmap/direct-to-hybrid-final-state-roadmap.md`
  - the future backlog and issue-seed sync
- `docs/plans/interactive-session-productization-implementation-plan.md` remains important execution history, but it is no longer the future mainline for complete hybrid final-state closure.
- This plan intentionally converts the executable gap audit into ordered work batches instead of reusing older `GAP-035` through `GAP-044` labels as the only future planning lens.

## Current Baseline

- The repository has already landed:
  - repo attachment binding and light-pack generation or validation
  - attachment-aware verification execution
  - first attached write governance and execution loop
  - session-bridge write, approval, status, evidence, and handoff command surface plus local CLI entrypoint
  - Codex adapter posture plus smoke-trial evidence wiring
  - profile-based multi-repo trial model
  - `PolicyDecision` contract and same-contract verifier boundary
- The repository still does not satisfy the complete hybrid final state because:
  - `HFG-001` through `HFG-007` remain blocking gaps
  - `HFG-H1` through `HFG-H3` remain hardening gaps
- Phase 0 planning closeout is complete on the current branch baseline:
  - master outline exists
  - direct roadmap exists
  - this implementation plan exists as the future-facing mainline
  - plans index, backlog, issue seeds, and the GitHub seeding script are aligned and validated against the direct-to-final-state queue

## Source Inputs

- `docs/architecture/hybrid-final-state-master-outline.md`
- `docs/roadmap/direct-to-hybrid-final-state-roadmap.md`
- `docs/reviews/2026-04-19-hybrid-final-state-executable-gap-audit.md`
- `docs/architecture/local-baseline-to-hybrid-final-state-migration-matrix.md`
- `docs/plans/interactive-session-productization-implementation-plan.md`
- `docs/plans/governance-runtime-strategy-alignment-plan.md`
- `docs/architecture/governed-ai-coding-runtime-target-architecture.md`
- `docs/prd/governed-ai-coding-runtime-prd.md`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/`
- `scripts/`
- `tests/runtime/`

## Dependency Graph

```text
Phase 0 planning closeout
  -> Phase 1 governed execution surface
       -> Phase 2 live host adapter reality
            -> Phase 3 real multi-repo and machine-local sidecar reality
                 -> Phase 4 service-shaped runtime extraction
                      -> Phase 5 hardening and operational completion

Phase 1
  HFG-001 runtime-owned attached write chain
  HFG-002 session bridge execution surface
  HFG-006 governed execution coverage

Phase 2
  HFG-003 live Codex attach and event ingestion
  HFG-005 executable adapter registry

Phase 3
  HFG-004 real attached multi-repo trial loop
  HFG-007 machine-local state and workspace default

Phase 5
  HFG-H1 operator or control-plane query surface
  HFG-H2 same-contract runtime reader parity
  HFG-H3 remediation-capable doctor posture
```

## Planned File Structure

### Reuse As-Is Or Extend

- `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/attached_write_governance.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/attached_write_execution.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/codex_adapter.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/adapter_registry.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/multi_repo_trial.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/runtime_status.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/verification_runner.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/workspace.py`
- `scripts/run-governed-task.py`
- `scripts/session-bridge.py`
- `scripts/run-codex-adapter-trial.py`
- `scripts/run-multi-repo-trial.py`
- `tests/runtime/`

### Planned Create During Transition Phases

- `packages/contracts/src/governed_ai_coding_runtime_contracts/runtime_roots.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_queries.py`
- `packages/agent-runtime/service_facade.py`
- `packages/agent-runtime/persistence.py`
- `packages/agent-runtime/artifact_store.py`
- `packages/observability/runtime_tracing.py`
- `apps/control-plane/app.py`
- `apps/control-plane/main.py`
- `apps/control-plane/routes/session.py`
- `apps/control-plane/routes/operator.py`
- `apps/workflow-worker/main.py`
- `apps/agent-worker/main.py`
- `apps/tool-runner/main.py`
- `infra/local-runtime/docker-compose.yml`
- `infra/local-runtime/postgres/init.sql`
- `tests/runtime/test_runtime_roots.py`
- `tests/runtime/test_operator_queries.py`
- `tests/service/test_session_api.py`
- `tests/service/test_operator_api.py`

## Task List

**Cross-task evidence rule:**
- Any task that modifies planning docs, specs, schemas, or scripts must add one new `docs/change-evidence/<date>-<slug>.md` entry that records commands, key outputs, risks, and rollback notes.

### Task 0: Close Phase 0 Planning Sync

**Purpose:** Finish the planning baseline so future work executes against one canonical implementation plan instead of drifting between older historical plans.

**Status:** Complete on the current branch baseline via the `2026-04-19` planning and seeding rebaseline closeout.

**Files:**
- Modify: `docs/plans/README.md`
- Modify: `docs/backlog/issue-ready-backlog.md`
- Modify: `docs/backlog/issue-seeds.yaml`
- Modify: `scripts/github/create-roadmap-issues.ps1`
- Create: `docs/change-evidence/<date>-phase-0-planning-sync.md`

**Acceptance criteria:**
- [x] `docs/plans/README.md` marks this file as the future-facing implementation mainline.
- [x] Backlog items are grouped by `Phase 0` through `Phase 5` rather than only by historical productization labels.
- [x] Issue seeds can render the direct-to-final-state work without colliding with historical ids.
- [x] Historical plans remain linked as execution history, not active future mainline.

**Verification:**
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`.

**Dependencies:** None.

**Estimated scope:** Small.

### Task 1: Close Remaining Session Bridge Execution Gaps

**Purpose:** Close the remaining semantic gap between the already-landed bridge command surface and a real live-host-ready governed execution bus.

**Files:**
- Modify: `docs/specs/session-bridge-command-spec.md`
- Modify: `schemas/jsonschema/session-bridge-command.schema.json`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
- Modify: `scripts/session-bridge.py`
- Modify: `tests/runtime/test_session_bridge.py`
- Modify: `docs/product/session-bridge-commands.md`

**Acceptance criteria:**
- [x] Existing session bridge commands stay aligned while `run_quick_gate` and `run_full_gate` move from plan-only output to runtime-managed execution lifecycle.
- [x] Execution-like commands return stable execution ids and continuation ids across gate, write, approval, evidence, and handoff paths.
- [x] Unsupported capabilities still degrade explicitly instead of pretending execution happened.
- [x] Schema, product doc, Python contract, and CLI stay aligned.

**Verification:**
- [x] Run `python -m unittest tests.runtime.test_session_bridge -v`.
- [x] Run `python scripts/session-bridge.py --help`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`.

**Dependencies:** Task 0.

**Estimated scope:** Medium.

### Task 2: Bind Live Session Identity Into The Attached Write Flow

**Purpose:** Promote the already-landed bridge-backed attached write flow from local runtime ownership to live-session-bound runtime ownership.

**Files:**
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/attached_write_governance.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/attached_write_execution.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
- Modify: `scripts/run-governed-task.py`
- Modify: `tests/runtime/test_attached_write_governance.py`
- Modify: `tests/runtime/test_attached_write_execution.py`
- Modify: `tests/runtime/test_session_bridge.py`
- Modify: `docs/product/write-side-tool-governance.md`

**Acceptance criteria:**
- [x] The existing write request, approval, resume, and execute flow remains driven through the bridge.
- [x] Every attached write execution binds task id, adapter or session identity, approval ref, artifact refs, handoff ref, and replay ref.
- [x] Existing CLI paths become wrappers around the same runtime-owned write flow instead of parallel logic.
- [x] High-risk writes fail closed when approval state is absent or stale.

**Verification:**
- [x] Run `python -m unittest tests.runtime.test_attached_write_governance tests.runtime.test_attached_write_execution tests.runtime.test_session_bridge -v`.
- [x] Run `python scripts/session-bridge.py request-gate --help`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`.

**Dependencies:** Task 1.

**Estimated scope:** Medium.

### Task 3: Extend Governed Execution Coverage Beyond File Writes

**Purpose:** Close the current execution-surface gap so shell, git, and selected package-manager actions follow the same approval and evidence model as file writes.

**Files:**
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/tool_runner.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/write_tool_runner.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
- Modify: `scripts/run-governed-task.py`
- Modify: `tests/runtime/test_write_tool_runner.py`
- Create: `tests/runtime/test_tool_runner_governance.py`
- Modify: `docs/product/write-side-tool-governance.md`
- Modify: `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`

**Acceptance criteria:**
- [x] `shell`, `git`, and at least one package-manager dry-run path have explicit risk-tier mapping.
- [x] Allow, escalate, and deny paths all emit consistent evidence and rollback metadata.
- [x] `git status`, `git diff`, and one dependency dry-run path are covered by tests.
- [x] The execution surface remains explicitly bounded and does not silently broaden to arbitrary commands.

**Verification:**
- [x] Run `python -m unittest tests.runtime.test_write_tool_runner tests.runtime.test_tool_runner_governance -v`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`.

**Dependencies:** Task 2.

**Estimated scope:** Medium.

### Task 4: Add An Attached-Repo End-To-End Governed Execution Slice

**Purpose:** Prove one real attached repository can complete the governed loop end-to-end instead of only contract or smoke-level slices.

**Files:**
- Modify: `scripts/runtime-check.ps1`
- Modify: `scripts/runtime-flow.ps1`
- Modify: `scripts/runtime-flow-preset.ps1`
- Modify: `tests/runtime/test_run_governed_task_cli.py`
- Create: `tests/runtime/test_attached_repo_e2e.py`
- Modify: `docs/quickstart/use-with-existing-repo.md`
- Modify: `docs/quickstart/use-with-existing-repo.zh-CN.md`
- Create: `docs/change-evidence/<date>-attached-repo-e2e-execution.md`

**Acceptance criteria:**
- [x] One attached repo can execute `attach -> request medium write -> approve -> execute -> verify -> handoff -> replay`.
- [x] E2E output uses the same task model as local runtime flows.
- [x] Documentation explicitly states what is real versus what is still smoke or fallback.
- [x] Evidence captures the actual command sequence and resulting refs.

**Verification:**
- [x] Run `python -m unittest tests.runtime.test_attached_repo_e2e tests.runtime.test_run_governed_task_cli -v`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-check.ps1`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`.

**Dependencies:** Task 3.

**Estimated scope:** Medium.

### Task 5: Implement Live Codex Handshake And Continuation Identity

**Purpose:** Move the direct Codex adapter from posture and smoke-trial to a real live-session boundary.

**Files:**
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/codex_adapter.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/adapter_registry.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
- Modify: `tests/runtime/test_codex_adapter.py`
- Modify: `tests/runtime/test_adapter_registry.py`
- Modify: `docs/product/codex-direct-adapter.md`

**Acceptance criteria:**
- [x] The adapter can probe or handshake with a real Codex surface instead of relying only on manually declared flags.
- [x] Session id, resume id, and continuation identity are preserved in the runtime task model.
- [x] Adapter posture honestly records when live attach is unavailable.
- [x] The runtime can distinguish live attach, process bridge, and manual handoff for Codex.

**Verification:**
- [x] Run `python -m unittest tests.runtime.test_codex_adapter tests.runtime.test_adapter_registry -v`.
- [x] Run `python scripts/run-codex-adapter-trial.py --help`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`.

**Dependencies:** Task 4.

**Estimated scope:** Medium.

### Task 6: Ingest Real Adapter Events And Export Runtime Evidence

**Purpose:** Replace deterministic placeholder refs with evidence sourced from the real adapter event stream.

**Files:**
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/codex_adapter.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/evidence.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/delivery_handoff.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
- Modify: `tests/runtime/test_codex_adapter.py`
- Modify: `tests/runtime/test_evidence_timeline.py`
- Modify: `tests/runtime/test_delivery_handoff.py`
- Modify: `docs/change-evidence/20260418-codex-session-evidence-mapping.md`

**Acceptance criteria:**
- [x] Tool calls, diff events, gate runs, approval interruptions, and handoff entries can be linked back to one runtime-owned task.
- [x] Live adapter events and manual-handoff evidence remain distinguishable.
- [x] Unsupported or partially supported events are recorded explicitly rather than dropped silently.
- [x] Delivery handoff and replay readers can consume the richer evidence shape.

**Verification:**
- [x] Run `python -m unittest tests.runtime.test_codex_adapter tests.runtime.test_evidence_timeline tests.runtime.test_delivery_handoff -v`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`.

**Dependencies:** Task 5.

**Estimated scope:** Medium.

### Task 7: Turn The Adapter Registry Into An Executable Runtime Registry

**Purpose:** Make adapter selection, discovery, and execution delegation real instead of projection-only.

**Files:**
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/adapter_registry.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/codex_adapter.py`
- Modify: `docs/specs/agent-adapter-contract-spec.md`
- Modify: `schemas/jsonschema/agent-adapter-contract.schema.json`
- Modify: `tests/runtime/test_adapter_registry.py`
- Modify: `docs/product/adapter-capability-tiers.md`
- Modify: `docs/product/adapter-degrade-policy.md`

**Acceptance criteria:**
- [x] Registry supports registration, discovery, probing, selection, and delegation for `native_attach`, `process_bridge`, and `manual_handoff`.
- [x] Runtime selection is based on attached repo plus detected host capability, not only on static profile projection.
- [x] Codex and at least one non-Codex fixture share the same registry interface.
- [x] Degrade behavior is part of the runtime interface rather than only documentation.

**Verification:**
- [x] Run `python -m unittest tests.runtime.test_adapter_registry tests.runtime.test_codex_adapter -v`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`.

**Dependencies:** Task 6.

**Estimated scope:** Medium.

### Task 8: Convert Multi-Repo Trial From Profile Summary To Attached-Repo Loop

**Purpose:** Make onboarding evidence come from real attached repositories rather than only synthetic profiles.

**Files:**
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/multi_repo_trial.py`
- Modify: `scripts/run-multi-repo-trial.py`
- Modify: `tests/runtime/test_multi_repo_trial.py`
- Modify: `docs/product/multi-repo-trial-loop.md`
- Modify: `docs/quickstart/multi-repo-trial-quickstart.md`
- Modify: `docs/quickstart/multi-repo-trial-quickstart.zh-CN.md`

**Acceptance criteria:**
- [x] Trial runner can accept attached repo roots or bindings instead of only repo profile paths.
- [x] Each repo executes `attach -> doctor or status -> request gate -> verify attachment -> optional write probe -> evidence aggregation`.
- [x] Trial outputs capture real gate failures, approval friction, replay quality, and follow-up actions.
- [x] At least two attached external repos can be run without kernel rewrites.

**Verification:**
- [x] Run `python -m unittest tests.runtime.test_multi_repo_trial -v`.
- [x] Run `python scripts/run-multi-repo-trial.py --help`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`.

**Dependencies:** Task 7.

**Estimated scope:** Medium.

### Task 9: Normalize Machine-Local Runtime Roots And Migration Paths

**Purpose:** Make machine-local runtime state the end-to-end default instead of an optional attached-flow detail.

**Files:**
- Create: `packages/contracts/src/governed_ai_coding_runtime_contracts/runtime_roots.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/workspace.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_attachment.py`
- Modify: `scripts/run-governed-task.py`
- Modify: `tests/runtime/test_run_governed_task_cli.py`
- Modify: `tests/runtime/test_repo_attachment.py`
- Create: `tests/runtime/test_runtime_roots.py`
- Modify: `docs/architecture/local-baseline-to-hybrid-final-state-migration-matrix.md`
- Modify: `docs/quickstart/single-machine-runtime-quickstart.md`
- Modify: `docs/quickstart/single-machine-runtime-quickstart.zh-CN.md`

**Acceptance criteria:**
- [x] `tasks`, `artifacts`, `replay`, and `workspaces` share one runtime-root configuration model.
- [x] Repo-root `.runtime/` defaults become compatibility mode, not the primary end-state posture.
- [x] Migration and rollback behavior are documented and testable.
- [x] Self-runtime and attached-runtime flows consume the same root-placement model.

**Verification:**
- [x] Run `python -m unittest tests.runtime.test_runtime_roots tests.runtime.test_run_governed_task_cli tests.runtime.test_repo_attachment -v`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`.

**Dependencies:** Task 8.

**Estimated scope:** Medium.

### Task 10: Extract A Service-Shaped Control And Session API Boundary

**Purpose:** Begin the transition from script-heavy harnesses to explicit runtime services without losing current contract parity.

**Files:**
- Create: `packages/agent-runtime/service_facade.py`
- Create: `packages/observability/runtime_tracing.py`
- Create: `apps/control-plane/app.py`
- Create: `apps/control-plane/main.py`
- Create: `apps/control-plane/routes/session.py`
- Create: `apps/control-plane/routes/operator.py`
- Create: `tests/service/test_session_api.py`
- Create: `tests/service/test_operator_api.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`

**Acceptance criteria:**
- [x] Session operations and operator reads are exposed through a service API boundary.
- [x] Existing CLI entrypoints become wrappers or clients, not the only control surface.
- [x] OpenTelemetry hooks exist at the new boundary even if full backend shipping is deferred.
- [x] Contract parity is preserved between CLI and API paths.

**Verification:**
- [x] Run `python -m unittest tests.service.test_session_api tests.service.test_operator_api -v`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`.

**Dependencies:** Task 9.

**Estimated scope:** Large.

### Task 11: Add Service-Shaped Persistence And Local Deployment Scaffold

**Purpose:** Make the service extraction runnable locally with durable metadata beyond filesystem-only in-memory assumptions.

**Files:**
- Create: `packages/agent-runtime/persistence.py`
- Create: `packages/agent-runtime/artifact_store.py`
- Create: `apps/workflow-worker/main.py`
- Create: `apps/agent-worker/main.py`
- Create: `apps/tool-runner/main.py`
- Create: `infra/local-runtime/docker-compose.yml`
- Create: `infra/local-runtime/postgres/init.sql`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/runtime_status.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/verification_runner.py`
- Modify: `tests/service/test_session_api.py`

**Acceptance criteria:**
- [x] Local service deployment can run a control plane plus worker boundary with durable metadata storage.
- [x] Filesystem artifact handling stays supported through an abstraction layer instead of being hardwired.
- [x] Current contract bundle and evidence model remain consumable after the persistence split.
- [x] Transition-stack dependencies are introduced only where the service boundary requires them.

**Verification:**
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`.

**Dependencies:** Task 10.

**Estimated scope:** Large.

### Task 12: Add Attachment-Scoped Operator Query Surfaces

**Purpose:** Close the operator or control-plane visibility gap for approvals, evidence, handoff, replay, and attachment posture.

**Files:**
- Create: `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_queries.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/runtime_status.py`
- Create: `tests/runtime/test_operator_queries.py`
- Modify: `tests/runtime/test_session_bridge.py`
- Modify: `docs/product/minimal-approval-evidence-console.zh-CN.md`
- Modify: `docs/product/minimal-approval-evidence-console.md`

**Acceptance criteria:**
- [x] Attachment-scoped queries can list approvals, evidence refs, handoff refs, replay refs, and posture summary for one task or binding.
- [x] `inspect_evidence` no longer degrades by default for the primary attached path.
- [x] Query results are stable enough to be reused by later service APIs and console surfaces.
- [x] Operator read surfaces remain read-only unless explicitly escalated elsewhere.

**Verification:**
- [x] Run `python -m unittest tests.runtime.test_operator_queries tests.runtime.test_session_bridge -v`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`.

**Dependencies:** Task 11.

**Estimated scope:** Medium.

### Task 13: Extend Same-Contract Parity To Runtime Readers And CI

**Purpose:** Prevent hidden drift where verifier inputs are updated but session, adapter, or operator readers still consume older shapes.

**Files:**
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/verification_runner.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/adapter_registry.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/runtime_status.py`
- Modify: `tests/runtime/test_verification_runner.py`
- Modify: `tests/runtime/test_session_bridge.py`
- Modify: `tests/runtime/test_runtime_status.py`
- Create: `tests/runtime/test_contract_reader_parity.py`
- Modify: `docs/change-evidence/20260418-local-ci-same-contract-verification.md`

**Acceptance criteria:**
- [x] Runtime readers fail loudly on missing or incompatible contract fields instead of silently defaulting.
- [x] CI coverage includes session bridge, adapter, and attachment reader paths.
- [x] Contract changes can be traced to every consuming runtime reader.
- [x] The repository can show parity beyond verifier-only scope.

**Verification:**
- [x] Run `python -m unittest tests.runtime.test_verification_runner tests.runtime.test_session_bridge tests.runtime.test_runtime_status tests.runtime.test_contract_reader_parity -v`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`.

**Dependencies:** Task 12.

**Estimated scope:** Medium.

### Task 14: Add Remediation-Capable Attachment Doctor Behavior

**Purpose:** Move doctor and posture handling from passive reporting to guided remediation and fail-closed enforcement where required.

**Files:**
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_attachment.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/runtime_status.py`
- Modify: `scripts/doctor-runtime.ps1`
- Modify: `tests/runtime/test_runtime_doctor.py`
- Modify: `tests/runtime/test_repo_attachment.py`
- Modify: `docs/product/target-repo-attachment-flow.md`
- Modify: `docs/change-evidence/20260418-attachment-posture-status-doctor.md`

**Acceptance criteria:**
- [x] Missing, invalid, and stale bindings each have an explicit remediation path.
- [x] Guided remediation can point to the exact command or document needed to recover.
- [x] Fail-closed posture is used when execution should not continue.
- [x] Remediation actions are evidence-backed and rollback-aware.

**Verification:**
- [x] Run `python -m unittest tests.runtime.test_runtime_doctor tests.runtime.test_repo_attachment -v`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`.

**Dependencies:** Task 13.

**Estimated scope:** Medium.

### Task 15: Close Out Hardening, Backlog Sync, And Final-State Claim Discipline

**Purpose:** Finish the final-state mainline with evidence, backlog truth, and explicit claim discipline so the repository does not overstate completion.

**Files:**
- Modify: `docs/backlog/issue-ready-backlog.md`
- Modify: `docs/backlog/issue-seeds.yaml`
- Modify: `scripts/github/create-roadmap-issues.ps1`
- Modify: `docs/roadmap/direct-to-hybrid-final-state-roadmap.md`
- Modify: `docs/architecture/hybrid-final-state-master-outline.md`
- Create: `docs/change-evidence/<date>-direct-to-hybrid-final-state-closeout.md`

**Acceptance criteria:**
- [x] Backlog and issue seeds reflect only verified completed work.
- [x] Roadmap and master outline update claim wording only when exit criteria are actually met.
- [x] Final evidence records commands, outputs, risks, open residuals, and rollback paths.
- [x] The repository can defend a complete hybrid final-state claim with executable evidence rather than narrative alone.

**Verification:**
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`.

**Dependencies:** Tasks 0 through 14.

**Estimated scope:** Small.

## Checkpoints

### Checkpoint A: After Tasks 0-4
- Phase 0 planning baseline is closed.
- Phase 1 governed execution surface is real for one attached repository.
- Session bridge is no longer blocked on plan-only gate handling for the primary path.
- Runtime-owned attached writes and governed shell or git slices are evidence-linked.

### Checkpoint B: After Tasks 5-7
- At least one Codex path is live enough to bind session identity and evidence.
- Adapter selection is executable runtime behavior instead of projection-only posture.
- Degrade and fallback behavior remain explicit and honest.

### Checkpoint C: After Tasks 8-9
- Real attached multi-repo trials exist.
- Machine-local runtime roots are the default posture.

### Checkpoint D: After Tasks 10-11
- Service-shaped control-plane and worker boundaries exist.
- Local deployment can run the extracted runtime stack without breaking contract parity.

### Checkpoint E: After Tasks 12-15
- Operator queries, runtime-reader parity, and remediation-capable doctor behavior are real.
- Final-state claims are backed by evidence, gates, and synced backlog truth.

## Risks And Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Session bridge becomes a second ad hoc runtime instead of the control surface | High | Make bridge the canonical execution bus and keep CLI paths as wrappers. |
| Live Codex integration overfits the runtime to one host | High | Force Codex through the generic registry and keep at least one non-Codex fixture path. |
| Service extraction happens before execution truth is stable | High | Do not start Tasks 10-11 before Tasks 1-9 close their acceptance criteria. |
| Machine-local root migration breaks current users | Medium | Keep repo-root compatibility mode plus migration and rollback coverage in Task 9. |
| Docs claim full final-state closure too early | High | Keep claim discipline in the roadmap, master outline, and Task 15 closeout evidence. |
| Transition-stack dependencies explode too early | Medium | Introduce FastAPI, PostgreSQL, and OpenTelemetry only when the service boundary requires them; keep Temporal and other north-star pieces deferred. |

## Completion Definition

The direct-to-hybrid-final-state implementation is complete only when all of the following are true:

- one attached repo can complete a governed medium or high-risk write loop through the runtime-owned session surface
- at least one live Codex path produces runtime-owned task, execution, evidence, and handoff linkage
- at least one non-Codex adapter path exists with honest capability guarantees
- two or more attached external repos can run the onboarding or trial loop without kernel rewrites
- machine-local runtime roots are the default posture for tasks, artifacts, replay, and workspaces
- operator or control-plane queries can inspect attachment-scoped approvals, evidence, handoff, replay, and posture
- runtime readers, CI, and verifier surfaces consume the same declared contract model
- doctor can report and remediate attachment posture problems
- the runtime can run through service-shaped boundaries without losing contract parity
- roadmap, master outline, backlog, issue seeds, evidence, and gate results all agree on what is complete
