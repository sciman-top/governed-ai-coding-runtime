# 2026-04-24 Target Repo Gate Speed Controls

## Goal
- Landing: `D:\CODE\governed-ai-coding-runtime`
- Target home: `scripts/governance/`, `packages/contracts/src/governed_ai_coding_runtime_contracts/`, `schemas/`, `docs/specs/`
- Intent: improve target-repo coding speed without weakening required verification by adding explicit gate layers, bounded timeout behavior, non-blocking supplemental gates, and fail-fast execution.

## Changes
- Added `scripts/governance/level-check.ps1` for explicit `l1/l2/l3` target-repo gate runs.
- Extended `scripts/governance/gate-runner-common.ps1` to:
  - normalize `fast/quick/full/l1/l2/l3` into gate levels;
  - run `l2` as build/test/contract while skipping doctor/hotspot;
  - append `additional_gate_commands` by profile;
  - distinguish `required` from `blocking`;
  - support profile-level `gate_timeout_seconds` and per-command `timeout_seconds`;
  - stop on the first blocking failure unless `-ContinueOnError` is set;
  - kill timed-out process trees and emit timeout metadata.
- Updated Python verification execution to stop after a blocking failure by default while preserving diagnostic `continue_on_error=True`.
- Updated repo-profile schema/spec/template to document and validate `gate_timeout_seconds`, per-gate `timeout_seconds`, and `blocking`.

## Verification
- `codex --version`
  - exit_code: `0`
  - key_output: `codex-cli 0.124.0`
- `codex --help`
  - exit_code: `0`
  - key_output: CLI command list available
- `codex status`
  - exit_code: `1`
  - platform_na:
    - reason: `os error 5` access denied in current Codex desktop environment
    - alternative_verification: active rule path confirmed from conversation context and repository `AGENTS.md`
    - evidence_link: this file
    - expires_at: `n/a`
- `rg --files`
  - exit_code: `1`
  - platform_na:
    - reason: packaged `rg.exe` launch returned access denied
    - alternative_verification: `Get-ChildItem -Recurse -File`
    - evidence_link: this file
    - expires_at: `n/a`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`
  - exit_code: `0`
  - key_output: `OK powershell-parse`, `OK issue-seeding-render`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - exit_code: `0`
  - key_output: `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing`, `OK dependency-baseline`, `OK target-repo-governance-consistency`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  - exit_code: `0`
  - key_output: all runtime path/gate visibility checks `OK`; `WARN codex-capability-blocked` due current Codex capability environment
- Manual target-gate checks under ignored `.runtime/`:
  - `level-check.ps1 -Level l2 -Json`: exit_code `0`; gate_order `build,test,contract`; doctor command skipped.
  - `fast-check.ps1 -Json` with `additional_gate_commands`: exit_code `0`; non-blocking `quick-extra` failed without failing the run; full-only extra skipped.
  - `full-check.ps1 -GateTimeoutSeconds 30 -Json` with entry `timeout_seconds: 1`: exit_code `1` as expected; reason `timed_out`; gate exit_code `124`.
- Python fail-fast behavior:
  - inline verification with in-memory artifact store exited `0`;
  - default run executed only `test` after a blocking failure;
  - `continue_on_error=True` executed `test` and `contract`.

## Blocked Verification
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - exit_code: `1`
  - key_output: Python `compileall` failed at `.pyc` replacement with `PermissionError: [WinError 5]`
  - reason: current sandbox denies Python `os.replace`/`unlink` operations used by bytecode and atomic artifact writes.
  - alternative_verification: contract/schema/script checks plus manual gate-runner checks listed above.
  - evidence_link: this file
  - expires_at: `n/a`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - exit_code: `1`
  - key_output: `Ran 366 tests`; `FAILED (errors=149)`
  - reason: repeated Python `TemporaryDirectory`, `Path.mkdir`, and atomic write failures under `C:\Users\sciman\AppData\Local\Temp` from current sandbox filesystem restrictions.
  - alternative_verification: targeted manual PowerShell gate checks and inline in-memory Python verification listed above.
  - evidence_link: this file
  - expires_at: `n/a`
- `python -m unittest tests.runtime.test_governance_gate_runner tests.runtime.test_verification_runner`
  - exit_code: `1`
  - reason: current sandbox denies Python `TemporaryDirectory`, `os.replace`, and cleanup operations under both Windows temp and workspace temp paths.
  - alternative_verification: manual PowerShell gate checks and inline in-memory Python verification listed above.
  - evidence_link: this file
  - expires_at: `n/a`

## Compatibility
- Existing `fast-check.ps1` and `full-check.ps1` remain compatible entrypoints.
- `quick` remains an alias of `l1`; `full` remains an alias of `l3`.
- `required=true` still defaults to `blocking=true`; supplemental gates can explicitly set `required=false` and `blocking=false`.

## Rollback
- Preferred rollback: restore this change from git history.
- File-level rollback candidates:
  - `scripts/governance/gate-runner-common.ps1`
  - `scripts/governance/fast-check.ps1`
  - `scripts/governance/full-check.ps1`
  - `scripts/governance/level-check.ps1`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/verification_runner.py`
  - `schemas/jsonschema/repo-profile.schema.json`
  - `schemas/examples/repo-profile/target-repo-fast-full-template.example.json`
  - `docs/specs/repo-profile-spec.md`
  - `docs/specs/verification-gates-spec.md`
  - `tests/runtime/test_governance_gate_runner.py`
  - `tests/runtime/test_verification_runner.py`
