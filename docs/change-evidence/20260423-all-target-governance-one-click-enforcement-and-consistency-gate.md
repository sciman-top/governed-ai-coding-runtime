# 2026-04-23 全目标仓一键治理下发与一致性硬门禁

## Goal
- 强化“全目标仓一键应用”能力，让治理特性（含里程碑自动提交）可以一条命令批量下发。
- 增加全目标仓一致性硬门禁，未下发基线治理特性时 fail-closed 阻断。

## Scope
- `scripts/runtime-flow-preset.ps1`
- `scripts/runtime-flow.ps1`
- `scripts/verify-repo.ps1`
- `scripts/apply-target-repo-governance.py`
- `scripts/verify-target-repo-governance-consistency.py`
- `docs/targets/target-repo-governance-baseline.json`
- `docs/quickstart/use-with-existing-repo.md`
- `docs/quickstart/use-with-existing-repo.zh-CN.md`
- `tests/runtime/test_runtime_flow_preset.py`
- `tests/runtime/test_target_repo_governance_consistency.py`
- `tests/runtime/test_dependency_baseline.py`

## Changes
1. 新增全目标仓治理基线文件
- 新增 `docs/targets/target-repo-governance-baseline.json`，定义 active targets 的强制治理特性：
  - `required_entrypoint_policy`
  - 里程碑 `auto_commit_policy`（中文提交模板）

2. 新增目标仓治理下发脚本
- 新增 `scripts/apply-target-repo-governance.py`：
  - 将基线治理特性块写入目标仓 `.governed-ai/repo-profile.json`
  - 支持 `--check-only`
  - 输出结构化 JSON 结果

3. 新增全目标仓一致性校验脚本
- 新增 `scripts/verify-target-repo-governance-consistency.py`：
  - 读取 `docs/targets/target-repos-catalog.json`
  - 对全部 active target 执行 profile 基线对比
  - 输出 drift 明细并用退出码阻断

4. 强化一键入口
- `scripts/runtime-flow-preset.ps1` 新增：
  - `-AllTargets`：批量运行
  - `-ApplyGovernanceBaselineOnly`：仅下发治理基线（不执行 runtime-flow）
  - `-SkipGovernanceBaselineSync`：在 onboard 流程中显式跳过基线同步
  - `-CatalogPath` / `-GovernanceBaselinePath` / `-RuntimeFlowPath`：可覆盖路径
  - 批量 JSON 汇总输出（target 级状态与失败统计）

5. 修正 onboard 时序避免自阻断
- `scripts/runtime-flow.ps1` 新增 `-GovernanceBaselinePath`：
  - `FlowMode=onboard` 时，attach 后、runtime-check 前先执行治理基线同步
  - 防止目标仓在门禁前因 profile 暂态（未同步）被一致性门禁阻断

6. 接入合约硬门禁
- `scripts/verify-repo.ps1 -Check Contract` 新增 `target-repo-governance-consistency` 检查。
- 任一 active target 缺失基线治理特性时，合约门禁直接失败。

## Verification
1. 新增与回归测试
- `python -m unittest tests/runtime/test_runtime_flow_preset.py tests/runtime/test_target_repo_governance_consistency.py tests/runtime/test_dependency_baseline.py`
- 结果：`Ran 13 tests`, `OK`

2. 一致性校验脚本
- `python scripts/verify-target-repo-governance-consistency.py`
- 结果：`status = pass`, `drift_count = 0`

3. 一键全目标治理下发（仅治理特性）
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -ApplyGovernanceBaselineOnly -Json`
- 结果：`failure_count = 0`，5/5 `governance_sync_status = pass`

4. 合约门禁
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- 结果：`OK dependency-baseline` + `OK target-repo-governance-consistency`

5. 真实 onboard 批量回放（非纯治理下发）
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -FlowMode onboard -Mode quick -Overwrite -Json`
- 结果：脚本按 target 输出聚合结果；在本机实测中仍可能受目标仓自身 gate 失败影响（例如目标仓业务测试/构建异常），但治理基线同步链路与阻断语义按设计生效。

## Risks
- `-FlowMode onboard` 批量执行仍依赖各目标仓自身门禁稳定性；这类业务门禁失败不代表治理下发机制失效。
- 若操作者只想强制下发治理特性，应优先使用 `-ApplyGovernanceBaselineOnly`，避免被目标仓业务门禁噪声影响。

## Rollback
- 回退脚本与测试改动：
  - `git checkout -- scripts/runtime-flow-preset.ps1 scripts/runtime-flow.ps1 scripts/verify-repo.ps1`
  - `git checkout -- scripts/apply-target-repo-governance.py scripts/verify-target-repo-governance-consistency.py`
  - `git checkout -- tests/runtime/test_runtime_flow_preset.py tests/runtime/test_target_repo_governance_consistency.py tests/runtime/test_dependency_baseline.py`
- 回退文档与基线：
  - `git checkout -- docs/targets/target-repo-governance-baseline.json`
  - `git checkout -- docs/quickstart/use-with-existing-repo.md docs/quickstart/use-with-existing-repo.zh-CN.md`
  - `git checkout -- docs/change-evidence/20260423-all-target-governance-one-click-enforcement-and-consistency-gate.md`
