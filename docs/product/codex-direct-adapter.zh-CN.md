# Codex Direct Adapter

## Purpose
定义以 Codex 为优先的 adapter contract，同时避免把 runtime 做成 Codex-only。

这个 contract 记录 runtime 对 Codex CLI/App 集成姿态的认知，以及在缺少 full native attach capability 时应该如何降级。

## Adapter Identity
- adapter id: `codex-cli`
- auth ownership: `user_owned_upstream_auth`
- workspace control: `external_workspace`
- mutation model: `direct_workspace_write`

## Capability Fields
- tool visibility
- resume behavior
- evidence export capability
- adapter tier
- probe source
- posture reason
- unsupported capabilities
- unsupported capability behavior

## Adapter Tiers

### native_attach
仅在 live session attachment capability 可用时使用。

### process_bridge
当 native attach 不可用，但可以拉起并捕获一个 process boundary 时使用。

### manual_handoff
当 native attach 和 process bridge 都不可用时使用。

## 降级规则
- 缺失 native attach 必须被显式记录为 unsupported，不能靠暗示表达
- 缺失 structured event visibility 时，evidence quality 降级为 logs、transcript 或 manual summary
- 缺失 resume id support 时，必须记录为 manual resume behavior
- 缺失 structured evidence export 时，必须记录为 manual summary evidence capability
- process bridge 和 manual handoff 是兼容路径，不是 native attach

## Live Probe 与 Handshake
runtime 现在支持对 Codex surface 的真实探测与握手：
- `codex --version`：确认本机是否可达 Codex CLI。
- `codex --help`：推断 resume 与 event/export 能力提示。
- `codex status`：作为 live attach 握手信号。

当 `codex status` 无法完成（例如非交互环境出现 `stdin is not a terminal`）时，姿态会显式降级到 `process_bridge`，并保留降级原因。

Codex session identity 会进入 runtime task model：
- `session_id`
- `resume_id`
- `continuation_id`
- `flow_kind`（`live_attach` / `process_bridge` / `manual_handoff`）

## Runtime Boundary
Codex adapter 可以分类 Codex capability posture 和 evidence expectations，但它不能：
- 持有上游 Codex authentication
- 重定义 task lifecycle
- 放宽 approval requirements
- 改 canonical gate order
- 把弱能力伪装成 full native attach

## 工程态
- Codex 仍是 first-class direct adapter 优先对象。
- 过渡服务路径已支持 durable adapter-event 持久化。
- Claude Code 仍在通用 adapter contract 兼容边界内，但暂未成为 first-class direct adapter。

## Evidence Mapping
Codex session evidence 会按 governed task id 映射到 runtime evidence timeline：
- file changes -> `adapter_file_change`
- tool calls -> `adapter_tool_call`
- gate runs -> `adapter_gate_run`
- approval events -> `adapter_approval_event`
- handoff references -> `adapter_handoff`

姿态事件会记录 flow 属于 `live_attach`、`process_bridge` 还是 `manual_handoff`。

## Smoke Trial
使用 `scripts/run-codex-adapter-trial.py` 运行当前 Codex adapter smoke trial。

trial 默认是 safe-mode：
- 不需要真实高风险写入
- 除非显式传 `--native-attach`，否则不会宣称 native attach
- 会输出稳定 trial refs，便于在不依赖私有维护者上下文的情况下审查 task、binding、evidence、verification wiring
- 可以通过 `--probe-live` 使用真实 probe 结果推断 posture

示例：

```powershell
python scripts/run-codex-adapter-trial.py `
  --repo-id "python-service" `
  --task-id "task-codex-trial" `
  --binding-id "binding-python-service" `
  --probe-live
```

预期 JSON 字段：
- `mode`
- `repo_id`
- `task_id`
- `binding_id`
- `adapter_id`
- `adapter_tier`
- `unsupported_capabilities`
- `unsupported_capability_behavior`
- `flow_kind`
- `session_id`
- `resume_id`
- `continuation_id`
- `probe_source`
- `evidence_refs`
- `verification_refs`
- `handoff_ref`

## Related
- [Codex CLI/App 集成指南](./codex-cli-app-integration-guide.zh-CN.md)
- [Session Bridge 命令](./session-bridge-commands.zh-CN.md)
- [Adapter Degrade Policy](./adapter-degrade-policy.md)
- [English Version](./codex-direct-adapter.md)
