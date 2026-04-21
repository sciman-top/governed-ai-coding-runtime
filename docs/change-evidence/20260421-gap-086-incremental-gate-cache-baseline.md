# 20260421 GAP-086 Incremental Gate Cache Baseline

## Goal
实现 `GAP-086 NTP-07` 的最小可用增量 gate 缓存能力：在不改变 gate 顺序与 fail-closed 语义前提下，允许在相同 scope 下复用已执行 gate 输出并在 artifact 中显式标记缓存命中。

## Scope
- `packages/contracts/src/governed_ai_coding_runtime_contracts/verification_runner.py`
- `tests/runtime/test_verification_runner.py`
- `docs/product/verification-runner.md`

## Changes
1. verification artifact 增加缓存命中可见性：
- `VerificationArtifact` 增加 `cache_hits` 字段（`gate_id -> bool`）。
- reader 支持 `cache_hits` 可选读取；缺失时保持兼容。

2. `run_verification_plan` 增加可选缓存接口：
- 新增可选参数：
  - `cache_store`
  - `cache_scope_key`
- 仅在缓存记录满足 `exit_code:int + output:str` 时命中；否则回退 live execution。
- 命中时仍写入当前 run artifact（内容前缀 `[cache-hit]`），保证证据链完整。

3. 缓存键维度固定为：
- `mode`
- `gate_id`
- `gate.command`
- `cache_scope_key`（默认 `default`）

4. 文档更新：
- 在 `docs/product/verification-runner.md` 增补 Incremental Cache baseline 说明与 fail-closed 规则。

## Verification
### Targeted
1. `python -m unittest tests.runtime.test_verification_runner -v`
- result: `Ran 15 tests ... OK`
- includes: `test_verification_runner_reuses_cache_hits_when_scope_key_matches`

2. `python -m unittest tests.runtime.test_session_bridge tests.runtime.test_attached_repo_e2e tests.runtime.test_attached_write_governance -v`
- result: `Ran 40 tests ... OK`

### Gate order
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
- results: all `OK` (runtime: `Ran 271 tests ... OK`)

### Supporting checks
5. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts` -> `OK`
6. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs` -> `OK`

## Risks
- 当前缓存命中依赖调用方提供稳定 `cache_scope_key`；若 scope key 过粗，可能降低缓存收益或引入误命中风险。
- 目前缓存仅复用 gate 结果，不做 artifact 内容语义去重。

## Rollback
Revert:
- `packages/contracts/src/governed_ai_coding_runtime_contracts/verification_runner.py`
- `tests/runtime/test_verification_runner.py`
- `docs/product/verification-runner.md`
- `docs/change-evidence/20260421-gap-086-incremental-gate-cache-baseline.md`
