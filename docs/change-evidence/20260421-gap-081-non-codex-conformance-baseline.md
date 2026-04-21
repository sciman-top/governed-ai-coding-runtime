# 20260421 GAP-081 Non-Codex Conformance Baseline

## Goal
Start `GAP-081 NTP-02` by enforcing one shared conformance gate family across:
- Codex live adapter trial
- non-Codex (`generic.process.cli`) runtime-check fallback trial

## Scope
- `packages/contracts/src/governed_ai_coding_runtime_contracts/adapter_conformance.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/__init__.py`
- `tests/runtime/test_adapter_conformance.py`
- `docs/product/adapter-conformance-parity-matrix.md`
- `docs/README.md`

## Runtime Inputs Used
- Codex live trial command:
  - `python scripts/run-codex-adapter-trial.py --repo-id "governed-ai-coding-runtime" --task-id "task-gap080-live-adapter-trial-20260421" --binding-id "binding-governed-ai-coding-runtime" --probe-live`
- Non-Codex runtime-check command:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-check.ps1 -AttachmentRoot "D:\CODE\governed-ai-coding-runtime" -AttachmentRuntimeStateRoot "D:\CODE\governed-ai-runtime-state\self-runtime" -Mode quick -PolicyStatus allow -TaskId "task-gap081-generic-trial-20260421" -RunId "run-gap081-generic-trial-20260421" -CommandId "cmd-gap081-generic-trial-20260421" -AdapterId "generic.process.cli" -Json`

## Changes
1. Added shared conformance evaluator module with two entrypoints:
   - `evaluate_codex_trial_conformance(...)`
   - `evaluate_runtime_check_conformance(...)`
2. Added normalized parity matrix builder:
   - `build_parity_matrix(...)`
3. Added runtime tests to enforce the shared gate family for Codex and non-Codex payloads.
4. Added parity matrix documentation that explicitly records `supported / degraded / blocked` host statuses.

## Verification
### Targeted
- `python -m unittest tests.runtime.test_adapter_conformance -v`

### Full gates (post-change)
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`

## Current Status Note
This is the conformance baseline slice for `GAP-081`; full closeout should still include wider host fixtures and expanded non-Codex trial breadth.

## Rollback
Revert:
- `packages/contracts/src/governed_ai_coding_runtime_contracts/adapter_conformance.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/__init__.py`
- `tests/runtime/test_adapter_conformance.py`
- `docs/product/adapter-conformance-parity-matrix.md`
- `docs/README.md`
- this evidence file
