# Hybrid Final-State Master Outline

## Status
- This file is the canonical high-level entry for understanding the repository's hybrid final state.
- It does not replace the PRD, target architecture, lifecycle plan, ADRs, specs, or implementation plans.
- It defines how those files should be read together and what each one should own.

## Purpose
- Give the repository one explicit master outline for the hybrid final state.
- Explain why the current branch still looks script-heavy even though the end state is service-shaped.
- Separate:
  - current landed baseline
  - transition architecture
  - final-state best-practice architecture
- Define the direct path from today's branch baseline to the complete hybrid final state.

## Why This File Is Needed
The repository already has strong material, but it is split across several documents:
- product problem and value: `docs/prd/governed-ai-coding-runtime-prd.md`
- final-state north-star architecture: `docs/architecture/governed-ai-coding-runtime-target-architecture.md`
- current lifecycle and stage history: `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- MVP vs target stack trade-off: `docs/architecture/mvp-stack-vs-target-stack.md`

That split is useful for long-form reasoning, but it creates four recurring problems:
- readers have to reconstruct the actual canonical posture themselves
- "Stage complete" wording is easy to misread as "final state complete"
- the target stack looks too far from the landed code shape
- the PRD, architecture, and lifecycle docs have started to overlap in responsibility

This file is the compression layer that removes that ambiguity.

## Canonical Product Boundary
`governed-ai-coding-runtime` is a governance/runtime layer for AI coding sessions.

It is:
- a control and execution boundary around upstream AI coding hosts
- repository-aware
- evidence-first
- approval-aware
- verification-aware
- replay and rollback aware

It is not:
- a replacement IDE
- a new primary AI coding host
- a wrapper-first shell product
- a generation guardrail product

## Canonical Final Product Shape
The hybrid final state is:

`repo-local contract bundle + machine-local durable governance kernel + attach-first host adapters + same-contract verification/delivery plane`

In practical terms that means:
- target repositories keep only lightweight repo-local declarations and attachment metadata
- mutable runtime state stays machine-local
- governed actions are available inside an attached AI coding session when possible
- launch-mode fallback remains explicit when attach is unavailable
- host-specific behavior is isolated behind capability-tiered adapters
- verification, evidence, delivery, replay, and rollback use one shared contract model

## Current Baseline
The current branch baseline has already proven and landed:
- docs-first and contracts-first source-of-truth structure
- local durable task, evidence, replay, and handoff primitives
- local runtime execution and verification entrypoints
- target-repo attachment binding and light-pack generation or validation
- first attachment-aware verification execution
- first attached write governance and execution loop
- session-bridge contract and local entrypoint
- Codex posture contract and safe smoke-trial surface
- generic adapter capability-tier contract
- profile-based multi-repo trial evidence model and sample runner

This means the repository is not "just ideas and scripts." It already contains a validated governance kernel and a first attach-oriented product boundary.

## Capability Closure Snapshot
Use this table to separate "already landed on the current branch baseline" from "still required before complete hybrid final-state closure."

| surface | landed on current branch baseline | still missing for complete closure |
|---|---|---|
| Session bridge | `write_request` / `write_approve` / `write_execute` / `write_status`, `inspect_evidence`, `inspect_handoff`, status and posture reads already exist. | quick/full gate paths still return plans rather than runtime-managed execution; live host continuation identity is not yet bound end-to-end. |
| Attached write flow | runtime-owned attached write governance and execution loop exists and is tested through the local session bridge surface. | not yet proven as a live-host-backed attached external-repo execution chain with real adapter/session identity. |
| Codex direct adapter | posture, capability-tier projection, smoke-trial evidence mapping, and session-evidence normalization exist. | no real handshake, live attach, or runtime ingestion of real Codex session events yet. |
| Multi-repo trial | profile-based trial model, structured records, and sample runner exist. | not yet a real attached external-repo onboarding loop with differentiated runtime-sourced outcomes. |
| Governed execution coverage | file-write execution path exists. | shell, git, package-manager, and helper-tool execution are not yet on the same governed surface. |
| Runtime root placement | attached flows can already point at machine-local runtime state roots. | self-runtime still defaults to repo-root `.runtime/` and repo-relative workspace roots. |

## Why The Repository Still Looks Script-Heavy
The repository still looks script-heavy because the landed baseline is a deliberate tracer-bullet implementation, not the final deployment shape.

The current branch optimized for:
- proving the governed execution loop
- proving contract and schema boundaries
- keeping the system machine-local and inspectable
- minimizing infra width before the execution model is stable

That choice was valid for the baseline and the first productization slices.

The scripts currently do four jobs:
- local operator entrypoints
- verification and doctor entrypoints
- attachment and trial entrypoints
- thin execution harnesses around contract primitives

What they are not:
- the intended final runtime packaging model
- the final service boundary
- the final adapter runtime
- the final control-plane surface

So the difference is large, but it is not accidental drift. It is an intentional gap between:
- `landed proof shape`
- `transition shape`
- `final production shape`

The current problem is no longer "why are there scripts?" The current problem is "the transition from script-heavy proof shape to service-shaped hybrid runtime has not yet been made canonical and executable."

## Architecture Tiers

### 1. Current Landed Baseline
This is the code shape that exists now.

Primary characteristics:
- Python-centric runtime contracts
- filesystem-backed durable state
- PowerShell and Python entrypoints
- local `.runtime/` and attachment runtime roots
- JSON Schema and Markdown as source contracts
- local HTML and CLI-first operator surfaces

Representative stack:
- Python 3.x standard library
- `packages/contracts/`
- filesystem-backed `.runtime/`
- PowerShell verification entrypoints
- Markdown docs
- JSON Schema draft 2020-12

This tier is real, tested, and useful. It is not the final delivery model.

## Engineering-State Layers (2026-04-21)

### Current Landed Runtime
- local governed runtime kernel
- local facade control surface
- SQLite/filesystem compatibility path

### Transition Runtime Target
- real FastAPI control plane (`apps/control-plane/http_app.py`)
- optional Postgres metadata backend for `verification_runs` and `adapter_events`
- durable adapter event sink reused by operator reads

### North-Star Best-Practice Runtime
- broader service decomposition and workflow orchestration
- richer multi-host adapter productization beyond Codex-first depth
- deeper runtime operations and policy plane hardening

### 2. Committed Transition Architecture
This is the architecture that should be treated as the direct path from the current branch to the hybrid final state.

Primary characteristics:
- keep the kernel machine-local and durable
- turn session, approval, execution, and evidence flows into stable runtime APIs
- move from script-only entrypoints toward service-shaped boundaries
- keep the target repo light and the runtime state machine-local
- add live host integration before broad platform width

Recommended transition stack:
- Python 3.12+
- FastAPI for runtime API and session/control surfaces
- Pydantic v2 for typed runtime contracts
- PostgreSQL for durable task, approval, and evidence metadata
- local filesystem in dev plus object-store abstraction for artifacts
- OpenTelemetry for runtime tracing
- existing contract package reused behind service boundaries

Deferred from the direct transition unless justified by real pressure:
- `NATS JetStream`
- `Redis`
- `pgvector`
- `gRPC`
- A2A gateway
- full multi-service decomposition

### 3. Final-State Best-Practice Architecture
This is still the north star, not the mandatory next commit shape.

Primary characteristics:
- control-plane-first
- durable workflow orchestration
- governed agent execution
- event-driven observability
- service-shaped internal deployment
- attach-first host integration
- same-contract local and CI verification

Final-state candidate stack:
- Python 3.12+
- FastAPI
- Pydantic v2
- Temporal
- PostgreSQL
- pgvector
- Redis
- S3-compatible object storage
- OPA/Rego
- OpenTelemetry
- Prometheus / Grafana / Loki / Tempo or Jaeger
- Next.js
- TypeScript
- Tailwind

## Current Blocking Gap To Complete Hybrid Final State
The direct-to-final-state blocking and hardening gaps (`HFG-001` through `HFG-H3`) are implemented on the current branch baseline through `GAP-060`.

The remaining risk is claim drift, not missing implementation slices:
- complete-closure claims must stay tied to fresh executable evidence
- if verification or evidence drifts, claim wording must downgrade immediately until re-validated

Reference audit:
- `docs/reviews/2026-04-19-hybrid-final-state-executable-gap-audit.md`

## Recommended Planning Choice
The recommended planning choice is:

`incremental re-baseline, direct-to-final-state`

Meaning:
- preserve current GAP history as execution history
- preserve the current kernel and landed attachment/productization slices as validated substrate
- stop treating the historical lifecycle file as the only future mainline
- create a new canonical planning package for the direct path to complete hybrid final-state closure

Do not choose a full clean-sheet rewrite unless all of the following are true:
- existing GAP history is being abandoned
- backward compatibility expectations are being dropped
- the current kernel and contracts are being treated as throwaway prototypes

That is not the current repository posture and would likely destroy useful execution history.

## Improvement Recommendations For Existing Canonical Files

### `docs/prd/governed-ai-coding-runtime-prd.md`
Keep:
- problem statement
- product goals
- user stories
- capability boundary
- acceptance metrics

Reduce or move out:
- detailed implementation decisions
- detailed testing decisions
- long baseline execution-history material

Target role:
- product and capability source

### `docs/architecture/governed-ai-coding-runtime-target-architecture.md`
Keep:
- north-star architecture
- control-plane / execution-plane / assurance-plane / data-plane decomposition
- default delivery shape
- final-state candidate stack

Improve:
- add an explicit section for `Current Baseline vs Transition Architecture vs Final-State Architecture`
- mark the current target stack as north star, not next mandatory implementation slice
- pull key conclusions from `mvp-stack-vs-target-stack.md` into the main architecture doc

Target role:
- best-practice end-state architecture source

### `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
Keep:
- stage history
- what is complete on the current branch baseline
- lifecycle completion criteria

