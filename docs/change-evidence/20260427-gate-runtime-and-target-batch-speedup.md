# 2026-04-27 Gate Runtime And Target Batch Speedup

## Goal

Reduce real wall-clock time for heavy local and target-repo gates without reducing coverage.

## Changes

- Added `scripts/run-runtime-tests.py`, a stdlib-only parallel unittest file runner.
- Updated `scripts/verify-repo.ps1 -Check Runtime` to run all `tests/runtime/test_*.py` and `tests/service/test_*.py` files through the parallel runner.
- Fixed `tests/runtime/test_target_repo_rollout_contract.py` to decode subprocess output as UTF-8 on Windows.
- Added `scripts/runtime-flow-preset.ps1 -TargetParallelism` for `-AllTargets -Json` runtime-flow batches. Default remains `1`.
- Added a regression test proving `-TargetParallelism 3` runs three slow target fixtures below the serial wall-clock range.

## Baseline Evidence

- Runtime gate before optimization:
  - Command: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - Result: pass
  - Wall clock: `210.306s`
  - Coverage summary: `Ran 451 tests in 208.058s`, `Ran 12 tests in 1.286s`
- Full self-runtime gate before optimization:
  - Derived from measured segments: build `1.548s` + runtime `210.306s` + contract `13.315s`
  - Approximate wall clock: `225.169s`
- All-target daily batch before target parallelism:
  - Command: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -FlowMode daily -Json -BatchTimeoutSeconds 1200 -RuntimeFlowTimeoutSeconds 300`
  - Result: `target_count=5`, `failure_count=0`
  - Wall clock: `176.808s`

## Verification Evidence

- Runtime gate after optimization:
  - Command: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - Result: pass
  - Wall clock: `66.728s`
  - Runner summary: `Completed 72 test files in 66.042s; failures=0`
- Full self-runtime gate after optimization:
  - Command: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/governance/full-check.ps1 -Json`
  - Result: pass
  - Wall clock: `81.773s`
  - Gate details: build `1292ms`, test `66157ms`, contract `13666ms`
- All-target daily batch after target parallelism:
  - Command: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -FlowMode daily -Json -TargetParallelism 3 -BatchTimeoutSeconds 1200 -RuntimeFlowTimeoutSeconds 300`
  - Result: `target_count=5`, `failure_count=0`, `batch_timed_out=false`
  - Wall clock: `72.035s`
  - Batch payload: `batch_elapsed_seconds=71`
- Focused regression:
  - Command: `python -m unittest tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_all_targets_json_supports_target_parallelism`
  - Result: pass
- Script gate:
  - Command: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`
  - Result: pass

## Effect

- Runtime gate improved from `210.306s` to `66.728s`: about `68.3%` faster.
- Full self-runtime gate improved from about `225.169s` to `81.773s`: about `63.7%` faster.
- All-target daily batch improved from `176.808s` to `72.035s`: about `59.3%` faster with `-TargetParallelism 3`.

## Remaining Hotspots

The parallel runtime runner reports the slowest test files directly. Current slowest files are:

- `tests/runtime/test_runtime_flow_preset.py`: about `35s`
- `tests/runtime/test_attached_repo_e2e.py`: about `33s`
- `tests/runtime/test_runtime_doctor.py`: about `25s`
- `tests/runtime/test_run_governed_task_cli.py`: about `21s`

Further improvement should target those files individually rather than reducing gate coverage.

## Rollback

- Revert `scripts/run-runtime-tests.py`.
- Restore `scripts/verify-repo.ps1 -Check Runtime` to direct `python -m unittest discover` calls.
- Remove `-TargetParallelism` handling from `scripts/runtime-flow-preset.ps1`.
- Revert the UTF-8 subprocess decoding fix only if Windows subprocess output is otherwise normalized.
