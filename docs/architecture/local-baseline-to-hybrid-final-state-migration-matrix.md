# Local Baseline To Hybrid Final-State Migration Matrix

## Purpose
This document explains how the completed local baseline (`GAP-020` through `GAP-034`) relates to:

- the landed hybrid product boundary and hardening dependencies (`GAP-035` through `GAP-044`)
- the active direct-to-hybrid closure queue (`GAP-045` through `GAP-060`)

It answers one operational question directly:

> Do the historical completed plans and their landed code conflict with the new hybrid final state?

The answer is:

- not as baseline execution history or reusable kernel slices
- yes if the local baseline is misrepresented as the finished cross-repo product boundary

## Decision Summary
- Historical completed plans remain valid execution history.
- Landed runtime code under `packages/contracts/` remains the current kernel baseline unless it is explicitly replaced by active productization or strategy-alignment work.
- Repo-root runtime entrypoints such as `.runtime/`, CLI-first status, and local operator helpers remain valid for local bootstrap, smoke verification, recovery, and packaging.
- Those entrypoints are not the final deployment boundary for the attach-first product.
- Final-state work must change boundary placement and interface shape before it changes core task, evidence, verification, and rollback semantics.
- The active future-facing closure queue is now the direct-to-hybrid mainline (`GAP-045` through `GAP-060`), not the already-landed `GAP-035` through `GAP-044` slice.
- The governance-optimization lane (`GAP-061` through `GAP-068`) was follow-on work after `GAP-060` and is complete on the current branch baseline (verified on 2026-04-20); it is still not part of the closure proof for the hybrid final-state claim itself.

## Engineering-State Layers (2026-04-21)
- `Current Landed Runtime`: local kernel + local facade + SQLite/filesystem compatibility path.
- `Transition Runtime Target`: FastAPI control-plane boundary, optional Postgres metadata for `verification_runs` and `adapter_events`, and durable adapter-event sink.
- `North-Star Best-Practice Runtime`: broader service decomposition, stronger workflow orchestration, and wider host productization depth.

## Interpretation Rules
- Treat the completed local runtime as a `single-machine baseline`, not as the final attach-first product.
- Keep historical plans in `docs/plans/` as closed execution records; do not rewrite them to pretend they were designed for the new final shape.
- Keep mutable task, run, artifact, approval, and replay state machine-local in the final product, even though the current baseline stores them under this repo root.
- Treat repo-local packs or bundles as declarative inputs or runtime-consumable outputs, not as replacements for this repository's source-of-truth authoring structure.
- Treat the current write-policy and approval flow as a local baseline slice until `PolicyDecision` becomes the stable host-facing decision interface.

## Migration Matrix
| Surface | Historical completed shape | Hybrid final-state target | Assessment | Required action |
|---|---|---|---|---|
| Durable task and evidence kernel | `task_store.py`, `execution_runtime.py`, `verification_runner.py`, `evidence.py`, `delivery_handoff.py`, and `replay.py` provide a local, file-backed kernel for task state, verification, evidence, handoff, and replay. | Keep the kernel durable and machine-local behind attachment and adapter boundaries. | Aligned reusable kernel. | Reuse these primitives behind binding, session bridge, and adapter layers instead of copying them into target repos. |
| Repo profile and declarative repo inputs | Repo profiles, specs, schemas, and examples already exist and can drive current local flows. | Target repos expose a light pack or repo-native contract bundle validated from stable source inputs. | Compatible but incomplete. | Implement attachment binding plus light-pack generation or validation in `GAP-035` and `GAP-042`. |
| Runtime state placement | `scripts/bootstrap-runtime.ps1`, `scripts/run-governed-task.py`, `scripts/serve-operator-ui.py`, and `runtime_status.py` originally assumed `.runtime/` under the current repo root. | Repo-local declarations stay light; mutable runtime state lives in a machine-wide sidecar or equivalent machine-local binding root. | Runtime roots model landed; `.runtime/` is now compatibility mode rather than default. | Keep repo-root `.runtime/` for rollback/compatibility (`--compat-runtime-root`), while defaulting runtime execution to machine-local roots resolved by `runtime_roots.py`. |
| Session entrypoint | `run-governed-task.py` is CLI-first; `run-readonly-trial.py` is an explicit scripted trial path. | `attach-first` session bridge is the default product surface; `launch-second` remains fallback only. | Compatible fallback, not final primary surface. | Preserve CLI and scripted trial for smoke, replay, and recovery; add governed session bridge commands in `GAP-036`. |
| Codex integration | `trial_entrypoint.py` exposes `codex.cli.compatible` as `manual_handoff` with user-owned upstream auth and explicit degrade posture. | Add a direct Codex adapter path while keeping the kernel compatible with future agent products. | Compatible transitional surface. | Keep manual handoff as a visible degrade tier and add direct adapter plus evidence mapping in `GAP-037`. |
| Non-Codex tool support | `second_repo_pilot.py` includes a generic process adapter declaration with explicit compatibility gaps. | Capability-tiered adapter registry supports Codex-first and at least one non-Codex path without kernel forks. | Aligned seed, not a finished framework. | Generalize the current adapter declarations into a registry, capability tiers, and degrade fixtures in `GAP-038`. |
| Policy and approval interface | `write_policy.py` and `write_tool_runner.py` wire risk tier and approval flow directly. | `PolicyDecision` becomes the stable `allow / escalate / deny` interface before execution-like session commands proceed. | Semantic gap, not a hard contradiction. | Keep current write-side governance as the local baseline and insert `PolicyDecision` in `GAP-043` before deeper adapter work. |
| Workspace isolation | `workspace.py` originally enforced isolated relative workspaces under `.governed-workspaces/` and validated write paths from repo profiles. | Workspaces remain isolated and policy-bound, but binding and location become machine-local rather than implicitly repo-root. | Guardrail retained; runtime-root-aware workspace placement landed. | Preserve isolation and path validation while allocating default workspaces under `runtime_roots.workspaces_root`; keep relative `.governed-workspaces/` path as compatibility behavior. |
| Multi-repo semantics | `second_repo_pilot.py` and its tests prove that multiple repo profiles can share kernel semantics without kernel forks. | Real multi-repo attachment, trial execution, and onboarding evidence operate against attached target repos. | Aligned proof point, not the finished product loop. | Build attachment binding, trial evidence model, and multi-repo runner in `GAP-039`. |
| Operator surface | `runtime_status.py` and `operator_ui.py` expose local task, evidence, replay, and maintenance visibility for the baseline runtime. | Control-plane visibility extends to attached repos, binding posture, adapter posture, and session compatibility. | Compatible read-model seed, not the finished operator surface. | Extend the read model after attachment and adapter work instead of replacing the current local operator baseline prematurely. |

