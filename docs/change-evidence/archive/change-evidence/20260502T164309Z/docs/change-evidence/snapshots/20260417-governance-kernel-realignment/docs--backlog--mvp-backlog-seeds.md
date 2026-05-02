# MVP Backlog Seeds

## Purpose
Seed implementation work from the adopted governance mechanisms without importing the full `repo-governance-hub` shape.

## Current Baseline
- PRD, architecture, ADRs, roadmap, backlog, schema drafts, and the GitHub issue seeding script already exist.
- Root `README.md` and project `AGENTS.md` now exist as the repo entry contract.
- Missing: sample contract instances, `apps/`, `packages/`, `infra/`, `tests/`, CI, and executable services.

## P0
1. Bootstrap `apps/`, `packages/`, `infra/`, and `tests/` with shared tooling entrypoints
2. Turn existing schema drafts into executable contract assets with at least one sample repo profile and one sample tool contract
3. Wire local schema validation and PowerShell parsing into a documented verification entrypoint
4. Package control registry, repo profile, tool contract, risk, evidence, and gates definitions for code reuse
5. Establish quick and full verification policy as executable configuration
6. Keep root `README.md`, project `AGENTS.md`, roadmap, backlog, and schema catalog synchronized as implementation begins

## P1
1. Add prompt registry and runtime observability schema
2. Add trace field emission and basic eval recording
3. Add artifact classification policy for transient outputs
4. Add explicit delivery bundle format

## P2
1. Add trace grading thresholds
2. Add failure replay catalog
3. Add bounded subagent decision policy

## Derived Planning Artifacts
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/issue-seeds.yaml`

## Explicit Non-Goals
- multi-repo distribution
- backflow mirror management
- skill promotion lifecycle
- template sync hub
