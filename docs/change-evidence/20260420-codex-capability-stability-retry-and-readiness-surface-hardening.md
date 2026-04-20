# 20260420 Codex Capability Stability Retry And Readiness Surface Hardening

## Purpose
- 解决“机制已实现、环境未达标”导致的重复降级问题，减少 `manual_handoff` 与 `live_attach_available=false` 的误触发与粘滞。
- 把 `native_attach / structured_events / structured_evidence_export / resume_id` 的可用性状态前置到 status/doctor，可在执行前稳定观察与诊断。

## Clarification Trace
- `issue_id`: `codex-capability-stability-retry-and-readiness-hardening`
- `attempt_count`: `1`
- `clarification_mode`: `direct_fix`
- `clarification_scenario`: `n/a`
- `clarification_questions`: `[]`
- `clarification_answers`: `[]`

## Basis
- 核心代码：
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/codex_adapter.py`
  - `scripts/run-governed-task.py`
  - `scripts/doctor-runtime.ps1`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_attachment.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/__init__.py`
- 测试：
  - `tests/runtime/test_codex_adapter.py`
  - `tests/runtime/test_run_governed_task_cli.py`
- 文档：
  - `docs/product/codex-direct-adapter.md`
  - `docs/product/codex-direct-adapter.zh-CN.md`

## What Changed
1. Codex probe 增加稳定性重探测机制
   - `probe_codex_surface` 新增：
     - `retry_on_degraded`（默认 `true`）
     - `max_probe_attempts`（默认 `2`）
   - 降级姿态会自动重探测并择优结果，减少瞬态故障导致的长期误降级。
   - `CodexSurfaceProbe` 新增字段：
     - `probe_attempts`
     - `stability_state`（`single_pass` / `stabilized` / `degraded_after_retry`）

2. 新增能力就绪摘要（readiness）
   - 新增 `CodexCapabilityReadiness` 与：
     - `summarize_codex_capability_readiness(...)`
     - `codex_capability_readiness_to_dict(...)`
   - 状态分级：`ready` / `degraded` / `blocked`。

3. status / doctor 前置可观测能力状态
   - `python scripts/run-governed-task.py status --json` 新增 `codex_capability` 字段。
   - `doctor-runtime.ps1` 新增能力输出：
     - ready 时 `OK codex-capability-ready`
     - degraded/blocked 时输出 `WARN` + `HINT`。

4. 附加仓默认偏好下沉到 API 层
   - `attach_target_repo(...)` 默认 `adapter_preference` 从 `manual_handoff` 改为 `native_attach`。
   - 避免调用方遗漏参数时回落到旧默认值。

## Commands
1. `python -m unittest tests.runtime.test_codex_adapter -v`
   - `exit_code`: `0`
   - `key_output`: `Ran 20 tests`; `OK`
2. `python -m unittest tests.runtime.test_run_governed_task_cli -v`
   - `exit_code`: `0`
   - `key_output`: `Ran 6 tests`; `OK`
3. `python -m unittest tests.runtime.test_repo_attachment -v`
   - `exit_code`: `0`
   - `key_output`: `Ran 16 tests`; `OK`
4. `python -m unittest tests.runtime.test_runtime_status -v`
   - `exit_code`: `0`
   - `key_output`: `Ran 7 tests`; `OK`
5. `python -m unittest tests.runtime.test_runtime_doctor -v`
   - `exit_code`: `0`
   - `key_output`: `Ran 6 tests`; `OK`
6. `python -m unittest tests.runtime.test_trial_entrypoint -v`
   - `exit_code`: `0`
   - `key_output`: `Ran 4 tests`; `OK`
7. `python scripts/run-governed-task.py status --json`
   - `exit_code`: `0`
   - `key_output`: `codex_capability.status=ready`; `adapter_tier=native_attach`; `stability_state=single_pass`
8. `python scripts/run-codex-adapter-trial.py --repo-id classroomtoolkit --task-id task-stability-check-20260420 --binding-id binding-classroomtoolkit --probe-live`
   - `exit_code`: `0`
   - `key_output`: `live_probe.probe_attempts=1`; `live_probe.stability_state=single_pass`; `adapter_tier=native_attach`
9. 三目标仓日常流复验：
   - `pwsh -File scripts/runtime-flow-preset.ps1 -Target classroomtoolkit|self-runtime|skills-manager -FlowMode daily -Mode quick -PolicyStatus allow -Json`
   - `exit_code`: `0`
   - `key_output`: 3/3 `overall=pass`; 3/3 `adapter_tier=native_attach`; 3/3 `flow_kind=live_attach`; 3/3 `codex_capability.status=ready`
10. 门禁：
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
   - `exit_code`: `0`
   - `key_output`: `Ran 250 tests`; `OK codex-capability-ready`

## Findings Summary
- 通过“降级自动重探测 + 非粘滞降级缓存”机制，减少了同类环境瞬态问题引发的重复误降级。
- 通过 `status/doctor` 前置输出 `codex_capability`，可以在执行链路前就发现 `live_attach_available` 与四项关键能力状态，不再等到任务执行时才暴露。
- 通过 API 层默认值修正，减少调用方忘记传参导致的 `manual_handoff` 默认回退。

## Risks
- 自动重探测会增加少量探测命令开销（默认最多 2 轮）；但只在降级姿态触发，且收益是显著降低误降级与反复排障成本。

## Rollback
- 回滚文件：
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/codex_adapter.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/__init__.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_attachment.py`
  - `scripts/run-governed-task.py`
  - `scripts/doctor-runtime.ps1`
  - `tests/runtime/test_codex_adapter.py`
  - `tests/runtime/test_run_governed_task_cli.py`
  - `docs/product/codex-direct-adapter.md`
  - `docs/product/codex-direct-adapter.zh-CN.md`
  - `docs/change-evidence/20260420-codex-capability-stability-retry-and-readiness-surface-hardening.md`
- 回滚后门禁复测顺序：
  1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
