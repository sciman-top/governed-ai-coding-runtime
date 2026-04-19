# Governance Optimization Lane Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Define the governance follow-on work that should begin after hybrid final-state closure so the runtime can improve through trace grading, explicit admission signals, governed control rollout, curated knowledge inputs, provenance coverage, and controlled improvement proposals without mutating kernel semantics autonomously.

**Architecture:** Keep the direct-to-hybrid-final-state queue as the executable runtime mainline and land the optimization lane after `GAP-060` as a governance-only follow-on. First canonicalize the lane and its templates, then strengthen traces and repo admission, then harden control rollout and knowledge governance, then add provenance and controlled proposal outputs, and finally close the lane with explicit claim discipline.

**Tech Stack:** Markdown planning docs, JSON Schema-aligned specs, existing PowerShell verification entrypoints, existing issue-seed rendering script, and the current docs-first/contracts-first repository structure.

---

## Status

- This is the canonical implementation plan for the governance-optimization lane.
- It does not replace `docs/plans/direct-to-hybrid-final-state-implementation-plan.md`.
- `GAP-061` through `GAP-068` are complete on the current branch baseline (verified on 2026-04-20).
- The lane is intentionally planning-first and governance-first; it should not be used to sneak in unrelated runtime implementation work.

## Source Inputs

- `docs/roadmap/governance-optimization-lane-roadmap.md`
- `docs/roadmap/direct-to-hybrid-final-state-roadmap.md`
- `docs/architecture/minimum-viable-governance-loop.md`
- `docs/architecture/governance-boundary-matrix.md`
- `docs/specs/control-registry-spec.md`
- `docs/specs/eval-and-trace-grading-spec.md`
- `docs/specs/knowledge-source-spec.md`
- `docs/specs/repo-admission-minimums-spec.md`
- `docs/specs/provenance-and-attestation-spec.md`
- `docs/specs/waiver-and-exception-spec.md`
- `docs/product/maintenance-deprecation-and-retirement-policy.md`

## Dependency Graph

```text
GAP-060 hybrid final-state closeout
  -> GAP-061 lane canonicalization
       -> GAP-062 trace grading baseline
            -> GAP-063 repo admission and compatibility hardening
                 -> GAP-064 control rollout and waiver recovery
                      -> GAP-065 knowledge registry and repo-map shaping
                           -> GAP-066 provenance and attestation coverage
                                -> GAP-067 controlled improvement proposals
                                     -> GAP-068 lane closeout and claim discipline
```

## Planned File Structure

### Planning And Backlog
- `docs/roadmap/governance-optimization-lane-roadmap.md`
- `docs/plans/governance-optimization-lane-implementation-plan.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/issue-seeds.yaml`
- `docs/templates/governance-gap-acceptance-and-rollback-template.md`
- `docs/change-evidence/*.md`

### Anticipated Spec Targets For Later GAPs
- `docs/specs/control-registry-spec.md`
- `docs/specs/eval-and-trace-grading-spec.md`
- `docs/specs/repo-admission-minimums-spec.md`
- `docs/specs/knowledge-source-spec.md`
- `docs/specs/provenance-and-attestation-spec.md`
- `docs/specs/waiver-and-exception-spec.md`
- `docs/architecture/minimum-viable-governance-loop.md`
- `docs/architecture/governance-boundary-matrix.md`

## Task List

**Cross-task evidence rule:**
- Any task that modifies plans, backlog, seeds, specs, or policy docs must add one new `docs/change-evidence/<date>-<slug>.md` entry with commands, key outputs, risks, and rollback notes.

### Task 0: Canonicalize The Optimization Lane

**Purpose:** Give the lane a stable planning surface before changing any governance spec content.

**Files:**
- Create: `docs/roadmap/governance-optimization-lane-roadmap.md`
- Create: `docs/plans/governance-optimization-lane-implementation-plan.md`
- Create: `docs/templates/governance-gap-acceptance-and-rollback-template.md`
- Modify: `docs/plans/README.md`
- Modify: `docs/backlog/README.md`
- Modify: `docs/backlog/issue-ready-backlog.md`
- Modify: `docs/backlog/issue-seeds.yaml`
- Modify: `docs/README.md`
- Modify: `scripts/github/create-roadmap-issues.ps1`
- Create: `docs/change-evidence/<date>-governance-optimization-lane-planning.md`

**Acceptance criteria:**
- [x] The lane has a roadmap, implementation plan, template, backlog entries, issue seeds, and evidence.
- [x] Existing `GAP-045` through `GAP-060` remain the active hybrid-final-state queue.
- [x] `GAP-061` through `GAP-068` are visible as the next governance-optimization lane rather than an implicit backlog tail.
- [x] GitHub issue rendering can emit a dedicated governance-lane epic after the direct-to-hybrid `Phase 5` chain.

**Verification:**
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`.

**Dependencies:** `GAP-060`.

**Estimated scope:** Medium.

### Task 1: Strengthen Trace Grading And Postmortem Inputs

**Purpose:** Turn trace records into the first optimization-grade runtime signal.

**Files:**
- Modify: `docs/specs/eval-and-trace-grading-spec.md`
- Modify: `schemas/jsonschema/eval-trace-policy.schema.json`
- Modify: `docs/architecture/minimum-viable-governance-loop.md`
- Modify: `docs/backlog/issue-ready-backlog.md`
- Create: `docs/change-evidence/<date>-trace-grading-improvement-baseline.md`

**Acceptance criteria:**
- [x] Trace grading distinguishes evidence completeness, workflow correctness, replay readiness, and proposal input quality.
- [x] The governance loop explicitly includes trace grading and improvement proposal generation after evidence persistence.
- [x] The lane backlog links trace grading to later rollout and proposal tasks.

**Verification:**
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`.

