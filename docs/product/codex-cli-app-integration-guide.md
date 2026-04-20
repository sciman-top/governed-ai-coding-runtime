# Codex CLI/App Integration Guide

## Purpose
Explain how to use this repository with Codex CLI/App using the current executable capability boundary.

## Current State
- This project remains **Codex-compatible first** and keeps Codex auth ownership upstream (`user_owned_upstream_auth`).
- The runtime now exposes a direct Codex adapter surface for capability probing, session-identity handshake, and adapter-tier projection.
- Governed session operations can run through the local session bridge with Codex identity attached (`run_quick_gate`, `run_full_gate`, `write_request`, `write_approve`, `write_execute`, `write_status`).
- Capability posture is environment-dependent and may degrade (`native_attach -> process_bridge -> manual_handoff`) with explicit reasons.

## What Works Today

### 1. Capability Readiness And Degrade Visibility
The runtime can probe Codex capability and expose readiness posture from runtime status and doctor surfaces:
- adapter tier (`native_attach`, `process_bridge`, `manual_handoff`)
- flow kind (`live_attach`, `process_bridge`, `manual_handoff`)
- unsupported capabilities with explicit degrade behavior
- remediation hints and probe stability metadata

### 2. Runtime-Managed Session Bridge Surface
The local session bridge can execute governed gate and write flows with Codex identity metadata attached:
- `run_quick_gate` / `run_full_gate` execute verification by default (`plan_only` remains available)
- `write_request` / `write_approve` / `write_execute` / `write_status` enforce policy and approval requirements
- execution outputs include continuation identity plus evidence, handoff, and replay references
- adapter evidence mapping is emitted for governed execution events

### 3. Codex Adapter Smoke Trial
`scripts/run-codex-adapter-trial.py` remains available as a deterministic adapter-surface check.
- default mode is still safe-mode
- `--probe-live` can derive posture from live Codex capability probing

See:
- [First Read-Only Trial](./first-readonly-trial.md)
- [Adapter Degrade Policy](./adapter-degrade-policy.md)
- [Codex Direct Adapter](./codex-direct-adapter.md)

### 3. Runtime Smoke Task
`python scripts/run-governed-task.py run --json` proves the local governed runtime path:
- task persistence
- workspace allocation
- gate execution
- evidence and handoff generation
- runtime status projection

It should be understood as a **runtime smoke task**, not as a direct Codex coding integration.

## Recommended Workflow Today

### Option A: Attach-First Governed Flow (Recommended)
Use this when you want the runtime to manage attachment posture, gate execution, and write governance in one flow.

1. Run:
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/bootstrap-runtime.ps1`
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
2. Attach or validate the target repository light pack.
3. Run one-command daily flow:
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow.ps1 -FlowMode "daily" ...`
4. Verify full gates when needed:
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
5. Inspect runtime evidence/status surfaces:
   - `python scripts/run-governed-task.py status --json`
   - `python scripts/serve-operator-ui.py`

### Option B: Codex-Native Session + Governance Sidecar
Use this when you want minimal workflow change.

1. Run Codex CLI/App as your primary host workflow.
2. Use this runtime for readiness checks, governed verification, and evidence/handoff/replay inspection.
3. Use session-bridge commands only for bounded governed operations when needed.

## What Is Not Implemented Yet
- no runtime-owned replacement of the upstream Codex host UX
- no service-owned Codex authentication model (by design)
- no long-running managed Codex orchestration worker that ingests full upstream prompt/edit/tool-call streams as first-class runtime events
- no guarantee that `native_attach` is available in every host environment or Codex build
- no claim of universal full takeover for every external repo and every high-risk workflow

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
- a Codex-compatible governed execution layer with explicit capability tiers and degrade rules
- a governance sidecar around Codex workflows where full host replacement is not required

It should not be described as "the runtime fully replaces Codex host execution in every environment."
