# 2026-05-04 Code Optimization Audit

## Goal
- Current landing: `D:\CODE\governed-ai-coding-runtime`.
- Target home: runtime contract, host-environment robustness, governed gate execution, operator UI modularity, and runtime test speed in `packages/contracts` and `tests/runtime`.
- Verification: `build -> Runtime -> Contract -> doctor` using the repository hard-gate order.

## Baseline
- `git status --short --branch`: clean `main...origin/main` before changes.
- `.\run.ps1 fast`: pass; `build` plus `RuntimeQuick`, 53 tests in about 23 seconds.
- `python scripts/select-next-work.py --repo-root .`: pass; `next_action=wait_for_host_capability_recovery`, `ltp_decision=defer_all`.
- `python scripts/verify-evidence-recovery-posture.py --repo-root . --as-of 2026-05-04`: pass; host capability remains a bounded defer, not a trigger for new LTP implementation.

## Findings
- `subprocess_guard.py` inherited `ComSpec` from the ambient environment or Codex `shell_environment_policy.set`. For Windows `shell=True` execution this made the shell executable part of mutable local state instead of canonical host state.
- Governed gate execution was duplicated across `session_bridge.py`, `multi_repo_trial.py`, and `run-governed-task.py`, including timeout lookup, subprocess invocation, and stdout/stderr merging.
- Main maintainability hotspots were large mixed-responsibility files: `operator_ui.py`, `session_bridge.py`, `runtime-flow-preset.ps1`, and their paired large tests. `operator_ui.py` has now been split into bounded renderer, text, style, and script modules; remaining hotspot work should continue in similarly bounded slices.
- Runtime test speed is improved but still concentrated in a small slow set. The latest full runtime gate completed in about 97 seconds, down from about 123 seconds before the test-speed slice. Remaining slowest files include `test_runtime_flow_preset.py`, `test_attached_repo_e2e.py`, `test_dependency_baseline.py`, and `test_transition_stack_convergence.py`.
- Repository slimming evidence still shows `docs/change-evidence` and operator UI screenshots as the largest visible surface. Archive/delete work remains forbidden by default unless a dedicated dry-run, backup, and rollback slice is opened.

## Changes
- Removed `ComSpec` from Codex shell-policy inherited safe keys.
- Canonicalized Windows `SystemRoot`, `WINDIR`, and `ComSpec` after environment merge.
- Added regression coverage proving that neither Codex shell policy nor existing process environment can redirect governed Windows shell execution away from `System32\cmd.exe`.
- Added `run_governed_gate_command()` as the shared gate execution helper in `subprocess_guard.py`.
- Replaced duplicate governed gate execution paths in `session_bridge.py`, `multi_repo_trial.py`, and `scripts/run-governed-task.py`.
- Added helper regression coverage for stdout/stderr merge behavior and `GOVERNED_GATE_TIMEOUT_SECONDS` timeout handling.
- Split `operator_ui.py` into `operator_ui_text.py`, `operator_ui_style.py`, `operator_ui_script.py`, and the remaining main renderer.
- Preserved exact HTML output for zh-CN static, en static, and zh-CN interactive representative snapshots when compared to the pre-split `HEAD` renderer.
- Synced operator UI stale-source detection in `serve-operator-ui.py` and `operator-ui-service.ps1` so changes to split UI modules trigger the same restart/stale-content protection.
- Added a translation key parity regression test for `zh-CN` and `en`.
- Narrowed `test_run_governed_task_cli` to a temporary fast repo profile and mocked Codex capability in the `run_task` path; the file now runs in about 3.5 seconds locally instead of about 35 seconds.
- Forced attached repo e2e subprocesses through the explicit missing-Codex fallback path, preserving fallback assertions while avoiding repeated real host probes.
- Changed `select-next-work.py` to skip the expensive auto-detection chain when `gate_state`, `source_state`, and `evidence_state` are all supplied explicitly.
- Added a regression test proving explicit selector inputs do not call `_auto_detect_runtime_inputs`.

