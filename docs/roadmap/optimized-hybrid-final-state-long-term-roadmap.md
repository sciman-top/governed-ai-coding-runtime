# Optimized Hybrid Final-State Long-Term Roadmap

## Status
- This is the long-term roadmap created after the 2026-04-27 external benchmark and stack-staging review.
- It starts after the completed `GAP-090..092` trigger-audit queue.
- It does not mark any `LTP` package as already triggered or implemented.
- It translates the optimized hybrid final state into a dependency-ordered queue: `GAP-093..119`.
- `GAP-093..103` are complete on the current branch baseline. No `LTP-01..06` package was selected or implemented.
- `GAP-104..111` are the post-`GAP-103` realization queue and are complete on the current branch baseline. `GAP-111` is the certification point for complete hybrid final-state closure.
- `GAP-112` is the first post-certification guard and is complete on the current branch baseline. It mechanizes current-source compatibility after certification.
- `GAP-113` is complete on the current branch baseline. It mechanizes whether, why, and how autonomous `LTP-01..06` promotion can proceed after certification.
- `GAP-114` is complete on the current branch baseline. It turns the promotion result into a deterministic autonomous next-work action.
- `GAP-115..119` are complete as owner-directed bounded scope for Codex plus Claude Code dual first-class host entrypoints.

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
| `H6 fresh all-target workload window` | `GAP-103` | rerun the configured target-repo daily workload after optimized closeout | all configured target repos pass daily flow with no runtime-flow timeout |
| `H7 complete realization queue` | `GAP-104..111` | implement the service, adapter, execution, data/provenance, operations, and certification slices required for truthful complete closure | every final-state acceptance target has fresh runtime evidence or the claim is downgraded |
| `H8 post-certification source guard` | `GAP-112` | mechanize external-source compatibility after certification | A2A/MCP/Codex sandbox, host guardrail, and provenance assumptions are policy-checked in Docs gate |
| `H9 autonomous promotion fence` | `GAP-113` | mechanize whether, why, and how `LTP-01..06` can advance after certification | evaluator returns `defer_all` or exactly one scope-fenced `auto_selected` package |
| `H10 autonomous next-work selection` | `GAP-114` | mechanize the next autonomous action after LTP promotion evaluation | selector returns gate repair, evidence refresh, LTP promotion, owner-directed scope, or defer-and-refresh |
| `H11 dual first-class host support` | `GAP-115..119` | promote Claude Code to first-class supported host parity with Codex in governance outcome while keeping adapter-tier claims evidence-bound | Claude Code has context, settings/hooks, adapter probe, target sync, and certification evidence without overstating host API identity or ignoring degraded target-run posture |

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
7. `GAP-103` refreshes all-target daily evidence; it is not permission to claim heavy `LTP` implementation.
8. `GAP-104` rebaselines the realization queue before any new complete-closure claim.
9. `GAP-105` must establish the service-primary boundary before live-host, execution breadth, or data-plane implementation claims.
10. `GAP-106` and `GAP-107` must prove Codex and at least one non-Codex path through the same runtime-owned evidence chain.
11. `GAP-108` must close executable tool-family containment before broader autonomous write or release claims.
12. `GAP-109` must make data/provenance release paths reproducible before public or external consumption claims.
13. `GAP-110` must produce a sustained workload and remediation window before `GAP-111` can certify closure.
14. `GAP-111` is allowed to claim complete hybrid final-state closure only if all previous realization gates are fresh and reproducible.
15. Post-`GAP-111` protocol adoption must include a current-source compatibility review. A2A, MCP, Codex sandbox, host guardrails, and supply-chain provenance may strengthen adapter behavior, but they cannot replace kernel-owned approval, containment, verification, rollback, or evidence.
16. Post-`GAP-112` autonomous LTP promotion must pass the promotion policy: exactly one package, fresh trigger evidence, scope fence, full gate reference, rollback, and one vertical slice. Without that, the correct autonomous decision is `defer_all`.
17. Post-`GAP-113` autonomous continuation must use the next-work selector. Gate repair and source/evidence freshness outrank implementation; `defer_all` cannot be converted into heavy LTP work.
18. `GAP-115..119` are allowed as owner-directed bounded host-support work. They can make Claude Code first-class in governance outcome, but adapter-tier recovery claims require fresh host and target-run evidence. They cannot claim identical host APIs, claim recovered `native_attach` while target runs remain degraded, or start full `LTP-04` infrastructure without a separate scope fence.

