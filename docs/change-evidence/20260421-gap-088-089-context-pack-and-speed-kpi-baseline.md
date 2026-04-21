# 2026-04-21 GAP-088/089 Context Pack + Speed KPI Baseline

## Goal
- GAP-088: 在 attachment 阶段生成可复用 context pack，并在 status/operator query 中可读。
- GAP-089: 增加 `target-repo-runs` 的 speed KPI 基线导出（latest / rolling）。

## Changes
- attachment context pack:
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_attachment.py`
    - 新增 context pack 生成与读取：
      - `compile_attachment_context_pack(...)`
      - `inspect_attachment_context_pack(...)`
    - `attach_target_repo(...)` 输出新增 `context_pack_summary`
    - `inspect_attachment_posture(...)` 输出新增 `context_pack_summary`（含 `is_stale` / `refresh_command`）
  - `scripts/attach-target-repo.py`
    - CLI JSON 输出新增 `context_pack_summary`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/runtime_status.py`
    - attachment status 新增 `context_pack_summary`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_queries.py`
    - posture summary 新增 `context_pack_summary`
- speed KPI baseline:
  - 新增模块 `packages/contracts/src/governed_ai_coding_runtime_contracts/target_repo_speed_kpi.py`
    - `export_target_repo_speed_kpi(...)`
    - 支持 `window_kind=latest|rolling`、`window_size`
    - 指标：
      - `onboarding_latency_seconds`
      - `first_pass_latency_seconds`
      - `deny_to_success_retries`
      - `fallback_rate`
      - `medium_risk_loop_success_ratio`
  - 新增导出脚本 `scripts/export-target-repo-speed-kpi.py`
  - 新增 schema/spec/example：
    - `schemas/jsonschema/target-repo-speed-kpi.schema.json`
    - `docs/specs/target-repo-speed-kpi-spec.md`
    - `schemas/examples/target-repo-speed-kpi/latest.example.json`
    - `schemas/catalog/schema-catalog.yaml` 增补 catalog 条目
  - 导出快照：
    - `docs/change-evidence/target-repo-runs/kpi-latest.json`
    - `docs/change-evidence/target-repo-runs/kpi-rolling.json`

## Verification
- 定向测试：
  - `python -m unittest tests.runtime.test_repo_attachment tests.runtime.test_runtime_status tests.runtime.test_operator_queries tests.runtime.test_target_repo_speed_kpi -v`
- KPI 导出：
  - `python scripts/export-target-repo-speed-kpi.py --runs-root docs/change-evidence/target-repo-runs --window-kind latest --window-size 10`
  - `python scripts/export-target-repo-speed-kpi.py --runs-root docs/change-evidence/target-repo-runs --window-kind rolling --window-size 5`
- 门禁顺序：
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

## Risks
- latency 目前基于 evidence 文件时间窗口近似，不是 adapter 内部高精度时钟。
- medium-risk ratio 在样本不足时可能为 `null`，需要更多 daily 样本稳定趋势。

## Rollback
- 代码回滚：`git checkout -- packages/contracts/src/governed_ai_coding_runtime_contracts/repo_attachment.py packages/contracts/src/governed_ai_coding_runtime_contracts/runtime_status.py packages/contracts/src/governed_ai_coding_runtime_contracts/operator_queries.py packages/contracts/src/governed_ai_coding_runtime_contracts/target_repo_speed_kpi.py scripts/attach-target-repo.py scripts/export-target-repo-speed-kpi.py tests/runtime/test_repo_attachment.py tests/runtime/test_runtime_status.py tests/runtime/test_operator_queries.py tests/runtime/test_target_repo_speed_kpi.py`
- 契约回滚：`git checkout -- schemas/jsonschema/target-repo-speed-kpi.schema.json schemas/examples/target-repo-speed-kpi/latest.example.json docs/specs/target-repo-speed-kpi-spec.md schemas/catalog/schema-catalog.yaml`
- 证据回滚：`git checkout -- docs/change-evidence/target-repo-runs/kpi-latest.json docs/change-evidence/target-repo-runs/kpi-rolling.json docs/change-evidence/20260421-gap-088-089-context-pack-and-speed-kpi-baseline.md`