## Verification
- `python -m unittest tests.runtime.test_subprocess_guard -v`: pass, 7 tests.
- `python -m unittest tests.runtime.test_subprocess_guard tests.runtime.test_tool_runner tests.runtime.test_session_bridge -v`: pass, 69 tests.
- `python -m unittest tests.runtime.test_subprocess_guard tests.runtime.test_multi_repo_trial tests.runtime.test_session_bridge tests.runtime.test_run_governed_task_cli -v`: pass, 70 tests.
- `python -m unittest tests.runtime.test_operator_ui tests.runtime.test_operator_entrypoint -v`: pass, 37 tests.
- `python -m unittest tests.runtime.test_run_governed_task_cli -v`: pass, 9 tests in about 3.5 seconds.
- `python -m unittest tests.runtime.test_attached_repo_e2e -v`: pass, 5 tests in about 34 seconds.
- `python -m unittest tests.runtime.test_autonomous_next_work_selection -v`: pass, 8 tests in about 19.5 seconds.
- `python -m unittest tests.runtime.test_run_governed_task_cli tests.runtime.test_attached_repo_e2e tests.runtime.test_autonomous_next_work_selection -v`: pass, 22 tests in about 53.4 seconds.
- Pre-split vs post-split HTML exact comparison: pass for `empty-zh-static`, `empty-en-static`, and `full-zh-interactive`.
- `python -m py_compile packages\contracts\src\governed_ai_coding_runtime_contracts\subprocess_guard.py packages\contracts\src\governed_ai_coding_runtime_contracts\session_bridge.py packages\contracts\src\governed_ai_coding_runtime_contracts\multi_repo_trial.py scripts\run-governed-task.py tests\runtime\test_subprocess_guard.py`: pass.
- `python -m py_compile packages\contracts\src\governed_ai_coding_runtime_contracts\operator_ui.py packages\contracts\src\governed_ai_coding_runtime_contracts\operator_ui_text.py packages\contracts\src\governed_ai_coding_runtime_contracts\operator_ui_style.py packages\contracts\src\governed_ai_coding_runtime_contracts\operator_ui_script.py scripts\serve-operator-ui.py tests\runtime\test_operator_ui.py tests\runtime\test_operator_entrypoint.py`: pass.
- `python -m py_compile scripts\select-next-work.py tests\runtime\test_autonomous_next_work_selection.py tests\runtime\test_attached_repo_e2e.py tests\runtime\test_run_governed_task_cli.py`: pass.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`: pass.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`: pass, 104 test files, failures=0.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`: pass.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`: pass with existing `codex-capability-degraded` warning.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`: pass.
- `git diff --check`: pass; Git emitted only existing LF-to-CRLF working-copy warnings for edited files.

## Rollback
- Before commit: `git restore packages/contracts/src/governed_ai_coding_runtime_contracts/subprocess_guard.py packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py packages/contracts/src/governed_ai_coding_runtime_contracts/multi_repo_trial.py packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py scripts/run-governed-task.py scripts/serve-operator-ui.py scripts/operator-ui-service.ps1 scripts/select-next-work.py tests/runtime/test_subprocess_guard.py tests/runtime/test_operator_ui.py tests/runtime/test_operator_entrypoint.py tests/runtime/test_run_governed_task_cli.py tests/runtime/test_attached_repo_e2e.py tests/runtime/test_autonomous_next_work_selection.py docs/change-evidence/20260504-code-optimization-audit.md docs/change-evidence/runtime-test-speed-latest.json`; then remove the new split modules `operator_ui_script.py`, `operator_ui_style.py`, and `operator_ui_text.py`.
- After commit: `git revert <commit-sha>`.

## Next Task List
1. AI recommendation: turn the current static shell-risk scan into a deterministic contract check.
   - Acceptance: unguarded `shell=True`, destructive PowerShell file operations, and unbounded `Start-Process` patterns fail with allowlisted exceptions.
2. Keep repo-slimming cleanup separate.
   - Acceptance: archive/delete only starts with catalog, dry-run, backup, and rollback evidence; no broad deletion in optimization slices.
