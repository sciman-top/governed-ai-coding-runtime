# 2026-04-17 Governance Kernel Realignment

## Summary
Realigned the project from a broad platform-shaped roadmap toward a governance-kernel-first roadmap.

## Basis
- User request to turn the assessment into repo-native planning assets.
- Existing accepted ADRs already established `control-plane-first`, `single-agent baseline first`, and `no multi-repo distribution in MVP`.
- The active roadmap, backlog, and issue seeding script still leaned too heavily toward broad platform buildout before the governance kernel contract family was complete.

## Files Changed
- Added `docs/adrs/0005-governance-kernel-and-control-packs-before-platform-breadth.md`
- Updated `docs/README.md`
- Updated `docs/roadmap/governed-ai-coding-runtime-90-day-plan.md`
- Updated `docs/backlog/mvp-backlog-seeds.md`
- Updated `docs/backlog/issue-ready-backlog.md`
- Updated `docs/backlog/issue-seeds.yaml`
- Updated `scripts/github/create-roadmap-issues.ps1`

## Snapshots
Because the repository has no `.git` worktree, pre-edit snapshots were stored at:
- `docs/change-evidence/snapshots/20260417-governance-kernel-realignment/`

## Commands
### Snapshot existing files
```powershell
$slug='20260417-governance-kernel-realignment'
$snapDir = Join-Path 'docs/change-evidence/snapshots' $slug
New-Item -ItemType Directory -Force -Path $snapDir | Out-Null
$files = @(
  'docs/README.md',
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
Get-ChildItem schemas/jsonschema/*.json |
  ForEach-Object { Get-Content -Raw $_.FullName | ConvertFrom-Json > $null }
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
$errors
```
Result: `POWERSHELL_PARSE_OK`

### Linkage checks
```powershell
@(
  @{Name='ADR file exists'; Ok=(Test-Path 'docs/adrs/0005-governance-kernel-and-control-packs-before-platform-breadth.md')},
  @{Name='Docs index references ADR-0005'; Ok=([bool](Select-String -Path 'docs/README.md' -Pattern 'ADR-0005' -Quiet))},
  @{Name='Roadmap references ADR-0005'; Ok=([bool](Select-String -Path 'docs/roadmap/governed-ai-coding-runtime-90-day-plan.md' -Pattern 'ADR-0005' -Quiet))},
  @{Name='Backlog has GAP-018'; Ok=([bool](Select-String -Path 'docs/backlog/issue-ready-backlog.md' -Pattern 'GAP-018' -Quiet))},
  @{Name='Issue seeds has GAP-018'; Ok=([bool](Select-String -Path 'docs/backlog/issue-seeds.yaml' -Pattern 'GAP-018' -Quiet))},
  @{Name='Script uses Governance Kernel Alignment epic'; Ok=([bool](Select-String -Path 'scripts/github/create-roadmap-issues.ps1' -Pattern 'Governance Kernel Alignment' -Quiet))}
) | ForEach-Object { "{0}: {1}" -f $_.Name, ($(if($_.Ok){'OK'}else{'FAIL'})) }
```
Result:
- `ADR file exists: OK`
- `Docs index references ADR-0005: OK`
- `Roadmap references ADR-0005: OK`
- `Backlog has GAP-018: OK`
- `Issue seeds has GAP-018: OK`
- `Script uses Governance Kernel Alignment epic: OK`

## Gate Status
| gate | status | reason | alternative_verification | evidence_link | expires_at |
|---|---|---|---|---|---|
| build | `gate_na` | runtime services and build entrypoints still do not exist in this repo | roadmap/backlog/script alignment checks | `docs/change-evidence/20260417-governance-kernel-realignment.md` | `2026-05-31` |
| test | `gate_na` | no repository test harness or CI pipeline is landed yet | PowerShell script parsing plus planning artifact linkage checks | `docs/change-evidence/20260417-governance-kernel-realignment.md` | `2026-05-31` |
| contract/invariant | `active` | schema integrity remains the hardest machine-verifiable contract | schema JSON parse | `docs/change-evidence/20260417-governance-kernel-realignment.md` | `n/a` |
| hotspot | `gate_na` | no runtime doctor or health entrypoint exists yet | roadmap/backlog/script drift checks | `docs/change-evidence/20260417-governance-kernel-realignment.md` | `2026-05-31` |

## Rollback
Restore the pre-edit snapshots from:
- `docs/change-evidence/snapshots/20260417-governance-kernel-realignment/`

Files can be restored one-by-one by copying the snapshot version back over:
```powershell
Copy-Item \
  'docs/change-evidence/snapshots/20260417-governance-kernel-realignment/docs--roadmap--governed-ai-coding-runtime-90-day-plan.md' \
  'docs/roadmap/governed-ai-coding-runtime-90-day-plan.md' -Force
```

## Outcome
The active planning baseline now states that the repository should evolve as a governance kernel plus bounded reuse layer. The roadmap, backlog, issue seeds, and GitHub seeding script now all point at the same first-order priorities.
