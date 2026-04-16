# 2026-04-17 Schema Examples And Sample Profiles

## Summary
Added executable schema example assets for the current governance contract family and landed two sample repo profiles to demonstrate `same kernel, different profiles`.

## Basis
- ADR-0005 established that the repository should prioritize kernel contracts, reusable control assets, and repo-profile-based reuse before platform breadth.
- The previous change completed the missing contract family at the spec and schema level.
- The next correct step was to turn those contracts into reference instances and prove multi-target reuse through sample repo profiles.

## Files Changed
### Added example documentation
- `schemas/examples/README.md`

### Added contract-family examples
- `schemas/examples/hook-contract/pre-write-path-guard.example.json`
- `schemas/examples/skill-manifest/repo-map-audit.example.json`
- `schemas/examples/knowledge-source/docs-index-authoritative.example.json`
- `schemas/examples/waiver-and-exception/temporary-gate-waiver.example.json`
- `schemas/examples/provenance-and-attestation/schema-bundle-release.example.json`
- `schemas/examples/repo-map-context-shaping/hybrid-default.example.json`

### Added sample repo profiles
- `schemas/examples/repo-profile/python-service.example.json`
- `schemas/examples/repo-profile/typescript-webapp.example.json`

### Updated indexes and planning docs
- `README.md`
- `docs/README.md`
- `schemas/README.md`
- `docs/roadmap/governed-ai-coding-runtime-90-day-plan.md`
- `docs/backlog/mvp-backlog-seeds.md`
- `docs/backlog/issue-ready-backlog.md`

## Snapshots
Because the repository still has no `.git` worktree, pre-edit snapshots for updated files were stored at:
- `docs/change-evidence/snapshots/20260417-schema-examples-and-sample-profiles/`

## Commands
### Snapshot existing files
```powershell
$slug='20260417-schema-examples-and-sample-profiles'
$snapDir = Join-Path 'docs/change-evidence/snapshots' $slug
New-Item -ItemType Directory -Force -Path $snapDir | Out-Null
$files = @(
  'README.md',
  'docs/README.md',
  'schemas/README.md',
  'docs/roadmap/governed-ai-coding-runtime-90-day-plan.md',
  'docs/backlog/mvp-backlog-seeds.md',
  'docs/backlog/issue-ready-backlog.md'
)
foreach($f in $files){
  $name = ($f -replace '[\\/]+','--')
  Copy-Item $f (Join-Path $snapDir $name) -Force
}
```

### JSON parse verification
```powershell
Get-ChildItem schemas/jsonschema/*.json,schemas/examples/**/*.json |
  ForEach-Object { Get-Content -Raw $_.FullName | ConvertFrom-Json > $null }
```
Result: `JSON_PARSE_OK`

### Schema-example validation
```powershell
$pairs = @(
  @{Example='schemas/examples/hook-contract/pre-write-path-guard.example.json'; Schema='schemas/jsonschema/hook-contract.schema.json'},
  @{Example='schemas/examples/skill-manifest/repo-map-audit.example.json'; Schema='schemas/jsonschema/skill-manifest.schema.json'},
  @{Example='schemas/examples/knowledge-source/docs-index-authoritative.example.json'; Schema='schemas/jsonschema/knowledge-source.schema.json'},
  @{Example='schemas/examples/waiver-and-exception/temporary-gate-waiver.example.json'; Schema='schemas/jsonschema/waiver-and-exception.schema.json'},
  @{Example='schemas/examples/provenance-and-attestation/schema-bundle-release.example.json'; Schema='schemas/jsonschema/provenance-and-attestation.schema.json'},
  @{Example='schemas/examples/repo-map-context-shaping/hybrid-default.example.json'; Schema='schemas/jsonschema/repo-map-context-shaping.schema.json'},
  @{Example='schemas/examples/repo-profile/python-service.example.json'; Schema='schemas/jsonschema/repo-profile.schema.json'},
  @{Example='schemas/examples/repo-profile/typescript-webapp.example.json'; Schema='schemas/jsonschema/repo-profile.schema.json'}
)
$results = foreach($pair in $pairs){
  $ok = Get-Content -Raw $pair.Example | Test-Json -SchemaFile $pair.Schema
  '{0}: {1}' -f $pair.Example, ($(if($ok){'OK'}else{'FAIL'}))
}
$results
```
Result:
- `schemas/examples/hook-contract/pre-write-path-guard.example.json: OK`
- `schemas/examples/skill-manifest/repo-map-audit.example.json: OK`
- `schemas/examples/knowledge-source/docs-index-authoritative.example.json: OK`
- `schemas/examples/waiver-and-exception/temporary-gate-waiver.example.json: OK`
- `schemas/examples/provenance-and-attestation/schema-bundle-release.example.json: OK`
- `schemas/examples/repo-map-context-shaping/hybrid-default.example.json: OK`
- `schemas/examples/repo-profile/python-service.example.json: OK`
- `schemas/examples/repo-profile/typescript-webapp.example.json: OK`

