# 20260421 GAP-085 Deny-Loop Compression Baseline

## Goal
实现 `GAP-085 NTP-06` 的第一版落地：在 attached write 治理链中对确定性会被拒绝的写入做 preflight 拦截，给出确定性 remediation 与一键 retry 命令，并避免在 `runtime-check` 中继续进入无效 execute 步骤。

## Scope
- `packages/contracts/src/governed_ai_coding_runtime_contracts/attached_write_governance.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
- `scripts/runtime-check.ps1`
- `tests/runtime/test_attached_write_governance.py`
- `tests/runtime/test_session_bridge.py`
- `tests/runtime/test_attached_repo_e2e.py`

## Changes
1. 写入治理 preflight 语义增强（contract 层）
- `AttachedWriteGovernanceResult` 增加：
  - `preflight_blocked`
  - `remediation_hint`
  - `suggested_target_path`
  - `allowed_write_scopes`
- 当命中确定性路径拒绝（如 outside-allow-scope/blocked/invalid-relative-path）时，返回 deny 的同时携带可操作修复信息。

2. Session bridge deny 返回可重试命令
- `write_request` 在 `preflight_blocked=true` 时返回：
  - `preflight_blocked`
  - `remediation_hint`
  - `suggested_target_path`
  - `allowed_write_scopes`
  - `retry_command`
- `retry_command` 使用同一 `task_id` / binding / adapter 生成一条可直接重试的 `session-bridge write-request` 命令。

3. runtime-check 执行链压缩
- 新增 `write_preflight` 与 `next_actions` 输出。
- 在 `-ExecuteWriteFlow` 场景下，若 preflight 已确定 deny，则不再继续 `execute-attachment-write`，直接 fail-closed 并输出 retry action。

4. 测试覆盖
- `test_attached_write_governance`: 校验 preflight 字段与 write_allow scopes。
- `test_session_bridge`: 校验 denied write_request 返回 retry_command。
- `test_attached_repo_e2e`: 校验 runtime-check preflight deny 会阻断 execute 并输出 next_actions。

## Verification
### Targeted tests
1. `python -m unittest tests.runtime.test_attached_write_governance tests.runtime.test_session_bridge tests.runtime.test_attached_repo_e2e -v`
- Result: `Ran 40 tests ... OK`

2. `python -m unittest tests.runtime.test_attached_write_execution -v`
- Result: `Ran 5 tests ... OK`

### Gate order (required)
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- Result: `OK python-bytecode`, `OK python-import`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- Result: `Ran 270 tests ... OK`, `Ran 5 tests ... OK`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- Result: `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
- Result: doctor checks all `OK`

### Supporting checks
5. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`
6. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`

## Risks
- `retry_command` 目前是命令级建议，不是自动回放；若上下游策略变化，建议命令可能需要再次确认。
- preflight 拦截当前主要覆盖路径型确定性拒绝，非路径类 deny 仍按原路径处理。

## Rollback
Revert:
- `packages/contracts/src/governed_ai_coding_runtime_contracts/attached_write_governance.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
- `scripts/runtime-check.ps1`
- `tests/runtime/test_attached_write_governance.py`
- `tests/runtime/test_session_bridge.py`
- `tests/runtime/test_attached_repo_e2e.py`
- `docs/change-evidence/20260421-gap-085-deny-loop-compression-baseline.md`
