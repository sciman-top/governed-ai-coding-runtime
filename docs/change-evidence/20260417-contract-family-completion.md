# 2026-04-17 Contract Family Completion

## Summary
Completed the missing governance contract family by adding six new specs and six matching JSON Schema drafts, then wiring them into the docs and schema catalogs.

## Basis
- ADR-0005 established that the repository should prioritize governance-kernel contracts before broader platform breadth.
- The current roadmap and backlog already identified missing contract families for `hook`, `skill manifest`, `knowledge source`, `waiver`, `provenance`, and `repo map`.
- The repository remains `docs-first / contracts-first`, so the next correct move was to land spec and schema pairs before runtime implementation.

## Files Changed
### Added specs
- `docs/specs/hook-contract-spec.md`
- `docs/specs/skill-manifest-spec.md`
- `docs/specs/knowledge-source-spec.md`
- `docs/specs/waiver-and-exception-spec.md`
- `docs/specs/provenance-and-attestation-spec.md`
- `docs/specs/repo-map-context-shaping-spec.md`

### Added schemas
- `schemas/jsonschema/hook-contract.schema.json`
- `schemas/jsonschema/skill-manifest.schema.json`
- `schemas/jsonschema/knowledge-source.schema.json`
- `schemas/jsonschema/waiver-and-exception.schema.json`
- `schemas/jsonschema/provenance-and-attestation.schema.json`
- `schemas/jsonschema/repo-map-context-shaping.schema.json`

### Updated indexes and catalogs
- `docs/README.md`
- `schemas/README.md`
- `schemas/catalog/schema-catalog.yaml`

## Snapshots
Because the repository still has no `.git` worktree, pre-edit snapshots for existing files were stored at:
- `docs/change-evidence/snapshots/20260417-contract-family-completion/`

## Commands
### Snapshot existing files
```powershell
$slug='20260417-contract-family-completion'
$snapDir = Join-Path 'docs/change-evidence/snapshots' $slug
New-Item -ItemType Directory -Force -Path $snapDir | Out-Null
$files = @(
  'docs/README.md',
  'schemas/README.md',
  'schemas/catalog/schema-catalog.yaml'
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

### Linkage checks
```powershell
@(
  'hook-contract-spec.md',
  'skill-manifest-spec.md',
  'knowledge-source-spec.md',
  'waiver-and-exception-spec.md',
  'provenance-and-attestation-spec.md',
  'repo-map-context-shaping-spec.md'
) | ForEach-Object {
  if (-not (Select-String -Path 'docs/README.md' -Pattern $_ -Quiet)) { throw "MISSING_DOC_LINK $_" }
}

@(
  'hook-contract.schema.json',
  'skill-manifest.schema.json',
  'knowledge-source.schema.json',
  'waiver-and-exception.schema.json',
  'provenance-and-attestation.schema.json',
  'repo-map-context-shaping.schema.json'
) | ForEach-Object {
  if (-not (Select-String -Path 'schemas/README.md' -Pattern $_ -Quiet)) { throw "MISSING_SCHEMA_LINK $_" }
}

@(
  'hook-contract',
  'skill-manifest',
  'knowledge-source',
  'waiver-and-exception',
  'provenance-and-attestation',
  'repo-map-context-shaping'
) | ForEach-Object {
  if (-not (Select-String -Path 'schemas/catalog/schema-catalog.yaml' -Pattern $_ -Quiet)) { throw "MISSING_CATALOG_ENTRY $_" }
}
```
Result: `LINKAGE_OK`

## Gate Status
| gate | status | reason | alternative_verification | evidence_link | expires_at |
|---|---|---|---|---|---|
| build | `gate_na` | runtime services and build entrypoints still do not exist in this repo | docs/spec/schema/catalog alignment checks | `docs/change-evidence/20260417-contract-family-completion.md` | `2026-05-31` |
| test | `gate_na` | no repository test harness or CI pipeline is landed yet | schema parse plus linkage checks | `docs/change-evidence/20260417-contract-family-completion.md` | `2026-05-31` |
| contract/invariant | `active` | schema integrity remains the hardest machine-verifiable contract in this repo | JSON schema parse across the full schema set | `docs/change-evidence/20260417-contract-family-completion.md` | `n/a` |
| hotspot | `gate_na` | no runtime doctor or health entrypoint exists yet | docs/spec/schema/catalog drift checks | `docs/change-evidence/20260417-contract-family-completion.md` | `2026-05-31` |

## Rollback
Restore the pre-edit snapshots for updated files from:
- `docs/change-evidence/snapshots/20260417-contract-family-completion/`

Example restore command:
```powershell
Copy-Item \
  'docs/change-evidence/snapshots/20260417-contract-family-completion/schemas--catalog--schema-catalog.yaml' \
  'schemas/catalog/schema-catalog.yaml' -Force
```

For newly added files, rollback means deleting the added spec and schema files if the contract family must be removed.

## Outcome
The repository now has first-class spec/schema pairs for the missing governance contract family. The docs index and schema catalog no longer have a roadmap-level dependency on these contracts remaining conceptual only.
