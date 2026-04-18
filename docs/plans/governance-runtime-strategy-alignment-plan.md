# Governance Runtime Strategy Alignment Plan

## Status
- Completed strategy-alignment coordination plan.
- `GAP-040` through `GAP-044` are complete on the current branch baseline and remain dependency gates, not an active second implementation queue.
- Do not execute this file as the current implementation checklist.
- Current active execution entrypoint: [Interactive Session Productization Implementation Plan](./interactive-session-productization-implementation-plan.md).
- Current audit guardrail: [Hybrid Final-State And Plan Reconciliation](../reviews/2026-04-18-hybrid-final-state-and-plan-reconciliation.md).

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the positioning and competitive-layering discussion into a bounded strategy, ADR, architecture, and backlog alignment track without replacing the current `GAP-035` through `GAP-039` interactive-session productization plan.

**Architecture:** Preserve the existing source-of-truth structure: `docs/` for narrative decisions and specs, `schemas/` for machine-readable contracts, and `packages/contracts/` for executable contract primitives. Treat future repo-local light packs or `.governed-ai/`-style bundles as runtime-consumable outputs generated or validated from those sources, not as an immediate replacement for the repository's authoring structure. Keep external products as mechanism references, not product identities to copy.

**Tech Stack:** Markdown planning and ADRs under `docs/`, JSON Schema draft 2020-12 under `schemas/jsonschema/`, Python standard-library contract primitives under `packages/contracts/`, PowerShell repository verification under `scripts/`, and official-source research links recorded in `docs/research/`.

---

## Current Baseline

- `GAP-024` through `GAP-034` are documented as complete on the current branch baseline.
- `GAP-035` through `GAP-039` are the active execution queue for generic target-repo attachment, attach-first interactive sessions, direct Codex integration, capability-tiered adapters, and multi-repo trial feedback.
- `GAP-040` through `GAP-044` now exist as the strategy-alignment gate queue that constrains selected `GAP-035` through `GAP-039` hardening work.
- The project already rejects becoming a new IDE, generic chat host, default multi-agent orchestrator, memory-first platform, or enterprise gateway.
- The remaining strategic risk is terminology drift: external references such as governance toolkits, gateways, MCP, guardrails, and agent hosts can pull the roadmap in incompatible directions if they are not mapped into stable project layers.

## Target Position

The project should keep the final-state shorthand:

`Repo-native Contract Bundle + Host Adapters + Policy Decision Interface + Verification and Delivery Plane`

This is a product-positioning shape, not a directory migration instruction. The current repository source-of-truth remains:

| Current source | Responsibility | Future runtime output |
|---|---|---|
| `docs/` | strategy, PRD, ADRs, specs, runbooks, plans | human and agent-readable design context |
| `schemas/` | machine-readable schema contracts and examples | bundle validation inputs |
| `packages/contracts/` | executable contract primitives and local runtime helpers | runtime/kernel library |
| `scripts/` | verification, doctor, bootstrap, issue seeding | local and CI operational entrypoints |
| target repo light pack | not the source of truth for this repo | install or attachment surface for governed target repositories |

## External Reference Policy

Reference external products only through an adoption matrix:

| Reference | Borrow | Avoid |
|---|---|---|
| Microsoft Agent Governance Toolkit | runtime governance, cross-framework policy and audit concepts | enterprise breadth as near-term scope |
| OPA | policy decision separation, structured policy inputs, auditable allow/deny logic | immediate hard dependency before the local interface stabilizes |
| Keycard for Coding Agents | agent identity, scoped authorization, task-level permission vocabulary | building a standalone IAM product |
| Coder AI Gateway / AI Governance | centralized gateway, MCP management, firewall, observability | replacing the local-first product with org gateway infrastructure |
| MCP / MCP Gateway ecosystem | tool/resource/context adapter surface | treating MCP as the governance kernel or mandatory enforcement point |
| GAAI-framework-style repo files | repo-native declarative governance packs | adopting unverified conventions as a standard |
| OpenHands / SWE-agent / Hermes-like agents | sandboxing, issue-to-task loops, execution harness design | becoming another execution host |
| oh-my-codex / oh-my-claudecode-style wrappers | host UX, wrapper ergonomics, skills/hooks packaging | competing in orchestration-wrapper identity |
| NeMo Guardrails / Guardrails AI | generation-side guardrail and structured-output lessons | repositioning this project as output filtering |

Official references to use during execution:

