# 20260425 Pwsh-First Target Repo Policy

## Goal
- Stop recurring Windows PowerShell 5.1 misrouting in Codex/Claude coding sessions.
- Make PowerShell 7 / `pwsh` the default for target-repo CI, script wrappers, and child PowerShell invocations.
- Keep intentional Windows PowerShell 5.1 fallback explicit and auditable.

## Root Cause
- The existing Windows process environment hardening fixed missing variables and proxy inheritance, but the target-repo policy did not yet encode `pwsh` as the preferred shell.
- Several target repos still had CI YAML or scripts that directly invoked `powershell` / `powershell.exe`, causing agents to infer or execute Windows PowerShell 5.1 even on a machine where PowerShell 7 is available.

## Changes
- Updated `docs/targets/target-repo-governance-baseline.json`:
  - `preferred_powershell_executable`: `pwsh`
  - `fallback_powershell_executable`: `powershell`
  - `windows_powershell_escape_hatch_env`: `CODEX_ALLOW_WINDOWS_POWERSHELL`
  - guidance requiring `pwsh` / PowerShell 7 first in CI, `.cmd` wrappers, and child process calls
- Updated current runtime environment normalization so `PowerShell\7` is restored into `PATH` before Windows PowerShell 5.1.
- Updated target repo CI/script entrypoints in:
  - `D:\CODE\skills-manager`
  - `D:\CODE\ClassroomToolkit`
  - `D:\CODE\github-toolkit` environment initializer
- Added `scripts/verify-target-repo-powershell-policy.py` and wired it into `verify-repo.ps1 -Check Contract`, so active target repos fail the Contract gate if CI/scripts directly invoke Windows PowerShell 5.1.
- Re-applied the updated governance baseline to all active targets through the unified one-click baseline path.

## Verification
- `python -m unittest tests.runtime.test_target_repo_governance_consistency tests.runtime.test_runtime_doctor`
- `python -m unittest tests.runtime.test_target_repo_powershell_policy`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -ApplyGovernanceBaselineOnly -Json`
- Target repo source scans for direct normal-path `powershell` / `powershell.exe` invocations in CI and scripts.

## Compatibility And Risk
- Normal execution now prefers `pwsh`; Windows PowerShell 5.1 fallback remains available only when `pwsh` is unavailable or `CODEX_ALLOW_WINDOWS_POWERSHELL=1` is explicitly set in wrapper helpers.
- Comments, documentation text, and intentional fallback strings are not treated as direct execution regressions.

## Rollback
- Revert this evidence file and its README entry.
- Revert `docs/targets/target-repo-governance-baseline.json`, `docs/targets/target-repo-rollout-contract.json`, and the target repo CI/script edits.
- Re-run `scripts/runtime-flow-preset.ps1 -AllTargets -ApplyGovernanceBaselineOnly -Json` to restore the previous target profile baseline if needed.
