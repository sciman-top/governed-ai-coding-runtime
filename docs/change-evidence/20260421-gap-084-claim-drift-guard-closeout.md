# 20260421 GAP-084 Claim Drift Guard Closeout

## Goal
Close `GAP-084` by enforcing claim-to-evidence drift controls, evidence freshness checks, and time-bounded claim exception governance in docs CI.

## Scope
- `scripts/verify-repo.ps1`
- `docs/product/claim-exceptions.json`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/README.md`
- `docs/backlog/full-lifecycle-backlog-seeds.md`

## Changes
1. Extended claim drift sentinel with evidence freshness enforcement:
   - new gate signal: `OK claim-evidence-freshness`
   - fails when claim evidence is older than policy window.
2. Added claim exception path governance check:
   - validates `docs/product/claim-exceptions.json`
   - enforces required exception fields (`owner`, `expires_at`, `review_ref`, `rollback_ref`, `evidence_link`, etc.)
   - fails active-but-expired exceptions
   - new gate signal: `OK claim-exception-paths`
3. Added baseline claim exception registry:
   - `docs/product/claim-exceptions.json` (empty exceptions list, schema-ready for controlled exceptions)
4. Closed `GAP-084` acceptance criteria and advanced near-term queue posture:
   - `GAP-080` through `GAP-084` complete
   - no remaining execution-horizon item in current near-term range

## Verification
### Gate order
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
5. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
   - includes:
     - `OK claim-drift-sentinel`
     - `OK claim-evidence-freshness`
     - `OK claim-exception-paths`

## Status Note
`GAP-084` is complete on current branch baseline. The current near-term gap horizon queue (`GAP-080` through `GAP-084`) is fully closed.

## Rollback
Revert:
- `scripts/verify-repo.ps1`
- `docs/product/claim-exceptions.json`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/README.md`
- `docs/backlog/full-lifecycle-backlog-seeds.md`
- this evidence file