Improve:
- explicitly state that Stage 7/8 completion does not equal full hybrid final-state closure
- stop using this file as the only future-facing main roadmap
- pair it with a new direct-to-final-state roadmap

Target role:
- lifecycle history plus current posture

### `docs/architecture/mvp-stack-vs-target-stack.md`
Keep:
- the stack split
- the anti-confusion rule between target-state optionality and MVP obligation

Improve:
- promote its conclusion into the canonical master narrative instead of leaving it as an auxiliary note

Target role:
- stack interpretation and transition guardrail

## Direct Path To The Complete Hybrid Final State

### Phase 0: Canonical Re-Baseline
Goal:
- make the planning and document ownership model canonical before deeper implementation continues

Exit criteria:
- a master outline exists
- a direct-to-final-state roadmap exists
- a direct-to-final-state implementation plan exists
- backlog and issue seeds are aligned to that mainline

### Phase 1: Close The Governed Execution Surface
Goal:
- turn the current partial bridge and attached-write loop into the first complete governed execution surface

Scope:
- full session-bridge command surface
- attached write requests through session bridge
- approval continuation through session bridge
- evidence and handoff inspection through session bridge
- governed shell, git, and package-manager execution boundaries

Exit criteria:
- one attached repo can complete a governed medium-risk write loop entirely through the runtime surface

