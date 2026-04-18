# 单机 Runtime 快速开始

## Purpose
在一台机器上 bootstrap、运行、检查并清理 governed runtime，不依赖私有维护者知识。

## 范围边界
- 这个 quickstart 证明的是本地 governed runtime 路径
- 它不证明已经存在 direct Codex CLI/App execution adapter
- 下面的 `run-governed-task.py` 路径应理解为 runtime smoke task

当前 Codex 使用说明见：
- [Codex CLI/App Integration Guide](../product/codex-cli-app-integration-guide.md)
- [Codex CLI/App 集成指南](../product/codex-cli-app-integration-guide.zh-CN.md)
- [Codex Direct Adapter](../product/codex-direct-adapter.md)
- [在现有仓库中使用](./use-with-existing-repo.zh-CN.md)

## 运行 Codex adapter smoke trial

```powershell
python scripts/run-codex-adapter-trial.py `
  --repo-id "python-service" `
  --task-id "task-codex-trial" `
  --binding-id "binding-python-service"
```

预期 JSON 输出包含：
- `adapter_tier`
- `task_id`
- `binding_id`
- `evidence_refs`
- `verification_refs`
- `unsupported_capability_behavior`

## 前置条件
- Windows + PowerShell 7+
- `python` 或 `python3` 已在 `PATH`
- 当前仓库已 checkout 到现有 `Full Runtime` baseline

## Bootstrap
在仓库根目录运行：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/bootstrap-runtime.ps1
```

预期结果：
- `.runtime/tasks`
- `.runtime/artifacts`
- `.runtime/replay`
- JSON status 输出包含 `total_tasks`

## 创建并运行一个 runtime smoke task

```powershell
python scripts/run-governed-task.py create --goal "inspect runtime quickstart"
```

```powershell
python scripts/run-governed-task.py run --json
```

预期输出：
- `.runtime/tasks` 下的 task record
- `.runtime/artifacts/<task>/<run>/verification-output/` 下的 gate artifacts
- `.runtime/artifacts/<task>/<run>/evidence/` 下的 evidence bundle
- `.runtime/artifacts/<task>/<run>/handoff/` 下的 handoff package

## 检查运行状态

```powershell
python scripts/run-governed-task.py status --json
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
```

## 仓库验证

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```

## 清理
只重置本地 runtime state：

```powershell
Remove-Item -Recurse -Force .runtime
```

同时移除 managed workspaces：

```powershell
Remove-Item -Recurse -Force .governed-workspaces
```

## 相关文档
- [English Version](./single-machine-runtime-quickstart.md)
- [在现有仓库中使用](./use-with-existing-repo.zh-CN.md)