### Linkage checks
```powershell
@(
  @{Name='Examples README exists'; Ok=(Test-Path 'schemas/examples/README.md')},
  @{Name='Docs index links examples README'; Ok=([bool](Select-String -Path 'docs/README.md' -Pattern 'schemas/examples/README.md' -Quiet))},
  @{Name='Docs index links Python profile sample'; Ok=([bool](Select-String -Path 'docs/README.md' -Pattern 'python-service.example.json' -Quiet))},
  @{Name='Schemas README lists examples'; Ok=([bool](Select-String -Path 'schemas/README.md' -Pattern 'examples/README.md' -Quiet))},
  @{Name='Root README mentions sample repo profiles as landed'; Ok=([bool](Select-String -Path 'README.md' -Pattern 'sample repo profiles' -Quiet))},
  @{Name='Backlog baseline records landed examples'; Ok=([bool](Select-String -Path 'docs/backlog/mvp-backlog-seeds.md' -Pattern 'schema examples' -Quiet))},
  @{Name='Roadmap baseline records landed repo profiles'; Ok=([bool](Select-String -Path 'docs/roadmap/governed-ai-coding-runtime-90-day-plan.md' -Pattern 'two sample repo profiles are now landed' -Quiet))}
) | ForEach-Object { "{0}: {1}" -f $_.Name, ($(if($_.Ok){'OK'}else{'FAIL'})) }
```
Result:
- `Examples README exists: OK`
- `Docs index links examples README: OK`
- `Docs index links Python profile sample: OK`
- `Schemas README lists examples: OK`
- `Root README mentions sample repo profiles as landed: OK`
- `Backlog baseline records landed examples: OK`
- `Roadmap baseline records landed repo profiles: OK`

## Gate Status
| gate | status | reason | alternative_verification | evidence_link | expires_at |
|---|---|---|---|---|---|
| build | `gate_na` | runtime services and build entrypoints still do not exist in this repo | schema examples, repo-profile samples, and planning artifact linkage checks | `docs/change-evidence/20260417-schema-examples-and-sample-profiles.md` | `2026-05-31` |
| test | `gate_na` | no repository test harness or CI pipeline is landed yet | JSON parse plus `Test-Json` schema-example validation | `docs/change-evidence/20260417-schema-examples-and-sample-profiles.md` | `2026-05-31` |
| contract/invariant | `active` | schema integrity is still the hardest machine-verifiable contract in this repo | full schema parse plus example validation against matching schemas | `docs/change-evidence/20260417-schema-examples-and-sample-profiles.md` | `n/a` |
| hotspot | `gate_na` | no runtime doctor or health entrypoint exists yet | example and planning drift checks | `docs/change-evidence/20260417-schema-examples-and-sample-profiles.md` | `2026-05-31` |

## Rollback
Restore the pre-edit snapshots for updated files from:
- `docs/change-evidence/snapshots/20260417-schema-examples-and-sample-profiles/`

Example restore command:
```powershell
Copy-Item \
  'docs/change-evidence/snapshots/20260417-schema-examples-and-sample-profiles/README.md' \
  'README.md' -Force
```

For newly added files, rollback means deleting the added example files and the `schemas/examples/` entries introduced in this change.

## Outcome
The repository now contains auditable example instances for the newly added contract families plus two stack-specific repo profiles. This narrows the gap between schema design and executable governance assets without prematurely introducing runtime services.