- Microsoft Agent Governance Toolkit: `https://opensource.microsoft.com/blog/2026/04/02/introducing-the-agent-governance-toolkit-open-source-runtime-security-for-ai-agents/`
- Open Policy Agent: `https://www.openpolicyagent.org/docs`
- Keycard: `https://www.keycard.ai/`
- Coder AI Governance: `https://coder.com/docs/ai-coder/ai-governance`
- Model Context Protocol: `https://modelcontextprotocol.io/`
- GAAI framework: `https://github.com/Fr-e-d/GAAI-framework`
- OpenHands: `https://openhands.dev/`
- SWE-agent: `https://github.com/SWE-agent/SWE-agent`
- NVIDIA NeMo Guardrails: `https://developer.nvidia.com/nemo-guardrails`
- Guardrails AI: `https://guardrailsai.com/`

References without a stable official page or primary repository must be re-verified during Task 1 or excluded from the final borrowing matrix.

## Planned File Structure

### Create

- `docs/research/runtime-governance-borrowing-matrix.md`
- `docs/strategy/README.md`
- `docs/strategy/positioning-and-competitive-layering.md`
- `docs/adrs/0007-source-of-truth-and-runtime-contract-bundle.md`
- `docs/architecture/repo-native-contract-bundle.md`
- `docs/specs/policy-decision-spec.md`
- `schemas/jsonschema/policy-decision.schema.json`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/policy_decision.py`
- `tests/runtime/test_policy_decision.py`
- `docs/change-evidence/<date>-governance-runtime-strategy-alignment.md`

### Modify

- `README.md`
- `README.zh-CN.md`
- `README.en.md`
- `docs/README.md`
- `docs/architecture/README.md`
- `docs/architecture/governed-ai-coding-runtime-target-architecture.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/full-lifecycle-backlog-seeds.md`
- `docs/backlog/issue-seeds.yaml`
- `docs/plans/README.md`
- `docs/change-evidence/README.md`
- `schemas/catalog/schema-catalog.yaml`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/__init__.py`
- `scripts/verify-repo.ps1`
- `scripts/github/create-roadmap-issues.ps1`

## Task List

### Task 1: Create The Runtime Governance Borrowing Matrix

**Files:**
- Create: `docs/research/runtime-governance-borrowing-matrix.md`
- Modify: `docs/README.md`

**Purpose:** Record what to borrow from adjacent products before changing positioning, architecture, or backlog.

**Acceptance criteria:**
- [ ] Every referenced product is classified into one layer: governance control plane, policy engine, identity/scope, gateway, adapter protocol, execution host, wrapper/orchestration, or generation guardrail.
- [ ] Every referenced product has a `Borrow`, `Avoid`, `Impact`, `Confidence`, and `Source` row.
- [ ] Only official sources or primary repositories are used for claims.
- [ ] The matrix states that external references are mechanism inputs, not product identities.

**Steps:**
- [ ] Re-check official sources and current repository docs before writing.
- [ ] Create the matrix using the external reference policy above.
- [ ] Link the matrix from `docs/README.md` under Research.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`.

**Dependencies:** None.

**Estimated scope:** Small.

### Task 2: Consolidate Public Positioning Into Strategy Docs

**Files:**
- Create: `docs/strategy/README.md`
- Create: `docs/strategy/positioning-and-competitive-layering.md`
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `README.en.md`
- Modify: `docs/README.md`

**Purpose:** Keep the root README concise while preserving the detailed competitive-layering argument in a dedicated strategy document.

**Acceptance criteria:**
- [ ] README states the project as a governance/runtime layer for AI coding agents, not a host replacement.
- [ ] README links to the strategy document instead of carrying the full competitive discussion.
- [ ] The strategy document includes non-goals and the four-layer final-state shorthand.
- [ ] The strategy document explicitly distinguishes runtime/action guardrails from generation guardrails.

**Steps:**
- [ ] Create `docs/strategy/README.md` with links to active strategy documents.
- [ ] Create `docs/strategy/positioning-and-competitive-layering.md` from the discussion and borrowing matrix.
- [ ] Keep README entry text short: current phase, value claim, non-goals, active plan links.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`.

**Dependencies:** Task 1.

**Estimated scope:** Medium.

### Task 3: Record Source-Of-Truth And Runtime Bundle Decision

**Files:**
- Create: `docs/adrs/0007-source-of-truth-and-runtime-contract-bundle.md`
- Modify: `docs/README.md`

**Purpose:** Prevent future work from replacing the current authoring structure with a repo-local bundle shape too early.

