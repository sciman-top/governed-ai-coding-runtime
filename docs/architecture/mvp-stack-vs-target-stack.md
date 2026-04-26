# MVP Stack Vs Target Stack

## Purpose
Separate the technology needed to prove the governed AI coding runtime from the broader target-state architecture described elsewhere.

## Decision Principle
Final-state best practice defines direction. The MVP stack should prove the product thesis with the fewest moving parts that still preserve:
- durable execution
- policy enforcement
- approvals
- verification
- evidence
- agent compatibility through contracts

## Summary
The current target stack is directionally sound, but too broad to treat as the mandatory first implementation slice.

The MVP should optimize for governance proof and compatibility proof, not infrastructure completeness.

## 2026-04-27 Stack Decision
The best stack is not a single fixed shopping list. It is a staged stack ladder:

1. `verified local baseline`: keep the current Python/PowerShell/filesystem substrate while it is the fastest way to prove contracts and gates.
2. `direct transition stack`: introduce service-shaped APIs, typed validation, durable metadata, tracing, and sandbox/process containment where they close real execution risks.
3. `trigger-based final-state candidates`: add workflow engines, policy engines, eventing, semantic stores, and full operations tooling only when measured pressure justifies them.

This removes one earlier ambiguity: `Temporal` is a strong final-state candidate, but it is not part of the first mandatory MVP slice. The near-term requirement is deterministic, idempotent, replayable runtime behavior; the engine can remain local until pause/resume/compensation complexity proves the need for Temporal-class orchestration.

## Recommended MVP / Transition Stack

| Concern | MVP recommendation | Why |
|---|---|---|
| Runtime language | `Python 3.12+` | Strong AI/runtime/tooling support and clean path from current Python contracts |
| Local operator shell | PowerShell wrappers + Python CLIs | Matches current Windows-heavy operator workflow while keeping kernel semantics shell-neutral |
| Backend API | `FastAPI` when service boundary is needed | Fast iteration, broad ecosystem, but not required before the API surface is real |
| Validation / contracts | JSON Schema now; `Pydantic v2` at API/runtime boundary | Keep current schema truth while adding typed runtime validation where it pays for itself |
| Primary metadata store | SQLite/filesystem locally; `PostgreSQL` for service-shaped runtime | Keeps local single-user use simple while preserving a durable production path |
| Durable workflow | explicit state machine + replay/idempotency first | Proves durable execution semantics before adopting a workflow engine |
| Artifact storage | local filesystem plus object-store abstraction | Avoids early storage sprawl while keeping an S3-compatible path open |
| Policy layer | deterministic policy module/service first | Stable structured decisions now; `OPA/Rego` later when policy cardinality/audit pressure requires it |
| Execution containment | workspace roots + process guard now; Linux container/sandbox where writes broaden | Broad executable tool coverage needs containment before autonomy grows |
| Observability | structured evidence + `OpenTelemetry` hooks | Enough traceability without forcing a full metrics/logging stack early |
| Operator surface | CLI/API read model first; `Next.js` console later | Avoids a half-built UI before approval/evidence/read models stabilize |
| Agent integration | Codex CLI/App adapter + generic adapter contract | Matches the primary workflow while preventing Codex-specific assumptions from entering the kernel |

## Target Stack

| Concern | Target-state candidate | Why it remains attractive |
|---|---|---|
| Durable workflow engine | `Temporal`-class capability | Useful when pause/resume/timeout/retry/approval interruption exceeds local state-machine simplicity |
| Async eventing | `NATS JetStream` | Good for non-critical async flows and decoupled operators |
| Search / semantic memory | `pgvector` | Useful later for repo context shaping and retrieval, not Day 1 critical |
| Cross-service RPC | `gRPC` | Good internal contract option once service boundaries stabilize |
| Policy engine | `OPA/Rego` | Strong long-term fit for explicit policy ownership and auditability |
| Full observability suite | `Prometheus` + `Grafana` + `Loki` + `Tempo/Jaeger` | Valuable once the system is running enough traffic to justify the complexity |
| Web console | `Next.js` + TypeScript | Good later fit for approvals, evidence inspection, replay, and operator workflows |
| A2A gateway | separate gateway layer | Makes sense only after single-agent baseline proves out |
| Agent adapter family | CLI, MCP, app-server, IDE, browser/UI, cloud-agent, manual-handoff adapters | Keeps the runtime compatible with future agent products without rewriting kernel semantics |

## What To Defer

### Defer from the first runnable slice
- `Temporal`
- `NATS JetStream`
- `pgvector`
- `gRPC`
- `OPA/Rego`
- A2A gateway
- advanced memory layer
- broad tool catalog
- production `Next.js` console
- deep IDE replacement UX
- deep integrations with every new AI coding product
- full observability stack if a slim trace/log baseline already works

### Why defer
- They increase operational width faster than they improve the core governance loop.
- The product can validate its thesis before these parts exist.

## Architecture Rule
Do not confuse target-state optionality with MVP obligation.

The runtime should keep ports and boundaries clean enough that these capabilities can be introduced later without rewriting the domain model.

Final-state best practice is the north star. MVP implementation is the tracer bullet. A capability may be required by the final state while still deferred from the first runnable slice.

## Convergence Gate
Transition-stack adoption is now checked by `docs/architecture/transition-stack-convergence-policy.json` and `scripts/verify-transition-stack-convergence.py`.

The gate enforces the following baseline:
- observed `FastAPI`, `Pydantic`, PostgreSQL adapter, or external `OpenTelemetry` imports must map to an active boundary or fail closed
- JSON Schema remains the cross-tool source of truth
- local filesystem and SQLite-style operation remain valid for single-machine use
- CLI/API parity tests and wrapper drift guards must stay wired before service-shaped dependencies can broaden behavior

## Recommended Implementation Order
1. typed contracts and task model
2. durable task store
3. policy and approval path
4. governed tool runner
5. verification runner
6. evidence bundle
7. Codex CLI/App compatible operator path
8. execution-containment floor for broad tool families
9. minimal API/read model
10. only then broaden eventing, adapters, UI, and richer observability

## Red Flags
- adding infra because it looks platform-like rather than because it closes a runtime risk
- introducing distributed messaging before the first governed task loop exists
- making memory a prerequisite for approval/evidence/replay
- forcing all target-state services into the first deployment shape
- coupling kernel semantics to one agent product because it is the first adapter
- applying strict governance to low-risk work and degrading agent usefulness

## Practical Conclusion
The best stack for this project is not "the biggest plausible platform stack."

The best stack is:
- narrow enough to ship the governed loop
- explicit enough to preserve deterministic controls
- compatible enough to work with Codex CLI/App first and future agent products later
- modular enough to evolve into the target architecture without a rewrite
