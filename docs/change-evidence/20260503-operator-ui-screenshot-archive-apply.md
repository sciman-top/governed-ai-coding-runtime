# 2026-05-03 Operator UI Screenshot Archive Apply

## Rule
- `R1`: current landing point is operator UI screenshot retention; target home is a smaller active evidence screenshot surface with manifest-backed rollback.
- `R4`: only archive candidates with an explicit manifest were moved; target-run JSON deletion candidates were not applied because that tool deletes rather than archives.
- `R8`: command, moved files, manifest, verification, and rollback are recorded here.

## Basis
- `python scripts/prune-operator-ui-screenshots.py --dry-run --json` reported `archive_candidate_count=3`, `archive_candidate_size_bytes=338197`, and `moved_count=0`.
- `python scripts/prune-target-repo-runs.py --runs-root docs/change-evidence/target-repo-runs --keep-days 7 --keep-latest-per-target 2 --dry-run` reported `delete_candidates=25`; no target-run deletion was applied because the current tool has no archive manifest.

## Changes
- Moved 3 historical operator UI screenshots behind the archive surface:
  - `docs/change-evidence/claude-operator-ui-tabs.png`
  - `docs/change-evidence/codex-operator-ui-tabs.png`
  - `docs/change-evidence/codex-operator-ui.png`
- Wrote rollback manifest:
  - `docs/change-evidence/archive/operator-ui-screenshot-prune-manifests/20260503T093307Z.json`
- Archive destination:
  - `docs/change-evidence/archive/operator-ui-screenshots/20260503T093307Z/`

## Commands
- `python scripts/prune-operator-ui-screenshots.py --dry-run --json`
- `python scripts/prune-target-repo-runs.py --runs-root docs/change-evidence/target-repo-runs --keep-days 7 --keep-latest-per-target 2 --dry-run`
- `python scripts/prune-operator-ui-screenshots.py --apply --json`
- `python scripts/prune-operator-ui-screenshots.py --dry-run --json`

## Key Output
- Apply output: `status=pass`, `moved_count=3`, `archive_candidate_size_bytes=338197`.
- Post-apply dry-run output: `archive_candidate_count=0`, `archive_candidate_size_bytes=0`, `total_screenshots=10`.
- Target-run retention dry-run only: `total_run_files=59`, `kept=34`, `delete_candidates=25`, `deleted=0`, `derived_files_preserved=8`.

## Compatibility
- Latest root screenshots remain in place.
- Milestone screenshots remain in place.
- No target-run evidence was deleted.
- No evidence file was removed without a manifest.

## Rollback
- Use `docs/change-evidence/archive/operator-ui-screenshot-prune-manifests/20260503T093307Z.json`.
- Move each `destination` back to its recorded `source`.
