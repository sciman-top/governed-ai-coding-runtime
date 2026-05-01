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

## External Benchmark Update (2026-04-27)
An external review against current official docs and mature community projects keeps the canonical hybrid shape, but tightens the engineering interpretation:

- Repository-local, versioned instructions and executable docs are still the right context surface for coding agents.
- MCP, A2A, Codex, Claude Code, Copilot, and future host integrations should remain adapter or protocol boundaries, not kernel semantics.
- Guardrails inside agent SDKs or host products are not sufficient by themselves; runtime-owned policy, approval, sandboxing, and evidence must remain deterministic.
- Durable execution is a capability requirement, but specific workflow engines should be introduced by trigger, not by platform aesthetics.
- Sandboxed execution is not an optional future polish item for shell, git, package-manager, browser, or MCP tools; it is part of the transition safety floor once write coverage broadens.
- Supply-chain provenance should be treated as a final-state evidence class for generated packages, target-repo light packs, and release artifacts.
- Current OpenAI sandbox guidance reinforces separating harness/control state from sandbox execution state; this matches the machine-local governance kernel plus bounded execution-workspace model.
- Current OpenAI Agents SDK guardrail guidance leaves hosted and built-in execution tools outside the function-tool guardrail pipeline, so runtime-owned approval, containment, evidence, and rollback remain mandatory.
- MCP roots and A2A 1.0.0 are protocol inputs to adapter conformance. MCP roots must be revalidated by the runtime, and any future A2A work must map versioning, authorization scoping, and in-task authorization onto existing kernel-owned semantics.

Decision:
- Keep the product shape.
- Strengthen acceptance criteria and roadmap wording around sandbox containment, protocol boundaries, trigger-based component adoption, and provenance-backed claims.
- Keep `GAP-111` certification valid only while current-source compatibility checks and claim-drift gates continue to pass.
- Do not start a clean-sheet rewrite or broaden the platform stack before the current runtime-owned loop remains re-verifiable.

## Current Best-State Answer (2026-04-27 Refresh)
The optimized hybrid target is the best current engineering direction for this repository, but it is not best if read as a one-shot platform stack.

Best interpretation:
- keep the product shape: `repo-local contract bundle + machine-local durable governance kernel + attach-first host adapters + same-contract verification/delivery plane`
- keep the current Python/PowerShell/filesystem baseline as the verified local proof surface
- promote to the direct transition stack only where the runtime has an active service, persistence, tracing, containment, or release boundary
- keep Temporal-class orchestration, `OPA/Rego`, event buses, semantic stores, A2A gateway, full observability suites, and rich web console work trigger-based

Not best interpretation:
- treating the current script-heavy baseline as the final architecture
- treating `GAP-093..103` as complete final-state implementation
- importing the whole north-star stack before live-host, adapter, execution, data, operations, and provenance evidence require it

Complete realization is now certified on the current branch baseline by the post-`GAP-103` queue `GAP-104..111`. Executing only `GAP-093..103` proved optimized health and trigger discipline; executing `GAP-104..111` with passing evidence produced the truthful complete hybrid final-state closure recorded in `docs/change-evidence/20260427-gap-111-complete-hybrid-final-state-certification.md`.

Post-`GAP-112`, the correct way to decide whether to keep pushing toward a heavier long-term stack is `scripts/evaluate-ltp-promotion.py`. The current policy answer is `defer_all`: do not directly force Temporal, OPA/Rego, event bus, object store, A2A gateway, full observability, or external signing without package-specific trigger evidence. Autonomous promotion is allowed when the policy selects exactly one `LTP-01..06` package with a scope fence, full gate reference, rollback, and one vertical slice; owner-directed heavy-stack work must be labeled separately.

Post-`GAP-113`, the correct way to decide what to do next is `scripts/select-next-work.py`. The current selector answer is `defer_ltp_and_refresh_evidence`: do not convert `defer_all` into hidden LTP implementation; keep gates, evidence, and source compatibility fresh until a higher-priority repair, refresh, selected LTP, or owner-directed scope appears.

The user has now explicitly made Claude Code a frequent day-to-day host. That created an owner-directed bounded scope after `GAP-114`: Codex and Claude Code should be dual first-class entrypoints in governance outcome. The bounded queue `GAP-115..119` is complete. It promotes Claude Code from generic non-Codex compatibility to first-class supported host status while keeping adapter-tier claims evidence-bound. This is not a claim that both hosts expose identical APIs or that degraded Codex target-run posture has recovered to `native_attach`, and it still does not start the full `LTP-04 multi-host-first-class` package by default.

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
Use this table to separate what is certified now from what remains trigger-based future expansion.

