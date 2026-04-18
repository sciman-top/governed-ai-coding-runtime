# Write Policy Defaults

## Decision
MVP write policy 默认保持保守：

- `low` tier 写入在 path-scope 校验后可无人工审批执行
- `medium` tier 写入默认需要审批
- `high` tier 写入始终需要显式审批

## Runtime Contract
默认策略从每个 repo profile 解析：

- `risk_defaults.default_write_tier` 定义任务未声明 tier 时的默认值
- `approval_defaults.medium_write_requires_approval` 控制 medium-tier 行为，默认 `true`
- `approval_defaults.high_requires_explicit_approval` 必须为 `true`；关闭它的 profile 视为无效

## Downstream Implementation Notes
- Approval service 必须把 `high` 当作 fail-closed，直到存在显式审批结果
- Tool governance 只能自动执行 `low` tier 写入，且前提是 workspace / path policy checks 通过
- 未来若放宽 `medium` 行为，必须作为 policy change 留下 evidence 和 rollback notes

## Related
- [English Version](./write-policy-defaults.md)
