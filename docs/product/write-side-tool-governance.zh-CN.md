# 写侧工具治理

## 当前边界
本仓不再拥有基于 attachment 或 session-bridge 的写入执行链。

当前写侧治理只保留 repo-local 语义：
1. 严格遵守本仓 path policy
2. 对中高风险改动保留 rollback-ready 约束
3. 完成声明前仍需跑 canonical hard-gate chain
4. 证据与交接材料继续落在本地 runtime/task surface

## Fail-Closed 规则
- 被阻断路径在有效写入前就会失败
- 中高风险工作仍要求具备可回滚依据
- 已退役 attachment/write 命令会 fail-closed，而不是静默转发
- 打包等受保护操作仍受 repo-local policy 与 evidence 约束

## 不是当前能力的内容
- session-bridge 的 write request/approve/execute
- attached target-repo 的写入代理
- 基于 light-pack 的外部仓写入

## 相关文档
- [写策略默认值](./write-policy-defaults.zh-CN.md)
- [审批流程](./approval-flow.zh-CN.md)
