# 2026-04-23 Additional Gate Commands with Blocking/Profile Semantics

## Goal

Close governance drift when target repositories add new quality scripts by supporting repo-profile-declared extra gates with explicit `blocking` and `profiles` semantics.

## Scope

- `packages/contracts/src/governed_ai_coding_runtime_contracts/verification_runner.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_profile.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_attachment.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
- `scripts/run-governed-task.py`
- `scripts/runtime-check.ps1`
- `schemas/jsonschema/repo-profile.schema.json`
- `schemas/examples/repo-profile/governed-ai-coding-runtime.example.json`
- `tests/runtime/test_verification_runner.py`
- `tests/runtime/test_repo_profile.py`
- `tests/runtime/test_run_governed_task_service_wrapper.py`
- `tests/runtime/test_session_bridge.py`

## Changes

1. Extended verification artifact and outcome semantics:
   - Added `required_gate_ids` and `blocking_gate_ids` to verification artifact payload.
   - Added `verification_has_blocking_failures` and `verification_overall_outcome` helpers.
   - Runtime failure now follows `blocking` gates instead of blindly requiring every gate to pass.
2. Extended repo-profile gate model:
   - Added `additional_gate_commands` support in verification plan resolution.
   - Added profile targeting (`profiles`: `quick/full/l1/l2/l3/all/*`) for additional gates.
   - Added `blocking` semantics for both canonical and additional gate entries (default follows `required`).
3. Wired outcome semantics through runtime entrypoints:
   - `session_bridge` now emits `required_gate_ids`, `blocking_gate_ids`, and `outcome` based on blocking rules.
   - `run-governed-task verify-attachment` preserves service-provided outcome and gate-id metadata.
   - `runtime-check.ps1` now honors returned `outcome` first, then `blocking_gate_ids`, then legacy fallback.
4. Updated profile schema and example:
   - Added `additional_gate_commands` schema object with `blocking` and `profiles` fields.
   - Added a non-blocking `ui-sampling` sample command in governed runtime example profile.
5. Added regression tests:
   - Additional gate profile application (quick/full split).
   - Non-blocking gate failure does not force overall failure.
   - Invalid `additional_gate_commands.profiles` value rejected.
   - Service wrapper and session bridge payload fields asserted.

## Verification

1. Targeted tests:
   - `python -m unittest tests.runtime.test_verification_runner tests.runtime.test_repo_profile tests.runtime.test_run_governed_task_service_wrapper tests.runtime.test_session_bridge tests.runtime.test_source_string_contract_guard`
   - Result: `OK` (82 tests).
2. Repository hard gates (ordered):
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1` -> `OK`
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` -> `OK` (342 tests, 2 skipped)
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` -> `OK`
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1` -> `OK`

## Risks

- `additional_gate_commands` is intentionally optional; repositories still need to keep canonical `build/test/contract` commands declared for strict gate contract compatibility.
- Existing target repositories that only use legacy fields continue to work, but they will not benefit from non-blocking/profile-targeted semantics until profile updates are applied.

## Rollback

```powershell
git restore --source=HEAD~1 -- packages/contracts/src/governed_ai_coding_runtime_contracts/verification_runner.py packages/contracts/src/governed_ai_coding_runtime_contracts/repo_profile.py packages/contracts/src/governed_ai_coding_runtime_contracts/repo_attachment.py packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py scripts/run-governed-task.py scripts/runtime-check.ps1 schemas/jsonschema/repo-profile.schema.json schemas/examples/repo-profile/governed-ai-coding-runtime.example.json tests/runtime/test_verification_runner.py tests/runtime/test_repo_profile.py tests/runtime/test_run_governed_task_service_wrapper.py tests/runtime/test_session_bridge.py docs/change-evidence/20260423-additional-gate-commands-blocking-profile.md
```
