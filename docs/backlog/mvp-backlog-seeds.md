# MVP Backlog Seeds

## Purpose
Seed implementation work for a final-state-best-practice governance kernel that becomes trialable quickly, then expands into controlled write, delivery assurance, agent compatibility, and bounded multi-repo reuse.

## Current Baseline
- PRD, architecture, ADRs, roadmap, backlog, schema drafts, and the GitHub issue seeding script already exist.
- Root `README.md` and project `AGENTS.md` already act as the repo entry contract.
- Landed: governance contract families, schema examples, sample control-pack metadata, runtime-consumable control-pack asset, two sample repo profiles, repo admission checks, skeleton directories, local verification entrypoints, CI, runtime contract tests, first trial entrypoint, write governance contracts, delivery/eval contracts, second-repo pilot checks, minimal control console facade, and runbooks.
- Missing: production runtime services, durable workers, real package build artifacts, deployment targets, and a real doctor/hotspot command.

## P0
1. Keep roadmap, backlog, issue seeds, and the seeding script synchronized around a trial-first plan.
2. Bootstrap `apps/`, `packages/`, `infra/`, and `tests/`.
3. Add local verification entrypoints and minimum CI for schema, docs, and script integrity.
4. Promote at least one sample control-pack metadata record into a runtime-consumable sample control pack and define repo admission minimums.
5. Define the initial agent adapter capability contract and Codex CLI/App compatibility posture.
6. Keep root `README.md`, project `AGENTS.md`, roadmap, backlog, script, and schema catalog synchronized as implementation begins.

## P1
1. Implement deterministic task intake and repo profile resolution.
2. Implement a governed read-only tool path for the first operator trial.
3. Implement an evidence timeline and task result output.
4. Add a Codex CLI/App compatible CLI or scripted entrypoint that can run the first read-only governed session.
5. Define observe-only, advisory, enforced, and strict governance modes for trial use.

## P2
1. Implement isolated workspace or worktree allocation.
2. Make medium/high-risk write policy defaults explicit.
3. Implement approval interruption and write-side rollback references.
4. Add quick verification as the first write-side delivery gate.

## P3
1. Add full verification with escalation rules.
2. Add delivery handoff and replay references.
3. Add minimum eval suites, required trace fields, and trace grading baseline.
4. Prove compatibility on a second target repository without changing kernel semantics.
5. Represent at least one additional agent product shape through the same adapter capability contract.

## P4
1. Add minimum operator surfaces for approvals and evidence inspection.
2. Add rollout, waiver recovery, and control rollback runbooks.
3. Use observed trial friction to reprioritize the next slice.

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
- upstream agent UX replacement
- product-specific adapter sprawl before stable capability contracts exist
