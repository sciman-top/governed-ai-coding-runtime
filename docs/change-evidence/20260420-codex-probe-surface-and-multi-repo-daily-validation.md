# 20260420 Codex Probe Surface And Multi-Repo Daily Validation

## Purpose
- 修复 Codex live probe 的能力误判：当前 Codex CLI 版本不暴露 `status` 子命令，旧逻辑会把能力缺口错误归因为非交互失败。
- 把结构化能力判定改为基于可执行命令面（`codex --help` + `codex exec --help`）并验证在多个目标仓的一键链路实效。

## Clarification Trace
- `issue_id`: `codex-surface-probe-status-missing`
- `attempt_count`: `1`
- `clarification_mode`: `direct_fix`
- `clarification_scenario`: `n/a`
- `clarification_questions`: `[]`
- `clarification_answers`: `[]`

## Basis
- 代码变更：
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/codex_adapter.py`
  - `tests/runtime/test_codex_adapter.py`
- 文档变更：
  - `docs/product/codex-direct-adapter.md`
  - `docs/product/codex-direct-adapter.zh-CN.md`

## Commands
1. `python -m unittest tests.runtime.test_codex_adapter -v`
   - `exit_code`: `0`
   - `key_output`: `Ran 17 tests`; `OK`
2. `python scripts/run-codex-adapter-trial.py --repo-id classroomtoolkit --task-id task-codex-live-probe --binding-id binding-classroomtoolkit --probe-live`
   - `exit_code`: `0`
   - `key_output`: `adapter_tier=process_bridge`; `unsupported_capabilities=[native_attach]`; `failure_stage=live_attach_probe_unsupported_status_command_missing`
3. `codex.cmd exec --json "Reply with exactly OK."`
   - `exit_code`: `0`
   - `key_output`: `thread.started`; `turn.completed`; `agent_message=OK`
4. `codex.cmd exec resume --last --json "Reply with exactly RESUMED_OK."`
   - `exit_code`: `0`
   - `key_output`: `thread.started`; `turn.completed`; `agent_message=RESUMED_OK`
5. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target classroomtoolkit -FlowMode daily -Mode quick -PolicyStatus allow ... -Json`
   - `exit_code`: `0`
   - `key_output`: `overall_status=pass`; `session_identity.adapter_tier=process_bridge`; `unsupported_capabilities=[native_attach]`
6. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target self-runtime -FlowMode daily -Mode quick -PolicyStatus allow ... -Json`
   - `exit_code`: `0`
   - `key_output`: `overall_status=pass`; `session_identity.adapter_tier=process_bridge`; `unsupported_capabilities=[native_attach]`
7. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target skills-manager -FlowMode daily -Mode quick -PolicyStatus allow ... -Json`
   - `exit_code`: `0`
   - `key_output`: `overall_status=pass`; `session_identity.adapter_tier=process_bridge`; `unsupported_capabilities=[native_attach]`
8. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
   - `exit_code`: `0`
   - `key_output`: `OK python-bytecode`; `OK python-import`
9. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
   - `exit_code`: `0`
   - `key_output`: `Ran 245 tests`; `OK`
10. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
    - `exit_code`: `0`
    - `key_output`: `OK schema-json-parse`; `OK schema-example-validation`; `OK schema-catalog-pairing`
11. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
    - `exit_code`: `0`
    - `key_output`: `OK runtime-status-surface`; `OK adapter-posture-visible`

## Findings Summary
- 当前环境下：
  - `native_attach`: 仍不可用（原因是 Codex 版本未暴露 `status` 握手命令，不是 manual_handoff 级别故障）。
  - `structured_events`: 可用（`exec --help` 提供 `--json` JSONL 事件流）。
  - `structured_evidence_export`: 可用（`exec --help` 提供 `--output-last-message` 且可导出 JSONL 事件）。
  - `resume_id`: 可用（`resume` 命令面存在，`exec resume --last --json` 实测可执行）。
- 三个目标仓的一键 daily 链路均可运行并稳定产出 `process_bridge` posture 与证据。

## Risks
- 如果继续使用默认 `shell` 写入命令在某些目标仓执行写流，可能被策略拒绝或因 shell 解释器差异失败（例如 `Set-Content` 在非 PowerShell shell 上不可执行）。

## Rollback
- 回滚文件：
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/codex_adapter.py`
  - `tests/runtime/test_codex_adapter.py`
  - `docs/product/codex-direct-adapter.md`
  - `docs/product/codex-direct-adapter.zh-CN.md`
  - `docs/change-evidence/20260420-codex-probe-surface-and-multi-repo-daily-validation.md`
- 回滚后重跑门禁：
  1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
