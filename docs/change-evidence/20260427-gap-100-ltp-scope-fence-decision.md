# 20260427 GAP-100 LTP Scope Fence Decision

## Goal
Close `GAP-100` by selecting exactly one `LTP-01..06` package for implementation or deferring all packages with evidence.

## Decision
All `LTP-01..06` packages are deferred. No long-term package is selected for implementation in this queue.

## Scope Fence
| package id | decision | basis | next review trigger |
|---|---|---|---|
| `LTP-01 orchestration-depth` | deferred, watch | `GAP-097` found no repeated pause/resume/retry/compensation graph failure that requires a Temporal-class engine. | repeated runtime-flow orchestration failures after target command drift and process-environment failures are excluded |
| `LTP-02 policy-runtime-separation` | deferred | `GAP-097` found no policy cardinality, ownership split, or audit burden pressure that requires OPA/Rego-class separation. | policy rules become too numerous or multi-owned to audit locally |
| `LTP-03 data-plane-scaling` | deferred, watch | `GAP-098` found KPI/evidence volume remains manageable with current filesystem/local metadata paths. | sustained target-run volume, replay retention, query latency, or artifact size exceeds current paths |
| `LTP-04 multi-host-first-class` | deferred, watch | `GAP-099` found adapter conformance exists, but no product demand or parity pressure justifies broad first-class host productization. | explicit product demand plus repeated parity gap evidence |
| `LTP-05 operations-hardening` | deferred | `GAP-098` found full gates and doctor pass and known target-run failures are not operations-stack failures. | operational failures dominate after runtime and target functional failures are excluded |
| `LTP-06 supply-chain-hardening` | deferred | `GAP-095` established provenance floor, but there is no evidence that generated light packs, control packs, or releases are externally consumed or team-shared. | generated governance artifacts become externally consumed or team-shared and need signing/promotion workflow |

## Non-Goals
- Do not start `Temporal`, `OPA/Rego`, event bus, `Redis`, `pgvector`, `gRPC`, A2A gateway, full observability, web console, or supply-chain signing work from this decision.
- Do not remove deferred packages from the roadmap.

## Verification
Commands:
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
- `git diff --check`

Key output:
- issue rendering: `OK issue-seeding-render`
- docs: `OK active-markdown-links`, `OK backlog-yaml-ids`, `OK claim-drift-sentinel`, `OK claim-evidence-freshness`
- full gate: `OK runtime-build`, `OK runtime-unittest`, `OK runtime-service-parity`, `OK schema-catalog-pairing`, `OK transition-stack-convergence`, `OK runtime-doctor`
- full tests: `Ran 422 tests ... OK (skipped=5)`, `Ran 10 tests ... OK`
- `git diff --check`: no whitespace errors; Git reported CRLF normalization warnings for existing text files

## Risk
- Deferring all packages means `GAP-101` should close as `deferred-no-implementation` unless fresh trigger evidence appears.
- Future work must not silently start a deferred package without a new scope fence.

## Rollback
Revert this evidence file and the `GAP-100` status/checkbox updates in roadmap, plan, backlog, README, and evidence index files.
