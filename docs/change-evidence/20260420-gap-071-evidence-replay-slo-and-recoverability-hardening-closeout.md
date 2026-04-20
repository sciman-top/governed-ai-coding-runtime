# 20260420 GAP-071 Evidence Replay SLO And Recoverability Hardening Closeout

## Goal
Close `GAP-071` by making evidence and replay recoverability checks explicit, machine-checked, and regression-sensitive.

## Clarification Trace
- `issue_id`: `gap-071-evidence-replay-slo-and-recoverability-hardening`
- `attempt_count`: `1`
- `clarification_mode`: `direct_fix`
- `clarification_scenario`: `n/a`
- `clarification_questions`: `[]`
- `clarification_answers`: `[]`

## Scope
- Add an evidence-SLO gate that validates completed post-closeout GAP items have rollback-ready, verification-complete evidence.
- Tie SLO checks to executable runtime recoverability paths rather than narrative-only assertions.
- Keep the check fail-closed when required replay or verification anchors are missing.

## What Changed
1. Updated `scripts/verify-repo.ps1` with `Invoke-GapEvidenceSloCheck`.
2. The check inspects completed `GAP-069..072` entries in `docs/backlog/issue-ready-backlog.md`.
3. For each completed GAP in this range, the check requires:
   - one closeout evidence file under `docs/change-evidence/` with matching GAP id and `closeout` in filename
   - required sections: `## Verification` and `## Rollback`
   - required verification anchors:
     - `scripts/build-runtime.ps1`
     - `verify-repo.ps1 -Check Runtime`
     - `verify-repo.ps1 -Check Contract`
     - `scripts/doctor-runtime.ps1`
4. `Invoke-GapEvidenceSloCheck` is now part of `Invoke-DocsChecks` and fails merge-time verification if evidence recoverability regresses.

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
   - `key_output`: `OK gap-evidence-slo`

## Risks
- The SLO check currently scopes to `GAP-069..072`. If a new post-closeout lane starts, the target GAP range in the check must be expanded.

## Rollback
- Revert:
  - `scripts/verify-repo.ps1`
  - `docs/change-evidence/20260420-gap-071-evidence-replay-slo-and-recoverability-hardening-closeout.md`
- Re-run:
  1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  5. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
