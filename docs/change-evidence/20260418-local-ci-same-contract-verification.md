# 20260418 Local CI Same-Contract Verification

## Change Basis
- After completing `GAP-042` and `GAP-043`, the next dependency-safe strategy gate step was `GAP-044 Task 6`.
- The goal was to make the promise "one contract, local and CI consistent" mechanically testable.
- Landing point: verification spec/schema, markdown path collection in `verify-repo.ps1`, and regression tests.
- Target destination: local and CI verification consume the same declared contract shape, while CI is documented as the last line of defense rather than a separate contract system.
- Active rule path: `D:\OneDrive\CODE\governed-ai-coding-runtime\AGENTS.md`, carrying `GlobalUser/AGENTS.md v9.39`.
- Clarification trace: `issue_id=gap-044-task-6-same-contract-verification`, `attempt_count=1`, `clarification_mode=direct_fix`, `clarification_scenario=n/a`, `clarification_questions=[]`, `clarification_answers=[]`.

## Files Changed
- Updated `docs/specs/verification-gates-spec.md`
- Updated `schemas/jsonschema/verification-gates.schema.json`
- Updated `scripts/verify-repo.ps1`
- Updated `tests/runtime/test_runtime_doctor.py`
- Updated `docs/change-evidence/README.md`

## Summary
- Extended the verification spec with explicit local and CI execution contexts.
- Recorded the rule that local and CI consume the same declared contract inputs.
- Recorded that CI is the last line of defense when host hooks, wrappers, adapters, or session controls are bypassed.
- Added a non-ASCII markdown path regression test.
- Fixed active markdown path collection by using `git -c core.quotepath=false ls-files`.

## TDD Evidence
Red:

```powershell
python -m unittest tests.runtime.test_runtime_doctor -v
```

- Exit code: `1`
- Key output: the new non-ASCII docs-path regression failed because `verify-repo.ps1 -Check Docs` returned non-zero before path collection was fixed

Green:

```powershell
python -m unittest tests.runtime.test_runtime_doctor -v
```

- Exit code: `0`
- Key output: `Ran 5 tests`, `OK`

## Targeted Verification
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs
```

- Exit code: `0`
- Key output: `OK active-markdown-links`, `OK backlog-yaml-ids`, `OK old-project-name-historical-only`

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
```

- Exit code: `0`
- Key output: `OK runtime-unittest`, `Ran 125 tests`, `OK`

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
```

- Exit code: `0`
- Key output: `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing`

## Full Gate Verification
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
```

- Exit code: `0`
- Key output: `OK python-bytecode`, `OK python-import`

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
```

- Exit code: `0`
- Key output: `OK runtime-status-surface`, `OK maintenance-policy-visible`, `OK adapter-posture-visible`

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```

- Exit code: `0`
- Key output: `OK runtime-build`, `OK runtime-unittest`, `OK schema-catalog-pairing`, `OK runtime-doctor`, `OK active-markdown-links`, `OK issue-seeding-render`, `Ran 125 tests`, `OK`

```powershell
git diff --check
```

- Exit code: `0`
- Key output: no whitespace errors; line-ending warnings only

## Risks
- This task aligns local and CI contract semantics at the verifier boundary; it does not yet prove every future adapter or session bridge consumes the new shape.
- The schema and spec now distinguish execution contexts, but there is still no separate runtime reader for these fields.

## Rollback
- Revert the verification spec and schema updates.
- Revert the `git -c core.quotepath=false ls-files` change in `scripts/verify-repo.ps1`.
- Remove the non-ASCII regression test.
- Remove this evidence file and its index entry.
