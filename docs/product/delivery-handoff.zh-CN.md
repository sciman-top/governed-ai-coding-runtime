# Delivery Handoff

## Package Contents
每个已完成任务都会生成一个 delivery handoff package，包含：

- task id
- changed files
- verification artifact
- validation status
- risk notes
- replay references

## Validation Status
- `fully_validated`: full verification 已运行且所有 full gates 通过
- `partially_validated`: quick verification、`gate_na`、缺失 gates 或任何非 full verification 路径

## Replay References
失败、中断或未运行的路径必须附 replay references。它可以是命令、evidence 文件、failure log 或 recovery instruction，用来让下一个 operator 复现或继续该路径。

## Related
- [English Version](./delivery-handoff.md)
