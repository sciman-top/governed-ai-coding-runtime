# Windows process environment PATH hardening

## Goal
- Prevent all-target one-click rollout and target-repo gate execution from misdiagnosing missing `git`, `gh`, Python, Node, or PowerShell when Codex starts with a stripped Windows process environment.

## Changes
- Added `ProgramFiles` to the Windows process environment policy and doctor required-variable check.
- Extended `scripts/Initialize-WindowsProcessEnvironment.ps1` to restore default Windows system paths plus default Git and GitHub CLI install paths into the process `PATH`.
- Extended Python subprocess normalization to propagate the same `ProgramFiles` and PATH hardening to child processes.

## Verification
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

## Rollback
- Revert this commit to restore the previous required-variable set and PATH normalization behavior.
