# 2026-04-17 Second Project Audit And Plan Hardening Evidence

## Goal
Re-audit the repository before runtime coding starts, harden the planning baseline, and add the missing control-pack metadata contract required by ADR-0005.

## Rule Landing
- Current landing point: `D:\OneDrive\CODE\governed-ai-coding-runtime`
- Target destination:
  - documentation, review, and evidence: `docs/`
  - machine-readable contracts and examples: `schemas/`
  - GitHub planning helper text: `scripts/`
- Active rule path: `AGENTS.md`
- Risk tier: low
- Change type: additive contract plus planning/index alignment
- Rollback: revert this change set in git, or remove the files added below and restore modified docs from the previous commit.

## Clarification State
- issue_id: `second-project-audit-plan-hardening`
- attempt_count: `1`
- clarification_mode: `direct_fix`
- clarification_scenario: `plan`
- clarification_questions: `[]`
- clarification_answers: `[]`

## Codex Platform Diagnostics

| timestamp | cmd | exit_code | key_output | classification |
|---|---:|---:|---|---|
| `2026-04-17T02:36:57+08:00` | `codex --version` | `0` | `codex-cli 0.121.0` | active |
| `2026-04-17T02:36:57+08:00` | `codex --help` | `0` | commands include `exec`, `review`, `mcp`, `apply`, `cloud`, `features`, `help` | active |
| `2026-04-17T02:37:08+08:00` | `codex status` | `1` | `Error: stdin is not a terminal` | `platform_na` |

### platform_na
- reason: `codex status` requires an interactive terminal in this execution context.
- alternative_verification: recorded `codex --version`, `codex --help`, active working directory, branch, and active rule path.
- evidence_link: `docs/change-evidence/20260417-second-project-audit-plan-hardening.md`
- expires_at: `2026-05-31`

## Changes
- Added `docs/specs/control-pack-spec.md`.
- Added `schemas/jsonschema/control-pack.schema.json`.
- Added `schemas/examples/control-pack/minimum-governance-kernel.example.json`.
- Updated schema catalog to `schema_catalog_version: "1.2"` and added `control-pack`.
- Updated schema and docs indexes to expose the new spec, schema, and example.
- Updated PRD, architecture, roadmap, backlog, and issue-seeding text so implementation starts from the complete governance-kernel contract family.
- Added `docs/reviews/2026-04-17-second-project-audit-and-plan-hardening.md`.

## Review Findings Addressed
1. ADR-0005 made control packs first-class, but no machine-readable control-pack contract existed.
2. PRD, architecture, and roadmap document maps still listed the early contract subset.
3. Backlog and script language did not distinguish metadata examples from runtime-consumable control packs.
4. The first implementation slice needed a clearer handoff: build skeleton and verification entrypoints first, then promote the metadata example into an executable pack.

## Gate Results

| gate | status | command | result | reason | alternative_verification | evidence_link | expires_at |
|---|---|---|---|---|---|---|---|
| build | `gate_na` | `n/a` | not run | runtime services and build entrypoints still do not exist | checked README/docs/roadmap/backlog/script alignment | this file | `2026-05-31` |
| test | `gate_na` | `n/a` | not run | no repository test harness or CI pipeline exists yet | parsed PowerShell script and validated schema examples | this file | `2026-05-31` |
| contract/invariant | `active` | `Get-ChildItem schemas/jsonschema/*.json \| ForEach-Object { Get-Content -Raw $_.FullName \| ConvertFrom-Json > $null }` | pass | schema JSON remains the hardest machine-verifiable contract | catalog pairing and example validation also passed | this file | `n/a` |
| hotspot | `gate_na` | `n/a` | not run | no runtime doctor or health entrypoint exists yet | active markdown links, old-name scan, backlog/YAML ID alignment, and control-pack drift checks | this file | `2026-05-31` |

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
- key_output:
  - `SCHEMA_JSON_OK control-pack.schema.json`
  - `SCHEMA_JSON_OK control-registry.schema.json`
  - `SCHEMA_JSON_OK repo-profile.schema.json`
  - `SCHEMA_JSON_OK waiver-and-exception.schema.json`
  - all `15` schema files parsed successfully

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
- key_output:
  - `EXAMPLE_SCHEMA_OK schemas\examples\control-pack\minimum-governance-kernel.example.json`
  - existing hook, knowledge-source, provenance, repo-map, repo-profile, skill-manifest, and waiver examples also validated

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
$tokens=$null
$errors=$null
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

### Active markdown links
```powershell
# Scan active markdown files excluding docs/change-evidence/ for relative markdown links
# and verify each target exists.
```

Result:
- exit_code: `0`
- key_output: `ACTIVE_DOC_LINKS_OK`

### Drift checks
```powershell
# Check control-pack references across PRD, target architecture, roadmap,
# backlog, issue script, docs index, schema README, and schema catalog.
```

Result:
- exit_code: `0`
- key_output: `CONTROL_PACK_DRIFT_CHECK_OK`

```powershell
# Compare GAP IDs between docs/backlog/issue-ready-backlog.md and docs/backlog/issue-seeds.yaml.
```

Result:
- exit_code: `0`
- key_output: `BACKLOG_YAML_IDS_OK count=17`

```powershell
rg -n "governed-agent-platform|Governed Agent Platform|governed agent platform" `
  -g '!docs/change-evidence/**' .
```

Result:
- exit_code: `0`
- key_output: `OLD_NAME_REFERENCES_OK historical_only`

## Compatibility And Data Structure Notes
- E6 applies because `docs/specs/*`, `schemas/jsonschema/*`, and `schemas/catalog/schema-catalog.yaml` changed.
- Compatibility posture: additive. Existing schemas were not renamed or narrowed.
- Schema catalog moved from `1.1` to `1.2` to record the new `control-pack` entry.
- New example validates against its matching schema.
- Cross-artifact reference validation is deferred until a repo-local verification runner exists.

## Residual Risks
- The control-pack schema validates metadata shape only; it does not prove referenced controls, hooks, skills, gates, or eval suites exist.
- Build, test, CI, and hotspot/doctor entrypoints remain missing until implementation bootstrap.
- The GitHub issue seeding script still duplicates issue text instead of reading `docs/backlog/issue-seeds.yaml`.

## Rollback
- Preferred: `git revert <commit>` after this change is committed.
- Manual rollback:
  - delete `docs/specs/control-pack-spec.md`
  - delete `schemas/jsonschema/control-pack.schema.json`
  - delete `schemas/examples/control-pack/minimum-governance-kernel.example.json`
  - delete `docs/reviews/2026-04-17-second-project-audit-and-plan-hardening.md`
  - restore modified README/docs/schema/script files from the previous commit
