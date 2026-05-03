# 2026-05-03 Runtime Runner Parallel Scheduling

## Rule
- `R1`: current landing point is the self-runtime test runner; target home is faster full Runtime feedback without weakening `RuntimeQuick` or delivery gates.
- `R2`: optimize one bounded runner behavior, then verify with focused tests and the formal Runtime gate.
- `R4`: keep the explicit worker override and add a cap rollback knob instead of forcing unbounded parallelism.
- `R8`: record baseline, experiments, commands, evidence, compatibility, and rollback.

## Basis
- Current fresh baseline: `docs/change-evidence/runtime-test-speed-latest.json` reported `target_count=102`, `worker_count=4`, `elapsed_seconds=151.59558160000051`, and `failure_count=0`.
- Previous evidence kept the worker default conservative after older higher-worker experiments hit drift-sensitive instability.
- New 2026-05-03 experiments on the current clean baseline showed higher worker counts are stable again:
  - `--workers 8`: `102` files, `116.272s`, `0` failures.
  - `--workers 12`: `102` files, `106.269s`, `0` failures.
- A slowest-first-only run with the old 4-worker default was stable but only marginally faster:
  - default 4 workers with slowest-first scheduling: `102` files, `148.541s`, `0` failures.
- Combined slowest-first scheduling plus 8 workers gave the best low-risk default candidate:
  - `--workers 8` with slowest-first scheduling: `102` files, `94.659s`, `0` failures.

## Changes
- `scripts/run-runtime-tests.py` now reads a prior timing summary and starts known slow test files first.
- The automatic worker cap is raised from `4` to `8`.
- `GOVERNED_RUNTIME_TEST_AUTO_WORKER_CAP` can lower the automatic cap without changing command lines.
- Existing explicit controls remain:
  - `--workers`
  - `GOVERNED_RUNTIME_TEST_WORKERS`
  - `--timeout-seconds`
  - `GOVERNED_RUNTIME_TEST_TIMEOUT_SECONDS`
- `tests/runtime/test_run_runtime_tests_runner.py` covers slowest-first ordering, Windows path history loading, auto cap reduction, and explicit worker override precedence.
- `docs/targets/target-repo-test-slicing-policy.md` documents the new runner behavior.

## Commands
- `python -m unittest tests.runtime.test_run_runtime_tests_runner`
- `python scripts/run-runtime-tests.py --suite runtime=tests/runtime --suite service=tests/service --pattern test_run_runtime_tests_runner.py --summary-json .tmp/runtime-runner-focused-summary.json`
- `python -m unittest tests.runtime.test_target_repo_speed_kpi tests.runtime.test_target_repo_gate_speed_audit`
- `python scripts/run-runtime-tests.py --suite runtime=tests/runtime --suite service=tests/service --workers 8 --summary-json .tmp/runtime-test-speed-workers8.json`
- `python scripts/run-runtime-tests.py --suite runtime=tests/runtime --suite service=tests/service --workers 12 --summary-json .tmp/runtime-test-speed-workers12.json`
- `python scripts/run-runtime-tests.py --suite runtime=tests/runtime --suite service=tests/service --summary-json .tmp/runtime-test-speed-slowest-first-default4.json`
- `python scripts/run-runtime-tests.py --suite runtime=tests/runtime --suite service=tests/service --workers 8 --summary-json .tmp/runtime-test-speed-slowest-first-workers8.json`

## Key Output
- Focused runner tests: `Ran 7 tests in 1.233s`, `OK`.
- Target speed focused tests: `Ran 6 tests in 0.406s`, `OK`.
- 8-worker experiment before scheduling: `Completed 102 test files in 116.272s; failures=0`.
- 12-worker experiment before scheduling: `Completed 102 test files in 106.269s; failures=0`.
- 4-worker slowest-first experiment: `Completed 102 test files in 148.541s; failures=0`.
- 8-worker slowest-first experiment: `Completed 102 test files in 94.659s; failures=0`.
- Formal Runtime gate after implementation: `Running 102 test files with 8 workers`, `Prioritized 10 known slow test files`, `Completed 102 test files in 95.725s; failures=0`.
- Refreshed latest timing evidence: `docs/change-evidence/runtime-test-speed-latest.json` now records `worker_count=8`, `prioritized_target_count=10`, `elapsed_seconds=95.72457679999934`, and `failure_count=0`.
- Daily fast entrypoint after implementation: `.\run.ps1 fast` passed in `19.091s`; quick slice ran `50` tests in `16.703s`.
- Target-repo gate speed audit after implementation: `status=pass`, `target_count=5`, `error_count=0`, `warn_count=0`.
- `Contract` gate after implementation: passed through `OK functional-effectiveness`.
- `Docs` gate after implementation: passed through `OK post-closeout-queue-sync`.
- `doctor-runtime` after implementation: all hard checks passed; `WARN codex-capability-degraded` remains the known host boundary.

## Compatibility
- `RuntimeQuick` membership is unchanged.
- Full Runtime remains authoritative for delivery; this only changes its execution strategy.
- Explicit worker selection still wins over automatic cap selection.
- Operators can restore the older conservative behavior with `GOVERNED_RUNTIME_TEST_AUTO_WORKER_CAP=4`.
- The summary JSON remains backward compatible and only adds `timing_history_path` and `prioritized_target_count`.

## Rollback
- Revert `scripts/run-runtime-tests.py`, `tests/runtime/test_run_runtime_tests_runner.py`, and `docs/targets/target-repo-test-slicing-policy.md`.
- Or, without code rollback, set `GOVERNED_RUNTIME_TEST_AUTO_WORKER_CAP=4` to restore the old automatic worker ceiling.
