# AI 编码使用指南

## 目的
说明当前仍然有效的、本仓本地化的 AI 编码协作路径。

## 当前产品边界
- 本仓是治理/runtime 侧车，不是新的执行宿主。
- 本仓不再向外部目标仓 rollout。
- 本仓不再提供 attachment、session-bridge 或 governed write bridge。
- 本仓仍负责：自仓门禁、全局规则同步、host feedback、自演化证据、continuity 和打包。

## 推荐入口
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action Help
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action Readiness -OpenUi
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action FeedbackReport
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action SelfEvolutionRecommend
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -Apply
```

## 典型模式

### 模式 A：本仓 Readiness
当你在本仓改代码时，使用这一条：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
```

### 模式 B：宿主反馈闭环
当你想统一判断宿主状态、规则漂移、以及下一步 bounded maintenance 动作时，使用：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action FeedbackReport
```

输出会刷新：
- `.runtime/artifacts/host-feedback-summary/latest.md`
- 最新自演化 recommendation / promotion artifacts

### 模式 C：Repo-Local Task 执行
当你需要在本仓生成 task/evidence/handoff 时，使用：

```powershell
python scripts/run-governed-task.py run --mode quick --json
```

## 已退役工作流
不要再用本仓做以下事情：
- target-repo attach 或 baseline rollout
- target-repo daily 或 batch apply-all
- session-bridge posture/evidence/handoff 命令
- attached-write 的 request/approve/execute 闭环

这些名字现在都会 fail-closed 返回明确退休提示。

## 相关文档
- [在现有仓库中使用](./use-with-existing-repo.zh-CN.md)
- [功能反馈闭环](../product/host-feedback-loop.zh-CN.md)
- [共享上下文连续性指南](../product/agent-continuity.zh-CN.md)
