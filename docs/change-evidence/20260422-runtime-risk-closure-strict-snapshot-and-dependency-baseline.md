# 2026-04-22 Runtime risk closure: strict snapshot and dependency baseline

## Goal
- Close the remaining runtime hardening items left after the earlier persistence and snapshot work.
- Remove the last `write_file` direct-overwrite path from attached target execution without breaking symlink semantics.
- Add an explicit `strict` process-bridge snapshot mode for full-content verification when operators need maximal change detection.
- Turn `E5` from `gate_na` into an executable, stdlib-only dependency baseline without introducing premature package-manager metadata.

## Basis
- `attached_write_execution.py` still wrote attached target files with a direct `write_text()` call.
- The default launch snapshot had moved from full-content hashing to a faster balanced mode, but there was still a theoretical large-file false-negative window when size and `mtime_ns` were preserved and edits landed outside sampled regions.
- Repository policy in `packages/README.md` still forbids adding package-manager metadata without explicit dependency and supply-chain evidence.
- The repository's actual Python import graph is currently stdlib-only plus the local package `governed_ai_coding_runtime_contracts`.

## Changes
1. Attached write execution hardening
- `packages/contracts/src/governed_ai_coding_runtime_contracts/attached_write_execution.py`
  - `write_file` execution now uses `atomic_write_text()`.
  - Existing append semantics remain unchanged.
- `packages/contracts/src/governed_ai_coding_runtime_contracts/file_guard.py`
  - keeps symlink write-through behavior by falling back to direct write when the target is a symlink.
- Regression coverage:
  - a new test verifies that writing through a symlink updates the symlink target without replacing the link object.

2. Strict process-bridge snapshot mode
- `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
  - added `SnapshotMode = balanced | strict`
  - `balanced` remains the default
  - `strict` performs full-content digesting for launch snapshots
  - launch payload now records the effective `snapshot_mode`
- `scripts/session-bridge.py`
  - added `--snapshot-mode balanced|strict`
- Regression coverage:
  - balanced mode still detects same-size rewrites with restored `mtime`
  - strict mode detects large-file rewrites outside balanced sample windows
  - invalid snapshot mode is rejected

3. Dependency baseline / E5 activation
- Added:
  - `docs/dependency-baseline.md`
  - `docs/dependency-baseline.json`
  - `scripts/verify-dependency-baseline.py`
- `scripts/verify-repo.ps1`
  - now exposes `-Check Dependency`
  - contract checks now include dependency baseline verification
- `scripts/doctor-runtime.ps1`
  - now verifies dependency baseline doc, manifest, and verifier script visibility
- `AGENTS.md`
  - `E5` moved from `gate_na` to `active`
- `packages/README.md`
  - now states that the repo enforces a stdlib-only dependency baseline

## Commands
- Targeted regression:
  - `python -m unittest tests.runtime.test_attached_write_execution tests.runtime.test_session_bridge tests.runtime.test_dependency_baseline tests.runtime.test_runtime_doctor`
- Full gate order:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
- Direct E5 verification:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Dependency`
- Snapshot performance probe:
  - inline Python benchmark over 40 files x 1 MiB comparing `balanced` and `strict`

## Evidence
- Targeted regression:
  - `56` tests passed
  - `1` test skipped by environment guard:
    - `tests/runtime/test_attached_write_execution.py`
    - reason: file symlinks not available in this environment
- Full runtime gate:
  - `318` runtime tests passed
  - `1` runtime test skipped for the same symlink availability guard
  - `5` service parity tests passed
- Contract gate:
  - schema/spec pairing passed
  - dependency baseline passed
  - declared external modules remained `[]`
- Doctor gate:
  - runtime prerequisites passed
  - dependency baseline assets were visible
- Direct dependency gate:
  - passed
  - observed import roots remained stdlib-only plus `governed_ai_coding_runtime_contracts`
- Snapshot benchmark:
  - `balanced`: `7.46 ms`
  - `strict`: `87.40 ms`

## Interpretation
- The last attached `write_file` path is now consistent with the repository's atomic-write hardening story while still preserving symlink behavior.
- Operators now have an explicit knob to trade launch-snapshot cost for stronger change detection.
- `balanced` remains the default because it is materially cheaper for large-file worktrees.
- `E5` is now real and executable without pretending the repository already has a finalized `pyproject.toml` / lockfile strategy.

## Rollback
- Restore these files from git history if this slice must be reverted:
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/attached_write_execution.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
  - `scripts/session-bridge.py`
  - `scripts/verify-dependency-baseline.py`
  - `scripts/verify-repo.ps1`
  - `scripts/doctor-runtime.ps1`
  - `docs/dependency-baseline.md`
  - `docs/dependency-baseline.json`
  - `packages/README.md`
  - `AGENTS.md`
  - related tests under `tests/runtime/`
- No schema/data migration was introduced in this slice.
