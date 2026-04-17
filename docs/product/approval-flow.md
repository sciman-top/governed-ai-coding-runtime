# Approval Flow

## Runtime Contract
Approval-required work enters `approval_pending` before execution. The approval ledger records:

- the approval request object
- terminal decision state
- actor that made the decision
- audit events for creation and decision

## Supported Decisions
- `approve`: allows downstream execution to resume.
- `reject`: blocks the requested work.
- `revoke`: invalidates a previously pending request.
- `timeout`: closes stale pending requests without operator approval.

## Persistence Boundary
The current implementation is an in-memory contract ledger in `packages/contracts`. It proves the state model, retrieval by `approval_id`, and audit trail semantics. Production persistence is a later service concern and must preserve these state names and audit events.
