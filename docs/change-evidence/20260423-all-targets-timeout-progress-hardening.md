# 20260423 All-Targets Timeout And Progress Hardening

## Goal
- 修复 `runtime-flow-preset -AllTargets -ApplyAllFeatures` 执行耗时阶段“无反馈/疑似卡住”问题，并为 gate 执行补齐可配置超时保护。

## Clarification Trace
- `issue_id=all-targets-timeout-progress-hardening`
- `attempt_count=1`
- `clarification_mode=direct_fix`
- `clarification_scenario=bugfix`
- `clarification_questions=[]`
- `clarification_answers=[]`

## Scope
- `scripts/governance/gate-runner-common.ps1`
- `scripts/governance/fast-check.ps1`
- `scripts/governance/full-check.ps1`
- `scripts/runtime-flow-preset.ps1`
- `tests/runtime/test_governance_gate_runner.py`
- `tests/runtime/test_runtime_flow_preset.py`
- `docs/change-evidence/20260423-all-targets-timeout-progress-hardening.md`
- `docs/change-evidence/README.md`

## Changes
1. Gate 级超时保护（governance runner）
- 新增 `Resolve-GateTimeoutSeconds`，支持两种入口：
  - CLI 参数：`-GateTimeoutSeconds`
  - 环境变量：`GOVERNED_GATE_TIMEOUT_SECONDS`
- `Invoke-GateCommand` 新增超时执行分支：
  - 启用超时时以 `Start-Process` 执行 gate。
  - 超时后强制结束子进程并返回 `exit_code=124`。
  - 结果结构新增：`reason`、`timed_out`、`timeout_seconds`。
- gate 汇总新增 `gate_timeout_seconds`，文本汇总输出也显示超时配置和 timeout 标记。

2. fast/full 门禁入口参数透传
- `scripts/governance/fast-check.ps1` 与 `scripts/governance/full-check.ps1` 均新增参数：
  - `-GateTimeoutSeconds`
- 并透传给 `Invoke-RepoProfileGateRun`。

3. AllTargets 批量执行进度可视化
- `runtime-flow-preset.ps1` 新增 `Write-BatchProgressLine`，在 `-AllTargets` 且非 `-Json` 时输出实时阶段日志：
  - `target`（start/pass/fail，含 index 与 duration）
  - `runtime_flow`
  - `governance_sync`
  - `milestone_commit`
- `==> target` 输出增强为带序号：`(current/total)`。

4. 里程碑 full-check 默认超时
- `runtime-flow-preset.ps1` 新增参数 `-MilestoneGateTimeoutSeconds`（默认 `900`，允许 `0` 关闭）。
- `Invoke-TargetMilestoneAutoCommit` 调用 `full-check.ps1` 时透传 `-GateTimeoutSeconds`。
- JSON 批量结果新增 `milestone_gate_timeout_seconds` 字段。

5. 回归测试补齐
- 新增 `tests/runtime/test_governance_gate_runner.py`：
  - 覆盖 `-GateTimeoutSeconds` 参数触发 timeout。
  - 覆盖 `GOVERNED_GATE_TIMEOUT_SECONDS` 环境变量触发 timeout。
- 扩展 `tests/runtime/test_runtime_flow_preset.py`：
  - 校验 `milestone_gate_timeout_seconds` 字段。
  - 新增 `AllTargets + ApplyAllFeatures` 非 JSON 阶段进度日志断言。

## Verification
1. 新增/受影响单测
- Command:
  - `python -m unittest tests/runtime/test_runtime_flow_preset.py`
  - `python -m unittest tests/runtime/test_governance_gate_runner.py`
- Result:
  - `test_runtime_flow_preset.py`: `Ran 7 tests ... OK`
  - `test_governance_gate_runner.py`: `Ran 2 tests ... OK`

2. Gate order（硬门禁）
- Build:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - key output: `OK python-bytecode`, `OK python-import`
- Test:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - key output: `Ran 356 tests ... OK (skipped=2)`, `Ran 5 tests ... OK`
- Contract/Invariant:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - key output: `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing`, `OK dependency-baseline`, `OK target-repo-governance-consistency`
- Hotspot:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  - key output: `OK gate-command-build`, `OK gate-command-test`, `OK gate-command-contract`, `OK gate-command-doctor`, `OK adapter-posture-visible`

## Risks
- `-MilestoneGateTimeoutSeconds` 默认值 `900` 可能对超大仓、超慢 CI 命令偏紧；如有必要可显式增大或设为 `0` 关闭。
- 启用 timeout 的分支通过重定向文件汇总 stdout/stderr；在超时场景下不保证与实时交错输出完全一致。

## Rollback
1. 回滚本仓改动
- `git checkout -- scripts/governance/gate-runner-common.ps1`
- `git checkout -- scripts/governance/fast-check.ps1`
- `git checkout -- scripts/governance/full-check.ps1`
- `git checkout -- scripts/runtime-flow-preset.ps1`
- `git checkout -- tests/runtime/test_runtime_flow_preset.py`
- `git checkout -- docs/change-evidence/20260423-all-targets-timeout-progress-hardening.md`
- `git checkout -- docs/change-evidence/README.md`
- `git clean -f tests/runtime/test_governance_gate_runner.py`
