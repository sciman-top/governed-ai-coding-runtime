# 2026-04-17 GAP-021 Task 2 Build / Doctor Gates

## Goal
- Land `Foundation / GAP-021 / Task 2`.
- Replace the remaining `build` and `hotspot` placeholders with honest Foundation-grade commands.

## Basis
- Foundation scope: the repo still exposes a Python contract substrate rather than a packaged product service.
- `build` therefore means byte-compilation and import validation of the current Python runtime substrate.
- `doctor` therefore means runtime prerequisite checks over Python, expected directories, schema catalog visibility, and active gate command presence.

## Files Changed
- `scripts/build-runtime.ps1`
- `scripts/doctor-runtime.ps1`
- `scripts/verify-repo.ps1`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/verification_runner.py`
- `schemas/jsonschema/verification-gates.schema.json`
- `docs/specs/verification-gates-spec.md`
- `docs/product/verification-runner.md`
- `AGENTS.md`
- `README.md`
- `README.zh-CN.md`
- `README.en.md`
- `docs/README.md`
- `packages/contracts/README.md`
- `tests/README.md`
- `tests/runtime/test_runtime_doctor.py`
- `tests/runtime/test_verification_runner.py`
- `tests/runtime/test_delivery_handoff.py`

## Decisions Landed
- `scripts/build-runtime.ps1` is the first live build command and verifies Python bytecode compilation plus contract-module importability.
- `scripts/doctor-runtime.ps1` is the first live doctor command and verifies Python availability, required repo paths, schema catalog visibility, and build/test/contract/doctor command presence.
- `scripts/verify-repo.ps1` now exposes `-Check Build` and `-Check Doctor`, and `-Check All` now runs in canonical order `build -> test -> contract -> doctor -> docs -> scripts`.
- Verification contracts now use live gate ids `build`, `test`, `contract`, and `doctor` while still mapping to canonical names `build`, `test`, `contract_or_invariant`, and `hotspot_or_health_check`.

## Verification Commands
1. `python -m unittest tests.runtime.test_runtime_doctor tests.runtime.test_verification_runner tests.runtime.test_delivery_handoff -v`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
4. `python -m unittest discover -s tests/runtime -p "test_*.py"`
5. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
6. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
7. `git diff --check`

## Verification Result
- `tests.runtime.test_runtime_doctor/tests.runtime.test_verification_runner/tests.runtime.test_delivery_handoff`: pass
- `scripts/build-runtime.ps1`: pass
  - `OK python-bytecode`
  - `OK python-import`
- `scripts/doctor-runtime.ps1`: pass
  - `OK python-command`
  - `OK gate-command-build`
  - `OK gate-command-test`
  - `OK gate-command-contract`
  - `OK gate-command-doctor`
- `python -m unittest discover -s tests/runtime -p "test_*.py"`: pass, `Ran 77 tests`
- `scripts/verify-repo.ps1 -Check Contract`: pass
  - `OK schema-json-parse`
  - `OK schema-example-validation`
  - `OK schema-catalog-pairing`
- `scripts/verify-repo.ps1 -Check All`: pass
  - `OK runtime-build`
  - `OK runtime-unittest`
  - `OK schema-json-parse`
  - `OK schema-example-validation`
  - `OK schema-catalog-pairing`
  - `OK runtime-doctor`
  - `OK active-markdown-links`
  - `OK backlog-yaml-ids`
  - `OK old-project-name-historical-only`
  - `OK powershell-parse`
  - `Ran 77 tests`
- `git diff --check`: pass with LF to CRLF normalization warnings only; no whitespace errors

## issue_id / clarification_mode
- `issue_id`: `GAP-021`
- `attempt_count`: `1`
- `clarification_mode`: `direct_fix`
- `clarification_scenario`: `bugfix`
- `clarification_questions`: `[]`
- `clarification_answers`: `[]`

## Gate Status
| gate | status | command | result | reason | alternative_verification | evidence_link | expires_at |
|---|---|---|---|---|---|---|---|
| build | `active` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1` | pass | Foundation build currently means compile/import validation for the Python contract substrate | `python -m compileall packages/contracts/src scripts/run-readonly-trial.py` | `docs/change-evidence/20260417-gap-021-task-2-build-doctor-gates.md` | `n/a` |
| test | `active` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` | pass | runtime contract tests remain the live test gate | `python -m unittest discover -s tests/runtime -p "test_*.py"` | `docs/change-evidence/20260417-gap-021-task-2-build-doctor-gates.md` | `n/a` |
| contract/invariant | `active` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` | pass | schema/spec/example/catalog pairing remains the hardest machine contract | direct schema parse/example/catalog checks | `docs/change-evidence/20260417-gap-021-task-2-build-doctor-gates.md` | `n/a` |
| hotspot | `active` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1` | pass | Foundation doctor currently acts as the live hotspot/health entrypoint | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Doctor` | `docs/change-evidence/20260417-gap-021-task-2-build-doctor-gates.md` | `n/a` |

## Risks
- These commands are honest for the current repo, but they are not production package/release or service-health gates yet.
- `E5` remains `gate_na`; this task does not introduce dependency manifests or supply-chain checks.

## Rollback
- Revert the modified docs, schema, contracts, tests, and gate scripts from git history for branch `feature/gap-020-task-1`.
- Remove `scripts/build-runtime.ps1`, `scripts/doctor-runtime.ps1`, and this evidence file if the repo returns to pre-Foundation gate semantics.
