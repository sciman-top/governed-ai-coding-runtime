# 20260420 Trial Entrypoint Native-Attach Projection And Multi-Target Recheck

## Purpose
- 清除 `trial_entrypoint` 中静态 `manual_handoff` 旧姿态声明。
- 将只读试运行入口切到“默认 `native_attach` 优先 + 可选 live probe”。
- 复验三目标仓日常流是否仍保持 `native_attach/live_attach` 可用。

## Clarification Trace
- `issue_id`: `trial-entrypoint-native-attach-projection`
- `attempt_count`: `1`
- `clarification_mode`: `direct_fix`
- `clarification_scenario`: `n/a`
- `clarification_questions`: `[]`
- `clarification_answers`: `[]`

## Basis
- 代码：
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/trial_entrypoint.py`
  - `scripts/run-readonly-trial.py`
  - `tests/runtime/test_trial_entrypoint.py`
- 文档：
  - `docs/product/first-readonly-trial.md`
  - `docs/product/first-readonly-trial.zh-CN.md`
  - `docs/architecture/local-baseline-to-hybrid-final-state-migration-matrix.md`

## Commands
1. `python -m unittest tests.runtime.test_trial_entrypoint -v`
   - `exit_code`: `0`
   - `key_output`: `Ran 4 tests`; `OK`
2. `python -m unittest tests.runtime.test_codex_adapter -v`
   - `exit_code`: `0`
   - `key_output`: `Ran 18 tests`; `OK`
3. `python -m unittest tests.runtime.test_attached_repo_e2e -v`
   - `exit_code`: `0`
   - `key_output`: `Ran 2 tests`; `OK`
4. `python -m unittest tests.runtime.test_run_governed_task_cli -v`
   - `exit_code`: `0`
   - `key_output`: `Ran 6 tests`; `OK`
5. `python scripts/run-readonly-trial.py ...`
   - `exit_code`: `0`
   - `key_output`: `adapter_tier=native_attach`; `invocation_mode=live_attach`; `probe_source=declared_defaults`; `unsupported_capability_behavior=none`
6. `python scripts/run-readonly-trial.py ... --probe-live`
   - `exit_code`: `0`
   - `key_output`: `adapter_tier=native_attach`; `invocation_mode=live_attach`; `probe_source=live_probe`
7. 三目标仓日常流复验：
   - `pwsh -File scripts/runtime-flow-preset.ps1 -Target classroomtoolkit|self-runtime|skills-manager -FlowMode daily -Mode quick -PolicyStatus allow -Json`
   - `exit_code`: `0`
   - `key_output`: 3/3 `overall=pass`; 3/3 `binding_pref=native_attach`; 3/3 `adapter_tier=native_attach`; 3/3 `flow_kind=live_attach`; 3/3 `live_attach_available=true`; 3/3 `verify_test=pass`; 3/3 `verify_contract=pass`
8. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
   - `exit_code`: `0`
   - `key_output`: `OK python-bytecode`; `OK python-import`
9. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
   - `exit_code`: `0`
   - `key_output`: `Ran 248 tests`; `OK`
10. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
    - `exit_code`: `0`
    - `key_output`: `OK schema-json-parse`; `OK schema-example-validation`; `OK schema-catalog-pairing`
11. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
    - `exit_code`: `0`
    - `key_output`: `OK runtime-status-surface`; `OK adapter-posture-visible`

## Findings Summary
- `run-readonly-trial` 不再把 Codex 声明硬编码为 `manual_handoff`。
- 默认声明姿态为：`adapter_tier=native_attach`、`invocation_mode=live_attach`、`unsupported_capability_behavior=none`。
- `--probe-live` 已可将只读试运行入口切换为真实命令面 posture 投影。
- 三目标仓当前仍保持“已应用”状态：绑定偏好与运行姿态都为 `native_attach/live_attach`，且日常门禁流通过。

## Risks
- `--probe-live` 结果受本机 Codex CLI 版本与命令面影响，未来若上游命令面变化，可能引发 posture 变化；已保留默认 `declared_defaults` 作为稳定入口。

## Rollback
- 回滚文件：
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/trial_entrypoint.py`
  - `scripts/run-readonly-trial.py`
  - `tests/runtime/test_trial_entrypoint.py`
  - `docs/product/first-readonly-trial.md`
  - `docs/product/first-readonly-trial.zh-CN.md`
  - `docs/architecture/local-baseline-to-hybrid-final-state-migration-matrix.md`
  - `docs/change-evidence/20260420-trial-entrypoint-native-attach-projection-and-multi-target-recheck.md`
- 回滚后门禁：
  1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
