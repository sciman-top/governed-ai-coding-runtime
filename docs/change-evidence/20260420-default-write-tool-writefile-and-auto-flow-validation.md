# 20260420 Default Write Tool To write_file And Auto-Flow Validation

## Purpose
- 修复一键 runtime flow 默认写流路径在 `shell` 下易被 deny/执行器不兼容的问题。
- 将默认写工具切换到 attached write governance 原生路径（`write_file`），确保无需手工指定也能产出真实写入效果。

## Clarification Trace
- `issue_id`: `default-write-tool-writefile`
- `attempt_count`: `1`
- `clarification_mode`: `direct_fix`
- `clarification_scenario`: `n/a`
- `clarification_questions`: `[]`
- `clarification_answers`: `[]`

## Basis
- 变更文件：
  - `scripts/runtime-check.ps1`
  - `scripts/runtime-flow.ps1`
  - `scripts/runtime-flow-preset.ps1`
  - `scripts/runtime-flow-classroomtoolkit.ps1`
  - `tests/runtime/test_attached_repo_e2e.py`

## Commands
1. `python -m unittest tests.runtime.test_attached_repo_e2e -v`
   - `exit_code`: `0`
   - `key_output`: `Ran 2 tests`; `OK`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target classroomtoolkit ... -ExecuteWriteFlow -Json`
   - `exit_code`: `0`
   - `key_output`: `overall_status=pass`; `write_governance.governance_status=allowed`; `write_execute.execution_status=executed`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target self-runtime ... -ExecuteWriteFlow -Json`
   - `exit_code`: `0`
   - `key_output`: `overall_status=pass`; `write_governance.governance_status=allowed`; `write_execute.execution_status=executed`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target skills-manager ... -ExecuteWriteFlow -Json`
   - `exit_code`: `0`
   - `key_output`: `overall_status=pass`; `write_governance.governance_status=allowed`; `write_execute.execution_status=executed`
5. 文件落地核验（3 仓）：
   - `D:\OneDrive\CODE\ClassroomToolkit\docs\runtime-auto-write-ctk-20260420191516.txt`
   - `D:\OneDrive\CODE\governed-ai-coding-runtime\docs\runtime-auto-write-self-20260420191516.txt`
   - `D:\OneDrive\CODE\skills-manager\docs\runtime-auto-write-sm-20260420191516.txt`
   - `key_output`: `exists=true` 且内容与写入 payload 一致
6. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
   - `exit_code`: `0`
   - `key_output`: `OK python-bytecode`; `OK python-import`
7. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
   - `exit_code`: `0`
   - `key_output`: `Ran 246 tests`; `OK`
8. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
   - `exit_code`: `0`
   - `key_output`: `OK schema-json-parse`; `OK schema-example-validation`; `OK schema-catalog-pairing`
9. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
   - `exit_code`: `0`
   - `key_output`: `OK runtime-status-surface`; `OK adapter-posture-visible`

## Findings Summary
- 默认写工具切换后，`runtime-check` / `runtime-flow` / `runtime-flow-preset` 在未显式传 `-WriteToolName` 时可直接走 attached write path。
- 三个目标仓默认写流均实写成功，且保留 handoff/replay/artifact 引用。

## Risks
- `native_attach` 仍依赖上游 Codex 是否暴露可用的 live attach handshake 命令；当前环境仍降级为 `process_bridge`。

## Rollback
- 回滚文件：
  - `scripts/runtime-check.ps1`
  - `scripts/runtime-flow.ps1`
  - `scripts/runtime-flow-preset.ps1`
  - `scripts/runtime-flow-classroomtoolkit.ps1`
  - `tests/runtime/test_attached_repo_e2e.py`
  - `docs/change-evidence/20260420-default-write-tool-writefile-and-auto-flow-validation.md`
- 回滚后重跑门禁：
  1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
