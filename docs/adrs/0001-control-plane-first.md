# ADR-0001: Control Plane First

## Status
Accepted

## Date
2026-04-17

## Context
The platform is intended to govern AI coding execution, not just host agent logic. If the execution runtime is built first without explicit control-plane contracts, approval, risk, audit, and rollback logic become ad hoc and difficult to recover later.

## Decision
Build the platform around a control plane first:
- task intake and scope lock
- policy and risk evaluation
- approval orchestration
- evidence and rollback references
- execution state tracking

Agent execution remains a subordinate capability inside this control plane.

## Alternatives Considered
### Runtime-first
- Pros: faster demo
- Cons: weak governance boundaries, harder to retrofit approval and audit
- Rejected: optimizes for demo velocity over product integrity

### Pure workflow-first without explicit control plane
- Pros: durable execution from the start
- Cons: workflows alone do not define ownership, risk, or policy source of truth
- Rejected: durable execution is necessary but insufficient

## Consequences
- early implementation effort shifts toward contracts and policy modeling
- agent runtime can remain simpler in Phase 1
- control, approval, and audit become stable integration surfaces
