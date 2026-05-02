# 2026-05-03 Runtime Gate Timing Split

## Rule
- `R1`: current landing point is Task 6 gate-timing closeout; target home is a faster daily entrypoint with the full readiness path unchanged.
- `R4`: this slice changes command ownership and timing evidence only; it does not weaken hard-gate order or promote `fast` into a delivery authority.
- `R8`: command routing, timing evidence, compatibility, verification, and rollback are recorded here.

## Basis
- Task 6 of `docs/plans/repo-slimming-and-speed-plan.md`
- The repo already had a bounded `RuntimeQuick` slice and a timing-capable `run-runtime-tests.py`, but the human-facing `fast` entrypoint did not reuse the shared quick gate and the latest runtime timing artifact was stale failure evidence.
- The required outcome for this slice is explicit: keep `.\run.ps1 fast` as the daily default, keep `readiness` as the delivery path, and make slow runtime files visible in a fresh timing report.

## Changes
- Updated `scripts/operator.ps1` so `FastFeedback` now delegates to `scripts/verify-repo.ps1 -Check RuntimeQuick` instead of owning a separate inline unittest list.
- Updated `scripts/verify-repo.ps1` so the full `Runtime` gate refreshes `docs/change-evidence/runtime-test-speed-latest.json` on every passing run.
- Updated `tests/runtime/test_operator_entrypoint.py` to assert the root `fast` path routes through the shared `RuntimeQuick` gate surface.
- Refreshed `docs/change-evidence/runtime-test-speed-latest.json` with fresh passing runtime timing evidence.

## Commands
- `python -m unittest tests.runtime.test_operator_entrypoint tests.runtime.test_run_runtime_tests_runner`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check RuntimeQuick`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File run.ps1 fast`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`

## Key Output
- Focused tests: `Ran 30 tests in 26.188s`, `OK`
- Shared quick gate: `OK runtime-quick-slice`, `Ran 50 tests in 20.338s`, `OK`
- Daily entrypoint: `.\run.ps1 fast` completed with `build` plus `RuntimeQuick`; quick feedback ran `50` tests in `33.031s`
- Full runtime gate: `Completed 101 test files in 188.408s; failures=0`
- Fresh slowest runtime files in `runtime-test-speed-latest.json`:
  - `tests/runtime/test_attached_repo_e2e.py` `65.195s`
  - `tests/runtime/test_autonomous_next_work_selection.py` `64.679s`
  - `tests/runtime/test_runtime_flow_preset.py` `58.095s`
  - `tests/runtime/test_dependency_baseline.py` `50.637s`
  - `tests/runtime/test_runtime_evolution.py` `44.590s`

## Verification
- The root `fast` entrypoint still works as the daily coding default and now exercises the shared `RuntimeQuick` ownership path.
- `readiness` remains unchanged as the delivery entrypoint for `build -> test -> contract/invariant -> hotspot`.
- The full `Runtime` gate now leaves fresh machine-readable timing evidence in `docs/change-evidence/runtime-test-speed-latest.json`.

## Compatibility
- No `run.ps1` aliases changed.
- No `Readiness` behavior changed.
- No RuntimeQuick test membership changed in this slice; only the ownership path changed.
- The timing JSON schema remains backward compatible for existing fields; this slice only refreshed the artifact contents.

## Rollback
- Revert `scripts/operator.ps1`, `scripts/verify-repo.ps1`, and `tests/runtime/test_operator_entrypoint.py`.
- Restore the previous `docs/change-evidence/runtime-test-speed-latest.json` from git history if the refreshed timing artifact should be discarded.
