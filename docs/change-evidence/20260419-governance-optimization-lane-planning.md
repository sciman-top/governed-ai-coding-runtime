# 2026-04-19 Governance Optimization Lane Planning

## Goal
- Add a canonical governance-optimization planning lane without changing runtime behavior.
- Keep the existing `GAP-045` through `GAP-060` direct-to-hybrid-final-state queue as the active executable mainline.

## Basis
- `docs/roadmap/direct-to-hybrid-final-state-roadmap.md`
- `docs/plans/direct-to-hybrid-final-state-implementation-plan.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/architecture/minimum-viable-governance-loop.md`
- `docs/architecture/governance-boundary-matrix.md`
- user-approved direction to add a `governance-optimization-lane` with GAP-level backlog and acceptance or rollback template

## Changes
- added `docs/roadmap/governance-optimization-lane-roadmap.md`
- added `docs/plans/governance-optimization-lane-implementation-plan.md`
- added `docs/templates/governance-gap-acceptance-and-rollback-template.md`
- updated planning and backlog indexes to reference the new lane
- appended `GAP-061` through `GAP-068` as the next governance-optimization lane after `GAP-060`
- updated `scripts/github/create-roadmap-issues.ps1` with the minimum label mapping needed for `GAP-061` through `GAP-068`
- kept issue-seeding structure stable by preserving `### GAP-xxx` task headings and appending new YAML entries only

## Commands
```powershell
git status --short
```

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
- The new lane could be mistaken for a replacement of the direct-to-hybrid mainline.
- The issue-seeding parser could fail if backlog heading structure drifts.
- The lane could expand prematurely into spec or runtime implementation work.

## Mitigations
- marked `GAP-061` through `GAP-068` as a future governance-optimization lane with `GAP-060` as the default activation blocker
- preserved the current direct-to-hybrid mainline as the active executable queue
- limited this change to planning, index, seed, and evidence surfaces only

## Rollback
- remove the new lane roadmap, implementation plan, template, and evidence files
- remove `GAP-061` through `GAP-068` entries from `docs/backlog/issue-ready-backlog.md`
- remove `GAP-061` through `GAP-068` entries from `docs/backlog/issue-seeds.yaml`
- remove references from `docs/plans/README.md`, `docs/backlog/README.md`, and `docs/README.md`

## Expected Verification
- docs and script checks continue to pass
- full repo verification order remains `build -> test -> contract/invariant -> doctor`
- no runtime behavior claims change as part of this planning-only update

## Verification Results
- `scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
  - output: `{"issue_seed_version":"3.5","rendered_tasks":51,"rendered_issue_creation_tasks":23,"rendered_epics":13,"rendered_initiative":true}`
- `scripts/verify-repo.ps1 -Check Docs`
  - output: `OK active-markdown-links`, `OK backlog-yaml-ids`, `OK old-project-name-historical-only`
- `scripts/verify-repo.ps1 -Check Scripts`
  - output: `OK powershell-parse`, `OK issue-seeding-render`
- `scripts/build-runtime.ps1`
  - output: `OK python-bytecode`, `OK python-import`
- `scripts/verify-repo.ps1 -Check Runtime`
  - output: `OK runtime-unittest`, `Ran 204 tests`, `OK`
- `scripts/verify-repo.ps1 -Check Contract`
  - output: `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing`
- `scripts/doctor-runtime.ps1`
  - output: `OK runtime-policy-compatibility`, `OK runtime-policy-maintenance`, `OK gate-command-build`, `OK gate-command-test`, `OK gate-command-contract`, `OK gate-command-doctor`
