# 2026-04-17 repo-governance-hub Mechanism Adoption Matrix

## Goal
- Convert the earlier lightweight borrowing notes into a formal mechanism adoption decision.
- Capture the selection rule for `adopt_now / defer / do_not_adopt`.
- Record the ten reviewed mechanisms and their decisions in a repo-native research document.

## Basis
- User request to explain how to choose and to turn the ten mechanisms into a formal research document.
- Existing lightweight review in `docs/research/repo-governance-hub-borrowing-review.md`.
- Existing product boundary decisions:
  - `docs/adrs/0001-control-plane-first.md`
  - `docs/adrs/0002-no-multi-repo-distribution-in-mvp.md`
  - `docs/adrs/0003-single-agent-baseline-first.md`
  - `docs/adrs/0005-governance-kernel-and-control-packs-before-platform-breadth.md`

## Files Changed
- Updated `docs/research/repo-governance-hub-borrowing-review.md`
- Updated `docs/README.md`
- Added `docs/change-evidence/20260417-repo-governance-hub-mechanism-adoption-matrix.md`

## Snapshots
Because the repository still has no `.git` worktree, pre-edit snapshots were stored at:
- `docs/change-evidence/snapshots/20260417-repo-governance-hub-mechanism-adoption-matrix/`

Snapshot coverage:
- `docs/README.md`
- `docs/research/repo-governance-hub-borrowing-review.md`

## Commands
### Snapshot existing files
```powershell
$slug='20260417-repo-governance-hub-mechanism-adoption-matrix'
$snapDir=Join-Path 'docs/change-evidence/snapshots' $slug
New-Item -ItemType Directory -Force -Path $snapDir | Out-Null
$files=@(
  'docs/README.md',
  'docs/research/repo-governance-hub-borrowing-review.md'
)
foreach($f in $files){
  $name=($f -replace '[\\/]+','--')
  Copy-Item -LiteralPath $f -Destination (Join-Path $snapDir $name) -Force
}
```

### Research inputs reviewed
```powershell
Get-Content -Raw 'D:\OneDrive\CODE\repo-governance-hub\config\governance-control-registry.json'
Get-Content -Raw 'D:\OneDrive\CODE\repo-governance-hub\config\update-trigger-policy.json'
Get-Content -Raw 'D:\OneDrive\CODE\repo-governance-hub\config\target-control-rollout-matrix.json'
Get-Content -Raw 'D:\OneDrive\CODE\repo-governance-hub\config\clarification-policy.json'
Get-Content -Raw 'D:\OneDrive\CODE\repo-governance-hub\.governance\tracked-files-policy.json'
Get-Content -Raw 'D:\OneDrive\CODE\repo-governance-hub\.governance\session-compaction-trigger-policy.json'
Get-Content -Raw 'D:\OneDrive\CODE\repo-governance-hub\.governance\external-baseline-policy.json'
Get-Content -Raw 'D:\OneDrive\CODE\repo-governance-hub\.governance\failure-replay\policy.json'
Get-Content -Raw 'D:\OneDrive\CODE\repo-governance-hub\.governance\failure-replay\replay-cases.json'
Get-Content -Raw 'D:\OneDrive\CODE\repo-governance-hub\docs\governance\verification-entrypoints.md'
Get-Content -Raw 'D:\OneDrive\CODE\repo-governance-hub\docs\governance\failure-replay-policy.md'
Get-Content -Raw 'D:\OneDrive\CODE\repo-governance-hub\docs\governance\governance-noise-budget.md'
Get-Content -Raw 'D:\OneDrive\CODE\repo-governance-hub\docs\governance\cross-repo-compatibility-gate.md'
Get-Content -Raw 'D:\OneDrive\CODE\repo-governance-hub\templates\change-evidence.md'
Get-Content -Raw 'D:\OneDrive\CODE\repo-governance-hub\tests\clarification-mode.tests.ps1'
Get-Content -Raw 'D:\OneDrive\CODE\repo-governance-hub\tests\repo-governance-hub.full-fast.tests.ps1'
```

