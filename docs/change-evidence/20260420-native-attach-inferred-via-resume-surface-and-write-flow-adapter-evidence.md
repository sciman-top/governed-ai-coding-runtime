# 20260420 Native Attach Inferred Via Resume Surface And Write-Flow Adapter Evidence

## Purpose
- 在当前 Codex CLI 构建缺少 `status` 子命令的前提下，补齐 `native_attach` 能力识别，不再长期降级到 `process_bridge`。
- 将写流执行链路的 adapter 身份统一到 `codex-cli`，确保写流也产出结构化 adapter evidence（`adapter_event_ref`）。

## Clarification Trace
- `issue_id`: `native-attach-resume-surface-and-write-adapter-evidence`
- `attempt_count`: `1`
- `clarification_mode`: `direct_fix`
- `clarification_scenario`: `n/a`
- `clarification_questions`: `[]`
- `clarification_answers`: `[]`

## Basis
- 代码变更：
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/codex_adapter.py`
  - `scripts/run-governed-task.py`
  - `scripts/runtime-check.ps1`
- 测试变更：
  - `tests/runtime/test_codex_adapter.py`
  - `tests/runtime/test_attached_repo_e2e.py`
- 文档变更：
  - `docs/product/codex-direct-adapter.md`
  - `docs/product/codex-direct-adapter.zh-CN.md`

## Commands
1. `python -m unittest tests.runtime.test_codex_adapter -v`
   - `exit_code`: `0`
   - `key_output`: `Ran 18 tests`; `OK`
2. `python -m unittest tests.runtime.test_run_governed_task_cli -v`
   - `exit_code`: `0`
   - `key_output`: `Ran 6 tests`; `OK`
3. `python -m unittest tests.runtime.test_attached_repo_e2e -v`
   - `exit_code`: `0`
   - `key_output`: `Ran 2 tests`; `OK`
4. `python scripts/run-codex-adapter-trial.py --repo-id classroomtoolkit --task-id task-codex-live-probe-native --binding-id binding-classroomtoolkit --probe-live`
   - `exit_code`: `0`
   - `key_output`: `adapter_tier=native_attach`; `unsupported_capabilities=[]`; `failure_stage=null`
5. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target classroomtoolkit ... -Json`
   - `exit_code`: `0`
   - `key_output`: `overall=pass`; `request_gate.session_identity.adapter_tier=native_attach`; `unsupported_capabilities=[]`
6. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target self-runtime ... -Json`
   - `exit_code`: `0`
   - `key_output`: `overall=pass`; `request_gate.session_identity.adapter_tier=native_attach`; `unsupported_capabilities=[]`
7. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target skills-manager ... -Json`
   - `exit_code`: `0`
   - `key_output`: `overall=pass`; `request_gate.session_identity.adapter_tier=native_attach`; `unsupported_capabilities=[]`
8. 写流实效与结构化证据核验（3 仓）
   - `scripts/runtime-flow-preset.ps1 ... -ExecuteWriteFlow -Json`
   - `exit_code`: `0`
   - `key_output`: `write_execute.execution_status=executed`; `write_execute.adapter_id=codex-cli`; `write_execute.adapter_event_ref=artifacts/.../evidence/adapter-events.json`
9. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
   - `exit_code`: `0`
   - `key_output`: `OK python-bytecode`; `OK python-import`
10. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
    - `exit_code`: `0`
    - `key_output`: `Ran 247 tests`; `OK`
11. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
    - `exit_code`: `0`
    - `key_output`: `OK schema-json-parse`; `OK schema-example-validation`; `OK schema-catalog-pairing`
12. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
    - `exit_code`: `0`
    - `key_output`: `OK runtime-status-surface`; `OK adapter-posture-visible`

## Findings Summary
- `native_attach` 在当前环境已可判定为可用（依据：`resume` 命令面可用，且 `status` 缺失时走 resume surface 推断路径）。
- `structured_events`、`structured_evidence_export`、`resume_id` 已在目标仓日常流和写流中落地可用。
- 写流不再以 `cli-process-bridge` 身份执行，已统一为 `codex-cli`，并能产出 `adapter_event_ref`（结构化 evidence）。

## Risks
- 当前 `native_attach` 是基于命令面推断（`resume` 能力），不是 `status` 握手成功路径；若上游 CLI 调整 resume 能力或行为，需要同步 probe 规则与回归测试。

## Rollback
- 回滚文件：
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/codex_adapter.py`
  - `scripts/run-governed-task.py`
  - `scripts/runtime-check.ps1`
  - `tests/runtime/test_codex_adapter.py`
  - `tests/runtime/test_attached_repo_e2e.py`
  - `docs/product/codex-direct-adapter.md`
  - `docs/product/codex-direct-adapter.zh-CN.md`
  - `docs/change-evidence/20260420-native-attach-inferred-via-resume-surface-and-write-flow-adapter-evidence.md`
- 回滚后重跑门禁：
  1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
