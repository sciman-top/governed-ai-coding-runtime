# 20260614 Continuous Execution Teaching Yield Guardrail

## Goal
- current landing: `D:\CODE\governed-ai-coding-runtime`
- target home:
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/interaction_governance.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/__init__.py`
  - `tests/runtime/test_interaction_governance.py`
  - `docs/specs/response-policy-spec.md`
  - `docs/specs/teaching-budget-spec.md`
  - `schemas/examples/teaching-budget/default-runtime.example.json`
  - `docs/plans/continuous-execution-readiness-and-rollout-plan.md`
  - `docs/change-evidence/20260614-continuous-execution-teaching-yield-guardrail.md`
- verification path: complete `Task 6` by adding a deterministic, machine-reviewable teaching-yield downgrade guardrail without starting target-repo rollout

## Why This Slice Was Needed
- After `Task 5`, the repo could persist alignment and misalignment metrics, but it still lacked a deterministic runtime rule that turns low teaching yield into a bounded downgrade decision.
- The plan explicitly required:
  - explicit guardrail thresholds
  - deterministic downgrade path `teaching -> guided -> terse`
  - explicit stop/handoff behavior at exhaustion
- The smallest honest next slice was therefore a contract-level guardrail layered onto the already-landed interaction primitives.

## Change Summary
1. Added a deterministic teaching-yield guardrail helper
- Added `apply_teaching_yield_guardrail(...)` in `interaction_governance.py`.
- The helper consumes:
  - current `ResponsePolicy`
  - active `TeachingBudget`
  - current `LearningEfficiencyMetricsRecord`
- It keeps the downgrade machine-reviewable and one-step-per-evaluation:
  - `teaching -> guided`
  - `guided -> terse`

2. Made thresholds explicit in `TeachingBudget.soft_thresholds`
- Added required soft-threshold keys for the guardrail:
  - `guided_downgrade_explanation_tokens`
  - `terse_downgrade_explanation_tokens`
  - `minimum_alignment_confirmations`
- Added fail-closed validation:
  - every key must be present and non-negative
  - terse threshold must be greater than or equal to guided threshold

3. Preserved exhaustion semantics as explicit stop behavior
- `budget_status=exhausted` still resolves to explicit `stop_on_budget` behavior.
- The guardrail cannot silently continue or weaken stop/handoff semantics at exhaustion.

4. Added focused coverage for downgrade and threshold behavior
- Added tests that prove:
  - `teaching` downgrades to `guided` when explanation spend crosses the first threshold without alignment improvement
  - `guided` downgrades to `terse` when explanation spend crosses the second threshold without alignment improvement
  - alignment confirmation suppresses the downgrade
  - invalid threshold ordering fails closed

## Verification
### Focused checks
- `python -m unittest tests.runtime.test_interaction_governance -v`
  - result: pass
  - key output includes:
    - `test_teaching_yield_guardrail_downgrades_teaching_to_guided ... ok`
    - `test_teaching_yield_guardrail_downgrades_guided_to_terse ... ok`
    - `test_teaching_yield_guardrail_stays_put_when_alignment_improved ... ok`
    - `test_teaching_yield_guardrail_rejects_invalid_threshold_order ... ok`

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
- This slice completes `Task 6`.
- This slice does **not** start `Task 7` rollout work.
- This slice does **not** change the selector away from `defer_ltp_and_refresh_evidence`.

## Risk
- risk_level: `low`
- reason:
  - additive contract and test slice
  - deterministic thresholds live in existing budget structure
  - no target-repo mutation or host-side control path changed

## Rollback
- revert:
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/interaction_governance.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/__init__.py`
  - `tests/runtime/test_interaction_governance.py`
  - `docs/specs/response-policy-spec.md`
  - `docs/specs/teaching-budget-spec.md`
  - `schemas/examples/teaching-budget/default-runtime.example.json`
  - `docs/plans/continuous-execution-readiness-and-rollout-plan.md`
  - `docs/change-evidence/20260614-continuous-execution-teaching-yield-guardrail.md`
  - `docs/change-evidence/README.md`
- re-run:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
