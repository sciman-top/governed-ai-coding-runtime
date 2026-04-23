# 2026-04-23 全目标仓“特性基线同步 + 里程碑自动提交”一键入口

## Goal
- 把“新增功能统一一键下发到各目标仓”落地为可执行入口。
- 在同一条一键命令里连续执行：
  - 特性基线同步（target repo profile overrides）
  - 里程碑门禁并触发 auto-commit（中文备注模板）

## Changes
1. 统一入口增强
- 更新 `scripts/runtime-flow-preset.ps1`：
  - 新增 `-ApplyAllFeatures`（统一执行“旧流程 + 新特性”）。
  - 新增 `-ApplyFeatureBaselineOnly`（兼容旧参数 `-ApplyGovernanceBaselineOnly`）。
  - 新增 `-ApplyFeatureBaselineAndMilestoneCommit`。
  - 新增 `-MilestoneTag`（默认 `milestone`）。
  - 新增 `-GovernanceFullCheckPath`（默认 `scripts/governance/full-check.ps1`）。

2. 连续任务能力
- 新增批量目标仓分支：先同步基线，再执行 `full-check` 里程碑门禁。
- 新增“全功能一键”分支：每个目标仓串行执行
  - runtime-flow（保留旧流程能力）
  - 特性基线同步
  - full-check 里程碑门禁 + 自动提交
- 聚合 JSON 输出新增里程碑提交结果字段：
  - `milestone_commit_status`
  - `auto_commit_status`
  - `auto_commit_reason`
  - `auto_commit_commit_hash`
  - `auto_commit_trigger`

3. 文档更新（中英双语）
- `docs/quickstart/use-with-existing-repo.md`
- `docs/quickstart/use-with-existing-repo.zh-CN.md`
- 新增“一键特性基线同步 + 里程碑自动提交”命令示例。

4. 回归测试
- 更新 `tests/runtime/test_runtime_flow_preset.py`：
  - 新增 `test_runtime_flow_preset_all_targets_apply_feature_baseline_and_milestone_commit`。
  - 新增 `test_runtime_flow_preset_all_targets_apply_all_features`。

## Commands
- `python -m unittest tests/runtime/test_runtime_flow_preset.py`

## Verification
- 新增测试覆盖通过后，证明以下行为可用：
  - `-AllTargets -ApplyFeatureBaselineAndMilestoneCommit -Json`
  - `-AllTargets -ApplyAllFeatures -Json`
  - 每个 target 均输出基线同步状态与里程碑自动提交状态。
  - 基线下发后，目标仓 profile 与 baseline 对齐。

## Rollback
- `git checkout -- scripts/runtime-flow-preset.ps1`
- `git checkout -- tests/runtime/test_runtime_flow_preset.py`
- `git checkout -- docs/quickstart/use-with-existing-repo.md docs/quickstart/use-with-existing-repo.zh-CN.md`
- `git checkout -- docs/change-evidence/20260423-feature-baseline-and-milestone-one-click.md`
