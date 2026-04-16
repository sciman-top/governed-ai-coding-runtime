# MVP Stack Vs Target Stack

## Purpose
Separate the technology needed to prove the governed AI coding runtime from the broader target-state architecture described elsewhere.

## Decision Principle
The target architecture defines direction. The MVP stack should prove the product thesis with the fewest moving parts that still preserve:
- durable execution
- policy enforcement
- approvals
- verification
- evidence

## Summary
The current target stack is directionally sound, but too broad to treat as the mandatory first implementation slice.

The MVP should optimize for governance proof, not infrastructure completeness.

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

## Target Stack

| Concern | Target-state candidate | Why it remains attractive |
|---|---|---|
| Async eventing | `NATS JetStream` | Good for non-critical async flows and decoupled operators |
| Search / semantic memory | `pgvector` | Useful later for repo context shaping and retrieval, not Day 1 critical |
| Cross-service RPC | `gRPC` | Good internal contract option once service boundaries stabilize |
| Policy engine | `OPA/Rego` | Strong long-term fit for explicit policy ownership and auditability |
| Full observability suite | `Prometheus` + `Grafana` + `Loki` + `Tempo/Jaeger` | Valuable once the system is running enough traffic to justify the complexity |
| A2A gateway | separate gateway layer | Makes sense only after single-agent baseline proves out |

## What To Defer

### Defer from the first runnable slice
- `NATS JetStream`
- `pgvector`
- `gRPC`
- A2A gateway
- advanced memory layer
- broad tool catalog
- full observability stack if a slim trace/log baseline already works

### Why defer
- They increase operational width faster than they improve the core governance loop.
- The product can validate its thesis before these parts exist.

## Architecture Rule
Do not confuse target-state optionality with MVP obligation.

The runtime should keep ports and boundaries clean enough that these capabilities can be introduced later without rewriting the domain model.

## Recommended Implementation Order
1. typed contracts and task model
2. durable task store
3. policy and approval path
4. governed tool runner
5. verification runner
6. evidence bundle
7. minimal console
8. only then broaden eventing, adapters, and richer observability

## Red Flags
- adding infra because it looks platform-like rather than because it closes a runtime risk
- introducing distributed messaging before the first governed task loop exists
- making memory a prerequisite for approval/evidence/replay
- forcing all target-state services into the first deployment shape

## Practical Conclusion
The best stack for this project is not "the biggest plausible platform stack."

The best stack is:
- narrow enough to ship the governed loop
- explicit enough to preserve deterministic controls
- modular enough to evolve into the target architecture without a rewrite
