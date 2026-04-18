# Write-Side Tool Governance

## Runtime Contract
write-side tools 不直接执行。一次写请求必须先经过治理：

1. 按已分配 workspace 的 path policy 校验目标路径
2. 对 `medium` 和 `high` tier 写入要求 rollback reference
3. 需要审批的写入在执行前暂停
4. 只有在 policy checks 通过且不需要审批时，才返回 allowed decision

## Fail-Closed Rules
- blocked paths 在创建 approval request 前就失败
- 没有 rollback reference 的 medium/high tier 写入在执行前失败
- 需要审批的写入返回 `approval_pending`，不会直接执行

## Rollback Reference Boundary
rollback reference 是 risky writes 必填的 trace 字段。根据下游实现，它可以指向 git diff、snapshot、migration rollback，或 recovery command。

## Related
- [English Version](./write-side-tool-governance.md)
