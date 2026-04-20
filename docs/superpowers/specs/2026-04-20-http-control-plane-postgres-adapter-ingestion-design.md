# HTTP Control Plane, Postgres Metadata, and Adapter Event Ingestion Design

## Status
- Proposed and approved in interactive design review on 2026-04-20.
- This spec defines the next engineering-state slice, not a full platform rewrite.

## Goal
Move the repository one concrete step from a script-heavy governed runtime toward a service-shaped runtime by landing:
- a real HTTP control plane
- a durable Postgres-backed metadata path
- a durable adapter-event ingestion path
- synchronized engineering-state documentation

## Why This Change Is Needed
The repository already has a validated governance kernel, session bridge, attachment model, and Codex-first adapter posture. That is enough to support the current direct-to-hybrid final-state claim on the repository's own terms.

It is not yet the strongest engineering end state because three important runtime traits are still only partially real:
- the control plane is still primarily a local facade and dispatch surface rather than a true HTTP API boundary
- metadata persistence is still centered on SQLite and filesystem primitives instead of the documented PostgreSQL transition target
- adapter evidence is normalized and summarized, but not yet written through a durable event sink that later service and operator surfaces can reuse

This change addresses those gaps without discarding the current kernel.

## Non-Goals
- Do not replace the governance kernel.
- Do not replace the current CLI/operator entrypoints in one pass.
- Do not migrate every runtime artifact, task record, replay record, or evidence bundle into PostgreSQL in this slice.
- Do not take ownership of upstream Codex authentication.
- Do not introduce a first-class Claude Code direct adapter in this slice.
- Do not introduce Temporal, Redis, OPA/Rego, or other north-star dependencies.
- Do not change canonical gate order: `build -> test -> contract/invariant -> hotspot`.

## Current State

### Landed Today
- `apps/control-plane/app.py` provides an internal dispatch layer for `/session`, `/operator`, and `/health` semantics.
- `packages/agent-runtime/service_facade.py` exposes a service-shaped facade, but it is still consumed primarily as local Python wiring.
- `packages/agent-runtime/persistence.py` provides a SQLite metadata store.
- `packages/contracts/.../codex_adapter.py` can probe Codex posture, derive session identity, and map normalized adapter evidence.
- `packages/contracts/.../session_bridge.py` already carries adapter identity through governed gate and write flows.

### Engineering-State Gap
- No true FastAPI application exists yet.
- No Postgres metadata store exists behind the service layer.
- No dedicated adapter event sink persists structured adapter events for later query and replay use.
- Engineering-state docs still mix landed baseline, transition target, and north-star target too loosely.

## Options Considered

### Option A: Thin Vertical Slice Across All Three Gaps
Land a minimal FastAPI control plane, a Postgres metadata store for a narrow namespace set, and an adapter event sink in one integrated slice.

Pros:
- turns the target direction into real code immediately
- produces a usable engineering-state upgrade rather than another facade-only step
- gives docs a truthful new transition boundary

Cons:
- touches multiple subsystems in one iteration
- requires disciplined scope control

### Option B: HTTP First, Persistence and Ingestion Later
Make the control plane a real API first, but keep existing metadata and adapter evidence paths.

Pros:
- lowest immediate implementation risk
- easiest to explain and test

Cons:
- mostly produces a transport shell around the current implementation
- delays the harder but more meaningful engineering-state improvements

### Option C: Adapter Ingestion First, Service Later
Make adapter events durable first, then add HTTP and Postgres shape around them later.

Pros:
- improves host-integration truth fastest
- directly strengthens evidence quality

Cons:
- risks creating another intermediate local-only path that will need reshaping later
- weaker operator and service story in the short term

## Chosen Approach
Choose Option A, but keep it narrow.

The slice will land three things together:
1. a real FastAPI application with minimal endpoints
2. a Postgres metadata store for only `verification_runs` and `adapter_events`
3. a dedicated adapter event sink wired into the Codex adapter evidence path

Everything else remains compatibility-mode or fallback.

## Architecture

### Layering
The new runtime shape remains layered:
- contracts and governance semantics stay in `packages/contracts/`
- service orchestration stays in `packages/agent-runtime/`
- HTTP transport lives in `apps/control-plane/`
- infra scaffolding remains under `infra/local-runtime/`

