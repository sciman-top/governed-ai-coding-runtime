# Interactive Session Productization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement `GAP-035` through `GAP-039` so the landed local runtime becomes a generic, attach-first, interactive governed AI coding runtime for multiple target repositories and multiple AI coding tools.

**Architecture:** Keep the kernel machine-local and durable. The hybrid final state is repo-local contract bundle plus machine-local governance kernel plus attach-first host adapters plus same-contract verification and delivery. Put only declarative contract inputs in target repositories, expose governed actions through a session bridge, and route host-specific behavior through capability-tiered adapters. Strategy Alignment Gates `GAP-040` through `GAP-044` are complete on the current branch baseline and remain encoded as dependency gates around the light-pack shape, `PolicyDecision`, and local/CI verification inputs.

**Tech Stack:** Python 3.x standard library, `packages/contracts/` runtime contract primitives, filesystem-backed `.runtime/` state, PowerShell verification entrypoints, Markdown docs, JSON Schema draft 2020-12, and Codex CLI/App as the first direct adapter target.

---

## Current Baseline

- `GAP-024` through `GAP-034` are complete on the current branch baseline.
- `GAP-035` through `GAP-039` are the active productization implementation queue.
- `GAP-040` through `GAP-044` are complete on the current branch baseline and remain encoded as dependency gates for productization work:
  - `GAP-035` waits for `GAP-042`
  - `GAP-036` and `GAP-037` wait for `GAP-043`
  - `GAP-038` and `GAP-039` wait for `GAP-044`
- The older `docs/plans/interactive-session-productization-plan.md` records the planning realignment that created this queue. This file is the implementation plan for the queue itself.

## Source Inputs

- `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/issue-seeds.yaml`
- `docs/plans/governance-runtime-strategy-alignment-plan.md`
- `docs/architecture/repo-native-contract-bundle.md`
- `docs/architecture/local-baseline-to-hybrid-final-state-migration-matrix.md`
- `docs/architecture/generic-target-repo-attachment-blueprint.md`
- `docs/product/interaction-model.md`
- `docs/product/codex-cli-app-integration-guide.md`
- `docs/product/adapter-degrade-policy.md`
- `docs/product/delivery-handoff.md`
- `docs/specs/repo-profile-spec.md`
- `docs/specs/agent-adapter-contract-spec.md`
- `docs/specs/policy-decision-spec.md`
- `docs/specs/verification-gates-spec.md`
- `docs/specs/evidence-bundle-spec.md`
- `schemas/catalog/schema-catalog.yaml`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/`
- `tests/runtime/`

## Dependency Graph

```text
Strategy gates
  GAP-040 borrowing matrix
    -> GAP-041 source-of-truth ADR
      -> GAP-042 repo-native bundle architecture
        -> GAP-035 target-repo attachment
        -> GAP-044 same-contract verification
  GAP-042 repo-native bundle architecture
    -> GAP-043 PolicyDecision contract
      -> GAP-036 session bridge
      -> GAP-037 direct Codex adapter
  GAP-044 same-contract verification
    -> GAP-038 adapter framework
    -> GAP-039 multi-repo trial loop
```

## Planned File Structure

### Already Landed Dependency Surfaces

- `docs/architecture/repo-native-contract-bundle.md`
- `docs/specs/policy-decision-spec.md`
- `schemas/jsonschema/policy-decision.schema.json`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/policy_decision.py`
- `tests/runtime/test_policy_decision.py`

### Planned Create

