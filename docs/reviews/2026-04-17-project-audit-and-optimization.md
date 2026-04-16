# 2026-04-17 Project Audit And Optimization

## Goal
Review the repository deeply before implementation, identify planning/documentation gaps, and tighten the repo so the next execution phase starts from a coherent baseline.

## Audit Scope
- Root repository structure
- PRD, architecture, roadmap, ADRs, backlog, specs, and schema drafts
- GitHub roadmap issue seeding script
- Current evidence and reference integrity

## Repo Facts
- The repository is currently `docs-first / contracts-first`.
- The implemented top-level directories are `docs/`, `schemas/`, and `scripts/`.
- There was no root `README.md` or project-level `AGENTS.md` before this audit.
- The active planning baseline already exists, but implementation skeleton directories (`apps/`, `packages/`, `infra/`, `tests/`) do not.

## Findings
1. Root onboarding was incomplete. The repo had a docs index under `docs/`, but no root entry file explaining current state, reading order, or verification baseline.
2. Repo-specific operating rules were missing. Global agent rules existed outside the repo context, but the project itself had no `AGENTS.md` that mapped gates, evidence paths, or rollback behavior to current repo facts.
3. Early planning artifacts assumed a pre-bootstrap state that is no longer true. The roadmap, backlog seeds, and issue seeding script still described creating docs/schemas that already exist, instead of bootstrapping the missing implementation layers around them.
4. Multiple active documents referenced `docs/FinalStateBestPractices.md`, but that compatibility document did not exist locally.

## Optimization Decisions
- Add a root `README.md` so new work starts from a stable repo entrypoint.
- Add a project-level `AGENTS.md` so repo-specific gates, evidence paths, and `gate_na` handling are explicit.
- Add `docs/FinalStateBestPractices.md` as a compatibility bridge for historical references.
- Refresh roadmap and backlog wording so Phase 1 starts from the current docs/spec baseline rather than re-describing already-landed assets.
- Align `scripts/github/create-roadmap-issues.ps1` with the updated baseline so generated issues reflect real repo state.

## Recommended Next Execution Order
1. Bootstrap `apps/`, `packages/`, `infra/`, and `tests/` with shared tooling entrypoints.
2. Add sample contract instances for repo profiles, tool contracts, and verification policy.
3. Add local verification scripts and CI entrypoints for schema, docs, and script integrity.
4. Start the first executable control-plane slice only after the repo skeleton and verification entrypoints exist.

## Expected Benefit
- The repository now has a clean entrypoint, a repo-level operating contract, and a planning baseline that matches reality.
- The next implementation session can focus on missing runtime assets instead of re-auditing document drift.
