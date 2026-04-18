# Interactive Session Productization Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Execute `GAP-035` through `GAP-039` so the current local runtime baseline evolves into a generic, attach-first, interactive governed AI coding runtime that can onboard many target repositories and integrate with real AI coding sessions.

**Architecture:** Build on the landed local runtime rather than replacing it. Keep the kernel machine-local and durable. Add a repo-local light pack, an attach-first session bridge, a direct Codex path, capability-tiered adapters for non-Codex tools, and structured multi-repo trial evidence. Batch CLI remains a fallback path for automation, replay, and recovery, not the primary product surface.

**Tech Stack:** Python 3.x standard library, `packages/contracts/` domain models, local filesystem persistence under `.runtime/`, PowerShell entrypoints under `scripts/`, Markdown docs under `docs/`, JSON Schema under `schemas/jsonschema/`, and the existing repo profile plus adapter contract surfaces.

---

## Source Inputs
- `docs/prd/governed-ai-coding-runtime-prd.md`
- `docs/product/interaction-model.md`
- `docs/architecture/governed-ai-coding-runtime-target-architecture.md`
- `docs/architecture/generic-target-repo-attachment-blueprint.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- `docs/change-evidence/20260418-maintenance-execution-plan.md`

## Planned File Structure

### Create
- `docs/architecture/generic-target-repo-attachment-blueprint.md`
- `docs/plans/interactive-session-productization-plan.md`
- `docs/change-evidence/20260418-interactive-session-productization-realignment.md`

### Modify
- `README.md`
- `README.zh-CN.md`
- `README.en.md`
- `docs/README.md`
- `docs/prd/governed-ai-coding-runtime-prd.md`
- `docs/product/interaction-model.md`
- `docs/architecture/README.md`
- `docs/architecture/governed-ai-coding-runtime-target-architecture.md`
- `docs/backlog/README.md`
- `docs/backlog/full-lifecycle-backlog-seeds.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/issue-seeds.yaml`
- `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- `docs/plans/README.md`
- `docs/change-evidence/README.md`
- `scripts/github/create-roadmap-issues.ps1`

## Task List

### Task 1: Re-anchor The Final Product Boundary

**Files:**
- Modify: `docs/prd/governed-ai-coding-runtime-prd.md`
- Modify: `docs/product/interaction-model.md`
- Modify: `docs/architecture/governed-ai-coding-runtime-target-architecture.md`

**Purpose:** Move the final target away from "single-machine lifecycle complete" and toward "generic, interactive, attach-first governed runtime."

**Steps:**
- [ ] Replace final-target wording that treats the local runtime baseline as the finished product.
- [ ] Make attach-first interactive sessions the preferred product posture.
- [ ] Add explicit requirements for repo-local light packs, machine-local runtime state, and multi-repo trial feedback.

### Task 2: Land The Generic Attachment Blueprint

**Files:**
- Create: `docs/architecture/generic-target-repo-attachment-blueprint.md`
- Modify: `docs/architecture/README.md`

**Purpose:** Give the project one canonical architecture document for repo-local light packs, machine-wide runtime state, and session bridges.

**Steps:**
- [ ] Define the three-layer model: repo-local pack, machine-wide sidecar, session bridge.
- [ ] Define attach-first and launch-second modes.
- [ ] Define capability tiers for adapters and state placement rules.

### Task 3: Rebase The Active Queue To GAP-035 Through GAP-039

**Files:**
- Modify: `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- Modify: `docs/backlog/full-lifecycle-backlog-seeds.md`
- Modify: `docs/backlog/issue-ready-backlog.md`
- Modify: `docs/backlog/issue-seeds.yaml`
- Modify: `docs/plans/README.md`

**Purpose:** Turn the new final-state direction into executable roadmap, backlog, and plan artifacts.

**Steps:**
- [ ] Preserve completed history through `GAP-034`.
- [ ] Add the interactive session productization stage and its acceptance criteria.
- [ ] Add `GAP-035` through `GAP-039` with blockers, user stories, and acceptance criteria.

### Task 4: Re-align Entry Docs And Automation Seeds

**Files:**
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `README.en.md`
- Modify: `docs/README.md`
- Modify: `scripts/github/create-roadmap-issues.ps1`

**Purpose:** Make repo entrypoints and issue-seeding automation agree on the new active lifecycle and product boundary.

**Steps:**
- [ ] Update all status summaries so they describe `GAP-034` as baseline complete, not final completion.
- [ ] Point entry docs to the generic attachment blueprint and active productization plan.
- [ ] Update issue-seeding script labels, initiative language, and new active epic or tasks.

### Task 5: Close The Planning Realignment With Evidence

**Files:**
- Create: `docs/change-evidence/20260418-interactive-session-productization-realignment.md`
- Modify: `docs/change-evidence/README.md`

**Purpose:** Record the reasoning, commands, risks, and rollback notes for the planning reset.

**Steps:**
- [ ] Record why the prior "steady-state maintenance" wording is no longer sufficient.
- [ ] Record the new active queue and supporting documents.
- [ ] Run `build -> test -> contract/invariant -> hotspot` plus `verify-repo -Check All` before closing the realignment.

## Checkpoints
- After Task 1: PRD, interaction model, and target architecture no longer overstate the landed baseline as the final product.
- After Task 2: there is one canonical generic attachment blueprint for future implementation work.
- After Task 3: roadmap, backlog, issue seeds, and plans agree on `GAP-035` through `GAP-039`.
- After Task 4: entry docs and GitHub issue seeding are aligned with the new lifecycle posture.
- After Task 5: the realignment is traceable and verified.