- `docs/product/target-repo-attachment-flow.md`
- `docs/product/session-bridge-commands.md`
- `docs/product/codex-direct-adapter.md`
- `docs/product/adapter-capability-tiers.md`
- `docs/product/multi-repo-trial-loop.md`
- `schemas/jsonschema/repo-attachment-binding.schema.json`
- `schemas/jsonschema/session-bridge-command.schema.json`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_attachment.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/adapter_registry.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/codex_adapter.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/multi_repo_trial.py`
- `scripts/attach-target-repo.py`
- `scripts/session-bridge.py`
- `tests/runtime/test_repo_attachment.py`
- `tests/runtime/test_session_bridge.py`
- `tests/runtime/test_codex_adapter.py`
- `tests/runtime/test_adapter_registry.py`
- `tests/runtime/test_multi_repo_trial.py`

### Planned Modify

- `README.md`
- `README.zh-CN.md`
- `README.en.md`
- `docs/README.md`
- `docs/architecture/README.md`
- `docs/product/interaction-model.md`
- `docs/product/codex-cli-app-integration-guide.md`
- `docs/product/adapter-degrade-policy.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/issue-seeds.yaml`
- `docs/plans/README.md`
- `docs/change-evidence/README.md`
- `schemas/catalog/schema-catalog.yaml`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/__init__.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/write_tool_runner.py`
- `scripts/verify-repo.ps1`
- `scripts/doctor-runtime.ps1`
- `scripts/run-governed-task.py`
- `docs/product/write-side-tool-governance.md`
- `tests/runtime/test_write_tool_runner.py`

## Task List

### Task 0: Confirm Strategy Gate Inputs Are Ready

**Purpose:** Prevent productization from hardening around unstable bundle, policy, or verification boundaries.

**Files:**
- Read: `docs/research/runtime-governance-borrowing-matrix.md`
- Read: `docs/adrs/0007-source-of-truth-and-runtime-contract-bundle.md`
- Read: `docs/architecture/repo-native-contract-bundle.md`
- Read: `docs/specs/policy-decision-spec.md`
- Read: `docs/specs/verification-gates-spec.md`
- Modify if needed: `docs/change-evidence/<date>-interactive-session-productization-implementation.md`

**Acceptance criteria:**
- [ ] `GAP-040`, `GAP-041`, and `GAP-042` are complete before implementing `GAP-035`.
- [ ] `GAP-043` is complete before implementing deeper `GAP-036` or `GAP-037` behavior.
- [ ] `GAP-044` is complete before broadening `GAP-038` or running `GAP-039` trials.
- [ ] Evidence records any gate not yet complete and the implementation tasks blocked by it.

**Verification:**
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`.

**Dependencies:** None.

**Estimated scope:** Small.

### Task 1: Define Repo Attachment Binding Contract

**Purpose:** Add the runtime contract that binds one target repository to the machine-wide runtime without copying the kernel into the target repository.

**Files:**
- Create: `docs/specs/repo-attachment-binding-spec.md`
- Create: `schemas/jsonschema/repo-attachment-binding.schema.json`
- Create: `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_attachment.py`
- Create: `tests/runtime/test_repo_attachment.py`
- Modify: `schemas/catalog/schema-catalog.yaml`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/__init__.py`

**Acceptance criteria:**
- [ ] Binding records include target repo root, repo profile reference, light-pack path, runtime state root, adapter preference, gate profile, and doctor posture.
- [ ] Binding validation rejects paths outside the target repo for repo-local declarations.
- [ ] Binding validation keeps mutable task, run, approval, artifact, and replay state machine-local.
- [ ] Schema and Python contract agree on required fields and enum values.

**Verification:**
- [ ] Run `python -m unittest tests.runtime.test_repo_attachment -v`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`.

**Dependencies:** `GAP-042`.

**Estimated scope:** Medium.

### Task 2: Implement Repo-Local Light Pack Generator And Validator

**Purpose:** Make `GAP-035` concrete by generating or validating the target repo's declarative light pack.

**Files:**
- Create: `scripts/attach-target-repo.py`
- Create: `docs/product/target-repo-attachment-flow.md`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_attachment.py`
- Modify: `tests/runtime/test_repo_attachment.py`
- Modify: `docs/architecture/generic-target-repo-attachment-blueprint.md`

**Acceptance criteria:**
- [ ] A new target repo can receive a minimal declarative light pack without runtime implementation code.
- [ ] Existing light packs are validated instead of overwritten.
- [ ] Invalid gate commands, path scopes, or repo profile references fail with actionable diagnostics.
- [ ] The generated or validated binding can be consumed by the runtime and doctor surfaces.