| surface | certified on current branch baseline | trigger-based future expansion |
|---|---|---|
| Session bridge | runtime-managed gate/write/status/evidence/handoff paths share the service/control contract and preserve continuation identity in tested runtime flows. | richer product UI after read models stabilize. |
| Attached write flow | medium-risk attached write and executable-tool loops pass approval, execution, evidence, replay, rollback, and handoff linkage. | broader high-risk catalogs only after explicit policy and containment expansion. |
| Codex direct adapter | a live Codex continuity path is recorded with `native_attach` posture, session/resume/continuation ids, runtime evidence, and explicit fallback semantics. | deeper host event ingestion when upstream exposes richer stable event surfaces. |
| Non-Codex adapter | at least one generic non-Codex path passes parity through honest `manual_handoff` degraded posture without bypassing runtime-owned guarantees. | first-class productization for additional hosts when demand and conformance evidence justify it. |
| Governed execution coverage | file-write, shell, git, and package-manager paths are on the governed containment/evidence surface; browser/MCP families are declared and fail closed. | executable browser/MCP bridges only after sandbox and waiver policy are implemented. |
| Data/provenance | task/evidence/artifact/replay/provenance metadata has migration, replay export, retention, rollback, and release provenance evidence. | event streams, object stores, semantic indexes, and external signing when scale or release pressure requires them. |
| Operations | five configured targets passed a sustained quick window and doctor/operator remediation surfaces remain verified. | production SLO/error-budget/failover stack after transition runtime pressure justifies it. |

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
- SQLite or filesystem metadata for local single-user runs, PostgreSQL for service-shaped durable task, approval, and evidence metadata
- local filesystem in dev plus object-store abstraction for artifacts
- OpenTelemetry for runtime tracing
- sandbox/process-guard abstraction for executable tool containment
- existing contract package reused behind service boundaries

Deferred from the direct transition unless justified by real pressure:
- Temporal-class workflow engine
- `OPA/Rego`
- `NATS JetStream`
- `Redis`
- `pgvector`
- `gRPC`
- A2A gateway
- full observability stack
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
The direct-to-final-state blocking and hardening gaps (`HFG-001` through `HFG-H3`) are implemented on the current branch baseline through `GAP-060`, and the post-optimized realization queue `GAP-104..111` is complete on the current branch baseline.

The remaining risk after certification is claim drift, not an open implementation slice:
- complete-closure claims must stay tied to fresh executable evidence
- if verification or evidence drifts, claim wording must downgrade immediately until re-validated
- any new LTP implementation must use ids beyond `GAP-111` and pass a scope fence before it can alter the certified posture
- if external protocol or host semantics change, the adapter/conformance layer must be refreshed before the change can strengthen final-state claims

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
The repository claims complete hybrid final-state closure on the current branch baseline because all of the following are now true and evidence-backed:
- a target repo can attach without copying the kernel
- runtime state is machine-local by default for attached flows
- governed actions are usable from attached runtime flows
- medium and high-risk writes flow through deterministic policy and approval
- verification, evidence, replay, rollback, and handoff stay inside one runtime-owned task model
- at least one live Codex path is real and explicitly reports attach/degrade posture
- at least one non-Codex path exists with honest degraded runtime guarantees
- multi-repo evidence comes from configured target repositories, not only sample profiles
- the service-shaped control/session/operator boundary is active for execution-like behavior and parity gates

Claim reference:
- `docs/change-evidence/20260427-gap-111-complete-hybrid-final-state-certification.md`

## Optimized Best-State Definition (2026-04-21, updated 2026-04-27)
The repository keeps the existing hybrid final-state shape, but raises the engineering bar with six explicit invariants:

1. Runtime execution truth:
- attach-first governed execution is real for both Codex and at least one non-Codex adapter path
- approval, verification, evidence, handoff, replay, and rollback stay linked by one runtime-owned execution chain

2. Service-boundary truth:
- control/session/operator surfaces are API-first in runtime behavior
- CLI and facade paths remain compatibility wrappers, not a second execution model

3. Operability truth:
- machine-local runtime state, migration, and rollback are deterministic and testable
- runtime posture failures are remediable through doctor/operator guidance

