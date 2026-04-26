# 20260426 Target Repo Pwsh Local Guard

## Goal
- Prevent target repos from repeatedly regressing from `pwsh` / PowerShell 7 back to direct normal-path `powershell` / `powershell.exe` invocations.
- Make the prevention part of the existing one-click target governance application path, not a manual reminder.

## Changes
- Added `required_managed_files` to `docs/targets/target-repo-governance-baseline.json` with sync revision `2026-04-26.1`.
- Added `docs/targets/templates/verify-powershell-policy.py` as the managed repo-local guard.
- Updated `scripts/apply-target-repo-governance.py` to sync managed files and report `changed_managed_files`.
- Updated `scripts/verify-target-repo-governance-consistency.py` to fail on managed-file drift.
- Added runtime tests for managed-file apply and drift detection.

## Commands And Evidence
- `python -m unittest tests.runtime.test_target_repo_governance_consistency tests.runtime.test_target_repo_powershell_policy`
  - result: pass, 8 tests
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -ApplyGovernanceBaselineOnly -Json`
  - result: pass, 5 targets, `failure_count=0`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - result: pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - result: pass, 388 runtime tests with 2 skipped, 10 service tests
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - result: pass, including `target-repo-governance-consistency` and `target-repo-powershell-policy`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  - result: pass
- `python .governed-ai\verify-powershell-policy.py`
  - result: pass in `governed-ai-coding-runtime`
- `python .governed-ai\verify-powershell-policy.py`
  - result: pass in `D:\CODE\skills-manager`

## Target Sync
- One-click baseline sync wrote or refreshed `.governed-ai/verify-powershell-policy.py` for active catalog targets.
- Observed untracked guard files after sync:
  - `D:\CODE\governed-ai-coding-runtime\.governed-ai\verify-powershell-policy.py`
  - `D:\CODE\github-toolkit\.governed-ai\verify-powershell-policy.py`
  - `D:\CODE\skills-manager\.governed-ai\verify-powershell-policy.py`
  - `D:\CODE\vps-ssh-launcher\.governed-ai\verify-powershell-policy.py`
- `D:\CODE\ClassroomToolkit\.governed-ai\verify-powershell-policy.py` exists; its repo status did not show an untracked file in the sampled status output.

## Rollback
- Revert the baseline `required_managed_files` entry and sync revision.
- Revert changes to `scripts/apply-target-repo-governance.py` and `scripts/verify-target-repo-governance-consistency.py`.
- Re-run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -ApplyGovernanceBaselineOnly -Json` if target profiles/files need to be restored to the previous baseline.
