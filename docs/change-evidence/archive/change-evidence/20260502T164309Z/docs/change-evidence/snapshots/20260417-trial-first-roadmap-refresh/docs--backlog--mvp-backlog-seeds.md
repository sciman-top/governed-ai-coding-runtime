# MVP Backlog Seeds

## Purpose
Seed implementation work for a governance kernel plus bounded multi-repo reuse without importing the shape of a broad agent platform or distribution hub.

## Current Baseline
- PRD, architecture, ADRs, roadmap, backlog, schema drafts, and the GitHub issue seeding script already exist.
- Root `README.md` and project `AGENTS.md` already act as the repo entry contract.
- Landed: governance contract families, schema examples, and two sample repo profiles.
- Missing: sample control packs; compatibility validation; repo admission checks; `apps/`, `packages/`, `infra/`, `tests/`; CI; and executable services.

## P0
1. Ratify the governance-kernel boundary and keep roadmap, backlog, and seeding artifacts aligned with it.
2. Add executable example instances for the governance contract family and keep them linked from active docs.
3. Use at least two sample repo profiles and one sample control pack as executable reference assets.
4. Add compatibility validation and repo admission rules before runtime bootstrap.
5. Keep root `README.md`, project `AGENTS.md`, roadmap, backlog, script, and schema catalog synchronized as implementation begins.

## P1
1. Bootstrap `apps/`, `packages/`, `infra/`, and `tests/` around the governance kernel.
2. Add control registry maturity and waiver semantics as executable validation rules.
3. Implement quick and full verification policy as executable configuration.
4. Implement repo map and context shaping as a bounded runtime input.
5. Implement policy decision logging and evidence bundle writing.

## P2
1. Implement deterministic task lifecycle and approval-aware tool governance.
2. Implement governed session bootstrap with isolated workspace allocation.
3. Add minimum eval suites, required trace fields, and trace grading baseline.
4. Add replay-oriented delivery handoff and rollback references.

## P3
1. Prove compatibility on a second target repository without changing kernel semantics.
2. Add minimum operator surfaces for approvals and evidence inspection.
3. Add rollout, waiver recovery, and control rollback runbooks.

## Derived Planning Artifacts
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/issue-seeds.yaml`

## Explicit Non-Goals
- multi-repo distribution
- backflow mirror management
- template sync hub
- skill marketplace or promotion lifecycle
- memory-first personalization stack in MVP
- default multi-agent orchestration
