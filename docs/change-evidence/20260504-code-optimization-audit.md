# 2026-05-04 Code Optimization Audit

## Goal
- Current landing: `D:\CODE\governed-ai-coding-runtime`.
- Target home: runtime contract, host-environment robustness, and governed gate execution in `packages/contracts`.
- Verification: `build -> Runtime -> Contract -> doctor` using the repository hard-gate order.

## Baseline
- `git status --short --branch`: clean `main...origin/main` before changes.
- `.\run.ps1 fast`: pass; `build` plus `RuntimeQuick`, 53 tests in about 23 seconds.
- `python scripts/select-next-work.py --repo-root .`: pass; `next_action=wait_for_host_capability_recovery`, `ltp_decision=defer_all`.
- `python scripts/verify-evidence-recovery-posture.py --repo-root . --as-of 2026-05-04`: pass; host capability remains a bounded defer, not a trigger for new LTP implementation.

## Findings
- `subprocess_guard.py` inherited `ComSpec` from the ambient environment or Codex `shell_environment_policy.set`. For Windows `shell=True` execution this made the shell executable part of mutable local state instead of canonical host state.
- Governed gate execution was duplicated across `session_bridge.py`, `multi_repo_trial.py`, and `run-governed-task.py`, including timeout lookup, subprocess invocation, and stdout/stderr merging.
- Main maintainability hotspots are large mixed-responsibility files: `operator_ui.py`, `session_bridge.py`, `runtime-flow-preset.ps1`, and their paired large tests. These should be split in bounded slices, not in one broad rewrite.
- Runtime test speed is serviceable but still concentrated in a small slow set. The latest full runtime gate completed in about 128 seconds; slowest files include `test_runtime_flow_preset.py`, `test_attached_repo_e2e.py`, `test_autonomous_next_work_selection.py`, and `test_run_governed_task_cli.py`.
- Repository slimming evidence still shows `docs/change-evidence` and operator UI screenshots as the largest visible surface. Archive/delete work remains forbidden by default unless a dedicated dry-run, backup, and rollback slice is opened.

## Changes
- Removed `ComSpec` from Codex shell-policy inherited safe keys.
- Canonicalized Windows `SystemRoot`, `WINDIR`, and `ComSpec` after environment merge.
- Added regression coverage proving that neither Codex shell policy nor existing process environment can redirect governed Windows shell execution away from `System32\cmd.exe`.
- Added `run_governed_gate_command()` as the shared gate execution helper in `subprocess_guard.py`.
- Replaced duplicate governed gate execution paths in `session_bridge.py`, `multi_repo_trial.py`, and `scripts/run-governed-task.py`.
- Added helper regression coverage for stdout/stderr merge behavior and `GOVERNED_GATE_TIMEOUT_SECONDS` timeout handling.

## Verification
- `python -m unittest tests.runtime.test_subprocess_guard -v`: pass, 7 tests.
- `python -m unittest tests.runtime.test_subprocess_guard tests.runtime.test_tool_runner tests.runtime.test_session_bridge -v`: pass, 69 tests.
- `python -m unittest tests.runtime.test_subprocess_guard tests.runtime.test_multi_repo_trial tests.runtime.test_session_bridge tests.runtime.test_run_governed_task_cli -v`: pass, 70 tests.
- `python -m py_compile packages\contracts\src\governed_ai_coding_runtime_contracts\subprocess_guard.py packages\contracts\src\governed_ai_coding_runtime_contracts\session_bridge.py packages\contracts\src\governed_ai_coding_runtime_contracts\multi_repo_trial.py scripts\run-governed-task.py tests\runtime\test_subprocess_guard.py`: pass.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`: pass.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`: pass, 104 test files, failures=0.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`: pass.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`: pass with existing `codex-capability-degraded` warning.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`: pass.
- `git diff --check`: pass; Git emitted only existing LF-to-CRLF working-copy warnings for edited files.

## Rollback
- `git restore packages/contracts/src/governed_ai_coding_runtime_contracts/subprocess_guard.py packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py packages/contracts/src/governed_ai_coding_runtime_contracts/multi_repo_trial.py scripts/run-governed-task.py tests/runtime/test_subprocess_guard.py docs/change-evidence/20260504-code-optimization-audit.md docs/change-evidence/runtime-test-speed-latest.json`

## Next Task List
1. AI recommendation: split `operator_ui.py` into translation, style/script, and renderer modules.
   - Reason: this is the next largest mixed-responsibility hotspot after gate execution consolidation.
   - Acceptance: generated HTML is equivalent for static snapshots, interactive smoke tests still pass, and bilingual keys remain complete.
2. Reduce slow runtime tests by fixture reuse and narrower subprocess work.
   - Acceptance: before/after `runtime-test-speed-latest.json` shows improvement without weakening coverage.
3. Turn the current static shell-risk scan into a deterministic contract check.
   - Acceptance: unguarded `shell=True`, destructive PowerShell file operations, and unbounded `Start-Process` patterns fail with allowlisted exceptions.
4. Keep repo-slimming cleanup separate.
   - Acceptance: archive/delete only starts with catalog, dry-run, backup, and rollback evidence; no broad deletion in optimization slices.
