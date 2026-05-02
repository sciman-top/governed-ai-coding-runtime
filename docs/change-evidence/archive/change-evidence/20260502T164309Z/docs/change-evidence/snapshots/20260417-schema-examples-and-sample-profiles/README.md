# Governed AI Coding Runtime

## Overview
`governed-ai-coding-runtime` is a docs-first, contracts-first repository for a governed runtime around AI coding agents.

The current repository captures the product definition, architecture, roadmap, backlog, schema drafts, and bootstrap planning scripts before runtime code is introduced.

## Current Baseline
- Available now: PRD, architecture, ADRs, roadmap, backlog, JSON Schema drafts, and a GitHub issue seeding script.
- Not landed yet: `apps/`, `packages/`, `infra/`, `tests/`, runtime services, CI, sample repo profiles, and executable workers.
- The active documentation index lives in [docs/README.md](docs/README.md).

## Repository Map
- `docs/`: product definition, architecture, roadmap, ADRs, reviews, and change evidence
- `schemas/`: machine-readable governance contract drafts and the schema catalog
- `scripts/github/`: GitHub backlog/bootstrap automation

## Read First
1. [docs/README.md](docs/README.md)
2. [Interaction Model](docs/product/interaction-model.md)
3. [AI Coding PRD](docs/prd/governed-ai-coding-runtime-prd.md)
4. [Target Architecture](docs/architecture/governed-ai-coding-runtime-target-architecture.md)
5. [Minimum Viable Governance Loop](docs/architecture/minimum-viable-governance-loop.md)
6. [MVP Stack Vs Target Stack](docs/architecture/mvp-stack-vs-target-stack.md)
7. [Compatibility Matrix](docs/architecture/compatibility-matrix.md)
8. [90-Day Plan](docs/roadmap/governed-ai-coding-runtime-90-day-plan.md)
9. [Issue-Ready Backlog](docs/backlog/issue-ready-backlog.md)
10. [Schemas README](schemas/README.md)
11. [Project AGENTS](AGENTS.md)

## Naming
The active project name is `governed-ai-coding-runtime`.
Historical evidence may still mention `governed-agent-platform` where preserving the original record is the correct audit behavior.

## Current Verification Entry Points
The repository does not have build/test services yet, so the current contract/invariant baseline is documentation and schema integrity:

```powershell
Get-ChildItem schemas/jsonschema/*.json |
  ForEach-Object { Get-Content -Raw $_.FullName | ConvertFrom-Json > $null }

$tokens = $null
$errors = $null
[void][System.Management.Automation.Language.Parser]::ParseFile(
  (Resolve-Path 'scripts/github/create-roadmap-issues.ps1'),
  [ref]$tokens,
  [ref]$errors
)
$errors
```

## Immediate Next Steps
1. Bootstrap `apps/`, `packages/`, `infra/`, and `tests/` while preserving the current docs/spec baseline.
2. Add local and CI verification entrypoints for schema, docs, and script integrity.
3. Add sample repo/profile/tool contract instances so the schema layer becomes executable rather than descriptive only.


