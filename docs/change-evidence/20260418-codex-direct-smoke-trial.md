# 20260418 Codex Direct Smoke Trial

## Purpose
Record `GAP-037 Task 9`, adding a safe-mode Codex adapter smoke trial that reports task, binding, evidence, and verification wiring without claiming a real high-risk write path.

## Scope
- add `CodexAdapterTrialResult` and trial result builder to the Codex adapter contract
- add `scripts/run-codex-adapter-trial.py`
- document the smoke-trial boundary in the product doc, quickstart, docs index, and root readmes
- keep the trial default in `safe` mode

## Basis
- `docs/plans/interactive-session-productization-implementation-plan.md` Task 9
- `docs/product/codex-direct-adapter.md`
- `tests/runtime/test_codex_adapter.py`

## Changes
- `packages/contracts/src/governed_ai_coding_runtime_contracts/codex_adapter.py`
  - added `CodexAdapterTrialResult`
  - added `build_codex_adapter_trial_result(...)`
  - added `codex_adapter_trial_to_dict(...)`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/__init__.py`
  - exported the new Codex adapter trial APIs
- `scripts/run-codex-adapter-trial.py`
  - added the safe-mode CLI smoke trial entrypoint
- `tests/runtime/test_codex_adapter.py`
  - added stable trial result coverage
  - added script JSON output coverage
- `docs/product/codex-direct-adapter.md`
  - documented smoke-trial intent, example, and output shape
- `docs/quickstart/single-machine-runtime-quickstart.md`
  - distinguished Codex adapter smoke trial from the read-only trial and runtime smoke path
- `README.md`
- `README.zh-CN.md`
- `README.en.md`
- `docs/README.md`
  - linked the new smoke-trial surface and clarified current product boundary

## Commands
1. `python -m unittest tests.runtime.test_codex_adapter -v`
   - exit `0`
2. `python scripts/run-codex-adapter-trial.py --help`
   - exit `0`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
   - exit `0`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
   - exit `0`
   - `Ran 178 tests`

## Result
- safe-mode is the default trial posture
- trial output now includes `adapter_tier`, `task_id`, `binding_id`, `evidence_refs`, `verification_refs`, and `unsupported_capability_behavior`
- docs now distinguish:
  - first scripted read-only trial
  - Codex adapter smoke trial
  - local runtime smoke task

## Risks
- current trial refs are deterministic wiring refs, not persisted runtime artifacts
- native attach still requires explicit capability declaration; the trial does not infer it automatically

## Rollback
- revert `scripts/run-codex-adapter-trial.py`
- revert the `codex_adapter.py` trial-result additions
- revert README / quickstart / product doc references