**Dependencies:** Task 0.

**Estimated scope:** Small.

### Task 2: Harden Repo Admission And Compatibility Signals

**Purpose:** Make repo reuse safer before broad optimization claims are made across attached repositories.

**Files:**
- Modify: `docs/specs/repo-admission-minimums-spec.md`
- Modify: `schemas/jsonschema/repo-admission-minimums.schema.json`
- Modify: `docs/architecture/governance-boundary-matrix.md`
- Modify: `docs/backlog/issue-ready-backlog.md`
- Create: `docs/change-evidence/<date>-repo-admission-compatibility-hardening.md`

**Acceptance criteria:**
- [x] Repo admission can describe stronger compatibility and readiness signals without weakening kernel rules.
- [x] Knowledge and eval readiness are treated as admission or warning signals, not implicit assumptions.
- [x] Cross-repo reuse boundaries remain explicit.

**Verification:**
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`.

**Dependencies:** Task 1.

**Estimated scope:** Small.

### Task 3: Add Control Rollout And Waiver Recovery Semantics

**Purpose:** Make observe-to-enforce promotion and exception recovery explicit before optimization controls tighten.

**Files:**
- Modify: `docs/specs/control-registry-spec.md`
- Modify: `schemas/jsonschema/control-registry.schema.json`
- Modify: `docs/specs/waiver-and-exception-spec.md`
- Modify: `schemas/jsonschema/waiver-and-exception.schema.json`
- Modify: `docs/product/maintenance-deprecation-and-retirement-policy.md`
- Create: `docs/change-evidence/<date>-control-rollout-waiver-recovery.md`

**Acceptance criteria:**
- [x] Progressive controls can express rollout state, review cadence, and rollback posture.
- [x] Waivers remain temporary and tied to recovery plans rather than becoming silent permanent exceptions.
- [x] Maintenance and retirement policy reference the same rollout and recovery discipline.

**Verification:**
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`.

**Dependencies:** Task 2.

**Estimated scope:** Medium.

### Task 4: Govern Knowledge Sources And Repo Maps

**Purpose:** Turn repo-map and curated knowledge inputs into reviewable governance assets.

**Files:**
- Modify: `docs/specs/knowledge-source-spec.md`
- Modify: `schemas/jsonschema/knowledge-source.schema.json`
- Modify: `docs/specs/repo-map-context-shaping-spec.md`
- Modify: `schemas/jsonschema/repo-map-context-shaping.schema.json`
- Create: `docs/change-evidence/<date>-knowledge-registry-and-repo-map.md`

**Acceptance criteria:**
- [x] Knowledge sources can express trust, freshness, precedence, and drift expectations.
- [x] Repo-map context shaping is treated as a governed input, not a hidden agent-side behavior.
- [x] Memory-like sources remain non-authoritative.

**Verification:**
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`.

**Dependencies:** Task 3.

**Estimated scope:** Small.

### Task 5: Extend Provenance And Attestation Coverage

**Purpose:** Add provenance discipline to governance assets without replacing evidence or approval records.

**Files:**
- Modify: `docs/specs/provenance-and-attestation-spec.md`
- Modify: `schemas/jsonschema/provenance-and-attestation.schema.json`
- Modify: `docs/backlog/issue-ready-backlog.md`
- Create: `docs/change-evidence/<date>-governance-asset-provenance.md`

**Acceptance criteria:**
- [x] Governance assets can express provenance minimums and verification state.
- [x] Provenance remains additive to evidence and rollback.
- [x] The backlog makes clear which governance assets should carry provenance first.

**Verification:**
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`.

**Dependencies:** Task 4.

**Estimated scope:** Small.

### Task 6: Define Controlled Improvement Proposals

**Purpose:** Enable structured improvement proposals while prohibiting autonomous kernel mutation.

**Files:**
- Modify: `docs/architecture/minimum-viable-governance-loop.md`
- Modify: `docs/architecture/governance-boundary-matrix.md`
- Modify: `docs/backlog/issue-ready-backlog.md`
- Create: `docs/change-evidence/<date>-controlled-improvement-proposals.md`

**Acceptance criteria:**
- [x] Improvement proposals are fed by traces, postmortems, and repeated failures.
- [x] Proposal outputs are clearly separated from automatic policy or kernel mutations.
- [x] Boundaries for unified governance, repo inheritance, override, and exclusion remain explicit.

**Verification:**
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`.

**Dependencies:** Task 5.

**Estimated scope:** Small.

### Task 7: Close The Lane With Explicit Claim Discipline

**Purpose:** Finish the lane with evidence-backed claims, deferred items, and rollback notes.

**Files:**
- Modify: `docs/roadmap/governance-optimization-lane-roadmap.md`
- Modify: `docs/plans/governance-optimization-lane-implementation-plan.md`
- Modify: `docs/backlog/issue-ready-backlog.md`
- Create: `docs/change-evidence/<date>-governance-optimization-lane-closeout.md`

**Acceptance criteria:**
- [x] The lane records allowed claims, prohibited claims, and residual risks.
- [x] Deferred non-goals remain explicit.
- [x] Closeout references real verification evidence rather than plan-only assertions.

**Verification:**
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`.
- [x] Run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`.

**Dependencies:** Task 6.

**Estimated scope:** Small.
