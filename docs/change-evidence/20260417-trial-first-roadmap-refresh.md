# 2026-04-17 Trial-First Roadmap Refresh

## Summary
Reordered the active planning baseline so the project targets a first trialable governed slice within 2-3 weeks, then layers controlled write, delivery assurance, and second-repo reuse on top.

## Basis
- User request to make the project trialable earlier and iterate through real usage feedback.
- Existing PRD and interaction model already define the product as an API-first governed runtime with CLI/scripted entrypoints and a minimal console rather than a full IDE shell.
- Existing roadmap delayed the first operator-visible end-to-end trial too far into the schedule.
- The governance-kernel contract family is already landed, so the next planning baseline should prioritize runnable trial slices instead of more contract-completion work.

## Files Changed
- Updated `docs/roadmap/governed-ai-coding-runtime-90-day-plan.md`
- Updated `docs/backlog/mvp-backlog-seeds.md`
- Updated `docs/backlog/issue-ready-backlog.md`
- Updated `docs/backlog/issue-seeds.yaml`
- Updated `scripts/github/create-roadmap-issues.ps1`

## Snapshots
Because the repository has no `.git` worktree, pre-edit snapshots were stored at:
- `docs/change-evidence/snapshots/20260417-trial-first-roadmap-refresh/`

## Commands
### Snapshot existing files
```powershell
$slug='20260417-trial-first-roadmap-refresh'
$snapDir = Join-Path 'docs/change-evidence/snapshots' $slug
New-Item -ItemType Directory -Force -Path $snapDir | Out-Null
$files = @(
  'docs/roadmap/governed-ai-coding-runtime-90-day-plan.md',
  'docs/backlog/mvp-backlog-seeds.md',
  'docs/backlog/issue-ready-backlog.md',
  'docs/backlog/issue-seeds.yaml',
  'scripts/github/create-roadmap-issues.ps1'
)
foreach($f in $files){
  $name = ($f -replace '[\\/]+','--')
  Copy-Item $f (Join-Path $snapDir $name) -Force
}
```

### Contract / invariant gate
```powershell
$schemaErrors = @()
Get-ChildItem 'schemas/jsonschema/*.json' |
  ForEach-Object {
    try {
      Get-Content -Raw $_.FullName | ConvertFrom-Json > $null
    } catch {
      $schemaErrors += "SCHEMA_PARSE_FAIL $($_.FullName): $($_.Exception.Message)"
    }
  }
if ($schemaErrors.Count -eq 0) { 'SCHEMA_PARSE_OK' } else { $schemaErrors }
```
Result: `SCHEMA_PARSE_OK`

### Script parse verification
```powershell
$tokens = $null
$errors = $null
[void][System.Management.Automation.Language.Parser]::ParseFile(
  (Resolve-Path 'scripts/github/create-roadmap-issues.ps1'),
  [ref]$tokens,
  [ref]$errors
)
if ($null -eq $errors -or $errors.Count -eq 0) {
  'POWERSHELL_PARSE_OK'
} else {
  $errors | ForEach-Object { "POWERSHELL_PARSE_FAIL $($_.Message)" }
}
```
Result: `POWERSHELL_PARSE_OK`

### Linkage checks
```powershell
@(
  @{Name='Roadmap has 2-3 week trial slice'; Ok=([bool](Select-String -Path 'docs/roadmap/governed-ai-coding-runtime-90-day-plan.md' -Pattern '2-3 week trial slice' -Quiet))},
  @{Name='Roadmap requires read-only end-to-end by week 3'; Ok=([bool](Select-String -Path 'docs/roadmap/governed-ai-coding-runtime-90-day-plan.md' -Pattern 'one governed session can run a read-only task end-to-end' -Quiet))},
  @{Name='Backlog has CLI trial entrypoint'; Ok=([bool](Select-String -Path 'docs/backlog/issue-ready-backlog.md' -Pattern 'CLI Or Scripted Trial Entrypoint' -Quiet))},
  @{Name='Issue seeds has GAP-017'; Ok=([bool](Select-String -Path 'docs/backlog/issue-seeds.yaml' -Pattern 'GAP-017' -Quiet))},
  @{Name='Script has read-only trial epic'; Ok=([bool](Select-String -Path 'scripts/github/create-roadmap-issues.ps1' -Pattern 'First Read-Only Governed Trial Slice' -Quiet))},
  @{Name='Script has CLI trial task'; Ok=([bool](Select-String -Path 'scripts/github/create-roadmap-issues.ps1' -Pattern 'Add CLI or scripted entrypoint for the first governed trial' -Quiet))}
) | ForEach-Object { "{0}: {1}" -f $_.Name, ($(if($_.Ok){'OK'}else{'FAIL'})) }
```
Result:
- `Roadmap has 2-3 week trial slice: OK`
- `Roadmap requires read-only end-to-end by week 3: OK`
- `Backlog has CLI trial entrypoint: OK`
- `Issue seeds has GAP-017: OK`
- `Script has read-only trial epic: OK`
- `Script has CLI trial task: OK`

## Gate Status
| gate | status | reason | alternative_verification | evidence_link | expires_at |
|---|---|---|---|---|---|
| build | `gate_na` | runtime services and build entrypoints still do not exist in this repo | roadmap/backlog/script alignment checks | `docs/change-evidence/20260417-trial-first-roadmap-refresh.md` | `2026-05-31` |
| test | `gate_na` | no repository test harness or CI pipeline is landed yet as runnable product code | PowerShell script parsing plus planning artifact linkage checks | `docs/change-evidence/20260417-trial-first-roadmap-refresh.md` | `2026-05-31` |
| contract/invariant | `active` | schema integrity remains the hardest machine-verifiable contract | schema JSON parse | `docs/change-evidence/20260417-trial-first-roadmap-refresh.md` | `n/a` |
| hotspot | `gate_na` | no runtime doctor or health entrypoint exists yet | trial-first roadmap/backlog/script drift checks | `docs/change-evidence/20260417-trial-first-roadmap-refresh.md` | `2026-05-31` |

## Rollback
Restore the pre-edit snapshots from:
- `docs/change-evidence/snapshots/20260417-trial-first-roadmap-refresh/`

Files can be restored one-by-one by copying the snapshot version back over:
```powershell
Copy-Item `
  'docs/change-evidence/snapshots/20260417-trial-first-roadmap-refresh/docs--roadmap--governed-ai-coding-runtime-90-day-plan.md' `
  'docs/roadmap/governed-ai-coding-runtime-90-day-plan.md' -Force
```

## Outcome
The active planning baseline now makes early trialability explicit: runnable baseline in week 1, read-only governed trial by week 3, controlled write and approval after that, and reuse/hardening only after the first real feedback loop exists.
