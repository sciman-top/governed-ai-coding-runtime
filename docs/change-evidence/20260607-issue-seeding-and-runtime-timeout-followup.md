# 2026-06-07 issue seeding and runtime timeout follow-up

- rule_id: issue_seeding_and_runtime_timeout_followup
- risk_level: medium
- current_landing: `scripts/github/create-roadmap-issues.ps1`, `scripts/run-runtime-tests.py`, `tests/runtime/test_issue_seeding.py`, `tests/runtime/test_run_runtime_tests_runner.py`, `docs/targets/target-repo-test-slicing-policy.md`, `docs/change-evidence/runtime-test-speed-latest.json`
- target_destination: keep conditional follow-up queue accounting explicit in issue-render validation output and restore a passing full `Runtime` gate by raising the default self-runtime per-file timeout to match observed suite latency
- rollback: revert the listed files from git and rerun `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Runtime`

## Why

- `create-roadmap-issues.ps1 -ValidateOnly -RenderAll` correctly skipped conditionally inactive `GAP-165..168` tasks for issue creation, but `tests.runtime.test_issue_seeding` still assumed every non-complete task should be rendered for creation. That drift surfaced as `rendered_issue_creation_tasks = 0` versus an expected value of `4`.
- The full `Runtime` gate timed out three test files at the default 300-second per-file limit even though the same files still passed when run with a 600-second cap. This made `verify-repo.ps1 -Check Runtime` fail on timeout pressure rather than assertion failures.

## Changes

- Added `conditionally_inactive_task_count` to the validate-only summary emitted by `scripts/github/create-roadmap-issues.ps1`.
- Updated issue-seeding tests so creation-task expectations exclude conditionally inactive backlog items and added a render check for `GAP-165` conditional follow-up wording.
- Raised `scripts/run-runtime-tests.py` default per-file timeout from `300` to `600` seconds and updated the runner test plus operator-facing slicing policy doc to match.
- Refreshed `docs/change-evidence/runtime-test-speed-latest.json` with a passing full-suite run under the new timeout budget.

## Verification

- Focused regression before the fix:
  - `python -m unittest tests.runtime.test_issue_seeding.IssueSeedingScriptTests.test_validate_only_render_all_checks_all_issue_body_sources`
  - result: fail with `AssertionError: 0 != 4`, proving the conditional queue accounting drift.
- Focused post-fix tests:
  - `python -m unittest tests.runtime.test_run_runtime_tests_runner`
  - `python -m unittest tests.runtime.test_issue_seeding`
  - result: both pass.
- Timeout diagnosis:
  - `python scripts\run-runtime-tests.py --suite runtime=tests/runtime --pattern test_functional_effectiveness.py --workers 1 --timeout-seconds 600`
  - `python scripts\run-runtime-tests.py --suite runtime=tests/runtime --pattern test_dependency_baseline.py --workers 1 --timeout-seconds 600`
  - `python scripts\run-runtime-tests.py --suite runtime=tests/runtime --pattern test_target_repo_powershell_policy.py --workers 1 --timeout-seconds 600`
  - result: all three pass; observed durations were approximately `327s`, `327s`, and `286s`, confirming the previous `300s` default was too tight for the current suite.
- Full gate after the fix:
  - build: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\build-runtime.ps1`
  - test: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Runtime`
  - contract/invariant: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Contract`
  - hotspot: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\doctor-runtime.ps1`
  - supplementary scripts check: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Scripts`
  - result: all pass; `doctor-runtime` retains the existing `WARN codex-capability-degraded` hint only.

## Compatibility and Risk

- Issue rendering remains non-mutating; the new summary field only makes the skipped conditional queue explicit.
- The runtime test runner still honors explicit `--timeout-seconds` and `GOVERNED_RUNTIME_TEST_TIMEOUT_SECONDS` overrides. Raising the default to `600` seconds widens headroom for slow but valid test files without changing test selection semantics.
- No schema, target-repo governance baseline, auth, provider, or host-owned state behavior was changed.

## Rollback

1. Revert the listed control-repo files from git.
2. Re-run:
   - `python -m unittest tests.runtime.test_issue_seeding`
   - `python -m unittest tests.runtime.test_run_runtime_tests_runner`
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Runtime`
3. If the timeout budget must be revisited again, use the refreshed `docs/change-evidence/runtime-test-speed-latest.json` slow-file list as the source of truth instead of guessing a smaller cap.
