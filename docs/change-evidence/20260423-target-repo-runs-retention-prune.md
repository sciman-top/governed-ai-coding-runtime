# 20260423 Target Repo Runs Retention Prune

## Goal
为 `docs/change-evidence/target-repo-runs` 提供可执行的自动清理能力，避免问题痕迹无限累积，同时保持审计可追溯与一键流兼容。

## Scope
- `scripts/prune-target-repo-runs.py`
- `scripts/runtime-flow-preset.ps1`
- `tests/runtime/test_prune_target_repo_runs.py`
- `tests/runtime/test_runtime_flow_preset.py`
- `docs/quickstart/use-with-existing-repo.md`
- `docs/quickstart/use-with-existing-repo.zh-CN.md`

## Changes
1. 新增 `scripts/prune-target-repo-runs.py`
   - 保留策略：`keep_days` + `keep_latest_per_target` 并集保留。
   - 仅清理 run evidence（匹配 `target-(onboard|daily)-<stamp>.json`）。
   - 默认保留 `summary-*.json` / `kpi-*.json` 这类衍生文件。
   - 支持 `--dry-run`，输出结构化 JSON 报告（总量、候删、已删、失败数、按 target 统计）。
2. `runtime-flow-preset.ps1` 增加可选清理参数
   - `-PruneTargetRepoRuns`
   - `-PruneRunsRoot`
   - `-PruneKeepDays`
   - `-PruneKeepLatestPerTarget`
   - `-PruneDryRun`
   - 当启用清理时，JSON 输出新增 `prune_target_repo_runs` 回执块。
   - 当启用清理且清理失败时，脚本整体退出码转为失败。
3. 测试覆盖
   - 新增 `test_prune_target_repo_runs.py`（dry-run 与实际删除场景）。
   - `test_runtime_flow_preset.py` 新增单目标下挂载 prune 的集成回归。
4. 使用文档
   - 在中英文 `use-with-existing-repo` quickstart 增加一键流 + 自动清理示例命令。

## Verification
1. `python -m unittest tests.runtime.test_prune_target_repo_runs tests.runtime.test_runtime_flow_preset`
   - result: `Ran 8 tests ... OK`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target self-runtime -FlowMode daily -Mode quick -SkipVerifyAttachment -PruneTargetRepoRuns -PruneDryRun -PruneKeepDays 30 -PruneKeepLatestPerTarget 30 -Json`
   - result: `overall_status=pass`
   - `prune_target_repo_runs.status=pass`
   - `prune_target_repo_runs.delete_candidates=0`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
   - result: `OK python-bytecode`, `OK python-import`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
   - result: `Ran 353 tests ... OK (skipped=2)`, service parity checks pass
5. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
   - result: `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing`, `OK dependency-baseline`, `OK target-repo-governance-consistency`
6. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
   - result: doctor checks pass（含 gate command 可见性、capability readiness）

## Risks
- 自动清理默认关闭；只有显式传 `-PruneTargetRepoRuns` 才执行，避免误删历史证据。
- `keep_days` 与 `keep_latest_per_target` 为保留并集；配置过小会减少历史可追溯窗口，建议先 `-PruneDryRun` 预演。

## Rollback
- 代码回滚：
  - `git checkout -- scripts/prune-target-repo-runs.py scripts/runtime-flow-preset.ps1 tests/runtime/test_prune_target_repo_runs.py tests/runtime/test_runtime_flow_preset.py`
- 文档回滚：
  - `git checkout -- docs/quickstart/use-with-existing-repo.md docs/quickstart/use-with-existing-repo.zh-CN.md docs/change-evidence/20260423-target-repo-runs-retention-prune.md`
