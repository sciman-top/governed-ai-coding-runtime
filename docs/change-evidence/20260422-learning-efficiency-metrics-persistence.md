# 20260422 Learning Efficiency Metrics Persistence

## Goal
执行用户指定的 `2`：在 interaction profile 已接入 runtime 后，补齐 learning-efficiency metrics 的 task-scoped 派生、持久化和 baseline 汇总能力。

## Scope
- `packages/contracts/src/governed_ai_coding_runtime_contracts/learning_efficiency_metrics.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/__init__.py`
- `scripts/run-governed-task.py`
- `docs/specs/learning-efficiency-metrics-spec.md`
- `tests/runtime/test_learning_efficiency_metrics.py`
- `tests/runtime/test_run_governed_task_service_wrapper.py`
- `docs/change-evidence/20260422-learning-efficiency-metrics-persistence.md`
- `docs/change-evidence/README.md`

## Changes
1. Added learning-efficiency metrics primitives
- Added `LearningEfficiencyMetricsRecord` and `LearningEfficiencyMetricsSnapshot`.
- Added `build_learning_efficiency_metrics(...)` to derive task-scoped metrics from evidence bundle `interaction_trace`.
- Added `persist_learning_efficiency_metrics(...)` for standalone JSON persistence.
- Added `summarize_learning_efficiency_metrics(...)` for the baseline rates:
  - `alignment_confirm_rate`
  - `misalignment_detect_rate`
  - `repeated_failure_before_clarify`
  - `observation_gap_prompt_rate`
  - `term_explanation_trigger_rate`
  - `compression_trigger_rate`
  - `explanation_token_share`
  - `handoff_recovery_success_rate`

2. Wired runtime metrics artifact generation
- `run-governed-task.py run` now writes `metrics/learning-efficiency.json` after the evidence bundle is persisted.
- The metrics artifact points back to its `metrics_source_ref` evidence bundle.
- The metrics artifact is added to the active run artifact refs.

3. Updated contract docs
- `learning-efficiency-metrics-spec.md` now states that runtime-generated metrics should be persisted as task/run artifacts that point back to the source evidence bundle.

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
1. `python -m unittest tests.runtime.test_learning_efficiency_metrics tests.runtime.test_run_governed_task_service_wrapper -v`
- result: pass
- key output:
  - `Ran 11 tests`
  - `OK`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- result: pass
- key output:
  - `OK active-markdown-links`
  - `OK claim-drift-sentinel`
  - `OK claim-evidence-freshness`

## Risks
- Metrics are derived from currently persisted interaction evidence. If an upstream agent omits interaction signals, the metrics stay conservative rather than inferring hidden user state.
- This adds artifact persistence and summary primitives, not a dashboard or telemetry service.

## Rollback
Revert:
- `packages/contracts/src/governed_ai_coding_runtime_contracts/learning_efficiency_metrics.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/__init__.py`
- `scripts/run-governed-task.py`
- `docs/specs/learning-efficiency-metrics-spec.md`
- `tests/runtime/test_learning_efficiency_metrics.py`
- `tests/runtime/test_run_governed_task_service_wrapper.py`
- `docs/change-evidence/20260422-learning-efficiency-metrics-persistence.md`
- `docs/change-evidence/README.md`
