# 20260614 Continuous Execution Phase 2 Runtime Enforcement And Misalignment Metrics

## Goal
- current landing: `D:\CODE\governed-ai-coding-runtime`
- target home:
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/learning_efficiency_metrics.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/evidence.py`
  - `docs/specs/evidence-bundle-spec.md`
  - `docs/specs/learning-efficiency-metrics-spec.md`
  - `schemas/jsonschema/evidence-bundle.schema.json`
  - `schemas/jsonschema/learning-efficiency-metrics.schema.json`
  - `schemas/examples/learning-efficiency-metrics/baseline.example.json`
  - `docs/plans/continuous-execution-readiness-and-rollout-plan.md`
  - `docs/change-evidence/20260614-continuous-execution-phase2-misalignment-metrics.md`
- verification path: truth-check `Task 4`, then add the smallest contract-backed `Task 5` metric slice without starting `Task 6`

## Why This Slice Was Needed
- `Continuous Execution Readiness And Rollout` moved into the active queue on `2026-06-14`, but Phase 2 still mixed two different states:
  - `Task 4` was already implemented by the older interaction-governance lane and only lacked current-plan truth reconciliation.
  - `Task 5` had persisted learning-efficiency metrics, but it still lacked explicit false-positive / false-negative misalignment metrics.
- The next honest autonomous slice was therefore not a new runtime behavior sweep. It was:
  - revalidate the already-landed runtime enforcement/projection boundary for `Task 4`
  - add one bounded, evidence-backed metric extension for `Task 5`

pre_change_review:
- control_repo_manifest_and_rule_sources:
  - `rules/manifest.json`
  - `rules/projects/governed-ai-coding-runtime/*`
  - `scripts/sync-agent-rules.py`
  - `scripts/verify-target-repo-governance-consistency.py`
- user_level_deployed_rule_files:
  - `C:\Users\sciman\.codex\AGENTS.md`
  - `C:\Users\sciman\.claude\CLAUDE.md`
  - `C:\Users\sciman\.gemini\GEMINI.md`
- target_repo_deployed_rule_files:
  - `D:\CODE\ClassroomToolkit\AGENTS.md`
  - `D:\CODE\external\Cockpit-Tools-Local\AGENTS.md`
  - `D:\CODE\k12-question-graph\AGENTS.md`
  - `D:\CODE\skills-manager\AGENTS.md`
- target_repo_gate_scripts_and_ci:
  - `scripts/verify-target-repo-governance-consistency.py`
  - `scripts/sync-agent-rules.py`
  - `scripts/verify-repo.ps1`
  - no workflow file changed in this slice
- target_repo_repo_profile:
  - `docs/targets/target-repos-catalog.json`
  - `docs/targets/target-repo-governance-baseline.json`
  - target `.governed-ai/repo-profile.json` files were reviewed as dependent surfaces and left structurally unchanged
- target_repo_readme_and_operator_docs:
  - `docs/plans/continuous-execution-readiness-and-rollout-plan.md`
  - `docs/specs/evidence-bundle-spec.md`
  - `docs/specs/learning-efficiency-metrics-spec.md`
  - `docs/change-evidence/README.md`
- current_official_tool_loading_docs:
  - current repo-managed rule loading contract remains `GlobalUser/AGENTS.md v9.53`
  - current project-level loading contract remains `AGENTS.md — governed-ai-coding-runtime`
  - this slice does not change tool loading semantics; it only keeps worktree-path resolution aligned with the existing contracts
- drift-integration decision:
  - keep the change additive and fail-closed: patch worktree path assumptions in the affected governance scripts, reconcile the active continuous-execution plan with current repo truth, and avoid broad rule-sync/runtime-flow redesign in the same slice

## Change Summary
1. Revalidated `Task 4` against current repo truth
- Confirmed that runtime task creation/run paths already consume repo-profile interaction defaults through:
  - `scripts/run-governed-task.py`
  - `packages/contracts/.../task_intake.py`
- Confirmed fail-closed validation still exists for invalid interaction defaults and budget overrides.
- Confirmed operator/runtime read models already project interaction posture fields from persisted `interaction_trace` through:
  - `packages/contracts/.../runtime_status.py`
  - `packages/contracts/.../operator_queries.py`
- Updated the active continuous-execution plan to mark `Task 4` complete from current repo truth instead of leaving it stale.

2. Added explicit misalignment review input to `interaction_trace`
- Extended the evidence-bundle contract with optional `interaction_trace.misalignment_reviews`.
- The new structured list stays additive and evidence-backed.
- Each review requires:
  - `review_id`
  - `review_outcome`
  - `summary`
  - `evidence_refs`
- Supported `review_outcome` values are:
  - `false_positive`
  - `false_negative`

3. Added explicit false-positive / false-negative metrics
- Extended `LearningEfficiencyMetricsRecord` with:
  - `misalignment_false_positive_count`
  - `misalignment_false_negative_count`
- The metrics builder now derives those counts only from explicit structured `misalignment_reviews`.
- This keeps the metric fail-closed and reviewable:
  - no free-form transcript inference
  - no hidden heuristic upgrade
  - no automatic runtime mutation
- The summary snapshot now also reports:
  - `misalignment_false_positive_rate`
  - `misalignment_false_negative_rate`

4. Reconciled the active plan with the new truth
- Marked `Task 5` complete in `docs/plans/continuous-execution-readiness-and-rollout-plan.md`.
- Marked the first two Phase 2 checkpoint bullets complete:
  - runtime and contract gates pass
  - learning-efficiency metrics remain persisted and evidence-linked
- Updated `Immediate Next Slice` to point at `Task 6` instead of the already-closed Phase 1 kickoff steps.

## Verification
### Focused checks
- `python -m unittest tests.runtime.test_evidence_timeline tests.runtime.test_learning_efficiency_metrics -v`
  - result: pass
  - key output includes:
    - `test_evidence_bundle_rejects_invalid_misalignment_reviews_shape ... ok`
    - `test_build_learning_efficiency_metrics_from_interaction_trace ... ok`
    - `test_summarize_learning_efficiency_metrics_baseline_rates ... ok`

### Gate order
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
- result: pass
- key output includes:
  - build: `OK python-bytecode`, `OK python-import`
  - runtime: `OK runtime-unittest`, `OK runtime-service-parity`, `OK runtime-service-wrapper-drift-guard`
  - contract: `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing`, `OK pre-change-review`, `OK reference-required-changes`
  - hotspot/doctor: `OK runtime-policy-compatibility`, `OK runtime-policy-maintenance`, `OK codex-capability-ready`, `OK adapter-posture-visible`

## Queue Boundary
- This slice completes `Task 5` and reconciles `Task 4` truth.
- This slice does **not** claim `Task 6` is complete.
- This slice does **not** change the current selector away from `defer_ltp_and_refresh_evidence`.

## Risk
- risk_level: `low`
- reason:
  - additive contract/schema/metrics change
  - no new host-control or target-repo mutation path
  - no change to approval order, gate order, or budget-stop authority

## Rollback
- revert:
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/evidence.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/learning_efficiency_metrics.py`
  - `tests/runtime/test_evidence_timeline.py`
  - `tests/runtime/test_learning_efficiency_metrics.py`
  - `docs/specs/evidence-bundle-spec.md`
  - `docs/specs/learning-efficiency-metrics-spec.md`
  - `schemas/jsonschema/evidence-bundle.schema.json`
  - `schemas/jsonschema/learning-efficiency-metrics.schema.json`
  - `schemas/examples/learning-efficiency-metrics/baseline.example.json`
  - `docs/plans/continuous-execution-readiness-and-rollout-plan.md`
  - `docs/change-evidence/20260614-continuous-execution-phase2-misalignment-metrics.md`
  - `docs/change-evidence/README.md`
- re-run:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
