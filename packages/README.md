# Packages

Shared runtime packages live here.

## Planned Boundaries
- `contracts/`: generated or hand-maintained runtime types derived from `schemas/`.
- `policy/`: deterministic risk and approval policy helpers.
- `testkit/`: shared fixtures for task lifecycle, evidence, gates, and repo profiles.

## Current Status
- `packages/contracts/` is the active Python contract package shipped by the current repository baseline.
- Additional packages remain deferred until `Full Runtime` and later stages need clearer module boundaries than the current single package provides.
- Package manager metadata is still intentionally absent; add it only with explicit dependency and supply-chain evidence.
