# 2026-04-22 Runtime Timeout Policy and Launch Config Hardening

## Goal
- Add configurable subprocess timeout controls with allowlist-based exemption.
- Enable launch snapshot strategy to accept repo-level and command-level configuration.
- Reuse resolved-path containment checks across write and repo-local path flows.

## Root Cause
- Several subprocess entry points had no timeout controls, so external command hangs could block runtime loops.
- Launch snapshot behavior was tied only to risk tier and CLI parameter, lacking repo runtime preference integration.
- Resolved-path containment checks existed in local implementations and were not consistently reused.

## Changes
- Added shared subprocess guard module:
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/subprocess_guard.py`
  - timeout parsing, allowlist-gated timeout exemption, timeout-safe subprocess execution (`exit_code=124` on timeout).
- Added shared resolved-path helpers in `file_guard.py`:
  - `is_resolved_under`
  - `ensure_resolved_under`
- Updated launch flow:
  - `run_launch_mode` now supports `timeout_seconds` and `timeout_exempt`
  - resolves snapshot mode from command payload / explicit argument / repo runtime preferences
  - emits `timed_out`, `timeout_seconds`, `timeout_exempt` in payload
  - supports repo runtime preferences from `.governed-ai/repo-profile.json`:
    - `runtime_preferences.launch_snapshot_mode`
    - `runtime_preferences.launch_timeout_seconds`
    - `runtime_preferences.subprocess_timeout_seconds`
    - `runtime_preferences.timeout_exempt_allowlist`
- Updated governed tool execution in session bridge:
  - supports timeout policy and exemption metadata in execution payload/artifacts.
- Added configurable gate timeout surface for shell-gate wrappers:
  - env: `GOVERNED_GATE_TIMEOUT_SECONDS` for
    - `scripts/run-governed-task.py`
    - `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
    - `packages/contracts/src/governed_ai_coding_runtime_contracts/multi_repo_trial.py`
- Added Codex probe timeout hardening:
  - env: `GOVERNED_CODEX_PROBE_TIMEOUT_SECONDS` (default 20s) in `codex_adapter.py`.
- Added CLI passthrough args in `scripts/session-bridge.py`:
  - `launch`: `--timeout-seconds`, `--timeout-exempt`
  - `write-execute`: `--timeout-seconds`, `--timeout-exempt`
- Reused shared resolved-path guard in:
  - `attached_write_execution.py`
  - `repo_attachment.py`

## Tests
- Added/updated tests:
  - `tests/runtime/test_tool_runner.py`
    - timeout behavior
    - allowlist-gated timeout exemption
  - `tests/runtime/test_session_bridge.py`
    - repo-driven launch snapshot mode
    - launch timeout behavior
    - timeout exemption deny/allowlist behavior

## Verification
1. `python -m unittest tests.runtime.test_tool_runner`
2. `python -m unittest tests.runtime.test_session_bridge`
3. `python -m unittest tests.runtime.test_run_governed_task_service_wrapper`
4. `python -m unittest tests.runtime.test_multi_repo_trial`
5. `python -m unittest tests.runtime.test_codex_adapter`
6. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
7. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
8. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
9. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

All commands passed.

## Compatibility
- No schema/catalog contract changes.
- No new third-party dependencies.
- Timeout controls are opt-in unless runtime preferences/env variables are set.

## Rollback
- Revert the changed files in this slice, then rerun:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