## What Is Safe To Reuse As-Is
- task lifecycle persistence and transition semantics
- verification runner ordering and evidence bundle assembly
- replay and delivery handoff primitives
- isolated workspace path validation semantics
- compatibility and degrade posture as an explicit concept

## What Must Not Be Misrepresented As Final State
- repo-root `.runtime/` as the final state placement model
- CLI-first `create/run/status` as the final primary interaction model
- manual-handoff Codex compatibility as equivalent to direct attach
- direct write-policy-to-approval wiring as the final host-facing decision interface

## Landed Boundary And Follow-On Closure Queue
- Already landed hybrid boundary and hardening dependencies:
  - `GAP-035`: target-repo attachment binding and light-pack surface
  - `GAP-036`: attach-first session bridge with launch-second fallback
  - `GAP-037`: direct Codex adapter and runtime evidence mapping
  - `GAP-038`: capability-tiered generic adapter framework
  - `GAP-039`: multi-repo trial loop and onboarding evidence
  - `GAP-042`: repo-native contract bundle architecture
  - `GAP-043`: `PolicyDecision` contract
  - `GAP-044`: local and CI same-contract verification hardening
- Active direct-to-hybrid closure queue:
  - `GAP-045` through `GAP-060`
- Completed governance-only follow-on lane after closure:
  - `GAP-061` through `GAP-068`

## Source References
- [Full Lifecycle Plan](../roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md)
- [Direct-To-Hybrid Final-State Roadmap](../roadmap/direct-to-hybrid-final-state-roadmap.md)
- [Direct-To-Hybrid Final-State Implementation Plan](../plans/direct-to-hybrid-final-state-implementation-plan.md)
- [Governance Optimization Lane Roadmap](../roadmap/governance-optimization-lane-roadmap.md)
- [Governed AI Coding Runtime Target Architecture](./governed-ai-coding-runtime-target-architecture.md)
- [Governance Runtime Strategy Alignment Plan](../plans/governance-runtime-strategy-alignment-plan.md)
- [Interactive Session Productization Implementation Plan](../plans/interactive-session-productization-implementation-plan.md)
- [Full Runtime Implementation Plan](../plans/full-runtime-implementation-plan.md)
- [Public Usable Release Implementation Plan](../plans/public-usable-release-implementation-plan.md)
- [Maintenance Implementation Plan](../plans/maintenance-implementation-plan.md)
- [run-governed-task.py](../../scripts/run-governed-task.py)
- [bootstrap-runtime.ps1](../../scripts/bootstrap-runtime.ps1)
- [serve-operator-ui.py](../../scripts/serve-operator-ui.py)
- [trial_entrypoint.py](../../packages/contracts/src/governed_ai_coding_runtime_contracts/trial_entrypoint.py)
- [second_repo_pilot.py](../../packages/contracts/src/governed_ai_coding_runtime_contracts/second_repo_pilot.py)
- [write_policy.py](../../packages/contracts/src/governed_ai_coding_runtime_contracts/write_policy.py)
- [write_tool_runner.py](../../packages/contracts/src/governed_ai_coding_runtime_contracts/write_tool_runner.py)
- [workspace.py](../../packages/contracts/src/governed_ai_coding_runtime_contracts/workspace.py)
