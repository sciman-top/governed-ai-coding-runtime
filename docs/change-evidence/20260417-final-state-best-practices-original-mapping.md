# 2026-04-17 FinalStateBestPractices Original Mapping

## Summary
Added a formal mapping review that compares `FinalStateBestPractices（原稿）.md` against the repository's active source-of-truth, then records which sections fit, which need adaptation, and which should not be promoted into the live project spec.

## Basis
- User requested a concrete mapping table from the original manuscript into the active project documents.
- The original manuscript is a strong end-state governance prompt, but it is broader and more multi-agent-oriented than the repository's current AI-coding-focused baseline.
- The repository already treats `docs/FinalStateBestPractices.md` as a north-star bridge rather than as the direct fact source.

## Scope Of This Change
This change only adds:
- one review document under `docs/reviews/`
- one docs index entry under `docs/README.md`
- one change-evidence file

The worktree already contained earlier uncommitted project changes before this mapping pass. Those were left untouched.

## Files Changed
- Added `docs/reviews/2026-04-17-final-state-best-practices-original-mapping.md`
- Updated `docs/README.md`
- Added `docs/change-evidence/20260417-final-state-best-practices-original-mapping.md`

## Commands

### Contract / invariant gate
```powershell
$ErrorActionPreference='Stop'
Get-ChildItem schemas/jsonschema/*.json |
  ForEach-Object { Get-Content -Raw $_.FullName | ConvertFrom-Json > $null }
'SCHEMA_PARSE_OK'
```
Result: `SCHEMA_PARSE_OK`

### Active Markdown link check
```powershell
$ErrorActionPreference='Stop'
$roots = @('README.md','AGENTS.md') +
  (Get-ChildItem docs -Recurse -Filter *.md |
    Where-Object { $_.FullName -notmatch '\\change-evidence\\' } |
    ForEach-Object { $_.FullName }) +
  (Get-ChildItem schemas -Recurse -Filter *.md | ForEach-Object { $_.FullName })
$missing=@()
foreach($path in $roots){
  $f=Get-Item $path
  $text=Get-Content -Raw $f.FullName
  $matches=[regex]::Matches($text, '\[[^\]]+\]\(([^)]+)\)')
  foreach($m in $matches){
    $target=$m.Groups[1].Value
    if($target -match '^(https?:|mailto:|#)'){ continue }
    $clean=($target -split '#')[0]
    if([string]::IsNullOrWhiteSpace($clean)){ continue }
    $candidate=Join-Path $f.DirectoryName $clean
    if(-not (Test-Path $candidate)){ $missing += "$($f.FullName): $target" }
  }
}
if($missing.Count){ $missing; exit 1 } else { 'ACTIVE_MARKDOWN_LINKS_OK' }
```
Result: `ACTIVE_MARKDOWN_LINKS_OK`

### Diff whitespace check
```powershell
git diff --check
```
Result: exit code `0`; only CRLF conversion warnings were emitted for existing tracked files in the working tree.

### Working tree visibility
```powershell
git status --short
```
Result: current worktree is dirty due to this change plus earlier uncommitted edits already present before this pass.

## Gate Status
| gate | status | reason | alternative_verification | evidence_link | expires_at |
|---|---|---|---|---|---|
| build | `gate_na` | runtime services and build entrypoints still do not exist in this docs-first/contracts-first repo | docs index and active markdown link checks | `docs/change-evidence/20260417-final-state-best-practices-original-mapping.md` | `2026-05-31` |
| test | `gate_na` | no repository test harness or CI pipeline is landed yet as runnable product code | `git diff --check` plus focused document review mapping | `docs/change-evidence/20260417-final-state-best-practices-original-mapping.md` | `2026-05-31` |
| contract/invariant | `active` | schema integrity is still the strongest machine-verifiable contract in the repo | schema JSON parse | `docs/change-evidence/20260417-final-state-best-practices-original-mapping.md` | `n/a` |
| hotspot | `gate_na` | no runtime doctor or health entrypoint exists yet | active markdown link check and source-of-truth mapping review | `docs/change-evidence/20260417-final-state-best-practices-original-mapping.md` | `2026-05-31` |

## Rollback
Remove the files added by this pass and revert the single docs index line if needed:
- `docs/reviews/2026-04-17-final-state-best-practices-original-mapping.md`
- `docs/change-evidence/20260417-final-state-best-practices-original-mapping.md`
- remove the corresponding review link from `docs/README.md`

This rollback should be performed carefully because the working tree already contains unrelated uncommitted changes from prior work.

## Outcome
The repository now has a reusable mapping review that clearly separates:
- what the original manuscript contributes as a governance checklist
- what the active project already covers
- what should be adapted later
- what should not be promoted into the live project spec
