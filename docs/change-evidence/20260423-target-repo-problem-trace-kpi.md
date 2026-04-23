# 20260423 Target Repo Problem Trace And KPI Aggregation

## Goal
- 让目标仓每次 AI 编码治理执行都沉淀可聚合的问题痕迹，优先覆盖门禁失败、写流失败与失败后恢复链路。

## Clarification Trace
- `issue_id=target-repo-problem-trace-kpi`
- `attempt_count=1`
- `clarification_mode=direct_fix`
- `clarification_scenario=bugfix`
- `clarification_questions=[]`
- `clarification_answers=[]`

## Changes
- Updated `scripts/runtime-check.ps1`
  - 新增 `problem_trace` 输出块，统一沉淀：
    - `has_problem`
    - `failure_stage`
    - `failure_signature`
    - `failure_reason`
    - `failed_steps`
    - `gate_failure_ids`
    - `write_issue`（含 `preflight_blocked/retry_command`）
    - `next_actions`
- Updated `packages/contracts/src/governed_ai_coding_runtime_contracts/target_repo_speed_kpi.py`
  - 新增按窗口聚合的问题指标：
    - `problem_run_rate`
    - `problem_recovery_retries`
    - `latest_problem_signature`
    - `latest_problem_run_ref`
  - 优先消费 `runtime_check.payload.problem_trace`，并保留向后兼容推断逻辑。
- Updated `docs/specs/target-repo-speed-kpi-spec.md`
  - 补充问题痕迹聚合字段与约束。
- Updated `schemas/jsonschema/target-repo-speed-kpi.schema.json`
  - 补齐新字段 schema 定义。
- Updated `schemas/examples/target-repo-speed-kpi/latest.example.json`
  - 补充新字段示例。
- Updated `tests/runtime/test_attached_repo_e2e.py`
  - 断言 `runtime-check` 输出 `problem_trace` 在通过/失败场景的行为。
- Updated `tests/runtime/test_target_repo_speed_kpi.py`
  - 断言 KPI 新增问题聚合字段的计算结果。

## Verification
1. Targeted tests
   - Command: `python -m unittest tests/runtime/test_target_repo_speed_kpi.py tests/runtime/test_attached_repo_e2e.py`
   - Result: `Ran 8 tests ... OK`
2. Build gate
   - Command: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
   - Key output: `OK python-bytecode`, `OK python-import`
3. Test gate
   - Command: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
   - Key output: `Ran 350 tests ... OK (skipped=2)`, `Ran 5 tests ... OK`
4. Contract/invariant gate
   - Command: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
   - Key output: `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing`, `OK dependency-baseline`
5. Hotspot gate
   - Command: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
   - Key output: `OK gate-command-build`, `OK gate-command-test`, `OK gate-command-contract`, `OK gate-command-doctor`, `OK adapter-posture-visible`

## Risks
- 历史 `target-repo-runs/*.json` 不包含 `problem_trace`；当前实现已做兼容推断，但历史问题签名可能粒度较粗。
- 新增字段会扩展 KPI 输出结构；依赖旧字段的消费者不受影响，但若做严格字段白名单解析需同步放行新字段。

## Rollback
1. Revert code/docs/tests for this change:
   - `git checkout -- scripts/runtime-check.ps1`
   - `git checkout -- packages/contracts/src/governed_ai_coding_runtime_contracts/target_repo_speed_kpi.py`
   - `git checkout -- docs/specs/target-repo-speed-kpi-spec.md`
   - `git checkout -- schemas/jsonschema/target-repo-speed-kpi.schema.json`
   - `git checkout -- schemas/examples/target-repo-speed-kpi/latest.example.json`
   - `git checkout -- tests/runtime/test_attached_repo_e2e.py`
   - `git checkout -- tests/runtime/test_target_repo_speed_kpi.py`
2. Revert this evidence record and index entry:
   - `git checkout -- docs/change-evidence/20260423-target-repo-problem-trace-kpi.md`
   - `git checkout -- docs/change-evidence/README.md`
