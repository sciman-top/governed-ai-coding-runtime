# 20260422 Interaction Governance Lane Closeout

## Goal
完成《Teaching Collaboration And Low-Token Governance Implementation Plan》的 Task 9，关闭 teaching-collaboration / low-token governance 这一条 bounded follow-on lane，并把指标基线、验证结果、完成边界和回滚入口留档。

## Scope
- `docs/plans/teaching-collaboration-and-low-token-governance-implementation-plan.md`
- `docs/plans/README.md`
- `docs/change-evidence/20260422-interaction-evidence-trace-and-runtime-projection.md`
- `docs/change-evidence/20260422-interaction-governance-lane-closeout.md`
- `docs/change-evidence/README.md`

## Changes
1. closeout the implementation plan
- 把 Task 4 到 Task 9 的 acceptance criteria 与 verification 全部回填为已完成。
- 修正 Task 4 中的测试路径，从计划占位 `tests/runtime/test_evidence.py` 回到仓库事实 `tests/runtime/test_evidence_timeline.py`。

2. update authoritative plan index
- `docs/plans/README.md` 现在把该计划标记为 `completed bounded follow-on implementation lane verified on 2026-04-22`。
- scope 描述同步扩展到 evidence/trace integration、task-intake defaults、minimal runtime/operator projection、repo-profile interaction defaults。

3. record minimal metrics baseline
- 本 lane 的 baseline metrics 记录为：
  - `alignment_confirm_rate`
  - `misalignment_detect_rate`
  - `repeated_failure_before_clarify`
  - `observation_gap_prompt_rate`
  - `term_explanation_trigger_rate`
  - `compression_trigger_rate`
  - `explanation_token_share`
  - `handoff_recovery_success_rate`
- 这些指标在本次 closeout 中是 design-and-contract baseline，不代表 runtime 已有完整采集和报表。

4. make completion boundary explicit
- design/spec/schema/example: complete for this lane.
- Python contract primitives: complete for this lane.
- runtime behavior: minimal task-intake binding and read-model projection are landed.
- not yet productized: telemetry aggregation, metrics rollup pipeline, repo-profile runtime enforcement, automatic postmortem generation.

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
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- result: pass
- key output:
  - `OK active-markdown-links`
  - `OK claim-drift-sentinel`
  - `OK claim-evidence-freshness`
  - `OK post-closeout-queue-sync`
2. `python -m unittest tests.runtime.test_evidence_timeline tests.runtime.test_task_intake tests.runtime.test_runtime_status tests.runtime.test_operator_queries -v`
- result: pass
- key output:
  - `Ran 32 tests`
  - `OK`

## Risks
- closeout 完成的是 bounded lane 本身，不意味着 interaction telemetry 或 full runtime teaching loop 已经产品化。
- repo-profile 的 interaction defaults 仍需后续执行器消费路径，当前主要用于 contract-ready profile reuse。
- metrics baseline 目前是治理契约与后续实现锚点，尚未变成 SLO dashboard。

## Rollback
Revert:
- `docs/plans/teaching-collaboration-and-low-token-governance-implementation-plan.md`
- `docs/plans/README.md`
- `docs/change-evidence/20260422-interaction-evidence-trace-and-runtime-projection.md`
- `docs/change-evidence/20260422-interaction-governance-lane-closeout.md`
- `docs/change-evidence/README.md`
