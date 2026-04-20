# 20260420 GAP-071-072 Docs Gate Stability Fix And Full Gate Replay

## Goal
Fix Docs gate stability regression introduced by GAP-071/072 checks and replay the full gate chain to green.

## Clarification Trace
- `issue_id`: `gap-071-072-docs-gate-stability-fix`
- `attempt_count`: `1`
- `clarification_mode`: `direct_fix`
- `clarification_scenario`: `n/a`
- `clarification_questions`: `[]`
- `clarification_answers`: `[]`

## Scope
- Repair `scripts/verify-repo.ps1` so Docs checks work for both single-object and array-like PowerShell pipeline outputs.
- Re-run repository gates in required order and confirm zero active tasks in issue seeding summary.

## What Changed
1. Updated `scripts/verify-repo.ps1`:
   - Wrapped evidence file matches with `@(...)` before `.Count` usage.
   - Wrapped `catalog.claims` and `claim.source_refs` with `@(...)` for safe count/iteration.
2. No behavior reduction in GAP-071/072 checks; only collection-shape robustness fix.

## Verification
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
   - `exit_code`: `0`
   - `key_output`: `OK python-bytecode`; `OK python-import`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
   - `exit_code`: `0`
   - `key_output`: `OK runtime-unittest`; `Ran 252 tests`; `OK`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
   - `exit_code`: `0`
   - `key_output`: `OK schema-json-parse`; `OK schema-example-validation`; `OK schema-catalog-pairing`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
   - `exit_code`: `0`
   - `key_output`: `OK runtime-status-surface`; `OK codex-capability-ready`; `OK adapter-posture-visible`
5. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
   - `exit_code`: `0`
   - `key_output`: `OK host-replacement-claim-boundary`; `OK gap-evidence-slo`; `OK claim-drift-sentinel`
6. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`
   - `exit_code`: `0`
   - `key_output`: `OK powershell-parse`; `OK issue-seeding-render`
7. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
   - `exit_code`: `0`
   - `key_output`: `"completed_task_count":55`; `"active_task_count":0`

## Risks
- Claim catalog uses exact text matching; future doc wording updates must update `docs/product/claim-catalog.json` in the same change.

## Rollback
- Revert:
  - `scripts/verify-repo.ps1`
  - `docs/change-evidence/20260420-gap-071-072-docs-gate-stability-fix-and-full-gate-replay.md`
- Re-run:
  1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  5. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  6. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`