**Verification:**
- [ ] Run `python -m unittest tests.runtime.test_repo_attachment -v`.
- [ ] Run `python scripts/attach-target-repo.py --help`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`.

**Dependencies:** Task 1.

**Estimated scope:** Medium.

### Task 3: Surface Attachment Posture In Doctor And Status

**Purpose:** Make target-repo onboarding visible and diagnosable before session-bridge work depends on it.

**Files:**
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/runtime_status.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_attachment.py`
- Modify: `scripts/doctor-runtime.ps1`
- Modify: `scripts/run-governed-task.py`
- Modify: `tests/runtime/test_runtime_status.py`
- Modify: `tests/runtime/test_runtime_doctor.py`
- Modify: `docs/product/target-repo-attachment-flow.md`

**Acceptance criteria:**
- [ ] Runtime status can report attached repo id, binding state, light-pack path, and adapter preference.
- [ ] Doctor distinguishes missing light pack, invalid light pack, stale binding, and healthy binding.
- [ ] Status output remains stable for existing local-baseline users.

**Verification:**
- [ ] Run `python -m unittest tests.runtime.test_runtime_status tests.runtime.test_runtime_doctor -v`.
- [ ] Run `python scripts/run-governed-task.py status --json`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`.

**Dependencies:** Task 2.

**Estimated scope:** Medium.

### Task 4: Define Session Bridge Command Contract

**Purpose:** Establish the stable command surface for governed actions callable from an active AI coding session.

**Files:**
- Create: `docs/specs/session-bridge-command-spec.md`
- Create: `schemas/jsonschema/session-bridge-command.schema.json`
- Create: `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
- Create: `tests/runtime/test_session_bridge.py`
- Create: `docs/product/session-bridge-commands.md`
- Modify: `schemas/catalog/schema-catalog.yaml`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/__init__.py`

**Acceptance criteria:**
- [ ] Command types include bind task, show repo posture, request approval, run quick gate, run full gate, inspect evidence, and inspect status.
- [ ] Every command carries task id, repo binding id, adapter id, risk tier, and PolicyDecision reference when execution is requested.
- [ ] Commands that imply execution fail closed when PolicyDecision is `deny`.
- [ ] Commands that require human approval carry escalation context instead of executing.

**Verification:**
- [ ] Run `python -m unittest tests.runtime.test_session_bridge -v`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`.

**Dependencies:** Task 3, `GAP-043`.

**Estimated scope:** Medium.

### Task 5: Add Local Session Bridge Entrypoint

**Purpose:** Provide a first local bridge surface that can be called by an AI session integration or by a launch-mode fallback.

**Files:**
- Create: `scripts/session-bridge.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/execution_runtime.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/write_tool_runner.py`
- Modify: `tests/runtime/test_session_bridge.py`
- Modify: `tests/runtime/test_write_tool_runner.py`
- Modify: `docs/product/session-bridge-commands.md`
- Modify: `docs/product/interaction-model.md`
- Modify: `docs/product/write-side-tool-governance.md`

**Acceptance criteria:**
- [ ] `session-bridge.py` can bind an existing task to an attached repo.
- [ ] The bridge can return repo posture and runtime status without mutating state.
- [ ] The bridge can request quick/full gates through the existing verification runner path.
- [ ] Existing local-baseline write governance results are normalized into `PolicyDecision` `allow / escalate / deny` before the bridge exposes execution-like outcomes.
- [ ] Unsupported command or adapter capabilities return explicit degrade results.

**Verification:**
- [ ] Run `python -m unittest tests.runtime.test_session_bridge -v`.
- [ ] Run `python scripts/session-bridge.py --help`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`.

**Dependencies:** Task 4.

**Estimated scope:** Medium.

### Task 6: Implement Launch-Second Fallback

**Purpose:** Keep the product usable when native session attach is unavailable while preserving honest capability posture.

**Files:**
- Modify: `scripts/session-bridge.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/adapter_registry.py`
- Modify: `tests/runtime/test_session_bridge.py`
- Modify: `docs/product/session-bridge-commands.md`
- Modify: `docs/product/adapter-degrade-policy.md`

**Acceptance criteria:**
- [ ] Launch mode is explicit and never presented as native attach.
- [ ] Process output, exit code, changed-file discovery, and verification references are captured when launch mode is used.
- [ ] Manual handoff remains available when process bridge capability is unavailable.

**Verification:**
- [ ] Run `python -m unittest tests.runtime.test_session_bridge tests.runtime.test_adapter_registry -v`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`.