The HTTP layer must not invent new runtime semantics. It should only expose the existing runtime model through a stable API boundary.

### Runtime Paths
There will now be two valid execution paths:

#### Path 1: Compatibility Path
- CLI invokes `RuntimeServiceFacade` directly.
- SQLite and filesystem remain valid.
- No service dependencies required.

#### Path 2: Service Path
- FastAPI serves `/health`, `/session`, and `/operator`.
- `RuntimeServiceFacade` is created inside the HTTP app.
- Metadata writes use Postgres when configured and available.
- Adapter events are written into the durable metadata sink.

The compatibility path is not removed in this slice.

## Component Design

### 1. FastAPI Control Plane
Create `apps/control-plane/http_app.py`.

Responsibilities:
- instantiate FastAPI
- wire `/health`, `/session`, `/operator`
- construct `RuntimeServiceFacade`
- choose metadata store based on configuration
- expose the same logical payloads already used by the current control-plane facade

This application is the first true HTTP control-plane boundary for the runtime.

`apps/control-plane/main.py` should evolve into a dual-mode entrypoint:
- `serve` mode for FastAPI/uvicorn startup
- existing one-shot route-dispatch mode for compatibility and tests

### 2. Service Facade Extension
`packages/agent-runtime/service_facade.py` remains the service orchestration boundary.

New responsibilities:
- accept injected metadata store
- accept injected adapter event sink
- route session/operator actions through those dependencies when present
- preserve existing contract parity for legacy callers

The facade remains the only boundary the HTTP layer should call directly.

### 3. Persistence Abstraction
Extend `packages/agent-runtime/persistence.py`.

Required interface:
- `upsert(namespace, key, payload)`
- `get(namespace, key)`
- `list_namespace(namespace)`

Existing `SqliteMetadataStore` remains.
Add `PostgresMetadataStore` with the same interface.

Initial Postgres coverage is intentionally narrow:
- `verification_runs`
- `adapter_events`

Do not migrate all runtime state in this slice.

### 4. Adapter Event Sink
Create `packages/agent-runtime/adapter_event_sink.py`.

Responsibilities:
- accept normalized adapter-event payloads
- persist them to the active metadata store
- return stable metadata references or ids for later operator queries

The sink is an application-layer component, not a contract-layer primitive. The contract layer continues to define event meanings; the sink only stores them durably.

### 5. Codex Adapter Event Flow
`packages/contracts/.../codex_adapter.py` already knows how to:
- probe capability
- derive session identity
- record normalized adapter evidence into an in-memory timeline

This slice extends the path so that relevant structured events are also emitted to the adapter event sink through service/session execution.

The sinked events must preserve:
- `task_id`
- `adapter_id`
- `adapter_tier`
- `flow_kind`
- `execution_id`
- `continuation_id`
- event type
- event payload
- event source
- timestamp

### 6. Operator Query Surface
The operator surface must gain access to durable adapter-event reads.

Query expectations:
- list adapter events for a task
- optionally filter by run or execution id when that context exists
- return both event summary and raw event records when requested

This extends the operator plane from evidence references toward actual adapter-event inspection.

## API Boundary

### `/health`
Purpose:
- expose service health and basic runtime identity

Minimum response:
- service status
- repo root
- task root
- active metadata backend type

### `/session`
Purpose:
- expose the current `session_bridge`-backed runtime command surface over HTTP

Requirements:
- preserve the existing payload semantics used by the current service tests
- preserve policy-decision and continuation-id behavior
- support attachment-root and attachment-runtime-state-root fields when relevant

### `/operator`
Purpose:
- expose status, evidence inspection, handoff inspection, and durable adapter-event reads

At minimum:
- `status`
- `inspect_evidence`
- `inspect_handoff`
- `inspect_adapter_events`

The operator plane remains read-only in this slice.

## Persistence Design

### Dependency Strategy
Add `pyproject.toml`.

Use optional dependency groups so the repository keeps a lightweight baseline while gaining reproducible service dependencies:
- base: minimal project metadata and baseline Python support
- `service` extra: `fastapi`, `uvicorn`, `psycopg`
- test/dev extras only if necessary for service tests

