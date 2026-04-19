# 2026-04-19 Governance Optimization Lane Epic Rendering

## Goal
- Promote the governance-optimization lane from task-only issue seeding into a dedicated follow-on epic rendering path.
- Keep the direct-to-hybrid `Phase 0` through `Phase 5` chain unchanged and authoritative for hybrid final-state closure.

## Basis
- `docs/roadmap/governance-optimization-lane-roadmap.md`
- `docs/plans/governance-optimization-lane-implementation-plan.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/README.md`
- `scripts/github/create-roadmap-issues.ps1`
- user-approved follow-up direction to make the governance lane render as an independent epic chain rather than task-only seeding

## Changes
- added phase-level `Status`, `Goal`, `Scope`, and `Exit Criteria` to the governance lane roadmap so it can back one epic body the same way the direct roadmap does
- clarified `GAP-061` backlog and implementation-plan acceptance so epic rendering is part of canonicalization rather than an implicit script detail
- updated backlog and docs indexes to state that the governance lane now renders as a dedicated follow-on epic after `Phase 5`
- extended `scripts/github/create-roadmap-issues.ps1` with:
  - governance-roadmap phase parsing
  - a new `Phase 6` epic definition
  - epic-body rendering support for governance-roadmap-backed phases
- preserved one initiative and one task chain; this change does not create a second initiative or redefine task ids

## Commands
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
```

## Risks
- The governance lane could be mistaken for a second active closure mainline if the new epic wording is too loose.
- Script parsing could regress if the governance roadmap drifts away from the phase-level heading structure expected by epic rendering.
- A second initiative would overstate the change and complicate milestone history.

## Mitigations
- kept the governance lane blocked behind `GAP-060` and explicitly follow-on in the roadmap and root entry docs
- reused the existing roadmap-epic render pattern instead of adding a new rendering model
- kept one initiative and only added one follow-on epic (`Phase 6`)

## Rollback
- remove the `Phase 6` epic definition and governance-roadmap parser from `scripts/github/create-roadmap-issues.ps1`
- remove the phase-level epic sections from `docs/roadmap/governance-optimization-lane-roadmap.md`
- revert the backlog and plan wording that now references dedicated epic rendering
- remove this evidence file and its index entry

## Expected Verification
- `-ValidateOnly -RenderAll` now renders one additional epic without changing task count
- docs, scripts, build, runtime, contract, and doctor verification continue to pass
- the initiative count remains `true` for one initiative, not two

## Verification Results
- `scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
  - output: `{"issue_seed_version":"3.5","rendered_tasks":51,"rendered_issue_creation_tasks":23,"rendered_epics":14,"rendered_initiative":true}`
- `scripts/verify-repo.ps1 -Check Docs`
  - output: `OK active-markdown-links`, `OK backlog-yaml-ids`, `OK old-project-name-historical-only`
- `scripts/verify-repo.ps1 -Check Scripts`
  - output: `OK powershell-parse`, `OK issue-seeding-render`
- `scripts/build-runtime.ps1`
  - output: `OK python-bytecode`, `OK python-import`
- `scripts/verify-repo.ps1 -Check Runtime`
  - output: `OK runtime-unittest`, `Ran 205 tests`, `OK`
- `scripts/verify-repo.ps1 -Check Contract`
  - output: `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing`
- `scripts/doctor-runtime.ps1`
  - output: `OK runtime-policy-compatibility`, `OK runtime-policy-maintenance`, `OK gate-command-build`, `OK gate-command-test`, `OK gate-command-contract`, `OK gate-command-doctor`
