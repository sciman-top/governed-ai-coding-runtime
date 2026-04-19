# 最小审批与证据控制台

## Scope
MVP 控制台聚焦 control plane，暴露以下能力：

- pending-step approval
- pending-step rejection
- 按 attachment 作用域查询 task/binding 证据
- 按 attachment 作用域查询 handoff 与 replay
- 查询 attachment posture 与 remediation 提示

它不会执行工具、不会管理工作区，也不会替代上游 coding agent UI。

## Control Operations
- `approve`: 通过 approval ledger 记录批准决定
- `reject`: 通过 approval ledger 记录拒绝决定
- `inspect_evidence`: 返回单个 task 的 approval/evidence/handoff/replay/posture refs
- `inspect_handoff`: 返回单个 task 的 handoff 与 replay refs
- `status`: 返回 attachment posture 摘要与只读 remediation 指引

## 只读约束
- Operator 查询面保持只读，不直接执行写操作。
- `missing_light_pack`、`invalid_light_pack`、`stale_binding` 视为 fail-closed 姿态，不应继续执行。
- 主 attachment 路径下的 `inspect_evidence` 在缺少 task 数据时返回空只读结果，而不是默认 degraded。

## Boundary
当前实现是 runtime facade，不是可视化 web console。后续 UI 可以调用同样的 control-plane operations，而不用改变 approval 或 evidence 语义。

## Related
- [English Version](./minimal-approval-evidence-console.md)
