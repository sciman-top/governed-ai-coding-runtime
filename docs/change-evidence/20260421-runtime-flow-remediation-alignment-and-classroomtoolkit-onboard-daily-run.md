# 20260421 Runtime Flow Remediation Alignment And ClassroomToolkit Onboard-Daily Run

## Goal
在不改变现有治理语义的前提下，修复 attachment remediation 命令漂移问题，并增强 preset 流程对不同 adapter tier 的可配置性；随后在真实目标仓 `..\ClassroomToolkit` 跑通 `onboard -> daily` 全链路。

## Basis
- 现状诊断发现 remediation 输出使用了旧参数：`attach --target-repo-root`，与当前 CLI (`--target-repo`) 不一致。
- 多宿主接入需要在 preset 入口快速切换 adapter preference，而不是固定 `native_attach`。

## Scope
- `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_attachment.py`
- `scripts/doctor-runtime.ps1`
- `scripts/runtime-flow-preset.ps1`
- `scripts/runtime-flow-classroomtoolkit.ps1`
- `tests/runtime/test_repo_attachment.py`
- `tests/runtime/test_runtime_doctor.py`

## Changes
1. 将 runtime posture remediation 命令从旧写法统一到现行写法：
   - from: `attach --target-repo-root ...`
   - to: `--target-repo ...`
2. 将 `doctor-runtime.ps1` 中 fail-closed remediation action 的 attach 命令统一为 `--target-repo` 参数。
3. 为 `runtime-flow-preset.ps1` 新增参数：
   - `-AdapterPreference {native_attach|process_bridge|manual_handoff}`
   - onboard 时透传给 `runtime-flow.ps1`，不再强制固定 `native_attach`。
4. 为 `runtime-flow-classroomtoolkit.ps1` 新增并透传 `-AdapterPreference`，保持 preset 与快捷脚本一致。
5. 补充回归测试断言，确保输出中不再出现 `--target-repo-root` 与 `attach --target-repo` 旧形态。

## Verification
### Targeted
- `python -m unittest tests.runtime.test_repo_attachment tests.runtime.test_runtime_doctor`
  - `Ran 24 tests`
  - `OK`

### Gate order (required)
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
   - evidence: `OK python-bytecode`, `OK python-import`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
   - evidence: `Ran 268 tests ... OK`, `Ran 5 tests ... OK`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
   - evidence: `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
   - evidence: `OK runtime-status-surface`, `OK codex-capability-ready`, `OK adapter-posture-visible`

### Extra safety
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`
  - evidence: `OK powershell-parse`, `OK issue-seeding-render`

## Real Target Repo Run (ClassroomToolkit)
### Onboard
- command:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-classroomtoolkit.ps1 -FlowMode onboard -Mode quick -PolicyStatus allow -Json`
- key evidence:
  - `overall_status: pass`
  - `onboard_attach.payload.operation: validated`
  - `binding_id: binding-classroomtoolkit`
  - `verify_attachment.results: { test: pass, contract: pass }`

### Daily
- command:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-classroomtoolkit.ps1 -FlowMode daily -Mode quick -PolicyStatus allow -Json`
- key evidence:
  - `overall_status: pass`
  - `summary.flow_kind: live_attach`
  - `summary.closure_state: live_closure_ready`
  - `verify_attachment.results: { test: pass, contract: pass }`

## Rollback
如需回退本次改动，执行：
1. 还原以下文件到变更前版本：
   - `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_attachment.py`
   - `scripts/doctor-runtime.ps1`
   - `scripts/runtime-flow-preset.ps1`
   - `scripts/runtime-flow-classroomtoolkit.ps1`
   - `tests/runtime/test_repo_attachment.py`
   - `tests/runtime/test_runtime_doctor.py`
   - `docs/change-evidence/20260421-runtime-flow-remediation-alignment-and-classroomtoolkit-onboard-daily-run.md`
2. 按门禁顺序复跑：`build -> runtime test -> contract -> doctor`。