4. Claim-discipline truth:
- closure claims are evidence-backed, continuously re-verifiable, and downgraded when drift is detected

5. Execution-containment truth:
- executable tools run inside declared workspace, permission, timeout, and resource boundaries
- shell, git, package-manager, browser, and MCP actions emit evidence and rollback metadata through the same governed surface

6. Protocol-boundary truth:
- MCP exposes tools, resources, prompts, auth, and roots; it does not own governance policy
- A2A may expose task, message, artifact, streaming, and discovery semantics; it does not replace local task lifecycle, approval, evidence, or rollback rules

### Quantified Acceptance Targets
| dimension | target | minimum evidence |
|---|---|---|
| governed execution closure | >= 95% successful medium-risk loops over last 30 attached runs | attached-repo loop evidence + replay/handoff refs |
| live-host continuity | >= 95% continuity id preservation from request to handoff | session-bridge runtime tests + runtime evidence snapshots |
| non-Codex parity | >= 1 non-Codex path passes the same conformance gate set as Codex path | adapter parity test report and trial evidence |
| dual first-class host parity | Codex and Claude Code are equally supported in governance outcome | dual-host rule/config sync, adapter conformance, target-repo evidence, and bounded claim catalog entry |
| service parity | API and CLI parity tests remain green for all execution-like commands | service/runtime parity test suite |
| recoverability | >= 90% posture failures have guided remediation path and successful retry evidence | doctor/runtime status evidence plus recovery runbook replay |
| claim freshness | closure evidence regenerated within the declared verification window | latest closeout evidence stamp and gate run outputs |
| execution containment | 100% governed write/execute tool families have declared scope, approval, timeout, and evidence metadata | sandbox or process-guard tests plus tool-runner evidence snapshots |
| provenance coverage | release artifacts and target-repo light packs carry reproducible provenance or an explicit waiver | provenance/attestation evidence and release gate output |

## Gap Horizons From The Optimized Definition
### Near-Term Gaps (next 1-2 quarters)
- close live host integration end-to-end beyond smoke posture (real handshake, real event ingestion, real continuation chain)
- establish non-Codex conformance parity and publish repeatable evidence
- converge service-shaped runtime as primary control surface while keeping compatibility wrappers
- harden operator query completeness and remediation-backed doctor behavior
- enforce claim-drift detection in CI for roadmap/plan/evidence consistency
- add an execution-containment floor for broad tool coverage before expanding autonomous write paths
- add provenance-backed release and light-pack evidence before stronger public final-state claims

### Long-Term Gaps (2+ quarters, trigger-based)
- introduce workflow orchestration depth when pause/resume/compensation complexity exceeds local runtime simplicity
- introduce policy-runtime separation depth when policy cardinality and audit pressure exceed local decision surfaces
- expand data-plane depth (event stream/object-store/indexed evidence) when scale and retention pressure require it
- productize multi-host first-class adapters beyond Codex after conformance parity and governance consistency are proven
- harden production operations (SLO/error-budget/chaos/failover) after transition runtime is stable under real workloads
- harden supply-chain provenance and artifact promotion after generated light packs, control packs, or releases become externally consumed

## Canonical Planning Package
The canonical planning package now consists of direct closure companions plus the optimized long-term package:

1. direct-to-final-state roadmap
2. direct-to-final-state implementation plan
3. optimized hybrid long-term roadmap
4. optimized hybrid long-term implementation plan
5. aligned backlog and task list

Those files are now the active planning chain for certified completion and future long-term optimization work. The completed implementation queue is `GAP-104..111`, which turned the optimized target into a complete realization plan instead of another planning-only closeout.

As of the 2026-04-27 certification batch, `GAP-104..111` are complete. Future work is no longer part of this certification queue; it must be selected by a new post-`GAP-111` scope fence.

## Source References
- `docs/prd/governed-ai-coding-runtime-prd.md`
- `docs/architecture/governed-ai-coding-runtime-target-architecture.md`
- `docs/architecture/mvp-stack-vs-target-stack.md`
- `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- `docs/roadmap/optimized-hybrid-final-state-long-term-roadmap.md`
- `docs/plans/optimized-hybrid-final-state-long-term-implementation-plan.md`
- `docs/reviews/2026-04-18-hybrid-final-state-and-plan-reconciliation.md`
- `docs/reviews/2026-04-19-hybrid-final-state-executable-gap-audit.md`
