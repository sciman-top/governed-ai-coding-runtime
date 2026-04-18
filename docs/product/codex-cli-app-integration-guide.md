# Codex CLI/App Integration Guide

## Purpose
Explain how to use this repository alongside Codex CLI/App today without overstating the current integration level.

## Current State
- This project is **Codex CLI/App compatible first**, but it is **not yet a direct Codex execution adapter**.
- The current runtime can bootstrap local state, load repo profiles, track tasks, run governed verification gates, persist evidence and replay artifacts, and expose runtime status.
- The current runtime does **not** directly invoke Codex to perform real coding work through a managed adapter worker.

## What Works Today

### 1. Manual-Handoff Governance Around Codex
Use this repository as the governance layer around a Codex-driven coding session:
- define or inspect repo expectations through repo profiles
- run local readiness checks with `bootstrap`, `doctor`, and `verify-repo`
- record or inspect governed runtime status
- preserve local evidence, verification, and replay artifacts for runtime-managed tasks

### 2. Codex-Compatible Read-Only Trial
The first Codex-related path is intentionally conservative:
- it models Codex as an adapter declaration
- it preserves upstream Codex authentication ownership
- it stays in manual handoff and read-only mode

See:
- [First Read-Only Trial](./first-readonly-trial.md)
- [Adapter Degrade Policy](./adapter-degrade-policy.md)

### 3. Runtime Smoke Task
`python scripts/run-governed-task.py run --json` proves the local governed runtime path:
- task persistence
- workspace allocation
- gate execution
- evidence and handoff generation
- runtime status projection

It should be understood as a **runtime smoke task**, not as a direct Codex coding integration.

## Recommended Workflow Today

### Option A: Use Codex Normally, Use This Repo As Governance Sidecar
Recommended when you want the least friction.

1. Run:
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/bootstrap-runtime.ps1`
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
2. Work in Codex CLI/App as usual.
3. Use this repository's docs and repo profile conventions as the governance baseline.
4. Run:
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
5. If you want runtime artifacts for the local governed path, run:
   - `python scripts/run-governed-task.py status --json`
   - `python scripts/serve-operator-ui.py`

### Option B: Use Manual Handoff Before Or After A Codex Session
Recommended when you want an explicit governed wrapper around a bounded task.

1. Use the read-only trial to validate the repo profile and adapter posture.
2. Run Codex CLI/App manually for the real coding work.
3. Use this repository's verification, evidence, and operator surface to inspect local governed outputs.

## What Is Not Implemented Yet
- no direct `codex` command invocation from `scripts/run-governed-task.py`
- no managed adapter worker that captures Codex prompts, edits, tool calls, or diffs as first-class runtime events
- no long-running Codex session orchestration inside this runtime
- no claim that the current smoke task represents real Codex-produced code changes

## Future Boundary For A Direct Codex Adapter
If a future direct Codex adapter is added, it should satisfy all of the following:
- remain adapter-owned rather than leaking Codex-specific semantics into the kernel
- preserve user-owned upstream authentication unless a separate integration decision is accepted
- emit enough run-level evidence to keep approvals, artifacts, verification, and rollback honest
- degrade explicitly when Codex capability surfaces are weaker than full governed enforcement expects
- preserve the canonical gate order `build -> test -> contract/invariant -> hotspot`

This section is a boundary definition, not a delivery promise or timeline commitment.

## Bottom Line
Today, this repository is best used as:
- a local governed runtime substrate
- a governance sidecar around Codex workflows
- a documented compatibility boundary for future deeper Codex integration

It should not be described as "Codex is already directly integrated and executing coding work through the runtime."
