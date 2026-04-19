# Minimal Approval And Evidence Console

## Scope
The MVP console is control-plane focused. It exposes:

- pending-step approval
- pending-step rejection
- attachment-scoped evidence inspection by task or binding
- attachment-scoped handoff and replay inspection
- attachment posture summary and remediation hints

It does not execute tools, manage workspaces, or replace an upstream coding agent UI.

## Control Operations
- `approve`: records an approval decision through the approval ledger.
- `reject`: records a rejection decision through the approval ledger.
- `inspect_evidence`: returns approval, evidence, handoff, replay, and posture refs for one task id.
- `inspect_handoff`: returns handoff and replay refs for one task id.
- `status`: returns attachment posture summary with read-only remediation guidance.

## Read-Only Contract
- Operator query surfaces are read-only.
- Attachment posture states `missing_light_pack`, `invalid_light_pack`, and `stale_binding` are fail-closed for execution paths.
- `inspect_evidence` on the primary attached path should return an empty read payload instead of degrading when task data is absent.

## Boundary
The current implementation is a runtime facade, not a visual web console. A future UI can call the same control-plane operations without changing approval or evidence semantics.
