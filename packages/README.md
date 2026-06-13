# Packages

Shared Python packages and lightweight package-shaped modules live here.

## Current Package Layout
- `contracts/`
  - the main reusable contract package
  - contains the repo-owned domain and governance primitives used by scripts, runtime flows, and tests
- `agent-runtime/`
  - service-shaped helpers for local persistence, artifacts, and service-facade glue
  - currently kept lightweight and repo-local rather than published as a standalone package
- `observability/`
  - tracing helpers such as `runtime_tracing.py`

## Current Boundaries
- `packages/contracts` is the canonical import surface for governance contracts.
- `packages/agent-runtime` and `packages/observability` are implementation-support layers, not separate product surfaces.
- Package-manager metadata is still intentionally absent; add it only with explicit dependency-baseline, supply-chain, and rollout evidence.

## Verification
- canonical runtime verification:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
```

- full repository integrity:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```
