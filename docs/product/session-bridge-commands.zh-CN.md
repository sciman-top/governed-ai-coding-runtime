# Session Bridge 命令

## Purpose
定义第一版交互式 command surface，供 host adapter 在活跃 AI coding session 中调用 governed runtime 动作。

## Commands
- `bind_task`
- `show_repo_posture`
- `request_approval`
- `run_quick_gate`
- `run_full_gate`
- `inspect_evidence`
- `inspect_status`

## 必要上下文
每个命令都要携带：
- task id
- repo binding id
- adapter id
- risk tier
- structured payload

执行类命令还要携带 `PolicyDecision` 引用。

## 执行语义
- 只读命令：`execution_mode = read_only`
- allow 的 quick/full gate：`execution_mode = execute`
- escalate 的 quick/full gate：`execution_mode = requires_approval`
- deny 的 quick/full gate：fail closed，不会变成可执行命令

## PolicyDecision 边界
session bridge 不自己做 policy 决策，它只消费结果并归一化命令姿态：
- `allow` -> executable
- `escalate` -> approval-required
- `deny` -> fail closed

## 本地入口

```powershell
python scripts/session-bridge.py --help
```

支持的子命令：
- `bind-task`
- `repo-posture`
- `status`
- `request-gate`
- `launch`

本地入口返回结构化 JSON。对不支持的命令或能力，返回明确的 degrade 结果，并带 `unsupported_capability_behavior = manual_handoff`。

## Gate Requests
`request-gate` 通过现有 verification runner plan path 生成请求：
- `quick` -> `test -> contract`
- `full` -> `build -> test -> contract -> doctor`
- 当提供 `attachment_root` 和 `attachment_runtime_state_root` 时，返回的 gate commands 来自 attached target repo 的 light pack / repo profile，而不是 runtime repo 默认值

被 deny 的执行类命令不会被静默执行。

## Launch-Second Fallback
`launch` 是显式的 process bridge fallback，不会伪装成 native attach。

结果会包含：
- launch mode
- adapter tier
- process exit code
- stdout
- stderr
- changed files
- verification refs

如果 process bridge 不可用，则返回 manual handoff。

## Write Governance 归一化
现有本地 write governance 结果会先归一化为 `PolicyDecision`：
- allowed -> `allow`
- paused -> `escalate`
- blocked / invalid -> `deny`

## 相关文档
- [Session Bridge Command Spec](../specs/session-bridge-command-spec.md)
- [Policy Decision Spec](../specs/policy-decision-spec.md)
- [Target Repo 接入流程](./target-repo-attachment-flow.zh-CN.md)
- [English Version](./session-bridge-commands.md)
