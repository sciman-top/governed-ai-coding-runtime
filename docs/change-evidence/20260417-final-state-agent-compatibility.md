# 2026-04-17 Final-State Agent Compatibility Realignment

## Summary
Reframed the project so final-state best practice is the long-term product target while the MVP remains a narrow tracer bullet. Added an agent adapter contract so Codex CLI/App, OpenClaw, Hermes, and future AI coding product shapes can be represented by capability mapping rather than kernel rewrites.

## Basis
- User confirmed the product should target final-state best practice.
- User raised the risk that governance and audit could become a drag on stronger upstream agents.
- User's primary current workflow is Codex CLI/App with user-owned authentication.
- Existing PRD and ADRs already positioned the project as a governed runtime around AI coding agents rather than a replacement IDE or chatbot.

## Clarification Trace
- `issue_id`: `final-state-agent-compatibility`
- `attempt_count`: `1`
- `clarification_mode`: `direct_fix`
- `clarification_scenario`: `plan`
- `clarification_questions`: whether to update the project to target final-state best practice
- `clarification_answers`: user confirmed

## Files Changed
- Updated `README.md`
- Updated `docs/FinalStateBestPractices.md`
- Updated `docs/README.md`
- Added `docs/adrs/0006-final-state-best-practice-agent-compatibility.md`
- Updated `docs/prd/governed-ai-coding-runtime-prd.md`
- Updated `docs/product/interaction-model.md`
- Updated `docs/architecture/governed-ai-coding-runtime-target-architecture.md`
- Updated `docs/architecture/governance-boundary-matrix.md`
- Updated `docs/architecture/compatibility-matrix.md`
- Updated `docs/architecture/mvp-stack-vs-target-stack.md`
- Updated `docs/roadmap/governed-ai-coding-runtime-90-day-plan.md`
- Updated `docs/backlog/mvp-backlog-seeds.md`
- Updated `docs/backlog/issue-ready-backlog.md`
- Updated `docs/backlog/issue-seeds.yaml`
- Added `docs/specs/agent-adapter-contract-spec.md`
- Added `schemas/jsonschema/agent-adapter-contract.schema.json`
- Updated `schemas/catalog/schema-catalog.yaml`
- Updated `schemas/README.md`
- Updated `scripts/github/create-roadmap-issues.ps1`

## Key Decisions
- Final-state best practice is now the north star, not the first-slice implementation checklist.
- Governance is risk-proportional: `observe_only`, `advisory`, `enforced`, and `strict`.
- Codex CLI/App compatibility is the first adapter priority.
- Codex authentication remains upstream user-owned unless a separate explicit integration decision changes that.
- Future agent products integrate by declared capabilities: invocation mode, auth ownership, workspace control, event visibility, mutation model, continuation model, and evidence model.
- Weak integrations degrade to observe-only, advisory, or manual handoff instead of pretending full enforcement exists.

## Commands

### Codex platform diagnostics
```powershell
codex --version
```
Result: `codex-cli 0.121.0`

```powershell
codex --help
```
Result: exit code `0`; key commands included `exec`, `review`, `mcp`, `mcp-server`, `app-server`, `sandbox`, `resume`, `fork`, `cloud`, and `exec-server`.

```powershell
codex status
```
Result: exit code `1`; key output: `Error: 拒绝访问。 (os error 5)`.

`platform_na`:
- `reason`: `codex status` was not usable in this local non-interactive environment because the command failed with OS access denied.
- `alternative_verification`: `codex --version`, `codex --help`, and explicit active repo rule path from `AGENTS.md`.
- `evidence_link`: `docs/change-evidence/20260417-final-state-agent-compatibility.md`
- `expires_at`: `2026-05-31`

### Contract / invariant gate
```powershell
$ErrorActionPreference='Stop'
Get-ChildItem schemas/jsonschema/*.json |
  ForEach-Object { Get-Content -Raw $_.FullName | ConvertFrom-Json > $null }
'SCHEMA_PARSE_OK'
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
if ($errors -and $errors.Count -gt 0) {
  $errors | ForEach-Object { $_.ToString() }
  exit 1
} else {
  'POWERSHELL_PARSE_OK'
}
```
Result: `POWERSHELL_PARSE_OK`

