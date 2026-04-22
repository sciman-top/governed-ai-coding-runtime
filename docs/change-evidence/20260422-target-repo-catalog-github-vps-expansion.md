# 20260422 Target Repo Catalog Github/Vps Expansion

## Goal
将 `D:\CODE\github-toolkit` 和 `D:\CODE\vps-ssh-launcher` 正式纳入 active target-repo catalog，并验证 `runtime-flow-preset.ps1` 能基于 catalog 持久化登记结果直接执行这两个目标仓。

## Scope
- `docs/targets/target-repos-catalog.json`
- `docs/quickstart/use-with-existing-repo.md`
- `docs/quickstart/use-with-existing-repo.zh-CN.md`
- `D:\CODE\github-toolkit\.governed-ai\repo-profile.json`
- `D:\CODE\vps-ssh-launcher\.governed-ai\repo-profile.json`

## Changes
1. 扩展 catalog active target 集：
- 新增 `github-toolkit`
- 新增 `vps-ssh-launcher`

2. 将两个新增 Python 仓的 preset gate 命令从历史占位值提升为真实可执行命令：
- `github-toolkit`
  - build: `python -m py_compile gh_utils.py list-forks.py sync-forks.py test_toolkit.py`
  - test: `python -m unittest test_toolkit.py`
  - contract: `python -m unittest test_toolkit.py`
- `vps-ssh-launcher`
  - build: `python -m py_compile auto_install.py ssh_tool.py test_ssh_tool.py`
  - test: `python -m unittest test_ssh_tool.py`
  - contract: `python -m unittest test_ssh_tool.py`

3. 更新双语 quickstart：
- preset 目标列表示例从 3 个目标扩展为 5 个目标
- 明确 `docs/targets/target-repos-catalog.json` 是 active preset target facts 的持久化登记文件

4. 通过 preset `onboard -Overwrite` 将 catalog 中的新 gate 命令写回两个目标仓的 `.governed-ai/repo-profile.json`

## Verification
### Gate order
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- result: `OK python-bytecode`, `OK python-import`

2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- result: `302` runtime tests pass
- result: `5` service-parity tests pass

3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- result: `OK schema-json-parse`
- result: `OK schema-example-validation`
- result: `OK schema-catalog-pairing`

4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
- result: doctor pass, including `OK gate-command-build/test/contract/doctor`

### Catalog source of truth
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -ListTargets -Json`
- result:
  - `catalog_path = D:\CODE\governed-ai-coding-runtime\docs\targets\target-repos-catalog.json`
  - `targets = ["classroomtoolkit","github-toolkit","self-runtime","skills-manager","vps-ssh-launcher"]`

### Supporting repo facts
1. `python -m unittest D:\CODE\github-toolkit\test_toolkit.py`
- result: `Ran 36 tests`, `OK`

2. `python -m unittest D:\CODE\vps-ssh-launcher\test_ssh_tool.py`
- result: `Ran 16 tests`, `OK`

### Target-repo execution
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target github-toolkit -FlowMode onboard -Mode quick -Overwrite -Json -TaskId task-onboard-github-toolkit-20260422190531 -RunId run-onboard-github-toolkit-20260422190531 -CommandId cmd-onboard-github-toolkit-20260422190531`
- result: `overall_status = pass`
- result: `verify_test = pass`, `verify_contract = pass`
- result: `binding_state = healthy`

2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target github-toolkit -FlowMode daily -Mode quick -Json -TaskId task-daily-github-toolkit-20260422190537 -RunId run-daily-github-toolkit-20260422190537 -CommandId cmd-daily-github-toolkit-20260422190537`
- result: `overall_status = pass`
- result evidence:
  - `.runtime/attachments/github-toolkit/artifacts/task-daily-github-toolkit-20260422190537/run-daily-github-toolkit-20260422190537/verification-output/contract.txt`
  - `.runtime/attachments/github-toolkit/artifacts/task-daily-github-toolkit-20260422190537/run-daily-github-toolkit-20260422190537/verification-output/test.txt`
  - `.runtime/attachments/github-toolkit/doctor/latest-remediation.json`

3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target vps-ssh-launcher -FlowMode onboard -Mode quick -Overwrite -Json -TaskId task-onboard-vps-ssh-launcher-20260422190555 -RunId run-onboard-vps-ssh-launcher-20260422190555 -CommandId cmd-onboard-vps-ssh-launcher-20260422190555`
- result: `overall_status = pass`
- result: `verify_test = pass`, `verify_contract = pass`
- result: `binding_state = healthy`

4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target vps-ssh-launcher -FlowMode daily -Mode quick -Json -TaskId task-daily-vps-ssh-launcher-20260422190602 -RunId run-daily-vps-ssh-launcher-20260422190602 -CommandId cmd-daily-vps-ssh-launcher-20260422190602`
- result: `overall_status = pass`
- result evidence:
  - `.runtime/attachments/vps-ssh-launcher/artifacts/task-daily-vps-ssh-launcher-20260422190602/run-daily-vps-ssh-launcher-20260422190602/verification-output/contract.txt`
  - `.runtime/attachments/vps-ssh-launcher/artifacts/task-daily-vps-ssh-launcher-20260422190602/run-daily-vps-ssh-launcher-20260422190602/verification-output/test.txt`
  - `.runtime/attachments/vps-ssh-launcher/doctor/latest-remediation.json`

## Risks
- `docs/targets/target-repos-catalog.json` 是 active preset target 的持久化登记源，但不是自动发现机制；新仓仍需显式登记。
- `github-toolkit` 在本次执行前已存在未提交工作区改动；本次只更新其 `.governed-ai/repo-profile.json`，未触碰其源码文件。
- `vps-ssh-launcher` 当前不是 git 仓；其 `.governed-ai/repo-profile.json` 回滚需要手动恢复文件内容。

## Rollback
Revert current-repo files:
- `docs/targets/target-repos-catalog.json`
- `docs/quickstart/use-with-existing-repo.md`
- `docs/quickstart/use-with-existing-repo.zh-CN.md`
- `docs/change-evidence/20260422-target-repo-catalog-github-vps-expansion.md`
- `docs/change-evidence/README.md`

Revert target-repo files if this expansion should be undone:
- `D:\CODE\github-toolkit\.governed-ai\repo-profile.json`
- `D:\CODE\vps-ssh-launcher\.governed-ai\repo-profile.json`
