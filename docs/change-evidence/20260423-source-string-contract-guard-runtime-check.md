# 2026-04-23 Source String Contract Guard for Runtime Check

## Goal

Prevent cross-repo migration regressions where source-string contract tests drift from implementation (for example, ImageManager/PhotoOverlay contract assertions in target repositories).

## Scope

- `scripts/check-source-string-contract-guard.py`
- `scripts/runtime-check.ps1`
- `tests/runtime/test_source_string_contract_guard.py`

## Changes

1. Added `scripts/check-source-string-contract-guard.py`:
   - Discovers source-string contract tests under `tests/**` by scanning `*ContractTests.cs` files for `source.Should().Contain/NotContain`.
   - Resolves target test project automatically (or accepts explicit project path).
   - Executes detected contract classes via batched `dotnet test --filter FullyQualifiedName~...`.
   - Emits machine-readable JSON with `pass/fail/skip` status and failed class list.
2. Integrated guard into `scripts/runtime-check.ps1`:
   - New step label: `source-string-contract-guard`.
   - Included payload in runtime-check JSON output (`source_string_contract_guard`).
   - Marks overall runtime-check failure and emits remediation hint when guard fails.
   - Added optional switch: `-SkipSourceStringContractGuard`.
3. Added runtime unit tests:
   - `skip` when no source-string contract tests exist.
   - `pass` when detected tests execute successfully.
   - `fail` when detected tests fail.

## Verification

1. Script unit tests:
   - `python -m unittest tests/runtime/test_source_string_contract_guard.py`
   - Result: `OK` (3 tests).
2. Runtime-check E2E compatibility sanity:
   - `python -m unittest tests.runtime.test_attached_repo_e2e.AttachedRepoE2ETests.test_runtime_check_default_write_tool_executes_attached_write`
   - Result: `OK`.
3. Repository hard gates (ordered):
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

## Risks

- The guard is intentionally heuristic (`source.Should().Contain/NotContain` marker based), so unusual contract styles may be skipped.
- Repositories with many source-string contract classes may see extra `dotnet test` runtime in `runtime-check`.

## Rollback

```powershell
git restore --source=HEAD~1 -- scripts/check-source-string-contract-guard.py scripts/runtime-check.ps1 tests/runtime/test_source_string_contract_guard.py docs/change-evidence/20260423-source-string-contract-guard-runtime-check.md
```
