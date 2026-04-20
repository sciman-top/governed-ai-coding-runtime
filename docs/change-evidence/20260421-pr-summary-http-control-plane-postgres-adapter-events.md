# PR Summary: HTTP Control Plane + Postgres Metadata + Adapter Event Ingestion

## Branch
- `feature/http-control-plane-postgres-adapter-events`

## Goal
Land a transition runtime slice that keeps compatibility mode intact while adding:
- real FastAPI control-plane boundary
- optional Postgres metadata path
- durable adapter-event sink and operator read surface
- synchronized engineering-state documentation

## What Changed
- Added durable adapter event sink:
  - `packages/agent-runtime/adapter_event_sink.py`
  - `tests/service/test_adapter_event_sink.py`
- Extended service facade/operator surface:
  - metadata backend visibility in health payload
  - operator `inspect_adapter_events` read action
- Added FastAPI control-plane app and serve mode:
  - `apps/control-plane/http_app.py`
  - `apps/control-plane/main.py` (`--serve --host --port`)
  - `tests/service/test_http_control_plane.py`
- Added durable Codex adapter event normalization and sink wiring:
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/codex_adapter.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
  - `tests/runtime/test_codex_adapter.py`
- Synced architecture/product docs and change evidence:
  - engineering-state layers (`Current / Transition / North-Star`)
  - Codex-first and Claude Code compatibility boundary wording

## Commits
- `1602fe8` feat: land transition service path for runtime control plane
- `50e0680` feat: normalize and persist codex adapter events
- `3e1a066` feat: add fastapi control plane entrypoint
- `cf64f27` feat: expose metadata backend and adapter event reads from service facade
- `b2a8996` feat: add durable adapter event sink
- plus previously landed Task 1 commits:
  - `9defc45`, `901abd7`, `154196b`

## Verification Evidence
- Service tests:
  - `python -m unittest tests.service.test_http_control_plane -v`
  - `Ran 3 tests in 0.143s`
  - `OK`
- Service compatibility tests:
  - `python -m unittest tests.service.test_persistence_postgres tests.service.test_adapter_event_sink tests.service.test_session_api tests.service.test_operator_api -v`
  - `Ran 11 tests in 0.506s`
  - `OK`
- Runtime contract tests:
  - `python -m unittest tests.runtime.test_codex_adapter -v`
  - `OK`
- Full repo gate chain:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
  - `Ran 243 tests`
  - `OK`

## Compatibility and Scope Notes
- Codex remains first-class direct-adapter productization priority.
- Claude Code remains within the generic adapter-contract compatibility boundary in this slice.
- Compatibility path remains valid: direct facade + SQLite/filesystem when service extras are absent.

## Risks
- Two-path operation (compatibility path vs service path) can drift without parity tests.
- Adapter-event payload shape can drift if future adapters bypass normalization.

## Rollback
- Disable service mode and continue direct facade path.
- Switch metadata backend to SQLite path.
- Revert this branch commit range if needed.
