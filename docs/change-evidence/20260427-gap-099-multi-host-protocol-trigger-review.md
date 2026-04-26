# 20260427 GAP-099 Multi-Host And Protocol Trigger Review

## Goal
Close `GAP-099` by reviewing whether `LTP-04 multi-host-first-class` or deeper protocol boundary work is justified.

## Scope
Decision evidence only. No MCP server/client implementation, A2A gateway, gRPC contract, IDE/cloud adapter, browser adapter, or new host integration is introduced.

## Trigger Decision
| decision area | decision | reason | next review trigger |
|---|---|---|---|
| `LTP-04 multi-host-first-class` | `watch` | Codex and at least one non-Codex path already share adapter conformance coverage, and current conformance tests pass. The evidence supports preserving the adapter contract, not broad first-class productization across more hosts yet. | explicit product demand plus repeated parity-gap evidence that cannot be handled by capability-tiered adapters |
| protocol-boundary depth | `not_triggered` | Current architecture already states MCP/A2A are integration protocols and must not own task lifecycle, approval, evidence, verification, or rollback. No current workload requires gRPC, A2A gateway, or deeper MCP runtime ownership. | stable multi-host demand requires protocol-specific execution/evidence boundaries while preserving kernel-owned governance semantics |

## Evidence Inputs
- `GAP-081` closed non-Codex conformance with shared Codex/non-Codex gate family and equivalent runtime linkage fields.
- `docs/architecture/compatibility-matrix.md` keeps Codex required, non-interactive CLI supported, MCP/app-server supported by adapter contract, and IDE/cloud/browser best-effort.
- `docs/architecture/hybrid-final-state-master-outline.md` and target architecture keep MCP/A2A as boundaries, not governance owners.
- Adapter conformance tests passed in this slice.

## Verification
Commands:
- `python -m unittest tests.runtime.test_adapter_conformance tests.runtime.test_adapter_registry`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
- `git diff --check`

Key output:
- adapter tests: `Ran 13 tests ... OK`
- full gate: `OK runtime-build`, `OK runtime-unittest`, `OK runtime-service-parity`, `OK schema-catalog-pairing`, `OK transition-stack-convergence`, `OK runtime-doctor`, `OK active-markdown-links`, `OK issue-seeding-render`
- full tests: `Ran 422 tests ... OK (skipped=5)`, `Ran 10 tests ... OK`
- `git diff --check`: no whitespace errors; Git reported CRLF normalization warnings for existing text files

## Risk
- This decision does not expand host coverage. Future protocol pressure should be handled by a new scope fence rather than making MCP/A2A/gRPC own governance semantics.

## Rollback
Revert this evidence file and the `GAP-099` status/checkbox updates in roadmap, plan, backlog, README, and evidence index files.

