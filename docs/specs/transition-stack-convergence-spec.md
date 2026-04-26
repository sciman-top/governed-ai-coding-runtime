# Transition Stack Convergence Spec

## Status
Draft

## Purpose
Define the mechanical gate that prevents the transition stack from becoming an unbounded dependency wishlist.

The runtime may introduce service-shaped dependencies only when an active boundary proves the need. The current local filesystem and JSON Schema baseline remains valid until a boundary pressure justifies promotion.

## Required Fields
- policy_id
- status
- components
- runtime_guards
- evidence_refs
- rollback_ref

## Component Fields
- component_id
- module_roots
- adoption_status
- owner_boundary
- allowed_when
- evidence_refs
- rollback_ref

## Enumerations
### status
- observe
- enforced
- waived

### adoption_status
- not_present
- local_only
- active_boundary
- watch
- deferred

## Invariants
- `FastAPI` is allowed only when a real service API boundary owns the route surface and parity evidence exists.
- `Pydantic v2` may validate API/runtime inputs, but JSON Schema remains the cross-tool contract truth.
- local filesystem and SQLite-style metadata remain valid for single-machine operation.
- `PostgreSQL` adoption requires service-shaped metadata pressure, rollback notes, and evidence.
- tracing hooks must exist at runtime/API boundaries without requiring the full external observability stack.
- CLI and API execution-like paths must share contract behavior and be protected by parity tests plus wrapper drift guards.
- observed transition-stack imports must map to a component whose status is `active_boundary` or `local_only`; otherwise the verifier fails closed.

## Non-Goals
- requiring `FastAPI`, `Pydantic`, `PostgreSQL`, or external `OpenTelemetry` packages before a boundary needs them
- replacing existing dependency-baseline checks
- approving final-state candidates such as workflow engines, external policy engines, event buses, semantic stores, or a full observability stack