### Contract / invariant gate
```powershell
Get-ChildItem schemas/jsonschema/*.json |
  ForEach-Object { Get-Content -Raw $_.FullName | ConvertFrom-Json > $null }
```

### Linkage checks
```powershell
@(
  @{Name='Research doc exists'; Ok=(Test-Path 'docs/research/repo-governance-hub-borrowing-review.md')},
  @{Name='Docs index updated'; Ok=([bool](Select-String -Path 'docs/README.md' -Pattern 'Mechanism Adoption Matrix' -Quiet))},
  @{Name='Research doc has decision rule'; Ok=([bool](Select-String -Path 'docs/research/repo-governance-hub-borrowing-review.md' -Pattern '## Decision Rule' -Quiet))},
  @{Name='Research doc has formal matrix'; Ok=([bool](Select-String -Path 'docs/research/repo-governance-hub-borrowing-review.md' -Pattern '## Formal Decision Matrix' -Quiet))},
  @{Name='Research doc has boundary exclusions'; Ok=([bool](Select-String -Path 'docs/research/repo-governance-hub-borrowing-review.md' -Pattern '## Boundary Exclusions' -Quiet))}
) | ForEach-Object { "{0}: {1}" -f $_.Name, ($(if($_.Ok){'OK'}else{'FAIL'})) }
```

## Verification
### Results
- `contract/invariant`: schema JSON parse passed
- `Research doc exists: OK`
- `Docs index updated: OK`
- `Research doc has decision rule: OK`
- `Research doc has formal matrix: OK`
- `Research doc has boundary exclusions: OK`

## Gate Status
| gate | status | reason | alternative_verification | evidence_link | expires_at |
|---|---|---|---|---|---|
| build | `gate_na` | runtime services and build entrypoints still do not exist in this repo | docs index and research linkage checks | `docs/change-evidence/20260417-repo-governance-hub-mechanism-adoption-matrix.md` | `2026-05-31` |
| test | `gate_na` | no repository test harness or CI pipeline is landed yet | document structure checks plus repo-local schema parse | `docs/change-evidence/20260417-repo-governance-hub-mechanism-adoption-matrix.md` | `2026-05-31` |
| contract/invariant | `active` | schema integrity remains the hardest machine-verifiable contract in this repository | JSON schema parse completed successfully | `docs/change-evidence/20260417-repo-governance-hub-mechanism-adoption-matrix.md` | `n/a` |
| hotspot | `gate_na` | no runtime doctor or health entrypoint exists yet | document boundary review and adoption sequencing were updated explicitly | `docs/change-evidence/20260417-repo-governance-hub-mechanism-adoption-matrix.md` | `2026-05-31` |

## Risks
- The research document formalizes adoption timing, but it does not yet create the new specs, schemas, or policy files.
- Several deferred mechanisms still depend on `apps/`, `packages/`, `infra/`, `tests/`, or historical runtime telemetry.
- Because the repository has no `.git` worktree, rollback still depends on snapshot copies rather than `git restore`.

## Rollback
Restore the pre-edit snapshots from:
- `docs/change-evidence/snapshots/20260417-repo-governance-hub-mechanism-adoption-matrix/`

Restore commands:
```powershell
Copy-Item `
  'docs/change-evidence/snapshots/20260417-repo-governance-hub-mechanism-adoption-matrix/docs--README.md' `
  'docs/README.md' -Force

Copy-Item `
  'docs/change-evidence/snapshots/20260417-repo-governance-hub-mechanism-adoption-matrix/docs--research--repo-governance-hub-borrowing-review.md' `
  'docs/research/repo-governance-hub-borrowing-review.md' -Force
```

Then remove the added evidence file if a full rollback is needed:
```powershell
Remove-Item 'docs/change-evidence/20260417-repo-governance-hub-mechanism-adoption-matrix.md' -Force
```

## issue_id / clarification_mode
- `issue_id`: `repo-governance-hub-mechanism-adoption-matrix-20260417`
- `attempt_count`: `0`
- `clarification_mode`: `direct_fix`
- `clarification_scenario`: `plan`
- `clarification_questions`: `[]`
- `clarification_answers`: `[]`
