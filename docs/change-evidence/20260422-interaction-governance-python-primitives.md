# 20260422 Interaction Governance Python Primitives

## Goal
执行《Teaching Collaboration And Low-Token Governance Implementation Plan》的 Task 3，新增可执行的 interaction governance Python contract primitives，并用最小单测覆盖 task-created、repeated-failure、observation-gap、term-confusion、budget-pressure 五类场景。

## Scope
- `packages/contracts/src/governed_ai_coding_runtime_contracts/interaction_governance.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/__init__.py`
- `tests/runtime/test_interaction_governance.py`
- `docs/plans/teaching-collaboration-and-low-token-governance-implementation-plan.md`
- `docs/change-evidence/20260422-interaction-governance-python-primitives.md`
- `docs/change-evidence/README.md`

## Changes
1. 新增 interaction governance contract primitives
- 新增 `InteractionSignal`、`ResponsePolicy`、`TeachingBudget` 三个 dataclass。
- 新增构造函数：
  - `build_interaction_signal`
  - `build_response_policy`
  - `build_teaching_budget`
  - `build_task_created_policy`
  - `derive_response_policy`

2. 保持 fail-closed 校验
- invalid signal kind / posture / budget status 会抛出 `ValueError`。
- `max_questions` 继续受 clarification cap 约束。
- `stop_on_budget` 要求显式 compression/handoff 语义。

3. 与 clarification primitives 保持兼容
- `derive_response_policy` 在 `repeated_failure` 场景下直接调用现有 `evaluate_clarification`。
- 未重造 clarification 语义，只把其结果投影为 response policy posture。

4. 新增最小单测与根导出
- 新增 `tests/runtime/test_interaction_governance.py`。
- 从包根导出 interaction governance API，保持 contract root 一致性。

## Verification
### Gate order
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
- result: all pass
- key output:
  - build: `OK python-bytecode`, `OK python-import`
  - runtime: `OK runtime-unittest`, `OK runtime-service-parity`, `OK runtime-service-wrapper-drift-guard`
  - contract: `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing`
  - hotspot/doctor: `OK runtime-policy-compatibility`, `OK runtime-policy-maintenance`, `OK codex-capability-ready`, `OK adapter-posture-visible`

### Supporting checks
1. `python -m unittest tests.runtime.test_interaction_governance -v`
- result: pass
- key output:
  - `Ran 9 tests`
  - `OK`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- result: pass
- key output:
  - `OK active-markdown-links`
  - `OK claim-drift-sentinel`
  - `OK claim-evidence-freshness`
  - `OK post-closeout-queue-sync`

## Risks
- 当前 primitives 只覆盖 policy derivation 与 validation，不包含 evidence bundle wiring 或 operator read-model projection。
- 目前 priority mapping 仍是 narrow baseline；后续如果 signal 家族扩大，需要同步扩测试，否则容易漂移。

## Rollback
Revert:
- `packages/contracts/src/governed_ai_coding_runtime_contracts/interaction_governance.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/__init__.py`
- `tests/runtime/test_interaction_governance.py`
- `docs/plans/teaching-collaboration-and-low-token-governance-implementation-plan.md`
- `docs/change-evidence/20260422-interaction-governance-python-primitives.md`
- `docs/change-evidence/README.md`
