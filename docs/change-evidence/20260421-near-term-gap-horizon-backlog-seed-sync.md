# 20260421 Near-Term Gap Horizon Backlog And Seed Sync

## Goal
Synchronize the optimized best-state near-term packages (`NTP-01..NTP-05`) into the operational backlog and issue seeding flow so they can be executed as a machine-renderable queue.

## Scope
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/issue-seeds.yaml`
- `docs/backlog/README.md`
- `docs/backlog/full-lifecycle-backlog-seeds.md`
- `docs/README.md`
- `scripts/github/create-roadmap-issues.ps1`

## Changes
1. Added a new active execution-horizon queue in backlog and seeds as:
   - `GAP-080 NTP-01 Live Host Closure`
   - `GAP-081 NTP-02 Non-Codex Conformance`
   - `GAP-082 NTP-03 Service-Primary Convergence`
   - `GAP-083 NTP-04 Operator Remediation Depth`
   - `GAP-084 NTP-05 Claim Drift Guard`
2. Kept post-closeout completion posture intact (`GAP-069..074 complete`) and intentionally started the new queue at `GAP-080` to avoid colliding with post-closeout sentinel scope.
3. Bumped issue seed version to `3.9`.
4. Extended GitHub seeding script task-label mapping to cover `GAP-080..084` with `phase:near-term-gap-horizon`.
5. Synced backlog/docs index posture lines to reflect the new near-term active queue.

## Verification
1. Render all issue bodies without GitHub side effects:
   - Command:
     - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
   - Result:
     - `{"issue_seed_version":"3.9","rendered_tasks":62,"rendered_issue_creation_tasks":5,"rendered_epics":14,"rendered_initiative":true,"completed_task_count":57,"active_task_count":5}`
2. Validate docs integrity checks:
   - Command:
     - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
   - Result:
     - `OK active-markdown-links`
     - `OK backlog-yaml-ids`
     - `OK old-project-name-historical-only`
     - `OK host-replacement-claim-boundary`
     - `OK gap-evidence-slo`
     - `OK claim-drift-sentinel`
     - `OK post-closeout-queue-sync`
3. Validate script parser and seeding rendering gate:
   - Command:
     - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`
   - Result:
     - `OK powershell-parse`
     - `OK issue-seeding-render`

## Gate Scope And N/A
| gate | status | reason | alternative_verification | evidence_link | expires_at |
|---|---|---|---|---|---|
| build | `gate_na` | change scope is planning/backlog/seed/script sync; no runtime implementation touched | `verify-repo -Check Docs` + `verify-repo -Check Scripts` + seeding render validation | `docs/change-evidence/20260421-near-term-gap-horizon-backlog-seed-sync.md` | `2026-05-31` |
| test | `gate_na` | same as above | same as above | `docs/change-evidence/20260421-near-term-gap-horizon-backlog-seed-sync.md` | `2026-05-31` |
| contract/invariant | `gate_na` | no schema/spec/contract payload changed | same as above | `docs/change-evidence/20260421-near-term-gap-horizon-backlog-seed-sync.md` | `2026-05-31` |
| hotspot | `gate_na` | no runtime behavior or dependency posture changed | same as above | `docs/change-evidence/20260421-near-term-gap-horizon-backlog-seed-sync.md` | `2026-05-31` |

## Risks
- New label `phase:near-term-gap-horizon` requires downstream dashboards or queries to accept an additional phase namespace.
- `GAP-080..084` are planned (not complete); completion posture must remain evidence-backed before any claim upgrade.

## Rollback
If rollback is required, restore the changed files from git history:
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/issue-seeds.yaml`
- `docs/backlog/README.md`
- `docs/backlog/full-lifecycle-backlog-seeds.md`
- `docs/README.md`
- `scripts/github/create-roadmap-issues.ps1`
- `docs/change-evidence/20260421-near-term-gap-horizon-backlog-seed-sync.md`
