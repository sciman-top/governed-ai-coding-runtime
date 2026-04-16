# Governed Agent Platform

## Overview
`governed-agent-platform` is a docs-first, contracts-first repository for a governed runtime around AI coding agents.

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
2. [AI Coding PRD](docs/prd/governed-agent-platform-ai-coding-prd.md)
3. [Target Architecture](docs/architecture/governed-agent-platform-target-architecture.md)
4. [Minimum Viable Governance Loop](docs/architecture/minimum-viable-governance-loop.md)
5. [90-Day Plan](docs/roadmap/governed-agent-platform-90-day-plan.md)
6. [Issue-Ready Backlog](docs/backlog/issue-ready-backlog.md)
7. [Schemas README](schemas/README.md)
8. [Project AGENTS](AGENTS.md)

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
