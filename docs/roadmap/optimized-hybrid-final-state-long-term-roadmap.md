# Optimized Hybrid Final-State Long-Term Roadmap

## Status
- This is the long-term roadmap created after the 2026-04-27 external benchmark and stack-staging review.
- It starts after the completed `GAP-090..092` trigger-audit queue.
- It does not mark any `LTP` package as already triggered or implemented.
- It translates the optimized hybrid final state into a dependency-ordered queue: `GAP-093..102`.
- `GAP-093..102` are complete on the current branch baseline. No `LTP-01..06` package was selected or implemented.

## Goal
Move from the current verified hybrid baseline to a sustained optimized hybrid final state without turning every attractive final-state component into mandatory near-term infrastructure.

The best long-term target remains:

`repo-local contract bundle + machine-local durable governance kernel + attach-first host adapters + same-contract verification/delivery plane`

The corrected implementation posture is:

1. keep the current verified local baseline as long as it is the fastest trustworthy proof surface
2. converge on the direct transition stack only where real API, persistence, tracing, containment, or service-boundary pressure exists
3. adopt heavyweight final-state candidates only through trigger evidence and one-package-at-a-time scope fences

## Stack Posture

| layer | current verified baseline | direct transition stack | trigger-based final-state candidates |
|---|---|---|---|
| runtime language | Python stdlib contracts and runtime primitives | Python 3.12+ with typed runtime boundaries | split services only after stable boundary pressure |
| operator shell | PowerShell wrappers and Python CLIs | CLI as wrapper around runtime/API contract | richer console after read models stabilize |
| API boundary | local scripts and contract readers | FastAPI only when API boundary is active | gRPC only after service boundaries stabilize |
| validation | JSON Schema and Python contract tests | Pydantic v2 at API/runtime boundary | external contract registry only if drift pressure proves it |
| persistence | filesystem and local runtime state | SQLite/filesystem locally, PostgreSQL for service-shaped metadata | event stream, retention tiers, object-store promotion |
| orchestration | explicit deterministic state machine | idempotency, replay, timeout, compensation contracts | Temporal-class workflow engine |
| policy | deterministic local policy module/service | stable `PolicyDecision` and audit metadata | OPA/Rego when policy cardinality or audit pressure requires it |
| execution containment | declared roots and governed execution metadata | process guard, sandbox contract, timeout and approval floor | stronger isolated runtimes where autonomy grows |
| observability | structured evidence and gate output | OpenTelemetry hooks at runtime/API boundaries | Prometheus/Grafana/Loki/Tempo/Jaeger stack |
| adapters/protocols | Codex-first adapter and generic adapter contract | conformance tests and protocol-boundary guards | A2A gateway or deeper multi-host productization |
| release/provenance | git history and evidence files | provenance records for generated light packs and releases | SLSA-style signing and artifact promotion workflow |

## Dependency Horizon

| horizon | gap ids | purpose | completion signal |
|---|---|---|---|
| `H0 planning baseline` | `GAP-093` | make the optimized roadmap, implementation plan, backlog, seeds, and evidence canonical | docs, seeds, and script validation agree |
| `H1 containment and provenance floor` | `GAP-094..095` | close the strongest near-term engineering risk before broader execution or release claims | executable tools and generated artifacts carry containment/provenance metadata |
| `H2 transition-stack convergence` | `GAP-096` | make service/API/persistence/tracing adoption criteria explicit | transition dependencies are boundary-driven, not decorative |
| `H3 trigger-review batches` | `GAP-097..099` | decide whether orchestration, policy, data, operations, multi-host, or protocol depth is now justified | each `LTP-01..06` is `not_triggered`, `watch`, or `triggered` with evidence |
| `H4 selected package implementation` | `GAP-100..101` | start at most one long-term package and implement one vertical slice | one selected package has contract, runtime, evidence, tests, and rollback |
| `H5 sustained release readiness` | `GAP-102` | refresh closeout claims against real workload and rollout evidence | final-state wording, evidence, gates, and target-repo posture agree |

## Track Ownership

| track | owns | should not own |
|---|---|---|
| control plane | task/session/operator API boundary, CLI/API parity, read models | UI polish before read models stabilize |
| execution plane | governed shell/git/package/browser/MCP execution, containment, timeout, rollback | unrestricted tool catalog expansion |
| assurance plane | policy decisions, approvals, evidence completeness, claim drift | replacing runtime semantics with host/protocol defaults |
| data plane | durable metadata, replay, artifact persistence, retention, query pressure | event buses or semantic stores before measured pressure |
| adapter plane | Codex-first reality, non-Codex conformance, protocol-boundary rules | making MCP/A2A own approval, rollback, or evidence semantics |
| release plane | light-pack provenance, artifact promotion, supply-chain evidence | external release claims without reproducible evidence |

## Long-Term Package Triggers

| package | trigger evidence required | default decision |
|---|---|---|
| `LTP-01 orchestration-depth` | pause/resume/timeout/retry/compensation graph repeatedly exceeds local state-machine maintainability | defer |
| `LTP-02 policy-runtime-separation` | policy cardinality, ownership, or audit burden exceeds local `PolicyDecision` surfaces | defer |
| `LTP-03 data-plane-scaling` | event throughput, replay retention, query latency, or artifact size exceeds current persistence path | defer |
| `LTP-04 multi-host-first-class` | non-Codex conformance parity is stable and product demand requires deeper host coverage | defer |
| `LTP-05 operations-hardening` | transition runtime is stable under sustained workloads and operational failures become the primary risk | defer |
| `LTP-06 supply-chain-hardening` | generated light packs, control packs, or release artifacts are externally consumed or team-shared | defer |

## Sequencing Rules
1. `GAP-094` and `GAP-095` must precede any broadening of autonomous execution or external release claims.
2. `GAP-096` must prove that transition-stack dependencies are attached to real runtime boundaries before adding heavier components.
3. `GAP-097..099` are decision gates, not implementation permission for multiple packages.
4. `GAP-100` may select exactly one `LTP` package or defer all packages with evidence.
5. `GAP-101` implements only the selected package's first vertical slice.
6. `GAP-102` may strengthen final-state claims only when fresh gates and workload evidence remain reproducible.

## Verification Floor
Every gap in this roadmap must preserve the repository gate order:

`build -> test -> contract/invariant -> hotspot`

Planning and backlog changes also require:

- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`

Implementation gaps must additionally run the relevant runtime, contract, doctor, and target-repo rollout checks for the touched surface.

## Companion Deliverables
- `docs/plans/optimized-hybrid-final-state-long-term-implementation-plan.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/issue-seeds.yaml`
- `docs/change-evidence/20260427-optimized-hybrid-long-term-plan.md`

## Source References
- `docs/architecture/hybrid-final-state-master-outline.md`
- `docs/architecture/mvp-stack-vs-target-stack.md`
- `docs/architecture/governed-ai-coding-runtime-target-architecture.md`
- `docs/roadmap/direct-to-hybrid-final-state-roadmap.md`
- `docs/plans/long-term-gap-trigger-audit-plan.md`
- `docs/research/2026-04-27-hybrid-final-state-external-benchmark-review.md`
