# 20260420 HTTP Control Plane, Postgres Metadata, and Adapter Event Ingestion

## Goal
Land a transition runtime slice with:
- FastAPI control-plane entrypoint
- optional Postgres-backed metadata path
- durable adapter-event sink and operator read path
- synchronized architecture/product engineering-state wording

## Scope
- `pyproject.toml` optional `service` extras are present.
- Added `AdapterEventSink` over metadata store.
- Extended service facade and operator route for `inspect_adapter_events`.
- Added FastAPI app factory and `--serve` mode in control-plane main entrypoint.
- Added durable Codex adapter event record normalization and optional sink wiring in session bridge.
- Updated architecture/product docs with `Current / Transition / North-Star` wording and Codex/Claude boundary.

## Verification
Executed in `feature/http-control-plane-postgres-adapter-events` worktree.

### Targeted tests
- `python -m unittest tests.service.test_persistence_postgres tests.service.test_adapter_event_sink tests.service.test_session_api tests.service.test_operator_api tests.service.test_http_control_plane -v`
  - `Ran 14 tests`
  - `OK (skipped=3)`
  - skipped reason: `service extras not installed` for FastAPI HTTP tests
- `python -m unittest tests.runtime.test_codex_adapter -v`
  - `Ran 15 tests`
  - `OK`

### Required gate order
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
   - `OK python-bytecode`
   - `OK python-import`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
   - `Ran 243 tests`
   - `OK`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
   - `OK schema-json-parse`
   - `OK schema-example-validation`
   - `OK schema-catalog-pairing`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
   - doctor checks all `OK`, including runtime paths and gate command visibility

## Compatibility Notes
- Codex remains first-class direct-adapter priority.
- Claude Code remains supported by the generic adapter contract boundary; this slice does not add Claude-specific direct adapter implementation.
- Legacy compatibility path remains valid: direct facade + SQLite/filesystem.

## Rollback
- Git rollback at commit granularity for this branch.
- Runtime rollback path remains: disable service mode and continue direct facade path.
- Metadata rollback path remains: use SQLite metadata backend when Postgres/service extras are unavailable.
