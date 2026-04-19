# Write-Side Tool Governance

## Runtime Contract
Write-side tools do not execute directly. A write request first passes through governance:

1. Validate the target path against the allocated workspace path policy.
2. Require rollback references for `medium` and `high` tier writes.
3. Pause approval-required writes before execution.
4. Return an allowed decision only after policy checks pass and approval is not required.

The runtime-owned write flow is session-bridge-first:
- `write_request` -> `write_approve` -> `write_execute` -> `write_status`
- each step carries stable `execution_id` and `continuation_id`
- each execution binds adapter/session identity and produces explicit approval/artifact/handoff/replay refs
- shell/git/package actions use the same flow when invoked as governed tool executions
- package-manager commands must stay dry-run/list/check bounded unless a stricter policy explicitly expands coverage

## Fail-Closed Rules
- Blocked paths fail before any approval request is created.
- Medium and high tier writes without rollback references fail before execution.
- Approval-required writes return `approval_pending` instead of executing.
- High-risk (`tier=high`) writes fail closed when approval is missing or stale.

## Rollback Reference Boundary
The rollback reference is a required trace field for risky writes. It may point to a git diff, snapshot, migration rollback, or recovery command, depending on the downstream implementation.
