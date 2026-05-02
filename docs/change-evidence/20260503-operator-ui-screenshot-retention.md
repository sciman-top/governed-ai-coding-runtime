# 2026-05-03 Operator UI Screenshot Retention

## Rule
- `R1`: current landing point is Task 7 screenshot retention; target home is an explicit latest/milestone/archive policy with dry-run-first archive planning.
- `R4`: this slice does not delete or move the repository's current screenshots; it adds a manifest-backed apply path and leaves real movement for an explicit later action.
- `R8`: retention categories, commands, dry-run output, compatibility, and rollback are recorded here.

## Basis
- Task 7 of `docs/plans/repo-slimming-and-speed-plan.md`
- The repo-slimming baseline already proved screenshots are a large visible surface, but there was no dedicated operator UI screenshot classifier or manifest-backed archive path.
- The existing archive index already separated `docs_operator_ui_screenshots` and `root_operator_ui_screenshots`; this slice turns that observation into an executable contract.

## Changes
- Added `scripts/prune-operator-ui-screenshots.py` to classify operator UI screenshots as `latest`, `milestone`, or `archive_candidate`.
- Added `tests/runtime/test_operator_ui_evidence_retention.py` to cover dry-run classification and apply-mode manifest-backed archive moves.
- Updated `docs/change-evidence/README.md` to define operator UI screenshot retention semantics in the active evidence index.

## Commands
- `python -m unittest tests.runtime.test_operator_ui_evidence_retention`
- `python scripts/prune-operator-ui-screenshots.py --dry-run`

## Key Output
- Focused tests: `Ran 2 tests`, `OK`
- Dry-run screenshot inventory:
  - `total_screenshots=26`
  - `latest_count=5`, `latest_size_bytes=1286936`
  - `milestone_count=5`, `milestone_size_bytes=1236617`
  - `archive_candidate_count=16`, `archive_candidate_size_bytes=4226988`
- Current `latest` set:
  - `operator-ui-current-runtime.png`
  - `operator-ui-current-codex.png`
  - `operator-ui-current-claude.png`
  - `operator-ui-current-feedback.png`
  - `operator-ui-current-mobile.png`
- Current `milestone` set:
  - `operator-ui-overview-button-aligned.png`
  - `docs/change-evidence/operator-ui-v2-workbench.png`
  - `docs/change-evidence/operator-ui-live-8770-after-stale-fix.png`
  - `docs/change-evidence/operator-ui-run-entry-desktop-20260502.png`
  - `docs/change-evidence/operator-ui-run-entry-mobile-20260502.png`

## Verification
- Dry-run now reports screenshot count, total size, and stable retention categories.
- Apply mode is explicit (`--apply`) and writes a manifest plus rollback instructions before any archive move is considered complete.
- Current operator-facing docs can point at the `latest` root screenshots only when needed, while milestone images stay named and traceable.

## Compatibility
- No screenshot files were moved in this slice.
- No operator UI runtime behavior changed.
- The archive path is additive and remains outside the default active work surface.

## Rollback
- Revert `scripts/prune-operator-ui-screenshots.py`, `tests/runtime/test_operator_ui_evidence_retention.py`, and the README/plan updates tied to this slice.
- Delete this evidence file if the retention policy should be discarded.
