# 20260425 One-Click Rollout Hook Enforcement

## Goal
- Stop repeated drift where target-repo features are added by AI coding sessions but not integrated into the existing unified one-click rollout path.
- Move the requirement from prose-only guidance into a repo-local pre-commit control that fails closed before commit.

## Root Cause
- The canonical invariant already exists in `docs/targets/target-repo-rollout-contract.json` and is verified by `scripts/verify-target-repo-rollout-contract.py`.
- The invariant was not automatically invoked before local commits.
- The local Git config pointed `core.hooksPath` at the stale external path `E:/CODE/repo-governance-hub/hooks-global`, so this repo did not own the hook that should enforce current repo rules.
- AI agents can miss prose requirements in `AGENTS.md`; machine gates and hooks must enforce the contract instead of relying on prompt adherence.

## Changes
- Added `.githooks/pre-commit` as the repo-local Git hook entrypoint.
- Added `scripts/hooks/pre-commit.ps1` to run:
  - `scripts/verify-repo.ps1 -Check Contract`
  - `python -m unittest tests.runtime.test_codex_executable_reference_guard`
- Added `scripts/install-repo-hooks.ps1` to set local `git config core.hooksPath .githooks`.
- Added a `doctor-runtime.ps1` hotspot check for the repo-local hook files and local `core.hooksPath=.githooks`.
- Updated `.github/workflows/verify.yml` to install the repo hooks before running `verify-repo.ps1 -Check All`, so CI uses the same hook activation contract as local development.
- Updated operator-facing quickstart/readme commands to include `scripts/install-repo-hooks.ps1` before full verification.
- Added `tests/runtime/test_repo_hook_enforcement.py` so Runtime tests fail if the hook, installer, or hook guard command drift.

## Verification
- `python -m unittest tests.runtime.test_repo_hook_enforcement tests.runtime.test_codex_executable_reference_guard`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/install-repo-hooks.ps1`
- `git hook run pre-commit`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/hooks/pre-commit.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`

## Compatibility And Risk
- This does not change target-repo public APIs, schemas, or one-click command contracts.
- The hook is local to this repo after `scripts/install-repo-hooks.ps1`; other clones must run the installer once or let CI/bootstrap run it before `verify-repo -Check All`.
- The hook intentionally runs a focused contract path instead of the full build/test/hotspot chain to keep commit feedback practical.

## Rollback
- Run `git config --unset core.hooksPath` to disable the local hook path.
- Revert:
  - `.githooks/pre-commit`
  - `scripts/hooks/pre-commit.ps1`
  - `scripts/install-repo-hooks.ps1`
  - `tests/runtime/test_repo_hook_enforcement.py`
  - this evidence file and its README entry
