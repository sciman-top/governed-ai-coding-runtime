# Approval Flow

## Runtime Contract
需要审批的工作在执行前进入 `approval_pending`。approval ledger 会记录：

- approval request object
- terminal decision state
- 做出决定的 actor
- creation / decision 对应的 audit events

## Supported Decisions
- `approve`: 允许下游执行恢复
- `reject`: 阻断所请求的工作
- `revoke`: 使先前 pending 的请求失效
- `timeout`: 在没有 operator approval 的情况下关闭过期 pending 请求

## Persistence Boundary
当前实现是在 `packages/contracts` 中的内存版 contract ledger。它证明了 state model、按 `approval_id` 检索、以及 audit trail 语义。生产级持久化属于后续服务化问题，但必须保持这些状态名和审计事件不变。

## Related
- [English Version](./approval-flow.md)
