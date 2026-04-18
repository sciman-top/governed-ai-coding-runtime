# Adapter Degrade Policy

## Goal
让 adapter compatibility posture 显式可见，尤其是在上游能力面弱于 full governed enforcement 预期时。

## Baseline
- Codex 仍然是第一优先 adapter
- runtime 对弱能力面保持诚实
- 不支持的能力不能静默降级成看起来 fully governed 的姿态
- generic adapter posture 通过 `native_attach`、`process_bridge`、`manual_handoff` 表达

## Rules
- `full_support` 在 repo 也支持时保持请求姿态
- `partial_support` 必须带显式 `degrade_to` 和原因
- `unsupported` 如果没有显式 `degrade_to`，按 fail-closed 处理
- `unsupported` 且 `degrade_to: fail_closed` 时直接阻断
- `unsupported` 且显式降级到更弱姿态时，仅当 runtime 能清楚解释 enforcement 损失时才允许

## Operator Visibility
- 文档必须解释 degrade behavior
- sample repo profiles 必须携带 compatibility signals
- `doctor-runtime.ps1` 必须报告 adapter posture 可见

## Current Public Usable Release Posture
- Codex-first compatibility 是显式的
- structured upstream event visibility 仍然只是 partial
- 本地 runtime 通过 artifact-backed 的 status、verification、evidence、replay 输出来补偿

## Launch-Second Fallback
- Native attach 仍是首选姿态
- Process bridge launch mode 必须显式，不能描述成 native attach
- Process bridge 结果必须捕获 process output、exit code、changed-file discovery、verification refs
- 当 process bridge 不可用时，runtime 必须降级到 manual handoff，而不是伪装成更强 tier

## Tier Guarantees
- `native_attach` 保证 attached session boundary + same-contract verification
- `process_bridge` 保证 captured process boundary + same-contract verification
- `manual_handoff` 保证 explicit handoff posture + same-contract verification
- 这些 tier guarantees 必须同时出现在文档和 machine-readable contract 中

## Related
- [Adapter Capability Tiers](./adapter-capability-tiers.zh-CN.md)
- [English Version](./adapter-degrade-policy.md)