**Acceptance criteria:**
- [ ] ADR states that `docs/`, `schemas/`, and `packages/contracts/` remain the source of truth.
- [ ] ADR states that a future `.governed-ai/` or equivalent repo-local light pack is a runtime-consumable output or target-repo attachment surface.
- [ ] ADR rejects hand-maintaining two competing contract copies.
- [ ] ADR defines migration posture: generate, validate, attach, then consider consolidation only if duplication becomes real.

**Steps:**
- [ ] Write the ADR with Context, Decision, Alternatives, and Consequences.
- [ ] Cross-link ADR-0005 and ADR-0006.
- [ ] Link ADR-0007 from `docs/README.md`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`.

**Dependencies:** Task 2.

**Estimated scope:** Small.

### Task 4: Define The Repo-Native Contract Bundle Architecture

**Files:**
- Create: `docs/architecture/repo-native-contract-bundle.md`
- Modify: `docs/architecture/README.md`
- Modify: `docs/architecture/governed-ai-coding-runtime-target-architecture.md`

**Purpose:** Map the target phrase `Repo-native Contract Bundle + Host Adapters + Policy Decision Interface + Verification and Delivery Plane` onto the landed runtime and active interactive-session work.

**Acceptance criteria:**
- [ ] Architecture doc defines source-of-truth inputs and runtime bundle outputs.
- [ ] Architecture doc defines repo-local state versus machine-local runtime state.
- [ ] Architecture doc maps bundle content to existing specs and schemas.
- [ ] Target architecture references the bundle as an adapter/attachment boundary, not a replacement kernel.

**Steps:**
- [ ] Document bundle contents: repo profile, gates, write policy, approval policy, adapter capabilities, policy decision outputs, evidence/handoff/rollback references.
- [ ] Document state placement rules: target repo declarations stay light; mutable task/run/artifact state stays machine-local.
- [ ] Document local and CI same-contract consumption.
- [ ] Link the architecture doc from `docs/architecture/README.md`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`.

**Dependencies:** Task 3.

**Estimated scope:** Medium.

### Task 5: Add The Policy Decision Contract

**Files:**
- Create: `docs/specs/policy-decision-spec.md`
- Create: `schemas/jsonschema/policy-decision.schema.json`
- Create: `packages/contracts/src/governed_ai_coding_runtime_contracts/policy_decision.py`
- Create: `tests/runtime/test_policy_decision.py`
- Modify: `schemas/catalog/schema-catalog.yaml`
- Modify: `packages/contracts/src/governed_ai_coding_runtime_contracts/__init__.py`

**Purpose:** Add the missing stable interface between host adapters, tool runners, approval flow, and verification gates.

**Acceptance criteria:**
- [ ] Policy decision statuses include `allow`, `escalate`, and `deny`.
- [ ] Decision records include task id, action id, risk tier, subject, decision basis, required approval reference, evidence reference, and remediation hint.
- [ ] `deny` fails closed and does not create an executable action.
- [ ] `escalate` can carry an approval request reference without conflating approval with execution.
- [ ] JSON Schema and Python contract agree on required fields and enum values.

**Steps:**
- [ ] Write the spec first.
- [ ] Add the schema and catalog entry.
- [ ] Write failing unit tests for `allow`, `escalate`, `deny`, and invalid status.
- [ ] Implement the Python dataclass and validation helpers.
- [ ] Export the contract from `__init__.py`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`.

**Dependencies:** Task 4.

**Estimated scope:** Medium.

### Task 6: Align Local And CI Same-Contract Verification

**Files:**
- Modify: `docs/specs/verification-gates-spec.md`
- Modify: `schemas/jsonschema/verification-gates.schema.json`
- Modify: `scripts/verify-repo.ps1`
- Modify: `tests/runtime/test_runtime_doctor.py`

**Purpose:** Make the target promise "one contract, local and CI consistent" testable.

**Acceptance criteria:**
- [ ] Verification spec distinguishes local gate execution, CI gate execution, and same-contract inputs.
- [ ] `verify-repo.ps1` collects markdown paths robustly, including non-ASCII paths, by using an unquoted path source such as `git -c core.quotepath=false ls-files`.
- [ ] Runtime tests cover ignored worktree markdown and at least one non-ASCII markdown filename or equivalent encoded-path fixture.
- [ ] Docs explain that CI is the last line of defense when host hooks, wrappers, or adapters are bypassed.

**Steps:**
- [ ] Extend the verification gates spec before changing scripts.
- [ ] Add the failing non-ASCII path regression test.
- [ ] Update `scripts/verify-repo.ps1` path collection.
- [ ] Run the targeted runtime test.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`.

