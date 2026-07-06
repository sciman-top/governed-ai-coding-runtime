# 共享上下文连续性指南

## 目的
说明本仓如何在不改写宿主原生历史、不复制 secret 的前提下，为 `Codex`、`Claude Code` 及相邻宿主面提供可移植的 cross-host continuity。

## 当前边界
- 宿主原生历史仍归宿主所有。
- 共享层只存放分类后的元数据：
  - summary
  - evidence refs
  - handoff refs
  - next actions
  - retention 与 sensitivity labels
- 含有 secret-like 内容的 payload 会在写入 runtime-owned continuity index 之前 fail closed。
- `Claude Desktop` 仍是 `referenced_only` 边界，不是共享可写历史存储。

## 连续性分类
| 分类 | 含义 | 常见用途 |
|---|---|---|
| `native_shared` | 同一宿主家族可安全复用自己的原生状态 | 共享 `~/.codex`、Claude Code transcript root |
| `portable_shared` | runtime-owned 共享工件 | handoff summary、evidence-linked continuity record |
| `referenced_only` | 只允许引用，不复制进共享层 | transcript 路径、Desktop 边界、外部导出路径 |
| `isolated_secret` | 绝不能复制进共享连续性 | API key、cookie、refresh token、原始 auth 快照 |

## 主要入口

### 只读审计
```powershell
python scripts/agent-continuity.py audit --json
```

它会返回当前 continuity posture：
- `codex-shared-home`
- `claude-shared-home`
- `claude-desktop-boundary`

这个审计是 classification-first，不会修改宿主状态。

### runtime-owned continuity index
```powershell
python scripts/agent-continuity.py search --index-root .runtime/agent-continuity --repo-id governed-ai-coding-runtime --json
```

本地 continuity index 是可移植共享面的入口，用于：
- classified shared records
- evidence-linked handoff 检索
- 按 repo/host/provider 范围查询

### Operator 面板
使用交互式 operator 查看 continuity 面板：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action OperatorUi
```

continuity 面板是只读的，会展示：
- 分类后的 continuity records
- continuity class
- redaction/secret boundary 状态
- runtime-owned continuity JSON

## 写入边界
只有分类后的 portable records 才允许写入 continuity index。

当前保证：
- 含 blocked secret material 的记录会被拒绝
- 命中 secret-like 文本模式的记录会被拒绝
- 这条流不会改写宿主原生 auth/provider/history 状态

## 实际应如何理解
- `Codex` continuity 在一个共享 Codex home 内最强；跨宿主共享只通过 classified records 实现。
- `Claude Code` continuity 锚定在一个 Claude home 上；跨宿主共享通过 handoff/index records 实现。
- `Claude Desktop` 会被诚实记录为边界面，而不是可写共享 continuity store。

## 不应宣称
- 不应宣称 Codex 与 Claude 的原生历史已经被合并。
- 不应宣称 Claude Desktop 聊天历史已经成为 runtime-owned shared store。
- 不应宣称 credentials、cookies、tokens 或 raw transcripts 会被复制进 continuity layer。

## 相关文件
- [Agent Continuity And Shared Context Plan](../plans/agent-continuity-and-shared-context-plan.md)
- [Codex / Claude 功能反馈闭环](./host-feedback-loop.zh-CN.md)
- [Codex CLI/App 集成指南](./codex-cli-app-integration-guide.zh-CN.md)
- [Change Evidence Index](../change-evidence/README.md)
