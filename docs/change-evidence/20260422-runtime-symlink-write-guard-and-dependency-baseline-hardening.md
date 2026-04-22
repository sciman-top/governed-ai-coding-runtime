# 2026-04-22 Runtime Symlink Write Guard and Dependency Baseline Hardening

## Goal
- Close a write-path escape risk in attached write execution without changing external API or workflow semantics.
- Improve dependency baseline verifier diagnostics and path-safety checks to reduce false triage time.

## Root Cause
- Attached write execution validated `target_path` against policy patterns but did not verify the resolved filesystem target remained inside `attachment_root` when symlinks were present.
- Dependency baseline verification trusted configured scan roots and surfaced parser failures with low-context exceptions.

## Changes
- Added resolved-target containment check in attached write execution:
  - Deny writes when `target_path` resolves outside `attachment_root`.
  - Preserve existing behavior for in-repo symlinks.
- Hardened dependency baseline verifier:
  - Enforce repo-relative path constraints for `python.scan_roots` and `target_repo.baseline_paths`.
  - Upgrade file read/JSON parse/import parse failures to actionable `ValueError` messages with file context.
- Added regression and guardrail tests for both areas.

## Files
- `packages/contracts/src/governed_ai_coding_runtime_contracts/attached_write_execution.py`
- `tests/runtime/test_attached_write_execution.py`
- `scripts/verify-dependency-baseline.py`
- `tests/runtime/test_dependency_baseline.py`

## Verification
1. `python -m unittest tests.runtime.test_attached_write_execution`
2. `python -m unittest tests.runtime.test_dependency_baseline`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
5. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
6. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

All commands passed.

## Compatibility
- No contract/schema field changes.
- No external dependency additions.
- Existing in-repo symlink write semantics remain supported.

## Rollback
- Revert only the four files listed above, then rerun:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
