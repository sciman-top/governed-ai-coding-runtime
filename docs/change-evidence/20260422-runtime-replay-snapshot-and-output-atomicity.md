# 2026-04-22 Runtime replay / snapshot / output atomicity hardening

## Goal
- Continue the runtime hardening work without changing external behavior.
- Close the remaining replay-path traversal gap.
- Remove the last direct overwrite writes on generated runtime outputs.
- Reduce the `process_bridge` same-size / restored-`mtime` change-miss risk.

## Basis
- Prior hardening already covered task, approval, artifact, context pack, and metrics state files, but generated outputs still had a few direct `write_text()` call sites.
- `scripts/run-governed-task.py::_write_replay_case()` still composed a filename from `task_id` and `run_id` without validating file-safe path segments.
- `session_bridge.run_launch_mode()` had been optimized to metadata-only snapshots, which improved scan cost but left an extreme false-negative window when file content changed while both size and `mtime_ns` were preserved.
- Package metadata / lockfile remains intentionally deferred by repository policy: `packages/README.md` states package-manager metadata should only be added with explicit dependency and supply-chain evidence.

## Changes
- Added a symlink-preserving fallback in `atomic_write_text()` so generated outputs can adopt atomic writes without changing symlink write-through behavior.
- Switched these generated outputs to `atomic_write_text()`:
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py`
  - `scripts/export-target-repo-speed-kpi.py`
  - `scripts/run-governed-task.py::_write_replay_case()`
- Added `validate_file_component()` checks for replay-case `task_id` / `run_id` before they are used in the replay filename.
- Updated `session_bridge._file_snapshot()` to use `size + mtime_ns + lightweight content signature`:
  - full content digest for smaller files
  - sampled digest for larger files
  - still compatible with `snapshot_scope`

## Commands
- `python -m unittest tests.runtime.test_operator_ui tests.runtime.test_target_repo_speed_kpi tests.runtime.test_run_governed_task_service_wrapper tests.runtime.test_session_bridge`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
- Snapshot micro-benchmark:
  - inline Python benchmark over 300 files x 1 KiB
  - compared `full_hash`, `metadata_only`, and current `hybrid_signature`

## Evidence
- Targeted regression:
  - `52` tests passed
  - Added coverage for:
    - restored-`mtime` same-size rewrites in `session_bridge`
    - unsafe replay `task_id` rejection in `run-governed-task`
- Full gate order:
  - `build`: passed
  - `test`: passed, `312` runtime tests + `5` service parity tests
  - `contract/invariant`: passed
  - `hotspot`: passed
- Snapshot benchmark result:
  - `metadata_only`: `14.52 ms`
  - `hybrid_signature`: `50.90 ms`
  - `full_hash`: `45.58 ms`

## Interpretation
- The launch snapshot now covers the previous metadata-only false-negative case for small files and for sampled regions of larger files.
- The cost is intentionally higher than metadata-only snapshots; `snapshot_scope` remains the primary control for bounding launch-mode scan cost on large worktrees.
- The replay filename path guard is a root-cause fix, not a surface-only mitigation.
- Dependency governance was reviewed again and intentionally not auto-modified because doing so would conflict with the repository's current evidence-first package-metadata rule.

## Rollback
- Revert this slice by restoring:
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/file_guard.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
  - `scripts/export-target-repo-speed-kpi.py`
  - `scripts/run-governed-task.py`
  - `tests/runtime/test_run_governed_task_service_wrapper.py`
  - `tests/runtime/test_session_bridge.py`
- Rollback path: git history for this working tree; no schema/data migration involved.
