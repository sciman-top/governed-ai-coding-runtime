# 20260418 Local Baseline To Hybrid Final-State Migration Matrix

## Change Basis
- User asked whether historical completed-stage plans and landed code conflict with the new hybrid final state at runtime.
- Review found the right answer was not "fully conflicting" or "already aligned"; the real split is reusable kernel versus outdated deployment boundary.
- Existing docs explained the target architecture and active queue, but they did not give one explicit decision bridge between completed baseline slices and the hybrid final-state queue.
- Active rule path: `D:\OneDrive\CODE\governed-ai-coding-runtime\AGENTS.md`, carrying `GlobalUser/AGENTS.md v9.39`.
- Clarification trace: `issue_id=baseline-vs-hybrid-final-state-matrix`, `attempt_count=1`, `clarification_mode=direct_fix`, `clarification_scenario=n/a`, `clarification_questions=[]`, `clarification_answers=[]`.

## Files Changed
- Added `docs/architecture/local-baseline-to-hybrid-final-state-migration-matrix.md`
- Updated `docs/architecture/README.md`
- Updated `docs/README.md`
- Updated `docs/plans/README.md`
- Updated `README.md`
- Updated `docs/change-evidence/README.md`

## Decision
- Keep historical completed plans as implementation history.
- Keep landed runtime primitives as the current reusable kernel baseline.
- Mark repo-root `.runtime/`, CLI-first operator flow, and manual-handoff Codex posture as valid baseline surfaces but not the final attach-first product boundary.
- Use the new migration matrix as the default reference whenever old completed plans or current baseline code are compared against the hybrid final-state target.

## Verification
### Docs Gate
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs
```

- Exit code: `0`
- Key output: `OK active-markdown-links`, `OK backlog-yaml-ids`, `OK old-project-name-historical-only`

### Required Gate Order
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
```

- Exit code: `0`
- Key output: `OK python-bytecode`, `OK python-import`

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
```

- Exit code: `0`
- Key output: `OK runtime-unittest`, `Ran 118 tests`, `OK`

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
```

- Exit code: `0`
- Key output: `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing`

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
```

- Exit code: `0`
- Key output: `OK runtime-status-surface`, `OK maintenance-policy-visible`, `OK adapter-posture-visible`

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```

- Exit code: `0`
- Key output: `OK runtime-build`, `OK runtime-unittest`, `OK schema-catalog-pairing`, `OK runtime-doctor`, `OK active-markdown-links`, `OK issue-seeding-render`, `Ran 118 tests`, `OK`

```powershell
git diff --check
```

- Exit code: `0`
- Key output: no whitespace errors; line-ending warnings only

## Risks
- Readers may still confuse "baseline remains valid" with "baseline already equals final product."
- The matrix reduces that risk, but the actual runtime boundary still needs implementation work in `GAP-035` through `GAP-044`.

## Rollback
- Revert the added matrix document and the index links above.
- Historical plans and landed runtime code are unchanged by this documentation-only clarification.
