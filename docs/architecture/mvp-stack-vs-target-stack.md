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

## Recommended MVP Stack

| Concern | MVP recommendation | Why |
|---|---|---|
| Backend API | `FastAPI` | Fast iteration, typed contracts, broad ecosystem |
| Core language | `Python 3.12+` | Strong AI/runtime/tooling support |
| Validation / contracts | `Pydantic v2` + JSON Schema | Single source for runtime contracts and payload validation |
| Primary store | `PostgreSQL` | Durable task, approval, evidence, and registry data |
| Durable workflow | `Temporal` | Native fit for pause/resume/timeout/retry/approval interruption |
| Artifact storage | local filesystem in dev, S3-compatible in runtime | Needed for evidence bundles and snapshots without overbuilding early |
| Policy layer | explicit policy service with room for `OPA` | Start with deterministic policy boundaries; adopt full OPA scope where justified |
| Observability | `OpenTelemetry` + basic log/trace pipeline | Enough to trace task and tool execution without full platform overhead |
| Web console | `Next.js` | Good fit for approvals, evidence inspection, and operator flows |
| Agent integration | Codex CLI/App adapter + generic process adapter contract | Matches the primary user workflow while preventing Codex-specific assumptions from entering the kernel |

## Target Stack

| Concern | Target-state candidate | Why it remains attractive |
|---|---|---|
| Async eventing | `NATS JetStream` | Good for non-critical async flows and decoupled operators |
| Search / semantic memory | `pgvector` | Useful later for repo context shaping and retrieval, not Day 1 critical |
| Cross-service RPC | `gRPC` | Good internal contract option once service boundaries stabilize |
| Policy engine | `OPA/Rego` | Strong long-term fit for explicit policy ownership and auditability |
| Full observability suite | `Prometheus` + `Grafana` + `Loki` + `Tempo/Jaeger` | Valuable once the system is running enough traffic to justify the complexity |
| A2A gateway | separate gateway layer | Makes sense only after single-agent baseline proves out |
| Agent adapter family | CLI, MCP, app-server, IDE, browser/UI, cloud-agent, manual-handoff adapters | Keeps the runtime compatible with future agent products without rewriting kernel semantics |

## What To Defer

### Defer from the first runnable slice
- `NATS JetStream`
- `pgvector`
- `gRPC`
- A2A gateway
- advanced memory layer
- broad tool catalog
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

## Recommended Implementation Order
1. typed contracts and task model
2. durable task store
3. policy and approval path
4. governed tool runner
5. verification runner
6. evidence bundle
7. Codex CLI/App compatible operator path
8. minimal console
9. only then broaden eventing, adapters, and richer observability

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
