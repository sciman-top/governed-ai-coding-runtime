# Minimal Approval And Evidence Console

## Scope
The MVP console is control-plane focused. It exposes:

- pending-step approval
- pending-step rejection
- evidence inspection by task

It does not execute tools, manage workspaces, or replace an upstream coding agent UI.

## Control Operations
- `approve`: records an approval decision through the approval ledger.
- `reject`: records a rejection decision through the approval ledger.
- `evidence_for_task`: returns evidence timeline events for one task id.

## Boundary
The current implementation is a runtime facade, not a visual web console. A future UI can call the same control-plane operations without changing approval or evidence semantics.
