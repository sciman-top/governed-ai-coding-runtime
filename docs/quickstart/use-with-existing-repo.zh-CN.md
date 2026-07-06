# 在现有仓库中使用

## 短答案
不能再通过本仓旧的一键 rollout 路径来做。

从 2026-07-06 起，本仓不再 attach 外部目标仓，不再向外部仓写治理基线，也不再暴露 attachment、session-bridge 或 apply-all 流程。

## 仍然保留的能力
- `~/.codex`、`~/.claude` 的全局规则同步
- 对采用 `AGENTS.md` 共同主体 + `CLAUDE.md` thin wrapper 的目标仓做项目规则协同审计
- 本仓自己的验证与 operator 工作流
- 通过 `scripts/run-governed-task.py` 生成 repo-local task/status/evidence
- host feedback、自演化、continuity、portable packaging

## 如果另一仓库也需要治理
直接在那一仓库内维护。

推荐做法：
1. 在目标仓自己维护 `build -> test -> contract/invariant -> hotspot`。
2. 在目标仓以 `AGENTS.md` 作为共同项目规则主体，并让 `CLAUDE.md` 保持 thin wrapper，而不是依赖本仓统一下发项目规则。
3. 只把本仓当作 audit / verifier / pattern source，不对目标仓根规则文件做 blind overwrite。
4. rollout evidence 与验收证明留在目标仓，不回写到本仓当作当前 live capability。

## 在本仓仍应使用的命令
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -Apply
```

```powershell
python scripts/verify-target-project-rules.py --targets local-ai-dev-orchestrator
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action Readiness -OpenUi
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action FeedbackReport
```

```powershell
python scripts/run-governed-task.py status --json
```

## 已退役命令
以下名称已明确退役，现在都会 fail-closed 返回退休提示：
- `runtime-flow-preset`
- `runtime-flow`
- `attach-target-repo`
- `session-bridge`
- `verify-attachment`
- `govern-attachment-write`
- `decide-attachment-write`
- `execute-attachment-write`
- `ApplyAllFeatures`
- `DailyAll`
- `GovernanceBaselineAll`
- `CleanupTargets`
- `UninstallGovernance`

## 相关文档
- [单机 Runtime 快速开始](./single-machine-runtime-quickstart.zh-CN.md)
- [AI 编码使用指南](./ai-coding-usage-guide.zh-CN.md)
- [功能反馈闭环](../product/host-feedback-loop.zh-CN.md)
