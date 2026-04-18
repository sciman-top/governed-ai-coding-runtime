# 20260418 Multi-Repo Trial Evidence Model

## Purpose
Record `GAP-039 Task 12`, adding the structured evidence model for multi-repo onboarding and adapter feedback.

## Basis
- `docs/plans/interactive-session-productization-implementation-plan.md` Task 12
- `docs/specs/evidence-bundle-spec.md`
- `docs/specs/eval-and-trace-grading-spec.md`
- `schemas/jsonschema/evidence-bundle.schema.json`

## Changes
- `packages/contracts/src/governed_ai_coding_runtime_contracts/multi_repo_trial.py`
  - added `MultiRepoTrialRecord`
  - added `MultiRepoTrialFollowUp`
  - added `build_multi_repo_trial_record(...)`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/evidence.py`
  - added optional `trial_feedback` support on evidence bundles
- `packages/contracts/src/governed_ai_coding_runtime_contracts/__init__.py`
  - exported the multi-repo trial primitives
- `tests/runtime/test_multi_repo_trial.py`
  - added trial record coverage and follow-up category validation
- `tests/runtime/test_evidence_timeline.py`
  - added evidence-bundle linkage coverage for trial feedback
- `docs/specs/evidence-bundle-spec.md`
  - documented `trial_feedback`
- `docs/specs/eval-and-trace-grading-spec.md`
  - documented `trial_id` and categorized follow-ups
- `schemas/jsonschema/evidence-bundle.schema.json`
  - added `trial_feedback`
- `schemas/catalog/schema-catalog.yaml`
  - bumped schema catalog version to `1.7`
- `docs/product/multi-repo-trial-loop.md`
  - added the public trial-evidence model doc
- `docs/README.md`
  - linked the new product doc

## Commands
1. `python -m unittest tests.runtime.test_multi_repo_trial tests.runtime.test_evidence_timeline -v`
   - exit `0`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
   - exit `0`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
   - exit `0`
   - `Ran 185 tests`

## Result
- multi-repo trial feedback is now a machine-readable record instead of free-form notes
- evidence bundles can optionally link back to the trial that produced onboarding or adapter feedback
- follow-up items are classified into repo-specific, onboarding-generic, adapter-generic, and contract-generic buckets

## Risks
- this task defines the model, not the runner
- `trial_feedback` is optional, so callers still need the next task to emit it consistently

## Rollback
- revert `multi_repo_trial.py`
- revert `evidence.py` optional `trial_feedback`
- revert spec/schema/doc additions for trial evidence