**Dependencies:** Task 5.

**Estimated scope:** Medium.

### Task 7: Add Direct Codex Adapter Contract

**Purpose:** Make Codex the first direct adapter target without making the runtime Codex-only.

**Files:**
- Create: `docs/product/codex-direct-adapter.md`
- Create: `packages/contracts/src/governed_ai_coding_runtime_contracts/codex_adapter.py`
- Create: `tests/runtime/test_codex_adapter.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/adapter_registry.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/__init__.py`
- Modify: `docs/product/codex-cli-app-integration-guide.md`
- Modify: `docs/product/codex-cli-app-integration-guide.zh-CN.md`

**Acceptance criteria:**
- [ ] Codex adapter declares auth ownership, workspace control, tool visibility, mutation model, resume behavior, and evidence export capability.
- [ ] Codex adapter can be classified as native attach, process bridge, or manual handoff based on available capability.
- [ ] Unsupported Codex capabilities degrade explicitly instead of being implied.

**Verification:**
- [ ] Run `python -m unittest tests.runtime.test_codex_adapter tests.runtime.test_adapter_registry -v`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`.

**Dependencies:** Task 5, `GAP-043`.

**Estimated scope:** Medium.

### Task 8: Map Codex Session Evidence To Runtime Evidence

**Purpose:** Make Codex-driven changes reviewable through the same evidence and handoff model as local runtime work.

**Files:**
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/codex_adapter.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/evidence.py`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/delivery_handoff.py`
- Modify: `tests/runtime/test_codex_adapter.py`
- Modify: `tests/runtime/test_evidence_timeline.py`
- Modify: `tests/runtime/test_delivery_handoff.py`
- Modify: `docs/product/codex-direct-adapter.md`

**Acceptance criteria:**
- [ ] Codex-driven file changes, tool calls, gate runs, approval events, and handoff entries can reference one governed task.
- [ ] Manual-handoff Codex flows remain distinguishable from direct adapter flows.
- [ ] Evidence records unsupported capabilities and adapter degrade state.

**Verification:**
- [ ] Run `python -m unittest tests.runtime.test_codex_adapter tests.runtime.test_evidence_timeline tests.runtime.test_delivery_handoff -v`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`.

**Dependencies:** Task 7.

**Estimated scope:** Medium.

### Task 9: Add Codex Direct Smoke Trial

**Purpose:** Prove at least one Codex path is direct enough to bind session/task/evidence without depending on private maintainer context.

**Files:**
- Create: `scripts/run-codex-adapter-trial.py`
- Modify: `tests/runtime/test_codex_adapter.py`
- Modify: `docs/product/codex-direct-adapter.md`
- Modify: `docs/quickstart/single-machine-runtime-quickstart.md`
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `README.en.md`

**Acceptance criteria:**
- [ ] Trial runs in a safe mode by default and does not require real high-risk writes.
- [ ] Trial output includes adapter tier, task id, binding id, evidence refs, verification refs, and unsupported capability behavior.
- [ ] Quickstart distinguishes direct Codex adapter trial from existing read-only trial and runtime smoke path.

**Verification:**
- [ ] Run `python -m unittest tests.runtime.test_codex_adapter -v`.
- [ ] Run `python scripts/run-codex-adapter-trial.py --help`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`.

**Dependencies:** Task 8.

**Estimated scope:** Medium.

### Task 10: Generalize Adapter Registry And Capability Tiers

**Purpose:** Turn Codex-specific lessons into a stable adapter framework for multiple AI tools.

**Files:**
- Create: `docs/product/adapter-capability-tiers.md`
- Create: `packages/contracts/src/governed_ai_coding_runtime_contracts/adapter_registry.py`
- Create: `tests/runtime/test_adapter_registry.py`
- Modify: `docs/specs/agent-adapter-contract-spec.md`
- Modify: `schemas/jsonschema/agent-adapter-contract.schema.json`
- Modify: `schemas/catalog/schema-catalog.yaml`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/__init__.py`
- Modify: `docs/product/adapter-degrade-policy.md`