### Schema catalog link check
```powershell
$ErrorActionPreference='Stop'
$catalog = Get-Content -Raw schemas/catalog/schema-catalog.yaml
$missing = @()
foreach ($line in ($catalog -split "`n")) {
  if ($line -match '^\s+path:\s+(.+)$') {
    $path = $Matches[1].Trim()
    if (-not (Test-Path $path)) { $missing += $path }
  }
  if ($line -match '^\s+source_spec:\s+(.+)$') {
    $path = $Matches[1].Trim()
    if (-not (Test-Path $path)) { $missing += $path }
  }
}
if ($missing.Count -gt 0) { $missing; exit 1 } else { 'SCHEMA_CATALOG_LINKS_OK' }
```
Result: `SCHEMA_CATALOG_LINKS_OK`

### Positioning consistency check
```powershell
$ErrorActionPreference='Stop'
$files = @(
  'README.md',
  'docs/README.md',
  'docs/prd/governed-ai-coding-runtime-prd.md',
  'docs/product/interaction-model.md',
  'docs/architecture/compatibility-matrix.md',
  'docs/architecture/mvp-stack-vs-target-stack.md',
  'docs/architecture/governed-ai-coding-runtime-target-architecture.md',
  'docs/roadmap/governed-ai-coding-runtime-90-day-plan.md',
  'docs/backlog/issue-ready-backlog.md',
  'docs/backlog/issue-seeds.yaml',
  'scripts/github/create-roadmap-issues.ps1',
  'schemas/catalog/schema-catalog.yaml',
  'schemas/README.md'
)
$needles = @('ADR-0006','final-state','Codex','agent adapter')
foreach ($needle in $needles) {
  $hits = Select-String -Path $files -Pattern $needle -SimpleMatch -ErrorAction SilentlyContinue
  if (-not $hits) { "MISSING:$needle"; exit 1 }
}
'POSITIONING_TERMS_PRESENT_OK'
```
Result: `POSITIONING_TERMS_PRESENT_OK`

### Roadmap / backlog / script drift check
```powershell
rg -n "GAP-001|GAP-007|Final-State|Codex-Compatible|Codex-compatible" `
  docs/backlog/issue-ready-backlog.md `
  docs/backlog/issue-seeds.yaml `
  scripts/github/create-roadmap-issues.ps1 `
  docs/roadmap/governed-ai-coding-runtime-90-day-plan.md
```
Result: exit code `0`; updated GAP-001 and GAP-007 wording appeared in backlog, issue seeds, roadmap, and seeding script.

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

## Gate Status
| gate | status | reason | alternative_verification | evidence_link | expires_at |
|---|---|---|---|---|---|
| build | `gate_na` | runtime services and build entrypoints still do not exist in this docs-first/contracts-first repo | root/docs/roadmap/backlog/script alignment checks | `docs/change-evidence/20260417-final-state-agent-compatibility.md` | `2026-05-31` |
| test | `gate_na` | no repository test harness or CI pipeline is landed yet as runnable product code | PowerShell script parsing plus positioning consistency checks | `docs/change-evidence/20260417-final-state-agent-compatibility.md` | `2026-05-31` |
| contract/invariant | `active` | schema integrity is the current machine-verifiable contract | JSON schema parse and schema catalog link check | `docs/change-evidence/20260417-final-state-agent-compatibility.md` | `n/a` |
| hotspot | `gate_na` | no runtime doctor or health entrypoint exists yet | active markdown link check, roadmap/backlog/script drift check, and compatibility-positioning scan | `docs/change-evidence/20260417-final-state-agent-compatibility.md` | `2026-05-31` |

## Rollback
The repository now has a git worktree, so rollback should use normal git review before commit:
- revert modified files from this change set
- remove added files:
  - `docs/adrs/0006-final-state-best-practice-agent-compatibility.md`
  - `docs/specs/agent-adapter-contract-spec.md`
  - `schemas/jsonschema/agent-adapter-contract.schema.json`
  - `docs/change-evidence/20260417-final-state-agent-compatibility.md`

The unrelated untracked file `FinalStateBestPractices（原稿）.md` was left untouched.

## Outcome
The project now explicitly targets final-state best practice while protecting MVP discipline. Codex CLI/App compatibility is the first adapter path, and future agent products are handled through a capability contract instead of kernel-specific product assumptions.
