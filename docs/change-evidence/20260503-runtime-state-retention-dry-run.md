# 2026-05-03 Runtime State Retention Dry Run

## Rule
- `R1`: current landing point is `D:\CODE\governed-ai-runtime-state\self-runtime`; target home remains the machine-local runtime state root for the `self-runtime` catalog entry.
- `R4`: this pass is dry-run only; no files were deleted or moved.
- `R8`: basis, command, candidate counts, compatibility, and rollback boundary are recorded before any later apply.

## Basis
- `docs/targets/target-repos-catalog.json` defines `self-runtime.attachment_runtime_state_root` as `${code_root}/governed-ai-runtime-state/self-runtime`.
- `docs/quickstart/ai-coding-usage-guide.zh-CN.md` documents attachment state as a machine-local runtime state root.
- `docs/change-evidence/target-repo-runs/*.json` stores target-run summaries that can reference runtime-state artifacts by relative `artifacts/...` refs.
- The inspected runtime-state root contains run artifacts, doctor remediation snapshots, approvals, and one context pack. It is not a stray repository file set.

## Dry-Run Policy
- Preserve the root directory and current catalog path.
- Preserve all `approvals/` files.
- Preserve `context/`.
- Preserve all artifact directories referenced by active `docs/change-evidence/target-repo-runs/*.json`.
- Preserve the latest 30 artifact directories regardless of references.
- Preserve `doctor/latest-remediation.json` and the latest 30 `doctor/remediation-*.json` files.
- Treat remaining candidates as delete candidates only after an explicit apply step with fresh inventory.

## Dry-Run Result
- `runtime_state_root`: `D:\CODE\governed-ai-runtime-state\self-runtime`
- `total_files`: `798`
- `total_size_bytes`: `1714019`
- `artifact_dirs_total`: `118`
- `artifact_dirs_referenced_by_target_runs`: `14`
- `artifact_dirs_kept_by_latest_window`: `30`
- `artifact_dirs_delete_candidates`: `79`
- `artifact_delete_candidate_size_bytes`: `700170`
- `doctor_remediation_files_total`: `89`
- `doctor_remediation_delete_candidates`: `59`
- `doctor_remediation_candidate_size_bytes`: `34633`
- `approvals_total`: `6`
- `context_files_total`: `1`

Representative artifact delete candidates:

- `task-20260501003041-self-runtime`
- `task-20260501002809`
- `task-20260501002445-self-runtime`
- `task-20260501001258-self-runtime`
- `task-20260501000837-self-runtime`
- `task-20260428012802-self-runtime`
- `task-20260428012634-self-runtime`
- `task-20260427201022`
- `task-20260427195931-self-runtime`
- `task-20260427174550`

Representative doctor remediation delete candidates:

- `remediation-20260502T161239342.json`
- `remediation-20260502T161004971.json`
- `remediation-20260502T113902094.json`
- `remediation-20260501T221314370.json`
- `remediation-20260501T200308500.json`

## Commands
- `git status --short`
- `Get-ChildItem -LiteralPath D:\CODE\governed-ai-runtime-state\self-runtime -Recurse -Force | Measure-Object -Property Length -Sum`
- inline Python dry-run classifier:
  - scans `docs/change-evidence/target-repo-runs/*.json` for `artifacts/...` refs
  - classifies artifact directories by latest-window and evidence-reference protection
  - classifies doctor remediation files by latest-window protection

## Compatibility
- No catalog path changed.
- No runtime-state file was deleted.
- Existing target-run evidence refs remain valid.
- The current posture continues to treat sibling `governed-ai-runtime-state` as machine-local state, not as source content that should be migrated into the repository.

## Rollback
- No filesystem rollback is required for this dry-run because no files were deleted or moved.
- If a later apply is performed and rejected, restore deleted files from the pre-apply backup manifest that the apply step must create before deletion.
- If a future migration changes `self-runtime.attachment_runtime_state_root`, first copy state to the new root, update the catalog, run governance consistency and hard gates, then delete the old root only after a successful fresh `self-runtime` daily run.
