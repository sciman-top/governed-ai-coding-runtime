# Adapter Capability Tiers

## Purpose
定义用于分类 AI coding host 集成的通用 adapter tier，同时避免夸大治理强度。

## Tiers

### native_attach
- 最强 tier
- 存在 attached session boundary
- runtime 可以感知 adapter posture，而不把 fallback 伪装成 native

Governance guarantees:
- attached session boundary
- runtime-visible adapter posture
- same-contract verification required

### process_bridge
- 当 native attach 不可用时的 fallback tier
- runtime 可以拉起并捕获一个 process boundary

Governance guarantees:
- captured process boundary
- runtime-visible adapter posture
- same-contract verification required

### manual_handoff
- 最弱但受支持的 tier
- 没有 native attach，也没有 process bridge
- 执行被明确移交，而不是被描述成 fully governed

Governance guarantees:
- explicit manual handoff
- runtime-visible adapter posture
- same-contract verification required

## Honest Degrade Rule
- native attach 可以降级为 process bridge
- process bridge 可以降级为 manual handoff
- unsupported capability behavior 必须显式且 machine-readable
- 弱 tier 绝不能被描述成强 tier

## Codex Projection
Codex 仍是第一优先 direct adapter 目标，但其 posture 通过同一套 tier contract 投影：
- live attachment 可用时为 `native_attach`
- 只有 launch capture 而没有 attach 时为 `process_bridge`
- 两者都没有时为 `manual_handoff`

## Example Fixtures
参考样例位于 `schemas/examples/agent-adapter-contract/`：
- `manual-handoff.example.json`
- `process-bridge.example.json`

它们故意不是 Codex 专属 fixture，这样 degrade posture 保持 generic，而不是 Codex-only。

## Related
- [Agent Adapter Contract Spec](../specs/agent-adapter-contract-spec.md)
- [Adapter Degrade Policy](./adapter-degrade-policy.md)
- [Codex Direct Adapter](./codex-direct-adapter.zh-CN.md)
- [English Version](./adapter-capability-tiers.md)
