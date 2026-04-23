# 20260424 Target Repo Speed And Loop Guard Hardening

## Goal
- 在不降低默认质量门槛的前提下，提高目标仓批量执行可控性和可恢复性：支持按任务自动触发里程碑门禁策略（fast/full）、关键子进程超时、批量超时防卡死。

## Clarification Trace
- `issue_id=target-repo-speed-and-loop-guard-hardening`
- `attempt_count=1`
- `clarification_mode=direct_fix`
- `clarification_scenario=bugfix`
- `clarification_questions=[]`
- `clarification_answers=[]`

## Scope
- `scripts/runtime-flow-preset.ps1`
- `tests/runtime/test_runtime_flow_preset.py`
- `docs/change-evidence/20260424-target-repo-speed-and-loop-guard-hardening.md`
- `docs/change-evidence/README.md`

## Changes
1. 里程碑门禁分层（不破坏默认行为）
- 新增参数：
  - `-MilestoneGateMode` (`full|fast`，默认 `full`)
  - `-GovernanceFastCheckPath`（默认 `scripts/governance/fast-check.ps1`）
- `ApplyAllFeatures`/`ApplyFeatureBaselineAndMilestoneCommit` 路径按 `MilestoneGateMode` 选择 `full-check.ps1` 或 `fast-check.ps1`。
- JSON 输出新增 `milestone_gate_mode`（batch）和 `result.milestone_gate_mode`（per-target）。

2. 按任务自动触发门禁策略（减少人工介入）
- 新增参数：
  - `-AutoMilestoneGateMode`
  - `-TaskType`
  - `-ReleaseCandidate`
- 自动策略引擎在 `runtime-flow-preset` 内根据 `FlowMode/Mode/PolicyStatus/WriteTier/ExecuteWriteFlow/TaskType/ReleaseCandidate` 进行风险判定：
  - 低风险日常任务优先 `fast`
  - onboarding、发布候选、高风险写入等自动提升为 `full`
  - 无法明确归类时 fail-safe 回落 `full`
- JSON 输出新增：
  - `milestone_gate_mode_source`（`manual|auto`）
  - `milestone_gate_mode_reason`
  - `result.milestone_gate_mode_source`
  - `result.milestone_gate_mode_reason`
  - `auto_milestone_gate_mode`
  - `task_type`
  - `release_candidate`

3. 子进程超时控制（防“假卡死/无限等待”）
- `Invoke-CommandCapture` 增强为可选超时执行：
  - `TimeoutSeconds > 0` 时使用 `Start-Process + WaitForExit(timeout)`。
  - 超时强制结束并返回 `exit_code=124`，附带 `timed_out=true`。
- 新增参数：
  - `-RuntimeFlowTimeoutSeconds`
  - `-GovernanceSyncTimeoutSeconds`
  - `-MilestoneCommandTimeoutSeconds`
- 里程碑执行默认超时推导：
  - 若未显式提供 `MilestoneCommandTimeoutSeconds` 且 `MilestoneGateTimeoutSeconds>0`，则自动使用 `MilestoneGateTimeoutSeconds + 120`。
- JSON 输出新增：
  - `result.flow_timed_out`
  - `result.milestone_command_timeout_seconds`
  - `milestone_command_timeout_seconds`（batch）
  - `runtime_flow_timeout_seconds`
  - `governance_sync_timeout_seconds`

4. 批量超时守卫（防批任务长期悬挂）
- 新增 `-BatchTimeoutSeconds`（默认 `0` 关闭）。
- `AllTargets` 循环每轮起始检查累计耗时，达到阈值即中断后续 target，标记 `batch_timed_out=true`。
- 总体退出码加入批量超时条件：`batch_timed_out` 时 `exit_code=1`。
- JSON 输出新增：
  - `batch_timeout_seconds`
  - `batch_timed_out`
  - `batch_elapsed_seconds`

5. 回归测试增强
- `test_runtime_flow_preset.py`：
  - existing `apply_all_features` / `apply_feature_baseline_and_milestone_commit` 断言新增 `milestone_gate_mode`、source/reason、超时字段。
  - 新增 `fast` 里程碑门禁模式分支测试。
  - 新增自动策略分支测试（`daily_low_to_medium_risk -> fast`、`release_candidate_full -> full`）。
  - 新增 runtime-flow 超时守卫测试（期望 `flow_exit_code=124`、`flow_timed_out=true`）。
  - 新增 batch 超时守卫测试（期望 `batch_timed_out=true` 且提前终止）。

## Verification
1. 定向单测
- Command:
  - `python -m unittest tests/runtime/test_runtime_flow_preset.py`
  - `python -m unittest tests/runtime/test_governance_gate_runner.py`
- Result:
  - `test_runtime_flow_preset.py`: `Ran 12 tests ... OK`
  - `test_governance_gate_runner.py`: `Ran 2 tests ... OK`

2. Gate order（硬门禁）
- Build:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - key output: `OK python-bytecode`, `OK python-import`
- Test:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - key output: `Ran 361 tests ... OK (skipped=2)`, `Ran 5 tests ... OK`
- Contract/Invariant:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - key output: `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing`, `OK dependency-baseline`, `OK target-repo-governance-consistency`
- Hotspot:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  - key output: `OK gate-command-build`, `OK gate-command-test`, `OK gate-command-contract`, `OK gate-command-doctor`, `OK adapter-posture-visible`

## Risks
- `MilestoneGateMode=fast` 会以更轻量门禁替代 `full`，应优先用于日常高频迭代；发布前仍建议 `full`。
- 启用 `BatchTimeoutSeconds` 后，可能出现“部分 target 已执行、其余未执行”的中间态，需要结合 `failure_count` 与 `batch_timed_out` 判读。
- 自动策略虽然默认 fail-safe 回落 `full`，但 `TaskType` 误标仍可能影响速度收益，应在目标仓逐步固化任务分类口径。

## Rollback
1. 回滚本仓改动
- `git checkout -- scripts/runtime-flow-preset.ps1`
- `git checkout -- tests/runtime/test_runtime_flow_preset.py`
- `git checkout -- docs/change-evidence/20260424-target-repo-speed-and-loop-guard-hardening.md`
- `git checkout -- docs/change-evidence/README.md`
