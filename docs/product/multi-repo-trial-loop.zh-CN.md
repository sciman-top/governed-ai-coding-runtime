# 多仓试运行循环

## 状态
已退役。

## 退役原因
本仓不再管理 target-repo rollout、attachment posture、session-bridge 流程，也不再提供 batch apply-all 治理。因此旧的 multi-repo trial loop 只保留历史意义，相关证据仅作为 `docs/change-evidence/target-repo-runs/**` 的归档材料。

## 现在由什么替代
- `scripts/verify-repo.ps1` 的 repo-local 验证
- `scripts/operator.ps1 -Action FeedbackReport` 的 host-only 反馈
- `scripts/run-governed-task.py` 的 repo-local task/evidence 生成

## 历史边界
旧 trial artifacts 可以继续保留用于追溯，但不能再用来证明多仓 rollout 仍是当前支持能力。

## 相关文档
- [功能反馈闭环](./host-feedback-loop.zh-CN.md)
- [AI 编码使用指南](../quickstart/ai-coding-usage-guide.zh-CN.md)