This approach is chosen because:
- it makes the new service path reproducible
- it avoids forcing the whole repository into service dependencies immediately
- it preserves the current compatibility path when extras are not installed

### Postgres Scope
Postgres is only required for the new service slice when configured.

Fallback behavior:
- if Postgres configuration is absent, the service can still use SQLite metadata
- if service extras are absent, the old compatibility path remains available

This is intentional. The slice is meant to advance engineering-state reality, not to break the current baseline.

## Codex and Claude Code Compatibility

### Codex CLI/App
Codex remains the first-class direct adapter priority.

This slice improves Codex compatibility by:
- giving Codex-backed governed flows a true HTTP service boundary
- persisting adapter events durably
- making operator inspection of adapter events more honest

It does not:
- replace Codex host UX
- take over Codex auth
- promise native attach in every environment

### Claude Code
Claude Code remains inside the supported adapter-contract boundary, but not as a first-class direct adapter in this slice.

Meaning:
- engineering docs should state that Claude Code is a supported host family by contract
- it may eventually map into the same `native_attach / process_bridge / manual_handoff` model
- this slice does not add a Claude-specific probe, handshake, or direct integration implementation

This distinction is important because the repository should remain host-compatible without pretending every host already has equal productization depth.

## Documentation Changes

### Update
- `docs/architecture/hybrid-final-state-master-outline.md`
- `docs/architecture/local-baseline-to-hybrid-final-state-migration-matrix.md`
- `docs/product/codex-cli-app-integration-guide.md`
- `docs/product/codex-cli-app-integration-guide.zh-CN.md`
- `docs/product/codex-direct-adapter.md`
- `docs/product/codex-direct-adapter.zh-CN.md`

### Add
- one new `docs/change-evidence/<date>-<slug>.md`

### Documentation Outcome
The engineering-state story should be rewritten in three layers:
- `Current Landed Runtime`
- `Transition Runtime Target`
- `North-Star Best-Practice Runtime`

That wording should explicitly state:
- what is already real today
- what becomes newly real after this slice
- what still remains north-star only

## Testing And Verification

### Existing Gates Must Still Pass
- `build`
- `test`
- `contract/invariant`
- `hotspot`

### New Verification Expectations
- service tests can hit real FastAPI endpoints with `TestClient`
- direct facade parity is preserved for existing service tests
- Postgres-backed metadata store passes basic CRUD tests for the two namespaces in scope
- adapter events can be durably written and later queried through the operator surface

### Minimum New Tests
- HTTP `/health` endpoint test
- HTTP `/session` parity test
- HTTP `/operator` status and adapter-event inspection test
- Postgres metadata store smoke test
- adapter event sink write/read test

## Rollout And Rollback

### Rollout
- land service dependencies as optional extras
- keep old CLI/facade paths valid
- default to compatibility mode unless service path is explicitly enabled

### Rollback
If the new slice regresses service or runtime behavior:
- disable service mode
- fall back to direct facade path
- fall back to SQLite metadata
- keep operator and session semantics on the current baseline path

Because the new slice is additive, rollback should not require reverting the governance kernel itself.

## Risks
- introducing service dependencies can create new environment drift if installation instructions are unclear
- dual-path execution can drift if API and facade parity are not tested strictly
- event persistence can become schema-fragile if adapter payloads are not normalized before storage
- documentation can overstate completion unless engineering-state wording is tightened carefully

## Mitigations
- keep dependencies optional and explicit
- keep facade and HTTP parity tests
- persist only normalized event shapes in this slice
- document remaining north-star-only items explicitly

## Success Criteria
This slice is successful when all of the following are true:
- the repository has a real FastAPI control plane
- the service path can use Postgres for `verification_runs` and `adapter_events`
- Codex adapter events can be durably persisted and queried
- existing compatibility paths still work
- engineering-state documentation clearly separates landed, transition, and north-star layers
- Codex CLI/App and Claude Code compatibility boundaries are documented honestly

## Out Of Scope For The Next Plan
The implementation plan for this spec should not include:
- full runtime-state migration to Postgres
- long-running worker orchestration redesign
- multi-host direct adapter rollout beyond Codex
- Temporal/Redis/OPA/Rego adoption
- host-auth ownership changes
