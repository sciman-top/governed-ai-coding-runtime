# 2026-05-03 Runtime State Prune Apply

## Rule
- `R1`: current landing point is `D:\CODE\governed-ai-runtime-state\self-runtime`; target home remains the external machine-local runtime state root for the `self-runtime` catalog entry.
- `R4`: deletion was bounded to unreferenced runtime artifacts and old doctor remediation snapshots; every deleted item was copied to an external backup root first.
- `R8`: dry-run classification, apply commands, partial failure, recovery, final candidate-zero proof, backup roots, compatibility, and rollback are recorded here.

## Basis
- `docs/change-evidence/20260503-runtime-state-retention-dry-run.md` classified the state root and established the retention policy.
- `docs/targets/target-repos-catalog.json` still points `self-runtime.attachment_runtime_state_root` at `${code_root}/governed-ai-runtime-state/self-runtime`.
- Target-run JSON refs under `docs/change-evidence/target-repo-runs/` can point to `artifacts/...`; those artifact directories were protected.

## Changes
- Added `scripts/prune-runtime-state.py`.
  - Default mode is dry-run.
  - `--apply` backs up candidates and writes `manifest.json`.
  - Artifact retention keeps the latest N directories and all target-run referenced directories.
  - Doctor retention keeps `latest-remediation.json` plus the latest N `remediation-*.json` files.
  - `approvals/` and `context/` are always preserved.
  - Windows delete recovery now retries read-only paths and isolates per-item failures.
- Added `tests/runtime/test_prune_runtime_state.py`.
- Applied cleanup to the live `self-runtime` state root in two passes.

## Apply Results

Initial state before apply:

- `total_files`: `798`
- `total_size_bytes`: `1714019`
- `artifact_dirs_total`: `118`
- `artifact_dirs_delete_candidates`: `79`
- `artifact_delete_candidate_size_bytes`: `700170`
- `doctor_remediation_files_total`: `89`
- `doctor_remediation_delete_candidates`: `59`
- `doctor_remediation_candidate_size_bytes`: `34633`

First apply:

- Output: `docs/change-evidence/runtime-state-prune-apply-20260503T203802Z.json`
- Backup root: `D:\CODE\governed-ai-runtime-state\_prune-backups\self-runtime-20260503T203802Z`
- Manifest: `D:\CODE\governed-ai-runtime-state\_prune-backups\self-runtime-20260503T203802Z\manifest.json`
- Result: partial failure after deleting `56` artifact directories.
- Failure: Windows `WinError 5 Access denied` while deleting an old artifact directory.
- Recovery: script was changed to retry read-only paths and continue per item instead of aborting the whole apply.

Second apply:

- Output: `docs/change-evidence/runtime-state-prune-apply-20260503T203844Z.json`
- Backup root: `D:\CODE\governed-ai-runtime-state\_prune-backups\self-runtime-20260503T203844Z`
- Manifest: `D:\CODE\governed-ai-runtime-state\_prune-backups\self-runtime-20260503T203844Z\manifest.json`
- Result: pass.
- Deleted remaining `23` artifact directories.
- Deleted `59` old doctor remediation files.
- Failed deletions: `0`.

Final state:

- `total_files`: `276`
- `total_size_bytes`: `979216`
- `artifact_dirs_total`: `39`
- `artifact_dirs_delete_candidates`: `0`
- `artifact_delete_candidate_size_bytes`: `0`
- `artifact_dirs_referenced_by_target_runs`: `14`
- `doctor_remediation_files_total`: `30`
- `doctor_remediation_delete_candidates`: `0`
- `approvals_total`: `6`
- `context_files_total`: `1`

## Commands
- `python -m unittest tests.runtime.test_prune_runtime_state`
- `python scripts/prune-runtime-state.py --runtime-state-root D:\CODE\governed-ai-runtime-state\self-runtime --target-run-root docs\change-evidence\target-repo-runs --keep-latest-artifacts 30 --keep-latest-remediations 30 --dry-run --json`
- `python scripts/prune-runtime-state.py --runtime-state-root D:\CODE\governed-ai-runtime-state\self-runtime --target-run-root docs\change-evidence\target-repo-runs --keep-latest-artifacts 30 --keep-latest-remediations 30 --backup-root D:\CODE\governed-ai-runtime-state\_prune-backups\self-runtime-20260503T203802Z --apply --json`
- `python scripts/prune-runtime-state.py --runtime-state-root D:\CODE\governed-ai-runtime-state\self-runtime --target-run-root docs\change-evidence\target-repo-runs --keep-latest-artifacts 30 --keep-latest-remediations 30 --backup-root D:\CODE\governed-ai-runtime-state\_prune-backups\self-runtime-20260503T203844Z --apply --json`
- `Get-ChildItem -LiteralPath D:\CODE\governed-ai-runtime-state\self-runtime -Recurse -Force | Measure-Object -Property Length -Sum`

## Compatibility
- Catalog path did not change.
- `approvals/` and `context/` were preserved.
- All target-run referenced artifact directories were preserved.
- The external state root remains outside the repository and is not treated as source content.
- Backups are external to `self-runtime`, so the live state root is smaller while rollback remains possible.

## Rollback
- To restore first-pass deletions, use `D:\CODE\governed-ai-runtime-state\_prune-backups\self-runtime-20260503T203802Z\manifest.json`.
- To restore second-pass deletions, use `D:\CODE\governed-ai-runtime-state\_prune-backups\self-runtime-20260503T203844Z\manifest.json`.
- Restore by copying each backup path back to its original path recorded in the corresponding manifest.
