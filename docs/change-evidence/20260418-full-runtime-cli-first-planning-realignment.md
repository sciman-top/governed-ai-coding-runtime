# 2026-04-18 Full Runtime CLI-First Planning Realignment

## Goal
- Resolve the mismatch between the Full Runtime execution plan and the active roadmap/backlog wording for `GAP-027`.
- Keep `Full Runtime` focused on getting the runtime path working first.
- Move the richer operator UI shell to a later stage without losing a stable operator-facing read model.

## Basis
- `docs/plans/full-runtime-implementation-plan.md`
- `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/change-evidence/20260417-foundation-execution-plan.md`

## Decision
- `GAP-027` is now explicitly a `Minimal Operator Surface`, not a mandatory web UI slice.
- The first operator surface delivery in `Full Runtime` may be CLI-first, as long as it is backed by stable runtime read models and query structures.
- The richer operator UI shell is moved to `Public Usable Release`, where it sits on top of the already-stable Full Runtime control surface.
- This is a stage-boundary clarification, not a reduction of final product scope.

## Files Changed
- `docs/plans/full-runtime-implementation-plan.md`
- `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/change-evidence/README.md`

## Rationale
- The repository still needs to prove the runtime path itself:
  - execution worker
  - managed workspace runtime
  - artifact persistence
  - replay metadata
  - operational verification
  - runtime status/query surfaces
- A CLI-first operator surface is a lower-risk way to validate those runtime structures.
- A richer UI shell is more stable after the read model, artifact layout, and query semantics stop moving.

## Verification Commands
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`

## Verification Result
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs` -> pass
  - `OK active-markdown-links`
  - `OK backlog-yaml-ids`
  - `OK old-project-name-historical-only`

## Risks
- `GAP-027` now needs disciplined wording so future execution does not quietly re-expand into a UI build inside `Full Runtime`.
- The later UI shell must still be explicitly planned and should not be assumed to "just appear" from CLI work.

## Rollback
- Restore the previous wording of:
  - `docs/plans/full-runtime-implementation-plan.md`
  - `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
  - `docs/backlog/issue-ready-backlog.md`
- If a UI becomes mandatory inside `Full Runtime`, revert this realignment and re-open the plan with explicit UI scope and acceptance criteria.
