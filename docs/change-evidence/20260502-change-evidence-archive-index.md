# 2026-05-02 Change Evidence Archive Index

## Rule
- `R1`: current landing point is Task 2 archive layout and index, limited to dry-run indexing only.
- `R4`: no evidence files were moved or deleted; this slice builds only semantic directories, a machine-readable index, and a dry-run classifier.
- `R8`: archive candidate groups, commands, verification, compatibility, and rollback are recorded here.

## Basis
- Task 1 proved that `docs/change-evidence/` is the dominant active work-surface weight.
- Before any archive movement, the repo needs explicit `current` and `archive` semantics plus a dry-run candidate classifier.
- The first archive-safe step is to surface the candidate groups and latest pointers without mutating history.

## Changes
- Added [archive-change-evidence.py](/D:/CODE/governed-ai-coding-runtime/scripts/archive-change-evidence.py) for dry-run archive classification.
- Added [test_archive_change_evidence.py](/D:/CODE/governed-ai-coding-runtime/tests/runtime/test_archive_change_evidence.py).
- Added [current/README.md](/D:/CODE/governed-ai-coding-runtime/docs/change-evidence/current/README.md) and [archive/README.md](/D:/CODE/governed-ai-coding-runtime/docs/change-evidence/archive/README.md).
- Updated [change-evidence/README.md](/D:/CODE/governed-ai-coding-runtime/docs/change-evidence/README.md) with `current/archive` semantics and dry-run entrypoint guidance.
- Generated [evidence-index.json](/D:/CODE/governed-ai-coding-runtime/docs/change-evidence/evidence-index.json).
- Updated [repo-slimming-and-speed-plan.md](/D:/CODE/governed-ai-coding-runtime/docs/plans/repo-slimming-and-speed-plan.md) with Task 2 completion state.

## Commands
- `python -m unittest tests.runtime.test_archive_change_evidence`
- `python scripts/archive-change-evidence.py --dry-run --json --write-index`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`

## Key Output
- Dry-run archive candidate groups: `5`
- Total archive candidate files: `237`
- Total archive candidate bytes: `9179905`
- Total archive candidate size: `8.75 MB`
- Candidate groups:
  - `historical_snapshots`: `49` files, `0.28 MB`
  - `rule_sync_backups`: `115` files, `0.94 MB`
  - `target_repo_raw_runs`: `50` files, `1.43 MB`
  - `docs_operator_ui_screenshots`: `17` files, `4.56 MB`
  - `root_operator_ui_screenshots`: `6` files, `1.55 MB`
- `evidence-index.json` now points at the latest machine-readable refs and latest dated markdown evidence without authorizing any move.

## Verification
- Focused archive-index test passed: `Ran 2 tests`, `OK`.
- Docs gate passed:
  - `OK active-markdown-links`
  - `OK evidence-recovery-posture`
  - `OK post-closeout-queue-sync`
  - no docs contract failures

## Compatibility
- No evidence file paths changed.
- No current README or plan links were broken.
- No runtime behavior, rule source, or gate command changed.
- The archive classifier is additive and dry-run only.

## Rollback
- Delete [archive-change-evidence.py](/D:/CODE/governed-ai-coding-runtime/scripts/archive-change-evidence.py).
- Delete [test_archive_change_evidence.py](/D:/CODE/governed-ai-coding-runtime/tests/runtime/test_archive_change_evidence.py).
- Delete [current/README.md](/D:/CODE/governed-ai-coding-runtime/docs/change-evidence/current/README.md) and [archive/README.md](/D:/CODE/governed-ai-coding-runtime/docs/change-evidence/archive/README.md).
- Delete or revert [evidence-index.json](/D:/CODE/governed-ai-coding-runtime/docs/change-evidence/evidence-index.json).
- Revert the Task 2 status updates in [repo-slimming-and-speed-plan.md](/D:/CODE/governed-ai-coding-runtime/docs/plans/repo-slimming-and-speed-plan.md).
