# Write-Side Tool Governance

## Runtime Contract
Write-side tools do not execute directly. A write request first passes through governance:

1. Validate the target path against the allocated workspace path policy.
2. Require rollback references for `medium` and `high` tier writes.
3. Pause approval-required writes before execution.
4. Return an allowed decision only after policy checks pass and approval is not required.

## Fail-Closed Rules
- Blocked paths fail before any approval request is created.
- Medium and high tier writes without rollback references fail before execution.
- Approval-required writes return `approval_pending` instead of executing.

## Rollback Reference Boundary
The rollback reference is a required trace field for risky writes. It may point to a git diff, snapshot, migration rollback, or recovery command, depending on the downstream implementation.