**Acceptance criteria:**
- [ ] Adapter registry supports native attach, process bridge, and manual handoff tiers.
- [ ] Each tier has explicit governance guarantees and unsupported capability behavior.
- [ ] Existing Codex posture is represented through the same generic adapter contract.
- [ ] Schema, spec, and Python contract agree on tier names and required fields.

**Verification:**
- [ ] Run `python -m unittest tests.runtime.test_adapter_registry tests.runtime.test_codex_adapter -v`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`.

**Dependencies:** Task 9, `GAP-044`.

**Estimated scope:** Medium.

### Task 11: Add Non-Codex Adapter Template And Degrade Fixtures

**Purpose:** Demonstrate that the runtime is Codex-first but not Codex-only without overbuilding support for every vendor.

**Files:**
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/adapter_registry.py`
- Modify: `tests/runtime/test_adapter_registry.py`
- Create: `schemas/examples/agent-adapter-contract/manual-handoff.example.json`
- Create: `schemas/examples/agent-adapter-contract/process-bridge.example.json`
- Modify: `schemas/examples/README.md`
- Modify: `docs/product/adapter-capability-tiers.md`

**Acceptance criteria:**
- [ ] At least one non-Codex manual-handoff fixture validates.
- [ ] At least one process-bridge fixture validates.
- [ ] Runtime examples show honest downgrade behavior when native attach is unavailable.

**Verification:**
- [ ] Run `python -m unittest tests.runtime.test_adapter_registry -v`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`.

**Dependencies:** Task 10.

**Estimated scope:** Small.

### Task 12: Define Multi-Repo Trial Evidence Model

**Purpose:** Capture onboarding and adapter feedback as product evidence rather than informal notes.

**Files:**
- Create: `docs/product/multi-repo-trial-loop.md`
- Create: `packages/contracts/src/governed_ai_coding_runtime_contracts/multi_repo_trial.py`
- Create: `tests/runtime/test_multi_repo_trial.py`
- Modify: `docs/specs/eval-and-trace-grading-spec.md`
- Modify: `docs/specs/evidence-bundle-spec.md`
- Modify: `schemas/jsonschema/evidence-bundle.schema.json`
- Modify: `schemas/catalog/schema-catalog.yaml`

**Acceptance criteria:**
- [ ] Trial records include repo identity, adapter tier, unsupported capabilities, approval friction, gate failures, replay quality, and follow-up onboarding fixes.
- [ ] Trial records can link to evidence bundles and delivery handoff refs.
- [ ] Trial evidence distinguishes repo-specific fixes from generic onboarding or adapter contract improvements.

**Verification:**
- [ ] Run `python -m unittest tests.runtime.test_multi_repo_trial tests.runtime.test_evidence_timeline -v`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`.

**Dependencies:** Task 11, `GAP-044`.

**Estimated scope:** Medium.

### Task 13: Add Multi-Repo Trial Runner And Onboarding Kit

**Purpose:** Make `GAP-039` executable by running the attach and adapter flow against more than one target repository profile.

**Files:**
- Create: `scripts/run-multi-repo-trial.py`
- Create: `docs/quickstart/multi-repo-trial-quickstart.md`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/multi_repo_trial.py`
- Modify: `tests/runtime/test_multi_repo_trial.py`
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `README.en.md`
- Modify: `docs/README.md`

**Acceptance criteria:**
- [ ] Trial runner can execute at least two repo-profile-based onboarding checks without kernel rewrites.
- [ ] Output includes per-repo attachment posture, adapter tier, verification refs, evidence refs, and follow-up items.
- [ ] Quickstart explains how to add a new target repo profile without changing runtime code.

**Verification:**
- [ ] Run `python -m unittest tests.runtime.test_multi_repo_trial -v`.
- [ ] Run `python scripts/run-multi-repo-trial.py --help`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`.

