# 20260420 Native Attach Default Onboarding And Multi-Target Application

## Purpose
- 将接入默认偏好从 `manual_handoff/process_bridge` 推进到 `native_attach`，并保留运行时自动回退。
- 把当前 runtime 能力重新应用到 3 个目标仓（`classroomtoolkit` / `self-runtime` / `skills-manager`），验证不仅 posture 正常，而且写流有真实落地效果。

## Clarification Trace
- `issue_id`: `native-attach-default-onboarding-and-multi-target-application`
- `attempt_count`: `1`
- `clarification_mode`: `direct_fix`
- `clarification_scenario`: `n/a`
- `clarification_questions`: `[]`
- `clarification_answers`: `[]`

## Basis
- 脚本与默认值更新：
  - `scripts/attach-target-repo.py`
  - `scripts/runtime-flow.ps1`
  - `scripts/runtime-flow-preset.ps1`
- 操作文档同步（中英）：
  - `docs/product/target-repo-attachment-flow.md`
  - `docs/product/target-repo-attachment-flow.zh-CN.md`
  - `docs/quickstart/use-with-existing-repo.md`
  - `docs/quickstart/use-with-existing-repo.zh-CN.md`

## Commands
1. `python -m unittest tests.runtime.test_repo_attachment -v`
   - `exit_code`: `0`
   - `key_output`: `Ran 16 tests`; `OK`
2. `python -m unittest tests.runtime.test_attached_repo_e2e -v`
   - `exit_code`: `0`
   - `key_output`: `Ran 2 tests`; `OK`
3. `python -m unittest tests.runtime.test_run_governed_task_cli -v`
   - `exit_code`: `0`
   - `key_output`: `Ran 6 tests`; `OK`
4. `pwsh -File scripts/runtime-flow-preset.ps1 -Target classroomtoolkit -FlowMode onboard -Overwrite -Json`
   - `exit_code`: `0`
   - `key_output`: `binding_pref=native_attach`; `adapter_tier=native_attach`; `live_attach=true`
5. `pwsh -File scripts/runtime-flow-preset.ps1 -Target self-runtime -FlowMode onboard -Overwrite -Json`
   - `exit_code`: `0`
   - `key_output`: `overall=pass`; `binding_pref=native_attach`; `adapter_tier=native_attach`
6. `pwsh -File scripts/runtime-flow-preset.ps1 -Target skills-manager -FlowMode onboard -Overwrite -Json`
   - `exit_code`: `0`
   - `key_output`: `overall=pass`; `binding_pref=native_attach`; `adapter_tier=native_attach`
7. 三目标仓日常流复验（daily quick，必要时自动重试）
   - `exit_code`: `0`
   - `key_output`: 3/3 `overall=pass`; 3/3 `verify_test=pass`; 3/3 `verify_contract=pass`; 3/3 `flow_kind=live_attach`
8. 三目标仓真实写流（`-ExecuteWriteFlow`）
   - `exit_code`: `0`
   - `key_output`: 3/3 `execution_status=executed`; 3/3 `adapter_id=codex-cli`; 3/3 `adapter_event_ref` 非空；3/3 目标文件存在
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
- 新增/重绑目标仓时，默认 adapter preference 已切到 `native_attach`，不再默认走 `manual_handoff` 或固定 `process_bridge`。
- 三目标仓当前都已落到：
  - `binding_pref=native_attach`
  - `adapter_tier=native_attach`
  - `flow_kind=live_attach`
  - `live_attach_available=true`
  - `unsupported_capabilities=[]`
- 三目标仓写流均已产生真实效果（文件落盘），并且都包含结构化 adapter evidence（`adapter_event_ref`）。

## Evidence Samples
- `D:\OneDrive\CODE\ClassroomToolkit\docs\runtime-auto-write-ctk-20260420200852.txt`
- `D:\OneDrive\CODE\governed-ai-coding-runtime\docs\runtime-auto-write-self-20260420200936.txt`
- `D:\OneDrive\CODE\skills-manager\docs\runtime-auto-write-sm-20260420201112.txt`

## Risks
- `classroomtoolkit` 的 dotnet gate 在个别时刻存在瞬态不稳定（示例：首次编译偶发 `GeneratedMSBuildEditorConfig.editorconfig` 缺失）；本次通过重跑可恢复通过，属于目标仓编译环境抖动，不是 runtime adapter 回退问题。

## Rollback
- 回滚文件：
  - `scripts/attach-target-repo.py`
  - `scripts/runtime-flow.ps1`
  - `scripts/runtime-flow-preset.ps1`
  - `docs/product/target-repo-attachment-flow.md`
  - `docs/product/target-repo-attachment-flow.zh-CN.md`
  - `docs/quickstart/use-with-existing-repo.md`
  - `docs/quickstart/use-with-existing-repo.zh-CN.md`
  - `docs/change-evidence/20260420-native-attach-default-onboarding-and-multi-target-application.md`
- 回滚后门禁复测顺序：
  1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