### Phase 2: Close Live Host Adapter Reality
Goal:
- move Codex and future adapters from posture declarations to live runtime integration

Scope:
- live attach or launch handshake
- session identity and continuation identity
- real event ingestion
- real evidence export mapping
- adapter runtime selection logic

Exit criteria:
- at least one real Codex path produces task, approval, execution, evidence, and handoff linkage from a live session

### Phase 3: Close Real Multi-Repo And Sidecar Reality
Goal:
- make multi-repo and machine-local state placement real, not sample-driven

Scope:
- real attached external-repo trial runner
- real onboarding feedback capture
- machine-local runtime root as the default posture
- workspace placement no longer tied to implicit repo-root defaults

Exit criteria:
- at least two real attached external repos can run the onboarding and trial loop without kernel rewrites

### Phase 4: Extract Service-Shaped Runtime
Goal:
- move from script-heavy local harnesses to stable service-shaped runtime boundaries

Scope:
- control and session API
- operator read API
- execution API or worker boundary
- artifact and evidence persistence abstraction
- clearer `apps/`, `packages/`, `infra/`, `tests/` physical shape

Exit criteria:
- the runtime can be run as a service-shaped local deployment without losing current contract parity

### Phase 5: Hardening And Operational Completion
Goal:
- close the gap from functioning hybrid runtime to stable, auditable, repeatable operating baseline

Scope:
- local and CI same-contract parity beyond verifier-only scope
- richer operator and control-plane surfaces
- remediation-capable doctor and posture handling
- observability hardening
- policy hardening

Exit criteria:
- runtime, adapters, CI, and operator surfaces all consume the same declared contract model and expose remediable failures

## What "Complete Hybrid Final State" Should Mean
The repository should only claim complete hybrid final-state closure when all of the following are true:
- a target repo can attach without copying the kernel
- runtime state is machine-local by default
- governed actions are usable from an attached AI coding session
- medium and high-risk writes flow through deterministic policy and approval
- verification, evidence, replay, rollback, and handoff stay inside one runtime-owned task model
- at least one live Codex path is real, not smoke-only
- at least one non-Codex path exists with honest runtime guarantees
- multi-repo trial evidence comes from real attached repositories, not only sample profiles
- the service-shaped deployment boundary is no longer hypothetical

Claim reference:
- `docs/change-evidence/20260420-direct-to-hybrid-final-state-closeout.md`

## Canonical Planning Package
The canonical planning package now consists of three direct companions:

1. direct-to-final-state roadmap
2. direct-to-final-state implementation plan
3. aligned backlog and task list

Those files are now the active mainline for future completion work.

## Source References
- `docs/prd/governed-ai-coding-runtime-prd.md`
- `docs/architecture/governed-ai-coding-runtime-target-architecture.md`
- `docs/architecture/mvp-stack-vs-target-stack.md`
- `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- `docs/reviews/2026-04-18-hybrid-final-state-and-plan-reconciliation.md`
- `docs/reviews/2026-04-19-hybrid-final-state-executable-gap-audit.md`
