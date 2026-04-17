# 20260417 Pre-Implementation Deep Audit And Doc Refresh

## Goal
- 在进入运行时代码实现前完成一次全仓复审。
- 收紧根入口、docs 索引和项目规则承接，让下一次实现直接进入 Phase 0 baseline。

## Rule Landing
- Current landing point: `D:\OneDrive\CODE\governed-ai-coding-runtime`
- Target destination:
  - documentation, reviews, and evidence: `docs/`
  - project rule mapping: `AGENTS.md`
- Active rule path: `AGENTS.md`
- Risk tier: low
- Change type: documentation and rule-alignment refresh
- Rollback: revert this change set in git, or restore the modified docs from the previous commit and remove the two added audit files.

## Clarification State
- issue_id: `pre-implementation-deep-audit-and-doc-refresh`
- attempt_count: `1`
- clarification_mode: `direct_fix`
- clarification_scenario: `plan`
- clarification_questions: `[]`
- clarification_answers: `[]`

## Codex Platform Diagnostics

| cmd | exit_code | key_output | classification |
|---|---:|---|---|
| `codex --version` | `0` | `codex-cli 0.121.0` | active |
| `codex --help` | `0` | commands include `exec`, `review`, `mcp`, `apply`, `cloud`, `features`, `help` | active |
| `codex status` | `1` | `Error: stdin is not a terminal` | `platform_na` |

### platform_na
- reason: `codex status` requires an interactive terminal in this execution context.
- alternative_verification: recorded `codex --version`, `codex --help`, current working directory, and active rule path.
- evidence_link: `docs/change-evidence/20260417-pre-implementation-deep-audit-and-doc-refresh.md`
- expires_at: `2026-05-31`

## Basis
- `README.md`
- `docs/README.md`
- `docs/architecture/README.md`
- `docs/specs/README.md`
- `docs/plans/README.md`
- `docs/backlog/README.md`
- `docs/reviews/README.md`
- `docs/change-evidence/README.md`
- `AGENTS.md`
- `docs/prd/governed-ai-coding-runtime-prd.md`
- `docs/product/interaction-model.md`
- `docs/architecture/minimum-viable-governance-loop.md`
- `docs/architecture/governed-ai-coding-runtime-target-architecture.md`
- `docs/architecture/mvp-stack-vs-target-stack.md`
- `docs/architecture/compatibility-matrix.md`
- `docs/roadmap/governed-ai-coding-runtime-90-day-plan.md`
- `docs/backlog/mvp-backlog-seeds.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/plans/phase-0-runnable-baseline-implementation-plan.md`
- `schemas/README.md`
- `schemas/examples/README.md`
- `schemas/catalog/schema-catalog.yaml`
- `scripts/github/create-roadmap-issues.ps1`

## Pre-Existing Worktree State
`git status --short` before this change showed:
- modified: `AGENTS.md`
- deleted: historical file `FinalStateBestPractices（原稿）.md`
- untracked: `docs/change-evidence/20260417-commit-message-language-guideline.md`

This audit refresh preserves those changes and does not revert them.

## Changes
- Updated `README.md` to foreground the latest audit, latest evidence, current Phase 0 plan, and active verification boundary.
- Updated `docs/README.md` to add the current working set, planning chain, navigation aids, execution posture, verification quickstart, latest review, and latest evidence.
- Added `docs/architecture/README.md` to define the architecture reading order and document roles.
- Added `docs/specs/README.md` to organize the contract families and spec/schema pairing rule.
- Added `docs/plans/README.md` to mark the current executable plan and required Task 0 starting posture.
- Added `docs/backlog/README.md` to define the roles of the phase seeds, issue-ready backlog, issue YAML, and GitHub seeding script.
- Added `docs/reviews/README.md` to distinguish the current review baseline from historical review milestones.
- Added `docs/change-evidence/README.md` to explain evidence semantics, snapshot purpose, and active verification boundaries.
- Updated `docs/plans/phase-0-runnable-baseline-implementation-plan.md` so its source inputs and starting instructions reflect the latest review/evidence baseline and Task 0-first posture.
- Updated `AGENTS.md` to align the project承接来源到 `GlobalUser/AGENTS.md v9.39` and reflect git-first rollback posture.
- Added `docs/reviews/2026-04-17-pre-implementation-deep-audit-and-doc-refresh.md`.
- Added this evidence file.

## Findings Addressed
1. The next operator starting point was not obvious from the repo entry files.
2. Project rules lagged the current global rule version and current git-backed rollback reality.
3. Active verification scope for live docs versus historical evidence archives was implicit rather than explicit.
4. Subdirectory-level navigation for plans, backlog, reviews, and evidence was missing, so operators still had to rediscover filenames manually.
5. Architecture and spec families lacked local indexes, so the root docs index still carried too much navigation burden.

## Gate Results