**Dependencies:** Task 12.

**Estimated scope:** Medium.

### Task 14: Close Productization With Evidence, Roadmap Updates, And Full Gates

**Purpose:** Record the implementation outcome and prevent the final product boundary from being overstated.

**Files:**
- Create: `docs/change-evidence/<date>-interactive-session-productization-implementation.md`
- Modify: `docs/change-evidence/README.md`
- Modify: `docs/backlog/issue-ready-backlog.md`
- Modify: `docs/backlog/issue-seeds.yaml`
- Modify: `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- Modify: `docs/plans/README.md`
- Modify: `docs/README.md`

**Acceptance criteria:**
- [ ] Evidence records exact commands, exit codes, key outputs, risks, and rollback path.
- [ ] Backlog status is updated only for tasks actually implemented and verified.
- [ ] Roadmap completion wording distinguishes complete local baseline, implemented interactive productization slices, and any remaining adapter/trial work.
- [ ] Final verification runs the project gate order: build, runtime tests, contract/invariant, hotspot/doctor, then all checks.

**Verification:**
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`.

**Dependencies:** Tasks 1 through 13.

**Estimated scope:** Small.

## Checkpoints

### Checkpoint A: After Tasks 0-3
- `GAP-035` has a contract-backed repo attachment path.
- Light packs remain declarative and target-repo local.
- Runtime status and doctor can explain attachment posture.
- Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`.

### Checkpoint B: After Tasks 4-6
- `GAP-036` has a session bridge command contract and local entrypoint.
- Attach-first is preferred and launch-second is explicit fallback.
- PolicyDecision is used before execution-like session commands.
- Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`.

### Checkpoint C: After Tasks 7-9
- `GAP-037` has a direct Codex adapter path and evidence mapping.
- Direct, process bridge, and manual handoff Codex modes are distinguishable.
- Codex trial output is documented and reproducible.
- Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`.

### Checkpoint D: After Tasks 10-11
- `GAP-038` has a generic adapter registry and capability tiers.
- At least one non-Codex fixture validates through the generic contract.
- Degrade and fail-closed behavior remain explicit.
- Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`.

### Checkpoint E: After Tasks 12-14
- `GAP-039` has structured multi-repo trial evidence and an onboarding kit.
- Roadmap and backlog reflect only verified implementation status.
- Evidence records commands, outputs, risks, and rollback.
- Run the full gate order and `verify-repo -Check All`.

## Risks And Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Session bridge overfits to Codex | High | Keep Codex behind adapter registry and capability tiers; require non-Codex fixtures in Task 11. |
| Light pack becomes a second hand-maintained source of truth | High | Depend on `GAP-041` and `GAP-042`; generate or validate runtime-consumable bundles from source-of-truth docs/schemas/contracts. |
| Policy and approval semantics are bypassed by in-session commands | High | Make Task 4 depend on `GAP-043`; require PolicyDecision references for execution-like commands. |
| Launch-second fallback is mistaken for native attach | Medium | Record adapter tier and unsupported capabilities in session bridge, Codex adapter, evidence, and trial outputs. |
| Multi-repo trial produces repo-specific hacks | Medium | Require trial evidence to classify follow-ups as repo-specific, onboarding generic, adapter generic, or contract generic. |
| Plan scope grows into enterprise gateway or replacement IDE | Medium | Preserve non-goals from roadmap and interaction model; keep UI as control-plane console and adapters as host boundaries. |

## Completion Definition

Interactive Session Productization is complete when:

- a target repository can be attached through a declarative light pack
- the runtime binds that repo to machine-local state and doctor/status surfaces
- governed commands are callable through a session bridge
- launch mode exists as an explicit fallback
- at least one Codex path is direct enough to bind task, session, evidence, and verification
- adapter capability tiers support Codex and at least one non-Codex fixture
- multi-repo trial evidence is captured and can drive onboarding or adapter improvements
- roadmap, backlog, issue seeds, docs, evidence, and gate results all agree on what is complete