## Post-GAP-103 Realization Queue

| gap id | purpose | completion signal |
|---|---|---|
| `GAP-104` | rebaseline the complete realization queue after the optimized review packages | `GAP-104..111` are aligned across roadmap, plan, backlog, seeds, and evidence |
| `GAP-105` | make service/API boundaries primary for execution-like runtime behavior | CLI, facade, and API paths share one contract-backed behavior and parity gate |
| `GAP-106` | prove live Codex attach continuity with real session identity and event linkage | one real Codex path links request, approval, execution, evidence, replay, rollback, and handoff |
| `GAP-107` | prove at least one non-Codex adapter path under the same conformance family | non-Codex degraded and successful postures are honest and fail closed |
| `GAP-108` | broaden governed executable tool coverage under declared containment | shell/git/package/browser/MCP-like execution emits containment, approval, evidence, and rollback metadata |
| `GAP-109` | make data-plane and provenance release paths service-shaped and reproducible | task/evidence/artifact/replay/provenance stores have migration, retention, replay, and rollback tests |
| `GAP-110` | run sustained operations and recovery evidence after the realization batches | multi-target workload and remediation evidence supports claim freshness |
| `GAP-111` | certify or downgrade complete hybrid final-state closure | every final-state target has fresh evidence or visible downgrade |
| `GAP-112` | enforce current-source compatibility after certification | external protocol/host/security assumptions are machine-checked before they can strengthen claims |
| `GAP-113` | enforce autonomous LTP promotion scope fencing after certification | promotion is either exactly one evidence-triggered package or a fail-closed `defer_all` decision |
| `GAP-114` | choose the next autonomous work action after promotion evaluation | selector returns one action and preserves gate/evidence priority |
| `GAP-115` | define the dual first-class host boundary | Codex and Claude Code are equally important first-class supported hosts in governance outcome |
| `GAP-116` | add Claude Code settings/hooks governance template | Claude Code context and enforceable controls are separated and synchronizable |
| `GAP-117` | add Claude Code adapter probe and conformance parity | `claude-code` has first-class probe/conformance evidence or explicit degraded posture |
| `GAP-118` | sync Claude Code rule/config surfaces across targets | all configured target repos have synchronized or explicitly N/A Claude Code managed surfaces |
| `GAP-119` | certify dual first-class host support | Codex and Claude Code governance-result parity is evidence-backed or visibly downgraded |

Current realization status on the 2026-05-01 branch baseline: `GAP-104` through `GAP-111` are complete. Complete hybrid final-state closure is certified by the `GAP-111` evidence batch and remains subject to claim-drift gates. `GAP-112` is complete as a post-certification guard that keeps external-source assumptions machine-checkable. `GAP-113` is complete as the autonomous promotion guard that keeps heavy `LTP` adoption evidence-triggered and one-package-at-a-time. `GAP-114` is complete as the next-work selector that answers what autonomous work should happen when LTP promotion is deferred. `GAP-115..119` are complete as bounded support for the user's frequent Claude Code workflow. `GAP-130..143` are complete as the governance hub reuse, controlled evolution, bounded host-capability defer, historical trace closure, degraded fresh-evidence guard, and evidence recovery posture contract queue.

## Does Executing This Plan Truly Realize The Final State?
Executing only `GAP-093..103` does not realize the complete hybrid final state. It proves optimized planning, containment/provenance floors, transition-stack discipline, trigger reviews, and fresh target-repo health.

