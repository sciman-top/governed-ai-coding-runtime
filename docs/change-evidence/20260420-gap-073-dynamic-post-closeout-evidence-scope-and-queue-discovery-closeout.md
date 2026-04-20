# 20260420 GAP-073 Dynamic Post-Closeout Evidence Scope And Queue Discovery Closeout

## Goal
Close `GAP-073` by removing hard-coded post-closeout id scope from docs verification and discovering queue coverage dynamically from backlog plus seeds.

## Clarification Trace
- `issue_id`: `gap-073-dynamic-post-closeout-evidence-scope`
- `attempt_count`: `1`
- `clarification_mode`: `direct_fix`
- `clarification_scenario`: `n/a`
- `clarification_questions`: `[]`
- `clarification_answers`: `[]`

## Scope
- Make `gap-evidence-slo` discover post-closeout scope from backlog section and seed ids.
- Keep closeout evidence requirements unchanged and fail-closed.

## What Changed
1. Updated `scripts/verify-repo.ps1` `Invoke-GapEvidenceSloCheck` to:
   - read post-closeout ids from `docs/backlog/issue-seeds.yaml`
   - discover queue members from `## Post-Closeout Optimization Queue` in `docs/backlog/issue-ready-backlog.md`
   - apply required closeout checks for all completed ids in discovered scope
2. Removed fixed `GAP-069..072` hard-coding.

## Verification
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
5. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`

## Risks
- Queue discovery depends on stable backlog heading structure (`## Post-Closeout Optimization Queue`).

## Rollback
- Revert:
  - `scripts/verify-repo.ps1`
  - `docs/change-evidence/20260420-gap-073-dynamic-post-closeout-evidence-scope-and-queue-discovery-closeout.md`
- Re-run:
  1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  5. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
