# 2026-05-02 Repo Map Archive Routing

## Rule
- `R1`: current landing point is Task 3 context routing and repo-map defaults for the repo-slimming lane.
- `R4`: this slice changes only repo-map selection behavior and metrics; it does not move or delete evidence.
- `R8`: routing rules, metrics, verification, compatibility, and rollback are recorded here.

## Basis
- Task 2 established explicit archive candidate groups and a dry-run index.
- The repo-map strategy already excluded `docs/change-evidence/**`, but it did not expose how much archive-candidate weight that exclusion removed.
- Task 3 needed explicit archive-facing patterns and direct metrics for later before/after closeout.

## Changes
- Updated [.governed-ai/repo-map-context-shaping.json](/D:/CODE/governed-ai-coding-runtime/.governed-ai/repo-map-context-shaping.json) to explicitly exclude:
  - `docs/change-evidence/snapshots/**`
  - `docs/change-evidence/rule-sync-backups/**`
  - `docs/change-evidence/target-repo-runs/*.json`
  - `docs/change-evidence/operator-ui*.png`
  - `operator-ui-*.png`
- Updated [build-repo-map-context-artifact.py](/D:/CODE/governed-ai-coding-runtime/scripts/build-repo-map-context-artifact.py) to report:
  - `excluded_archive_candidate_count`
  - `required_file_override_count`
- Updated [test_repo_map_context_artifact.py](/D:/CODE/governed-ai-coding-runtime/tests/runtime/test_repo_map_context_artifact.py) to assert the new metrics.
- Regenerated [repo-map-context-artifact.json](/D:/CODE/governed-ai-coding-runtime/docs/change-evidence/repo-map-context-artifact.json).

## Commands
- `python -m unittest tests.runtime.test_repo_map_context_artifact`
- `python scripts/build-repo-map-context-artifact.py`
- `python scripts/verify-repo-map-context-artifact.py`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`

## Key Output
- `decision=keep`
- `estimated_token_cost=5985`
- `max_tokens=6000`
- `selected_file_count=31`
- `excluded_archive_candidate_count=231`
- `required_file_override_count=0`
- `file_selection_accuracy=1.0`
- `clarification_reduction_proxy=1.0`

## Verification
- Focused repo-map test passed: `Ran 2 tests`, `OK`.
- Repo-map builder passed and wrote the updated artifact.
- Repo-map verifier passed with `decision=keep`.

## Compatibility
- Required governance files remain selected.
- Repo-map artifact format is backward compatible; new metrics are additive.
- No runtime execution path or gate command changed.

## Rollback
- Revert [.governed-ai/repo-map-context-shaping.json](/D:/CODE/governed-ai-coding-runtime/.governed-ai/repo-map-context-shaping.json).
- Revert [build-repo-map-context-artifact.py](/D:/CODE/governed-ai-coding-runtime/scripts/build-repo-map-context-artifact.py) and [test_repo_map_context_artifact.py](/D:/CODE/governed-ai-coding-runtime/tests/runtime/test_repo_map_context_artifact.py).
- Regenerate or restore [repo-map-context-artifact.json](/D:/CODE/governed-ai-coding-runtime/docs/change-evidence/repo-map-context-artifact.json).
