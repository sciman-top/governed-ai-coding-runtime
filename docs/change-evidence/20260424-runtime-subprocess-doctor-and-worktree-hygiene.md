# 20260424 Runtime Subprocess, Doctor, And Worktree Hygiene

## Goal
- Review and harden the current runtime code without changing public contracts, data formats, or target-repo rollout semantics.
- Keep the fix small and verifiable: process execution robustness, tool-runner CLI correctness, and repository hygiene.

## Baseline
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1` -> pass (`OK python-bytecode`, `OK python-import`)
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` -> pass (`Ran 366 tests`, plus 5 service checks)
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` -> pass (`OK dependency-baseline`, `OK target-repo-governance-consistency`)
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1` -> pass with `WARN codex-capability-blocked` before the fix
- Raw `codex --version`, `codex --help`, and `codex status` initially failed in this shell because `SystemRoot/ComSpec/WINDIR` were absent; after explicit shell env initialization:
  - `codex --version` -> `codex-cli 0.124.0`
  - `codex --help` -> pass
  - `codex status` -> `platform_na`, `Error: stdin is not a terminal`

## Main Issues
1. `apps/tool-runner/main.py` attempted to emit `result.command`, but `ToolExecutionResult` has no `command` field. The CLI could execute the child process and still crash before emitting structured output.
2. `run_subprocess(..., shell=True)` passed a normalized `env`, but Windows/Python shell lookup can still depend on parent-process `ComSpec/SystemRoot`. In stripped shells this raised `FileNotFoundError: shell not found`.
3. `scripts/doctor-runtime.ps1` did not initialize the Windows process environment even though adjacent runtime scripts already did. This could misclassify Codex capability as blocked.
4. Local Visual Studio state under `.vs/` was tracked in git, including binary index/state files.

## Changes
- `packages/contracts/src/governed_ai_coding_runtime_contracts/subprocess_guard.py`
  - Reuses the normalized subprocess environment and passes `executable=$ComSpec` for Windows `shell=True` calls.
- `apps/tool-runner/main.py`
  - Emits the input command and timeout metadata in structured JSON instead of reading a non-existent result field.
- `scripts/doctor-runtime.ps1`
  - Adds the same Windows environment initialization used by other runtime PowerShell entrypoints.
- `.gitignore`
  - Ignores `.vs/` and common Visual Studio user-state files.
- Tests
  - Added `tests/runtime/test_subprocess_guard.py`.
  - Extended `tests/runtime/test_tool_runner_governance.py`.
  - Extended `tests/runtime/test_runtime_doctor.py`.
- Repository hygiene
  - Removed tracked `.vs/` files from the worktree/index.

## Verification
- `python -m unittest tests.runtime.test_subprocess_guard tests.runtime.test_tool_runner_governance -v` -> pass (`Ran 6 tests`)
- `python apps/tool-runner/main.py --command 'python -c "print(''tool-cli-ok'')"'` -> pass, structured JSON output
- `python -m unittest tests.runtime.test_runtime_doctor.RuntimeBuildAndDoctorScriptTests.test_doctor_runtime_script_succeeds tests.runtime.test_runtime_doctor.RuntimeBuildAndDoctorScriptTests.test_doctor_runtime_initializes_windows_process_environment -v` -> pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1` -> pass (`OK python-bytecode`, `OK python-import`)
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` -> pass (`Ran 369 tests`, plus 5 service checks)
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` -> pass (`OK dependency-baseline`, `OK target-repo-governance-consistency`)
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1` -> pass with `OK codex-capability-ready`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts` -> pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs` -> pass

## Risk And Rollback
- Risk: low. The subprocess change only adds an explicit shell executable when `shell=True` on Windows and a normalized `ComSpec` exists.
- Risk: low. Tool-runner JSON output is additive for timeout fields and fixes an existing crash.
- Rollback: revert this evidence file plus `.gitignore`, `apps/tool-runner/main.py`, `scripts/doctor-runtime.ps1`, `subprocess_guard.py`, and the added/updated tests. Restore `.vs/` tracking only if local IDE state is intentionally part of the repository, which it should not be for this project.
