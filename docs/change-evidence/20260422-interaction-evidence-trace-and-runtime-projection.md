# 20260422 Interaction Evidence, Trace, And Runtime Projection

## Goal
执行《Teaching Collaboration And Low-Token Governance Implementation Plan》的 Task 4 到 Task 8，把 interaction governance 从 standalone primitives 扩展到 evidence bundle、trace/postmortem、task intake、runtime/operator read model、repo profile defaults。

## Scope
- `docs/specs/evidence-bundle-spec.md`
- `schemas/jsonschema/evidence-bundle.schema.json`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/evidence.py`
- `tests/runtime/test_evidence_timeline.py`
- `docs/specs/eval-and-trace-grading-spec.md`
- `schemas/jsonschema/eval-trace-policy.schema.json`
- `schemas/examples/eval-trace-policy/governed-runtime-improvement-baseline.example.json`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/task_intake.py`
- `tests/runtime/test_task_intake.py`
- `docs/specs/runtime-operator-surface-spec.md`
- `schemas/jsonschema/runtime-operator-surface.schema.json`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/runtime_status.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_queries.py`
- `tests/runtime/test_runtime_status.py`
- `tests/runtime/test_operator_queries.py`
- `docs/specs/repo-profile-spec.md`
- `schemas/jsonschema/repo-profile.schema.json`
- `schemas/examples/repo-profile/governed-ai-coding-runtime.example.json`
- `schemas/examples/repo-profile/target-repo-fast-full-template.example.json`
- `docs/plans/teaching-collaboration-and-low-token-governance-implementation-plan.md`

## Changes
1. Task 4: extend evidence bundle with `interaction_trace`
- 在 `evidence-bundle` spec/schema 中新增可选 `interaction_trace` 扩展块。
- `build_evidence_bundle(...)` 现在可选接收 `interaction_trace`，缺省时保持旧行为不变。
- 新增 shape normalization，fail-closed 拒绝非 dict 或 list-shaped fields。
- `test_evidence_timeline.py` 覆盖无 `interaction_trace` 的兼容路径、有扩展块的正常路径、以及非法 shape 路径。

2. Task 5: extend trace/postmortem interaction failure inputs
- 在 trace grading spec/schema 中新增 6 个 interaction-oriented failure classifications：
  - `misalignment_not_caught`
  - `over_explained_under_budget_pressure`
  - `under_explained_with_high_user_confusion`
  - `repeated_question_without_signal_upgrade`
  - `observation_gap_ignored`
  - `compression_without_recoverable_summary`
- 保持 4 个 primary grading dimensions 不变。
- 新增 `interaction_ref_fields`，明确 postmortem inputs 可以回链 interaction signal/policy refs，但不会自动改写 policy。

3. Task 6: bind interaction governance to task intake
- `TaskIntake` 新增可选 `interaction_defaults` 与 `interaction_budget_overrides`。
- defaults 支持 bounded `default_mode` 和 `max_questions`。
- overrides 只允许 non-negative int；`max_questions > 3` fail-closed，避免越过 clarification hard cap。

4. Task 7: add minimal interaction read-model projection
- `RuntimeTaskStatus` 与 `OperatorQueryResult` 新增 interaction 投影字段：
  - `interaction_posture`
  - `latest_task_restatement`
  - `interaction_budget_status`
  - `clarification_active`
  - `latest_compression_action`
  - `outstanding_observation_items_count`
- 投影来源是 active run/evidence refs 对应 evidence bundle 中的 `interaction_trace`，不是新 store。
- 无 interaction data 时所有新增字段保持 `None`/`False`，兼容现有只读 surface。

5. Task 8: add repo-profile interaction defaults
- `repo-profile` spec/schema 新增可选 `interaction_profile`。
- 允许声明：
  - `default_mode`
  - `term_explain_style`
  - `default_checklist_kind`
  - `compaction_preference`
  - `summary_template`
  - `handoff_teaching_notes`
- 明确 repo profile 不得覆盖 clarification hard caps、hard budget stop、explicit degrade semantics、canonical gate order。
- 现有 repo-profile examples 已补 interaction defaults，保持 summary/handoff template 一致。

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
1. `python -m unittest tests.runtime.test_evidence_timeline -v`
- result: pass
- key output:
  - `Ran 11 tests`
  - `OK`
2. `python -m unittest tests.runtime.test_task_intake tests.runtime.test_runtime_status tests.runtime.test_operator_queries -v`
- result: pass
- key output:
  - `Ran 21 tests`
  - `OK`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- result: pass
- key output:
  - `OK active-markdown-links`
  - `OK claim-drift-sentinel`
  - `OK claim-evidence-freshness`
  - `OK post-closeout-queue-sync`

## Risks
- 当前 runtime/operator 投影是从 persisted evidence 中读取 latest `interaction_trace`，属于最小 read-model projection；还没有独立 service-level aggregation 或 telemetry store。
- `interaction_profile` 目前只落在 spec/schema/example 层，尚未在 runtime 执行器里强制消费。
- trace/postmortem interaction failure classes 目前是 contract-ready，不代表已有自动生成流程。

## Rollback
Revert:
- `docs/specs/evidence-bundle-spec.md`
- `schemas/jsonschema/evidence-bundle.schema.json`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/evidence.py`
- `tests/runtime/test_evidence_timeline.py`
- `docs/specs/eval-and-trace-grading-spec.md`
- `schemas/jsonschema/eval-trace-policy.schema.json`
- `schemas/examples/eval-trace-policy/governed-runtime-improvement-baseline.example.json`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/task_intake.py`
- `tests/runtime/test_task_intake.py`
- `docs/specs/runtime-operator-surface-spec.md`
- `schemas/jsonschema/runtime-operator-surface.schema.json`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/runtime_status.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_queries.py`
- `tests/runtime/test_runtime_status.py`
- `tests/runtime/test_operator_queries.py`
- `docs/specs/repo-profile-spec.md`
- `schemas/jsonschema/repo-profile.schema.json`
- `schemas/examples/repo-profile/governed-ai-coding-runtime.example.json`
- `schemas/examples/repo-profile/target-repo-fast-full-template.example.json`
- `docs/plans/teaching-collaboration-and-low-token-governance-implementation-plan.md`
