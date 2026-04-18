# 20260419 Phase 0 Planning Sync

## Purpose
- Execute `Task 0` from the direct-to-hybrid-final-state implementation plan.
- Landing point: active future-facing backlog and issue-seed sync.
- Target destination: make the direct-to-final-state mainline renderable through the backlog and issue seeding surfaces instead of existing only in roadmap and plan documents.

## Clarification Trace
- `issue_id`: `phase-0-planning-sync`
- `attempt_count`: `1`
- `clarification_mode`: `direct_fix`
- `clarification_scenario`: `n/a`
- `clarification_questions`: `[]`
- `clarification_answers`: `[]`

## Basis
- `docs/plans/direct-to-hybrid-final-state-implementation-plan.md`
- `docs/roadmap/direct-to-hybrid-final-state-roadmap.md`
- `docs/architecture/hybrid-final-state-master-outline.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/issue-seeds.yaml`
- `scripts/github/create-roadmap-issues.ps1`

## Change
- Promoted `GAP-045` through `GAP-060` as the active future-facing direct-to-hybrid-final-state mainline in `docs/backlog/issue-ready-backlog.md`.
- Added matching issue seeds in `docs/backlog/issue-seeds.yaml` and bumped `issue_seed_version` to `3.3`.
- Extended `scripts/github/create-roadmap-issues.ps1` label mapping and phase labels so the new queue renders through the existing seeding flow.

## Why This Matters
- Before this change, the repository had:
  - a master outline
  - a future roadmap
  - a future implementation plan
  - but no synced backlog or issue-seed mainline for the final-state queue
- After this change, the active queue exists in the operational backlog and can be rendered through the seeding script without colliding with historical lifecycle ids.

## Files Modified
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/issue-seeds.yaml`
- `scripts/github/create-roadmap-issues.ps1`

## Verification
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
   - Result: pass
   - Evidence: rendered `43` task issue bodies, `7` epics, and the initiative body with `issue_seed_version` `3.3`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
   - Result: pass
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`
   - Result: pass
4. Repository hard gate order to run after this evidence:
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

## Risks
- The new queue is additive and keeps historical lifecycle GAP entries intact, so readers still need to understand that `GAP-018` through `GAP-044` are completion history, not the active future-facing queue.
- The seeding script now recognizes additional phase labels; any downstream automation that assumes only the older phase set should be rechecked when GitHub issue creation is used for the new queue.

## Rollback
- Revert:
  - `docs/backlog/issue-ready-backlog.md`
  - `docs/backlog/issue-seeds.yaml`
  - `scripts/github/create-roadmap-issues.ps1`
  - `docs/change-evidence/20260419-phase-0-planning-sync.md`
- Re-run:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
  - the normal repository gate order
