# 2026-04-22 Runtime target-repo baseline enforcement

## Goal
- Close the remaining runtime risks around target-repo dependency baseline drift.
- Enforce target-repo baseline checks on the attach-first execution path without changing external API contracts.

## Basis
- Previous slice added target-repo baseline verification capability, but onboarding/daily execution flow had not enforced required mode.
- `doctor-runtime.ps1 -AttachmentRoot` already fail-closed on attachment posture issues, but did not fail-closed when target-repo dependency baseline metadata was missing.

## Changes
1. Attachment writes/backfills target baseline metadata
- `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_attachment.py`
  - `attach_target_repo()` now ensures `.governed-ai/dependency-baseline.json` exists.
  - New attachments create the file.
  - Existing attachments validated without overwrite now backfill the file when missing.

2. Enforce required target baseline in onboarding/daily check chain
- `scripts/runtime-check.ps1`
  - Added `dependency-baseline-target-repo` step:
    - `python scripts/verify-dependency-baseline.py --target-repo-root <attachment-root> --require-target-repo-baseline`
  - Step result is included in JSON output as `dependency_baseline`.
  - Missing baseline now marks flow failure and emits actionable next step.

3. Doctor fail-closed integration for target baseline
- `scripts/doctor-runtime.ps1`
  - In `-AttachmentRoot` branch, healthy attachment posture now additionally requires target baseline presence.
  - Missing baseline emits:
    - `FAIL attachment-posture-missing-target-repo-dependency-baseline`
    - remediation actions
    - remediation evidence record under `<runtime_state_root>/doctor/`.

4. Regression coverage
- `tests/runtime/test_repo_attachment.py`
  - Assert attach flow creates/backfills `.governed-ai/dependency-baseline.json`.
- `tests/runtime/test_runtime_doctor.py`
  - Assert doctor reports target baseline check for healthy attachments.
  - Added fail-closed case when baseline file is removed.
- `tests/runtime/test_attached_repo_e2e.py`
  - Assert runtime-check pass payload contains `dependency_baseline.status == pass`.
  - Added failure case when target baseline file is missing.

## Commands
- Targeted regressions:
  - `python -m unittest tests.runtime.test_repo_attachment tests.runtime.test_runtime_doctor tests.runtime.test_attached_repo_e2e tests.runtime.test_dependency_baseline`
- Gate order:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

## Evidence
- Targeted regressions:
  - `35` tests passed.
- Build gate:
  - `OK python-bytecode`
  - `OK python-import`
- Runtime gate:
  - `322` tests passed, `1` skipped.
  - `5` service parity tests passed.
- Contract gate:
  - schema/example/catalog checks passed.
  - dependency baseline verification passed.
- Doctor gate:
  - runtime checks passed with dependency baseline assets visible.

## Rollback
- Revert this slice by restoring:
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_attachment.py`
  - `scripts/runtime-check.ps1`
  - `scripts/doctor-runtime.ps1`
  - `tests/runtime/test_repo_attachment.py`
  - `tests/runtime/test_runtime_doctor.py`
  - `tests/runtime/test_attached_repo_e2e.py`
- Runtime behavior rollback for affected attached repos:
  - rerun previous runtime-check/doctor behavior by reverting above files.
  - no schema migration introduced; only repo-local `.governed-ai/dependency-baseline.json` marker files may remain.
