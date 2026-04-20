# 20260420 GAP-072 Claim-Drift Sentinel And Continuous Doc-Runtime Sync Closeout

## Goal
Close `GAP-072` by making externally visible product claims machine-verifiable against source docs, executable commands, and evidence files.

## Clarification Trace
- `issue_id`: `gap-072-claim-drift-sentinel-and-continuous-doc-runtime-sync`
- `attempt_count`: `1`
- `clarification_mode`: `direct_fix`
- `clarification_scenario`: `n/a`
- `clarification_questions`: `[]`
- `clarification_answers`: `[]`

## Scope
- Introduce a claim catalog mapping claim text to proof commands and evidence links.
- Add a drift sentinel check that fails when source claim text, evidence links, or source anchors drift.
- Keep this check in standard docs verification so stale or over-claimed wording is caught before merge.

## What Changed
1. Added claim catalog file:
   - `docs/product/claim-catalog.json`
2. Catalog entries now define:
   - `claim_id`
   - `claim_text`
   - `proof_command`
   - `evidence_link`
   - `source_refs[]` with `path` + required `contains` snippet
3. Updated `scripts/verify-repo.ps1` with `Invoke-ClaimDriftSentinelCheck`:
   - validates catalog structure and required fields
   - validates `evidence_link` path exists
   - validates each `source_ref.path` exists
   - validates each `source_ref.contains` snippet exists in the source file
   - fails on any drift
4. Wired `Invoke-ClaimDriftSentinelCheck` into `Invoke-DocsChecks`.

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
   - `key_output`: `OK claim-drift-sentinel`
6. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`
   - `exit_code`: `0`
   - `key_output`: `OK issue-seeding-render`

## Risks
- Claim snippets in `source_refs.contains` are intentionally exact-string checks. Intentional wording changes require catalog updates in the same change set.

## Rollback
- Revert:
  - `docs/product/claim-catalog.json`
  - `scripts/verify-repo.ps1`
  - `docs/change-evidence/20260420-gap-072-claim-drift-sentinel-and-continuous-doc-runtime-sync-closeout.md`
- Re-run:
  1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  5. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  6. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`
