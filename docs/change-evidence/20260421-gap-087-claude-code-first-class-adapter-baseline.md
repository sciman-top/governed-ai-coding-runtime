# 20260421 GAP-087 Claude-Code First-Class Adapter Path Baseline

## Goal
为 `GAP-087 NTP-08` 落地第一版可执行基线：将 Claude Code 纳入一等 adapter 合同与 conformance 入口，而非仅依赖 generic fallback 叙述。

## Scope
- `packages/contracts/src/governed_ai_coding_runtime_contracts/adapter_registry.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/adapter_conformance.py`
- `tests/runtime/test_adapter_registry.py`
- `tests/runtime/test_adapter_conformance.py`
- `docs/product/adapter-conformance-parity-matrix.md`

## Changes
1. adapter registry 增加 Claude Code 一等合同构建器
- 新增 `build_claude_code_contract(adapter_tier="process_bridge"|"manual_handoff")`
- 输出固定：
  - `adapter_id=claude-code`
  - `product_family=claude_code`
  - user-owned upstream auth 语义
  - tier 对应 degrade 行为

2. conformance 增加 Claude trial 入口
- 新增 `evaluate_claude_trial_conformance(payload)`
- 与 Codex 复用同一 live-trial conformance gate family（identity/linkage/flow+unsupported semantics）

3. 测试补齐
- `test_claude_code_contract_is_available_as_first_class_adapter`
- `test_claude_trial_conformance_uses_same_gate_family`

4. 文档姿态同步
- parity matrix 增加 Claude baseline 行，明确当前为 first-class contract + degraded parity baseline。

## Verification
### Targeted
1. `python -m unittest tests.runtime.test_adapter_registry tests.runtime.test_adapter_conformance -v`
- result: `Ran 13 tests ... OK`

2. `python -m unittest tests.runtime.test_verification_runner -v`
- result: `Ran 15 tests ... OK`

3. `python -m unittest tests.runtime.test_session_bridge tests.runtime.test_attached_repo_e2e tests.runtime.test_attached_write_governance -v`
- result: `Ran 40 tests ... OK`

### Gate order
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
- results: all `OK` (runtime: `Ran 273 tests ... OK`)

### Supporting checks
5. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts` -> `OK`
6. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs` -> `OK`

## Risks
- 当前 Claude 路径为 contract/conformance baseline，尚未接入 live host probe 与事件 ingestion 深度。
- parity 行为现阶段仍以 degraded baseline 为主，避免 over-claim 为 supported live closure。

## Rollback
Revert:
- `packages/contracts/src/governed_ai_coding_runtime_contracts/adapter_registry.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/adapter_conformance.py`
- `tests/runtime/test_adapter_registry.py`
- `tests/runtime/test_adapter_conformance.py`
- `docs/product/adapter-conformance-parity-matrix.md`
- `docs/change-evidence/20260421-gap-087-claude-code-first-class-adapter-baseline.md`