**Dependencies:** Task 4.

**Estimated scope:** Medium.

### Task 7: Seed And Reconcile Backlog And Issue Seeds

**Files:**
- Modify: `docs/backlog/issue-ready-backlog.md`
- Modify: `docs/backlog/full-lifecycle-backlog-seeds.md`
- Modify: `docs/backlog/issue-seeds.yaml`
- Modify: `scripts/github/create-roadmap-issues.ps1`

**Purpose:** Make the new strategic alignment executable without derailing `GAP-035` through `GAP-039`. Initial gate seeding can happen before Tasks 1 through 6; final reconciliation still happens after the matrix, ADR, architecture, contract, and verification work land.

**Acceptance criteria:**
- [ ] The active `GAP-035` through `GAP-039` queue remains intact.
- [ ] New work is added as a bounded strategy-alignment track or as `GAP-040` onward.
- [ ] Dependencies identify which gates constrain deeper adapter work and which can run after multi-repo trials.
- [ ] Issue seeding renders the new tasks without breaking existing IDs.

**Steps:**
- [ ] Model the work as `GAP-040` onward under a named Strategy Alignment Gates track.
- [ ] Update backlog and seeds consistently.
- [ ] Update issue seeding script output for new tasks.
- [ ] After Tasks 1 through 6 complete, reconcile final backlog wording against the landed matrix, ADR, architecture, contract, and verification behavior.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`.
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`.

**Dependencies:** None for initial gate seeding; Tasks 1 through 6 for final closeout reconciliation.

**Estimated scope:** Medium.

### Task 8: Close With Evidence And Full Gates

**Files:**
- Create: `docs/change-evidence/<date>-governance-runtime-strategy-alignment.md`
- Modify: `docs/change-evidence/README.md`

**Purpose:** Record the reasoning, commands, evidence, risks, and rollback path for the strategy alignment.

**Acceptance criteria:**
- [ ] Evidence records the basis: target positioning, current active queue, external borrowing matrix, ADR decision, and backlog impact.
- [ ] Evidence records exact commands, exit codes, and key outputs.
- [ ] Evidence includes rollback notes for every modified documentation and contract surface.
- [ ] Evidence distinguishes implemented changes from planned future changes.

**Steps:**
- [ ] Create the evidence document after Tasks 1 through 7.
- [ ] Update `docs/change-evidence/README.md`.
- [ ] Run gates in order:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
- [ ] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`.

**Dependencies:** Tasks 1 through 7.

**Estimated scope:** Small.

## Checkpoints

### Checkpoint A: After Tasks 1-3
- External borrowing has a controlled matrix.
- Public positioning is separated from README.
- ADR-0007 prevents premature source-of-truth migration.

### Checkpoint B: After Tasks 4-6
- Repo-native contract bundle has a stable architecture.
- `PolicyDecision` exists as a first-class contract.
- Local and CI same-contract verification is specified and tested.

### Checkpoint C: After Tasks 7-8
- Backlog and issue seeds contain the new work without disrupting `GAP-035` through `GAP-039`.
- Evidence and gates close the strategy alignment.

## Risks And Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| External references pull the project toward enterprise gateway scope | High | Borrow mechanisms only; keep non-goals explicit in strategy and ADR. |
| `.governed-ai/` becomes a second hand-maintained contract source | High | ADR-0007 requires generated or validated runtime bundles, not duplicate authoring. |
| Policy implementation starts before the interface is stable | Medium | Land `PolicyDecision` as a local contract first; defer OPA integration. |
| Strategy work blocks interactive-session execution too long | Medium | Keep this as a bounded plan; only Tasks 1, 3, 4, and 6 are likely prerequisites for deeper adapter work. |
| README becomes too long again | Medium | Put competitive analysis in `docs/strategy/`, keep README as a short entrypoint. |

## Completion Definition

This alignment is complete when:

- the borrowing matrix exists and is linked
- strategy positioning lives outside the root README
- ADR-0007 records source-of-truth versus runtime bundle boundaries
- repo-native contract bundle architecture exists
- `PolicyDecision` is specified, schema-backed, and tested
- local/CI same-contract verification behavior is documented and regression-tested
- backlog and issue seeds reflect the work without breaking the active productization queue
- evidence records commands, results, risks, and rollback notes
