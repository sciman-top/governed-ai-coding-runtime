# Optimized Hybrid Long-Term Plan Evidence

## Goal
Create the long-term roadmap, implementation plan, and issue-ready task queue for the optimized hybrid final state after the 2026-04-27 benchmark and stack-staging review.

## Scope
Planning and automation metadata only:
- `docs/roadmap/optimized-hybrid-final-state-long-term-roadmap.md`
- `docs/plans/optimized-hybrid-final-state-long-term-implementation-plan.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/issue-seeds.yaml`
- `docs/README.md`
- `docs/plans/README.md`
- `docs/backlog/README.md`
- `docs/architecture/hybrid-final-state-master-outline.md`
- `docs/roadmap/direct-to-hybrid-final-state-roadmap.md`
- `scripts/github/create-roadmap-issues.ps1`

## Change Summary
- Added a canonical long-term roadmap for the optimized hybrid final state.
- Added an implementation-ready `GAP-093..102` task plan.
- Added `LTP-06 supply-chain-hardening` as a trigger-based future package.
- Preserved `Temporal`, `OPA/Rego`, eventing, semantic stores, A2A gateway, full observability, and console work as trigger-based candidates.
- Added backlog and issue-seed entries for the next long-term queue.
- Extended issue-seeding label mapping for the new `GAP-093..102` range.

## Verification
Commands:
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- `git diff --check`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`

Key output:
- issue rendering: `issue_seed_version=4.2`, `rendered_tasks=80`, `rendered_issue_creation_tasks=10`, `rendered_epics=14`, `rendered_initiative=true`, `completed_task_count=70`, `active_task_count=10`
- docs verification: `OK active-markdown-links`, `OK backlog-yaml-ids`, `OK old-project-name-historical-only`, `OK host-replacement-claim-boundary`, `OK gap-evidence-slo`, `OK claim-drift-sentinel`, `OK claim-evidence-freshness`, `OK claim-exception-paths`, `OK post-closeout-queue-sync`
- `git diff --check`: no whitespace errors; Git reported CRLF normalization warnings for existing text files
- full gate: `OK runtime-build`, `OK runtime-unittest`, `OK runtime-service-parity`, `OK runtime-service-wrapper-drift-guard`, `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing`, `OK dependency-baseline`, `OK target-repo-rollout-contract`, `OK target-repo-governance-consistency`, `OK target-repo-powershell-policy`, `OK agent-rule-sync`, `OK runtime-doctor`, `OK active-markdown-links`, `OK issue-seeding-render`, `Ran 412 tests ... OK (skipped=5)`, `Ran 10 tests ... OK`

## Risk
- Documentation/script-metadata change. No runtime behavior changed.
- Main risk is future claim drift if an `LTP` package is started without the `GAP-100` scope fence.

## Rollback
Use git to revert this planning package, backlog/seeds additions, issue-seeding label mapping, and evidence file.
