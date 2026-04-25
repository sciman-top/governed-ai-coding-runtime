# Codex Windows Proxy Process Environment Root Cause

## Goal

Root-cause and harden the recurring Windows/Codex process environment failures seen across target repos such as `skills-manager` and `github-toolkit`.

## Root Cause

Two related failure layers were being mixed together:

1. Reduced Windows process environments can omit canonical keys required by Python, Node, PowerShell, and `cmd.exe`, including `SystemRoot`, `WINDIR`, `ComSpec`, `APPDATA`, `LOCALAPPDATA`, `PROGRAMDATA`, and `ProgramFiles`.
2. Codex network failures such as `os error 11003` can occur when the already-running parent process does not inherit proxy variables. A reachable local proxy endpoint does not imply the current `codex.exe` parent process has `HTTP_PROXY`, `HTTPS_PROXY`, or `NO_PROXY`.

The previous hardening covered layer 1 in several entrypoints, but did not consistently import safe proxy variables from Codex `shell_environment_policy.set` or User/Machine environment, and did not document the no-hot-load behavior for existing PowerShell/Codex parent processes.

## Changes

- Extended `scripts/Initialize-WindowsProcessEnvironment.ps1` to import only safe, non-secret allowlisted variables from Codex config and User/Machine environment.
- Extended `subprocess_guard._subprocess_environment()` to normalize canonical Windows keys, expand `%SystemRoot%` registry values, and import proxy variables for child processes.
- Updated the target repo governance baseline and rollout contract so `windows_process_environment_policy` now includes inherited proxy variables and no-hot-load guidance.
- Added a runtime source guard that fails if active docs, scripts, or source files hard-code the exact Codex `.exe` executable name outside the adapter fallback and test fixtures.
- Updated the Windows environment runbook with the `os error 11003` / proxy reachability diagnosis path.
- Re-applied the updated governance baseline to all attached target repo profiles: `ClassroomToolkit`, `github-toolkit`, `self-runtime`, `skills-manager`, and `vps-ssh-launcher`.
- Hardened `D:\CODE\github-toolkit` and `D:\CODE\skills-manager` local Windows environment entrypoints directly.
- Updated `C:\Users\sciman\Documents\PowerShell\CodexProfile.ps1` so new Codex profile shells import the same safe allowlist before invoking `codex`.

## Verification

Commands run:

- `python -m unittest tests.runtime.test_subprocess_guard tests.runtime.test_target_repo_governance_consistency tests.runtime.test_target_repo_rollout_contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -Command ". .\scripts\Initialize-WindowsProcessEnvironment.ps1; Initialize-WindowsProcessEnvironment; ..."`
- `python scripts/apply-target-repo-governance.py --target-repo D:\CODE\skills-manager`
- `python scripts/apply-target-repo-governance.py --target-repo D:\CODE\github-toolkit`
- `python -m unittest test_toolkit.py` in `D:\CODE\github-toolkit`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Verify-WindowsProcessEnvironment.ps1 -Json -SkipGh` in `D:\CODE\github-toolkit`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File build.ps1` in `D:\CODE\skills-manager`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File tests\run.ps1` in `D:\CODE\skills-manager`
- `codex --version`
- `codex --help`
- `codex status`
- `codex exec '仅回复 ok' --json`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Dependency`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -ApplyGovernanceBaselineOnly -Json`
- Set User `NO_PROXY` and `no_proxy` to `localhost,127.0.0.1,::1` so future non-profile shells inherit local bypass behavior.

Results:

- Current repo targeted tests passed.
- Current repo initializer restored `HTTP_PROXY=http://127.0.0.1:10808`, `HTTPS_PROXY=http://127.0.0.1:10808`, and `NO_PROXY=localhost,127.0.0.1,::1`.
- Target governance consistency passed with five checked targets and zero drift.
- `github-toolkit` full unittest suite passed: 108 tests.
- `github-toolkit` Windows process environment verifier passed with proxy variables configured.
- `skills-manager` build passed.
- `skills-manager` Pester test suite could not run because the local Pester module is not installed; this is an environment prerequisite gap, not a code failure.
- `codex --version` returned `codex-cli 0.125.0`.
- `codex --help` completed and listed the expected command surface.
- `codex status` failed with `stdin is not a terminal`; this is recorded as Codex `platform_na` for the non-interactive shell path.
- `codex exec '仅回复 ok' --json` completed and emitted an `agent_message` with `ok`.
- Current repo hard gates passed in order: build, runtime test, contract/invariant, hotspot/doctor.
- Runtime now includes 381 tests; the added executable-name guard is part of the Runtime gate.
- Additional current repo checks passed: Docs, Scripts, Dependency, and `git diff --check`.
- Unified one-click baseline application passed for all five targets with `failure_count=0`.
- Fresh `pwsh -NoProfile` with proxy variables cleared restored `HTTP_PROXY`, `HTTPS_PROXY`, and `NO_PROXY` through the fixed initializer, then `codex exec "仅回复 ok" --json` returned `ok`.
- `github-toolkit` dry-run `python sync-forks.py --json --add-workflow --dry-run` completed with authenticated GitHub access and reported two workflow-template drift updates, not environment/DNS/proxy failures.

## Compatibility And Rollback

Compatibility:

- No public API, data schema, command contract, or target repo business behavior was changed.
- Secret-bearing variables are intentionally excluded from the import allowlist.

Rollback:

- Revert this change set with git if proxy inheritance causes unexpected local behavior.
- If only target repo profile rollout is undesirable, restore `.governed-ai/repo-profile.json` in the affected target repo to the previous git version.
