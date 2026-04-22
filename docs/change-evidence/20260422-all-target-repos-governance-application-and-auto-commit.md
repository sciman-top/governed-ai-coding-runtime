# 20260422 全量目标仓治理应用与自动提交实测

## Goal
- 将本项目当前已落地的跨仓治理能力应用到 5 个目标仓：`ClassroomToolkit`、`github-toolkit`、`self-runtime`、`skills-manager`、`vps-ssh-launcher`。
- 实测统一入口强制、受治理写入、里程碑自动提交，并修复执行中发现的根因错误。

## Scope
- 目标仓 profile 落地：`required_entrypoint_policy` + `auto_commit_policy`
- canonical 入口验证：`runtime-flow-preset.ps1 -FlowMode daily`
- write governance 闭环验证：`runtime-flow.ps1 -ExecuteWriteFlow`
- milestone auto-commit 验证：`full-check.ps1 -MilestoneTag milestone`
- 本仓根因修复：`scripts/governance/gate-runner-common.ps1`

## Changes
- 为 5 个目标仓写入统一入口策略：
  - `current_mode = targeted_enforced`
  - canonical 入口：`runtime-flow` / `runtime-flow-preset`
  - direct 只读例外：`status / inspect_* / verify-repo`
- 为 5 个目标仓写入 milestone-only 自动提交策略：
  - `enabled = true`
  - `on = ["milestone"]`
  - 中文提交模板：`自动提交：{repo_id} 里程碑 {milestone} 门禁通过 {timestamp}`
- 修复 `scripts/governance/gate-runner-common.ps1`：
  - `Resolve-FullGateCommands` / `Resolve-FastGateCommands` / auto-commit 触发分支不再假定反序列化对象总有 `.Count`
  - 统一使用 `@(...)` 包装，兼容单对象与数组输入

## Verification
### 1. canonical daily 全仓通过
- 命令：
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target <target> -FlowMode daily`
- 结果：5/5 通过，`entrypoint_policy_mode = targeted_enforced`，未引入回归。

### 2. direct 非 canonical 调用被拦截
- 命令：
  - `python scripts/session-bridge.py request-gate ... --entrypoint-id session-bridge.run_quick_gate`
- 结果：在目标仓 direct 调用会返回 `status = denied`，原因指向 `required canonical entrypoint policy blocks scope 'run_quick_gate'`。

### 3. canonical write governance 闭环通过
- 命令模板：
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow.ps1 -FlowMode daily -AttachmentRoot <repo> -AttachmentRuntimeStateRoot <state> -WriteTargetPath docs/governed-runtime-batch-validation.md -WriteTier medium -WriteToolName write_file -WriteContent "batch validation probe ..." -ExecuteWriteFlow -Json`
- 结果：5/5 通过，均完成：
  - `govern-attachment-write`
  - `decide-attachment-write`
  - `execute-attachment-write`
  - `session-bridge-write-status`
  - `session-bridge-inspect-evidence`
  - `session-bridge-inspect-handoff`
- 写入探针文件：`docs/governed-runtime-batch-validation.md`

### 4. milestone auto-commit 全仓通过
- 首次执行失败：
  - `full-check.ps1` 调用 `gate-runner-common.ps1` 时因 `.Count` 假设报错：`The property 'Count' cannot be found on this object.`
- 根因修复后重跑命令：
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File D:\CODE\governed-ai-coding-runtime\scripts\governance\full-check.ps1 -RepoProfilePath .governed-ai\repo-profile.json -MilestoneTag milestone`
- 结果：5/5 通过，并自动提交未提交变更。

## Auto Commit Evidence
- `ClassroomToolkit`: `cf24f711b6c11554fd66672f3ca844f9eee494cb`
- `github-toolkit`: `adcf1f6865890d91c8cf7c8132e35e3028420101`
- `self-runtime`: `04f8c3a594d9aff69590b5b29c0bde84b53c6597`
- `skills-manager`: `99e00f5ff566f0f366b93979a47b847895b607d1`
- `vps-ssh-launcher`: `8780aea8b5050bba2e7e03f3160ff3c7e05568af`

## KPI Snapshot
- 已刷新：
  - `docs/change-evidence/target-repo-runs/kpi-latest.json`
  - `docs/change-evidence/target-repo-runs/kpi-rolling.json`
- 说明：KPI 快照基于 `docs/change-evidence/target-repo-runs` 中已有 measured window 生成，不会自动吸收本轮临时执行的 runtime-flow / full-check 命令结果；本轮实效应以本文件中的命令结果和目标仓提交哈希为准。

## Notes
- `skills-manager` 在最终核查时存在另一个 agent 正在进行的业务代码改动，已获用户明确许可继续。本次收尾未触碰这些业务文件，仅完成跨仓治理相关验证与证据留痕。

## Rollback
- 本仓代码回滚：
  - `git checkout -- scripts/governance/gate-runner-common.ps1`
- 本仓证据回滚：
  - `git checkout -- docs/change-evidence/20260422-all-target-repos-governance-application-and-auto-commit.md docs/change-evidence/target-repo-runs/kpi-latest.json docs/change-evidence/target-repo-runs/kpi-rolling.json`
- 目标仓配置回滚：
  - 在各目标仓回退 `.governed-ai/repo-profile.json` 到自动提交前的提交
- 目标仓自动提交回滚：
  - 分别对 5 个目标仓按提交哈希执行普通 git revert 流程，不使用 destructive reset
