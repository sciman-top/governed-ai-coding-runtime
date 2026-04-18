# 最小审批与证据控制台

## Scope
MVP 控制台聚焦 control plane，暴露以下能力：

- pending-step approval
- pending-step rejection
- evidence inspection by task

它不会执行工具、不会管理工作区，也不会替代上游 coding agent UI。

## Control Operations
- `approve`: 通过 approval ledger 记录批准决定
- `reject`: 通过 approval ledger 记录拒绝决定
- `evidence_for_task`: 返回单个 task id 的 evidence timeline events

## Boundary
当前实现是 runtime facade，不是可视化 web console。后续 UI 可以调用同样的 control-plane operations，而不用改变 approval 或 evidence 语义。

## Related
- [English Version](./minimal-approval-evidence-console.md)
