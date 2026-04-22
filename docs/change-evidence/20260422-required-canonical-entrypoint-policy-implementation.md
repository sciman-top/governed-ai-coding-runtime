# 2026-04-22 Required Canonical Entrypoint Policy Implementation

## Goal
- 实现统一入口三阶段策略的最小可用版本。
- 让目标仓可以声明 canonical entrypoint，并在 `advisory / targeted_enforced / repo_wide_enforced` 三种模式下观测或阻断 direct 调用。

## Changes
- 在 `repo-profile` schema、loader、目标仓模板、默认 attachment profile 中加入 `required_entrypoint_policy`。
- 新增 `entrypoint_policy.py`，统一负责默认值、归一化、评估与阻断判定。
- `runtime-flow.ps1`、`runtime-flow-preset.ps1`、`runtime-check.ps1` 开始透传 `entrypoint_id`。
- `session-bridge` 与 `run-governed-task` 接入 entrypoint policy 判定，并把结果写入返回 payload。
- 维持向后兼容：Python helper 入口保留默认 `entrypoint_id`。
- 补充 runtime 单测，覆盖默认配置、direct deny、canonical pass。

## Commands
- `python -m py_compile scripts/session-bridge.py scripts/run-governed-task.py packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
- `python -m unittest tests.runtime.test_repo_profile tests.runtime.test_repo_attachment tests.runtime.test_run_governed_task_cli tests.runtime.test_session_bridge`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`

## Evidence
- 定向单测通过：`79 tests OK`
- `verify-repo -Check Runtime` 通过
- `verify-repo -Check Contract` 通过
- direct 调用在 `targeted_enforced` 下会返回 `entrypoint_policy_denied`
- canonical `runtime-flow` / `runtime-flow-preset` 透传后可正常继续 gate 与 write 流程

## Rollback
- 回滚本次涉及的 schema、contracts、scripts、tests 变更即可恢复到“只推荐统一入口、不执行阻断”的状态。
- 优先使用 git 历史回滚；若仅需停用策略，也可把目标仓 `required_entrypoint_policy.current_mode` 改回 `advisory`。
