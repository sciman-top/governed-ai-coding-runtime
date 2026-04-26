# 20260427 GAP-097 Orchestration And Policy Trigger Review

## Goal
Close `GAP-097` by reviewing whether `LTP-01 orchestration-depth` or `LTP-02 policy-runtime-separation` is justified after the transition-stack convergence gate.

## Scope
Decision evidence only. No workflow engine, external policy runtime, event bus, or new dependency is introduced.

## Trigger Decision
| package id | decision | reason | next review trigger |
|---|---|---|---|
| `LTP-01 orchestration-depth` | `watch` | Current runtime uses deterministic task/workflow primitives, timeout guards, replay/evidence, and target-flow wrappers. `GAP-096` and full gates pass without repeated pause/resume/retry/compensation graph failures that would justify a Temporal-class engine. | repeated runtime-flow orchestration failures after target command drift and process-environment failures are excluded |
| `LTP-02 policy-runtime-separation` | `not_triggered` | Current `PolicyDecision`, approval, waiver, claim-exception, and docs gates remain auditable locally. No policy cardinality, ownership split, or audit burden pressure currently requires OPA/Rego-class separation. | policy rules become too numerous or multi-owned to audit in local contract/code review, or claim/waiver gates show recurring policy drift |

## Evidence Inputs
- `GAP-090` classified `LTP-01` as `watch` and `LTP-02` as `not_triggered`.
- `GAP-092` deferred all `LTP-01..05` packages after sustained target evidence showed repairable target command drift rather than platform-depth pressure.
- `GAP-096` added a transition-stack convergence gate and passed with no observed `FastAPI`, `Pydantic`, PostgreSQL adapter, or external `OpenTelemetry` imports.
- The current full gate passes, including runtime tests, service parity, contract checks, doctor, docs checks, and issue rendering.

## Verification
Commands:
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
- `git diff --check`

Key output:
- full gate: `OK runtime-build`, `OK runtime-unittest`, `OK runtime-service-parity`, `OK schema-catalog-pairing`, `OK transition-stack-convergence`, `OK runtime-doctor`, `OK active-markdown-links`, `OK issue-seeding-render`
- tests: `Ran 422 tests ... OK (skipped=5)`, `Ran 10 tests ... OK`
- `git diff --check`: no whitespace errors; Git reported CRLF normalization warnings for existing text files

## Risk
- This decision intentionally does not implement `Temporal`, `OPA/Rego`, or equivalent runtime separation.
- Residual risk is under-detecting future complexity if runtime-flow failures are not classified separately from target-repo business failures.

## Rollback
Revert this evidence file and the `GAP-097` status/checkbox updates in roadmap, plan, backlog, README, and evidence index files.