| gate | status | command | result | reason | alternative_verification | evidence_link | expires_at |
|---|---|---|---|---|---|---|---|
| build | `gate_na` | `n/a` | not run | runtime services and build entrypoints still do not exist | verified repo entry docs, roadmap, backlog, plan, and rules alignment | this file | `2026-05-31` |
| test | `gate_na` | `n/a` | not run | no repository test harness or CI pipeline exists yet | schema/example/script/doc integrity checks executed manually | this file | `2026-05-31` |
| contract/invariant | `active` | `Get-ChildItem schemas/jsonschema/*.json \| ForEach-Object { Get-Content -Raw $_.FullName \| ConvertFrom-Json > $null }` | pass | schema JSON remains the hardest machine-verifiable contract | schema example validation and catalog pairing also passed | this file | `n/a` |
| hotspot | `gate_na` | `n/a` | not run | no runtime doctor or health entrypoint exists yet | scoped active-doc review plus roadmap/backlog/plan drift review | this file | `2026-05-31` |

## Verification Commands

### Contract / invariant
```powershell
$ErrorActionPreference='Stop'
Get-ChildItem schemas/jsonschema/*.json | Sort-Object Name |
  ForEach-Object {
    Get-Content -Raw $_.FullName | ConvertFrom-Json > $null
    "SCHEMA_JSON_OK $($_.Name)"
  }
```

Result:
- exit_code: `0`
- key_output: all `16` schema files parsed successfully

### Schema examples
```powershell
$schemaMap = @{}
Get-ChildItem schemas/jsonschema/*.json |
  ForEach-Object { $schemaMap[$_.BaseName -replace '\.schema$',''] = $_.FullName }
Get-ChildItem -Recurse -File schemas/examples -Filter *.json |
  ForEach-Object {
    $dir = Split-Path $_.DirectoryName -Leaf
    Test-Json -Json (Get-Content -Raw $_.FullName) -Schema (Get-Content -Raw $schemaMap[$dir])
  }
```

Result:
- exit_code: `0`
- key_output: all current schema examples validated, including `control-pack`, `repo-profile`, `hook-contract`, `repo-map-context-shaping`, and `waiver-and-exception`

### Schema catalog pairing
```powershell
# Parse path/source_spec entries from schemas/catalog/schema-catalog.yaml,
# verify every referenced file exists, and verify no schema/spec file is uncatalogued.
```

Result:
- exit_code: `0`
- key_output: `CATALOG_PAIRING_OK`

### PowerShell script parse
```powershell
$tokens = $null
$errors = $null
[void][System.Management.Automation.Language.Parser]::ParseFile(
  (Resolve-Path 'scripts/github/create-roadmap-issues.ps1'),
  [ref]$tokens,
  [ref]$errors
)
if ($errors.Count -gt 0) { throw 'PowerShell parser errors found' }
```

Result:
- exit_code: `0`
- key_output: `SCRIPT_PARSE_OK scripts/github/create-roadmap-issues.ps1`

### Issue backlog and YAML alignment
```powershell
# Compare GAP IDs between docs/backlog/issue-ready-backlog.md and docs/backlog/issue-seeds.yaml.
```

Result:
- exit_code: `0`
- key_output: `BACKLOG_YAML_IDS_OK count=17`

### Diff hygiene
```powershell
git diff --check
```

Result:
- exit_code: `0`
- key_output: no diff-format errors; only Git line-ending normalization warnings for tracked Markdown files

### Scoped active-doc links
```powershell
# Check relative markdown links only in live repo entry docs, directory indexes,
# architecture, ADRs, specs, roadmap/backlog/plan docs, schemas READMEs,
# and the latest review doc.
```

Result:
- exit_code: `0`
- key_output: `SCOPED_ACTIVE_DOC_LINKS_OK`

### Naming drift scan
```powershell
rg -n "governed-agent-platform|Governed Agent Platform|governed agent platform" `
  -g '!docs/change-evidence/**' `
  -g '!docs/reviews/**' .
```

Result:
- exit_code: `0`
- key_output: only expected historical references remain in `README.md` and rename ADR

### Scoped active-doc verification note
Active verification for this repository intentionally excludes:
- `docs/change-evidence/**`
- `docs/change-evidence/snapshots/**`
- ad hoc worktree archives or copied historical trees

Reason:
- those locations intentionally preserve historical paths, command snippets, and old naming for auditability, so treating them as active docs would create false failures.

## Risks
- The repo still lacks a repo-local verification script, so verification remains a documented manual sequence rather than a single entrypoint.
- `build`, `test`, and `hotspot` remain `gate_na`.
- The working tree was already dirty before this pass; the next implementation session still needs to freeze or explicitly carry those changes forward.

## Rollback
- Preferred: `git revert <commit>` after this change is committed.
- Manual rollback:
  - restore `README.md`
  - restore `docs/README.md`
  - restore `AGENTS.md`
  - delete `docs/reviews/2026-04-17-pre-implementation-deep-audit-and-doc-refresh.md`
  - delete `docs/change-evidence/20260417-pre-implementation-deep-audit-and-doc-refresh.md`
