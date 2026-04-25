# 20260425 Postgres Service Gate Hardening

## Goal
Close a service-boundary verification gap without changing existing runtime behavior, public CLI
contracts, schema shapes, or target-repo rollout semantics.

## Landing And Destination
- Current landing: `packages/agent-runtime/persistence.py`, `scripts/verify-repo.ps1`,
  `tests/service/test_persistence_postgres.py`, `tests/README.md`.
- Target destination: keep Postgres metadata persistence as an optional service-path backend, and keep
  Runtime gate coverage aligned with all service tests.

## Issue
`tests/service/test_persistence_postgres.py` existed but was not covered by `verify-repo.ps1 -Check Runtime`.
Running service discovery directly exposed that `PostgresMetadataStore` was missing from
`packages/agent-runtime/persistence.py`.

## Changes
- Added lazy optional `PostgresMetadataStore` using `psycopg` only when the Postgres store is
  constructed.
- Preserved the existing `SqliteMetadataStore` interface: `upsert`, `get`, and `list_namespace`.
- Changed the Runtime gate service step from two hand-picked modules to full discovery under
  `tests/service`.
- Updated `tests/README.md` to make the verifier the canonical test entrypoint on Windows hosts that
  require process-environment normalization before Python imports.

## Verification
- `python -m unittest discover -s tests/service -p "test_*.py"` -> pass, `Ran 10 tests`
- `python -m unittest tests.service.test_persistence_postgres -v` -> pass, `Ran 2 tests`
- `python scripts/verify-dependency-baseline.py` -> pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts` -> pass

- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1` -> pass,
  `OK python-bytecode`, `OK python-import`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` -> pass,
  `Ran 379 tests`, `OK (skipped=2)`, service discovery `Ran 10 tests`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` -> pass,
  schema/example/catalog/dependency/rollout/governance consistency checks OK
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1` -> pass,
  `OK python-asyncio`, `OK windows-node-csprng`, `OK codex-capability-ready`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs` -> pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts` -> pass

## Platform Notes
- Direct `codex --version`, `codex --help`, and `codex status` failed before Windows process
  environment initialization with Node `ncrypto::CSPRNG(nullptr, 0)`.
- After dot-sourcing `scripts/Initialize-WindowsProcessEnvironment.ps1`, `codex --version` and
  `codex --help` passed.
- `codex status` still returned `Error: stdin is not a terminal`; classified as `platform_na` for
  this non-interactive run. Alternative evidence: `scripts/doctor-runtime.ps1` reported
  `OK codex-capability-ready`.

## Risk And Rollback
- Risk: low. The Postgres path remains optional and lazy; no default dependency or default runtime
  backend changes were introduced.
- Rollback:
  - `git checkout -- packages/agent-runtime/persistence.py`
  - `git checkout -- scripts/verify-repo.ps1`
  - `git checkout -- tests/service/test_persistence_postgres.py`
  - `git checkout -- tests/README.md`
  - `git clean -f docs/change-evidence/20260425-postgres-service-gate-hardening.md`