Executing `GAP-104..111` has realized the complete hybrid final state on the current branch baseline because all acceptance criteria passed and no host capability, workload, or supply-chain evidence invalidated the claims. The certification condition remains evidence-based, not schedule-based: if any live-host, adapter, execution, data, operations, or provenance target later fails, claim-drift gates must downgrade the claim until fresh recovery evidence exists.

## Complete Realization Acceptance Matrix

| dimension | first implementation gap | certification evidence required at `GAP-111` | fail condition |
|---|---|---|---|
| service-primary runtime boundary | `GAP-105` | execution-like CLI, facade, and API paths share one contract-backed behavior and parity gate | wrapper-only behavior bypasses the service/control boundary |
| live Codex continuity | `GAP-106` | one real Codex path links request, approval, execution, verification, evidence, replay, rollback, and handoff ids | posture-only or smoke-only evidence is used as live attach evidence |
| non-Codex parity | `GAP-107` | at least one non-Codex path passes the same conformance family and exposes honest degraded posture | host limitations silently pass as full parity |
| governed executable coverage | `GAP-108` | shell, git, package-manager, browser, and MCP-like execution emit containment, approval, evidence, and rollback metadata | any supported executable family is unclassified or fail-open |
| data and provenance release path | `GAP-109` | task, evidence, artifact, replay, and provenance stores have migration, retention, replay, rollback, and release-adjacent provenance tests | release or generated-artifact claims lack provenance or waiver evidence |
| operations recovery | `GAP-110` | sustained multi-target workload and guided remediation evidence support claim freshness | recovery failures leave final-state claims unchanged |
| closure certification | `GAP-111` | every quantified final-state target has fresh evidence or visible downgrade | narrative-only evidence is used for complete closure |
| current-source compatibility | post-`GAP-111` scope fence | external host/protocol/security docs still match adapter and claim boundaries, or affected claims are downgraded | outdated protocol assumptions are used to justify stronger claims |
| autonomous LTP promotion | post-`GAP-112` scope fence | evaluator returns `defer_all` or exactly one scope-fenced `auto_selected` package | multiple packages advance or owner-directed work is mislabeled as evidence-triggered |
| autonomous next-work selection | post-`GAP-113` selector | selector returns one next action from gate, freshness, promotion, owner-directed, or defer paths | `defer_all` is treated as permission to implement heavy LTP work |
| dual first-class host support | `GAP-115..119` | Codex and Claude Code pass equal governance-result requirements while adapter-tier recovery claims require fresh target-run evidence | Claude Code is treated as generic degraded support, or degraded Codex target-run posture is mistaken for recovered `native_attach` |

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
- `docs/change-evidence/20260427-gap-104-111-realization-planning.md`
- `docs/change-evidence/20260427-gap-113-autonomous-ltp-promotion-scope-fence.md`
- `docs/change-evidence/20260427-gap-114-autonomous-next-work-selector.md`
- `docs/change-evidence/20260501-gap-142-degraded-fresh-evidence-next-work-guard.md`
- `docs/change-evidence/20260501-gap-143-evidence-recovery-posture-contract.md`
- `docs/plans/claude-code-first-class-entrypoint-plan.md`
- `docs/change-evidence/20260427-claude-code-first-class-entrypoint-planning.md`

## Source References
- `docs/architecture/hybrid-final-state-master-outline.md`
- `docs/architecture/mvp-stack-vs-target-stack.md`
- `docs/architecture/governed-ai-coding-runtime-target-architecture.md`
- `docs/roadmap/direct-to-hybrid-final-state-roadmap.md`
- `docs/plans/long-term-gap-trigger-audit-plan.md`
- `docs/research/2026-04-27-hybrid-final-state-external-benchmark-review.md`
- `docs/change-evidence/20260427-hybrid-final-state-current-source-refresh.md`
- `docs/change-evidence/20260427-gap-113-autonomous-ltp-promotion-scope-fence.md`
- `docs/change-evidence/20260427-gap-114-autonomous-next-work-selector.md`
