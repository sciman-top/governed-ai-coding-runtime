# 20260418 Interactive Session Productization Implementation Plan Evidence

## Change Basis

- Request: continue from the medium-granularity plan gap and add the missing implementation plan for `GAP-035` through `GAP-039`.
- Landing point: implementation planning only.
- Target destination: make the hybrid final-state productization work executable at medium granularity without confusing it with the earlier planning realignment file.
- Active rule path: `D:\OneDrive\CODE\governed-ai-coding-runtime\AGENTS.md`, carrying `GlobalUser/AGENTS.md v9.39`.
- Clarification trace: `issue_id=interactive-session-productization-medium-plan`, `attempt_count=1`, `clarification_mode=direct_fix`, `clarification_scenario=n/a`, `clarification_questions=[]`, `clarification_answers=[]`.

## Files Changed

- Added `docs/plans/interactive-session-productization-implementation-plan.md`
- Updated `docs/plans/README.md`
- Updated `docs/README.md`
- Updated `docs/backlog/README.md`
- Updated `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- Updated `README.md`
- Updated `README.zh-CN.md`
- Updated `README.en.md`
- Updated `docs/change-evidence/README.md`

## Plan Summary

The new implementation plan separates the active productization work from the previous planning realignment:

- `docs/plans/interactive-session-productization-plan.md`: historical planning realignment that created the `GAP-035` through `GAP-039` queue.
- `docs/plans/interactive-session-productization-implementation-plan.md`: active medium-granularity implementation plan for `GAP-035` through `GAP-039`.

The plan decomposes the work into 15 tasks:

- Task 0: confirm Strategy Gate inputs
- Tasks 1-3: `GAP-035` repo attachment binding, light-pack generation/validation, and doctor/status visibility
- Tasks 4-6: `GAP-036` session bridge contract, local bridge entrypoint, and launch-second fallback
- Tasks 7-9: `GAP-037` direct Codex adapter, evidence mapping, and safe smoke trial
- Tasks 10-11: `GAP-038` adapter registry, capability tiers, and non-Codex fixtures
- Tasks 12-13: `GAP-039` multi-repo trial evidence model and runner/onboarding kit
- Task 14: closeout evidence, roadmap updates, and full gates

## Verification Before Evidence

Executed from repository root on 2026-04-18:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs
```

- Exit code: `0`
- Key output: `OK active-markdown-links`, `OK backlog-yaml-ids`, `OK old-project-name-historical-only`

## Full Gate Verification

Executed from repository root on 2026-04-18:

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
- Key output: `OK runtime-policy-compatibility`, `OK runtime-policy-maintenance`, `OK runtime-status-surface`, `OK adapter-posture-visible`

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```

- Exit code: `0`
- Key output: `OK runtime-build`, `OK runtime-unittest`, `OK schema-catalog-pairing`, `OK runtime-doctor`, `OK active-markdown-links`, `OK issue-seeding-render`, `Ran 118 tests`, `OK`

## Risks

- This is a medium-granularity implementation plan, not the implementation itself.
- Several tasks are intentionally blocked by `GAP-040` through `GAP-044`; executing them early would harden unstable boundaries.
- File paths listed under "Planned Create" and "Planned Modify" are implementation targets. Actual execution must still verify current code and schema state task by task before editing.

## Rollback

- Remove `docs/plans/interactive-session-productization-implementation-plan.md`.
- Remove links to it from README files, `docs/README.md`, `docs/backlog/README.md`, `docs/plans/README.md`, and the full lifecycle roadmap.
- Remove this evidence file and its index entry.
