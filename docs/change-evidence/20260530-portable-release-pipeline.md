# 2026-05-30 Portable Release Pipeline

## Goal
Add a one-command portable release package and a new-machine initialization path for the governed runtime.

## Scope
- `scripts/package-runtime.ps1`
- `release.ps1`
- `install.ps1`
- `tests/runtime/test_package_runtime.py`
- `scripts/run-runtime-tests.py`
- `tests/runtime/test_run_runtime_tests_runner.py`
- `scripts/verify-shell-risk-contract.py`
- `README.md`, `README.zh-CN.md`, `README.en.md`, `docs/README.md`
- `docs/product/public-usable-release-criteria.md`
- `docs/product/public-usable-release-criteria.zh-CN.md`
- `docs/targets/target-repo-test-slicing-policy.md`

## Rule Mapping
- `R1`: current landing point is the control repo; target destination is a portable release artifact plus host-local install state.
- `R4`: release packaging is low-risk; user/global rule sync and hooks remain opt-in install flags.
- `R6`: verification followed `build -> test -> contract/invariant -> hotspot`.
- `R8`: commands, key output, compatibility, and rollback are recorded below.
- `E5`: release provenance and SHA256 are emitted with the archive.
- `E6`: no runtime state schema migration; the package excludes machine-local runtime state.

## Changes
- Added `release.ps1` as the short one-command packaging entrypoint.
- Added `install.ps1` with `Portable` and `User` modes, `DryRun`, optional `SyncRules`, optional `InstallHooks`, and optional `OpenUi`.
- Upgraded `scripts/package-runtime.ps1` to emit:
  - `.runtime/dist/public-usable-release/`
  - `.runtime/dist/releases/governed-ai-runtime-<version>-portable.zip`
  - `.manifest.json`
  - `.zip.sha256`
  - `.provenance.json`
- Added release allowlist behavior that includes source, contracts, rules, scripts, schemas, docs, tests, hooks, and root entrypoints.
- Excluded `.runtime`, temporary folders, historical evidence, archives, user homes, credentials, provider settings, and target repo working trees.
- Added release-output containment checks before package cleanup deletes generated files.
- Added filename-safe release version validation before archive paths are created.
- Made `scripts/package-runtime.ps1` resolve the repo root from the script path, so `release.ps1` works even when called from another current directory.
- Updated shell-risk allowlist for the bounded package cleanup commands.
- Hardened `scripts/run-runtime-tests.py` to serialize known runtime tests that nest the full `Contract` gate, after the default 8-worker full Runtime gate exposed resource-contention timeouts.

## Commands
```powershell
python -m unittest tests.runtime.test_package_runtime
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File release.ps1 -Version 0.1.0-test -Channel portable
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File install.ps1 -Mode Portable -DryRun
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File install.ps1 -Mode Portable -RuntimeRoot .runtime/install-smoke
```

```powershell
python -m unittest tests.runtime.test_shell_risk_contract tests.runtime.test_package_runtime
```

```powershell
python -m unittest tests.runtime.test_run_runtime_tests_runner
```

```powershell
python scripts/verify-shell-risk-contract.py --json
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check DocsLinks
```

## Key Output
- `release.ps1 -Version 0.1.0-test -Channel portable`: emitted `governed-ai-runtime-0.1.0-test-portable.zip`, manifest, SHA256, and provenance.
- `release.ps1` from a temporary current directory: emitted release outputs under the repo-local `.runtime/dist/releases`.
- `release.ps1 -Version '..\escape'`: rejected before archive path creation with `Invalid release version`.
- `install.ps1 -Mode Portable -DryRun`: reported package-local `.runtime` paths and skipped rule sync/hooks.
- `install.ps1 -Mode Portable -RuntimeRoot .runtime/install-smoke`: created isolated runtime roots and wrote `install-state.json`.
- `verify-shell-risk-contract.py --json`: `status=pass`, `finding_count=0`, `stale_allowlist_count=0`.
- First `verify-repo.ps1 -Check Runtime`: failed by timeout only, with `test_functional_effectiveness`, `test_transition_stack_convergence`, and `test_dependency_baseline` each killed at `300s` while nested `Contract` gates ran concurrently.
- Final `verify-repo.ps1 -Check Runtime`: completed 112 test files with `failures=0`, `worker_count=8`, `serial_target_count=3`, `elapsed_seconds=903.733`.
- `verify-repo.ps1 -Check Contract`: passed, including `shell-risk-contract`, `agent-rule-sync`, and `functional-effectiveness`.
- `doctor-runtime.ps1`: passed with existing `WARN codex-capability-degraded`.
- `verify-repo.ps1 -Check DocsLinks`: passed with `OK active-markdown-links`.

## Compatibility
- Compatibility class: `compatible_with_note`.
- Existing `scripts/package-runtime.ps1` remains callable with default parameters.
- New `release.ps1` is a convenience wrapper over `scripts/package-runtime.ps1`.
- `install.ps1 -Mode Portable` initializes only package-local runtime state by default.
- `install.ps1 -Mode User`, `-SyncRules`, and `-InstallHooks` are explicit operator choices.
- Runtime gate compatibility note: default 8-worker execution is preserved for ordinary files, while known nested-Contract test files run serially to avoid false timeout failures.

## Migration Boundary
Portable release packages carry generic repo content and governance contracts only.

They do not carry:
- `.runtime` task/artifact/replay state
- credentials or auth files
- Codex/Claude/Gemini provider settings
- Cockpit Tools or CC Switch state
- target repo working trees
- historical target-run evidence

On a new computer, target repos and global/user rules must be attached or synced again after host tools and accounts are configured.

## Rollback
- Delete generated release outputs under `.runtime/dist/public-usable-release/` and `.runtime/dist/releases/`.
- Remove `install.ps1` and `release.ps1`.
- Revert changes to `scripts/package-runtime.ps1`, `scripts/run-runtime-tests.py`, `scripts/verify-shell-risk-contract.py`, docs, and package/runner tests.
