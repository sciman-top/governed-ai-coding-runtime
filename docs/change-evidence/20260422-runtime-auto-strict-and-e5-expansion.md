# 2026-04-22 Runtime auto-strict snapshot and E5 expansion

## Goal
- Execute the remaining follow-up improvements after the previous risk-closure slice.
- Make process-bridge snapshot behavior stricter by default for high-risk launch flows.
- Expand E5 verification beyond Python import roots to include host tooling and optional target-repo dependency baseline checks in the same verifier.

## Basis
- Balanced snapshot mode remains significantly cheaper than strict mode, but high-risk actions should default to stronger change detection.
- The dependency baseline verifier already enforced Python import constraints; host-tooling and target-repo dependency baseline checks were still outside the same verification path.
- Repository policy still avoids premature package-manager metadata, so this slice keeps the baseline evidence-first and verifier-driven.

## Changes
1. High-risk launch defaults
- `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
  - `snapshot_mode` now supports `auto|balanced|strict`.
  - `run_launch_mode()` defaults to `auto`.
  - `auto` resolves to:
    - `strict` for `risk_tier=high`
    - `balanced` for `risk_tier=low|medium`
  - launch payload continues to expose the resolved `snapshot_mode`.
- `scripts/session-bridge.py`
  - `launch --snapshot-mode` now accepts `auto|balanced|strict`, default `auto`.

2. E5 verifier expansion
- `scripts/verify-dependency-baseline.py`
  - keeps existing Python import baseline checks.
  - adds `host_tooling` detection and fail-closed behavior for missing required tools.
  - adds optional target-repo baseline checks:
    - `--target-repo-root`
    - `--require-target-repo-baseline`
  - reports target-repo baseline status in verifier output.
- `docs/dependency-baseline.json`
  - now includes target-repo baseline path candidates:
    - `docs/dependency-baseline.md`
    - `.governed-ai/dependency-baseline.json`
- `docs/dependency-baseline.md`
  - now documents verifier usage for both repo baseline and target-repo baseline checks.

3. Regression coverage
- `tests/runtime/test_session_bridge.py`
  - added high-risk default-to-strict launch test.
- `tests/runtime/test_dependency_baseline.py`
  - added required-host-tool-missing failure test.
  - added target-repo baseline required-mode test (missing -> fail, present -> pass).

## Commands
- Targeted regressions:
  - `python -m unittest tests.runtime.test_session_bridge tests.runtime.test_dependency_baseline tests.runtime.test_runtime_doctor`
- Direct verifier runs:
  - `python scripts/verify-dependency-baseline.py`
  - `python scripts/verify-dependency-baseline.py --target-repo-root . --require-target-repo-baseline`
- Full gate order:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
- Additional checks:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`

## Evidence
- Targeted regressions:
  - `52` tests passed.
- Runtime gate:
  - `321` runtime tests passed, `1` skipped (symlink availability guard).
  - `5` service parity tests passed.
- Contract gate:
  - schema/example/catalog checks passed.
  - dependency baseline check passed with:
    - `allowed_external_modules=[]`
    - no missing required host tools.
- Doctor gate:
  - dependency baseline assets and runtime surface checks passed.
- Direct verifier:
  - repo baseline passed.
  - target-repo baseline required-mode passed for `--target-repo-root .` via `docs/dependency-baseline.md`.

## Rollback
- Revert this slice by restoring:
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
  - `scripts/session-bridge.py`
  - `scripts/verify-dependency-baseline.py`
  - `docs/dependency-baseline.json`
  - `docs/dependency-baseline.md`
  - `tests/runtime/test_session_bridge.py`
  - `tests/runtime/test_dependency_baseline.py`
- No schema migration or data migration introduced in this slice.
