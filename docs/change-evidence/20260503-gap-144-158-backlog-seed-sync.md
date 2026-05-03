# 2026-05-03 GAP-144..158 Backlog And Seed Sync

## Rule
- `R1`: current landing point is backlog/issue rendering metadata; target home is the machine-visible GAP queue for managed-asset removal and repo-slimming work.
- `R4`: low-risk planning contract sync; no target repo files, rule sources, credentials, or destructive cleanup paths are changed.
- `R8`: record basis, changed files, verification, compatibility, and rollback.

## Basis
- `docs/plans/README.md` already listed `GAP-144..151` and `GAP-152..158` as current follow-on queues.
- `docs/plans/target-repo-managed-asset-retirement-and-uninstall-plan.md` already described the managed-asset retirement/uninstall queue and its current implementation baseline.
- `docs/plans/repo-slimming-and-speed-plan.md` already described the completed bounded repo-slimming and coding-speed lane.
- `docs/backlog/issue-seeds.yaml` and `docs/backlog/issue-ready-backlog.md` still stopped at `GAP-143`, which made `scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll` report no active rendered tasks for those newer queues.

## Changes
- Bumped `docs/backlog/issue-seeds.yaml` to `issue_seed_version=5.4`.
- Added machine-readable seeds for `GAP-144..158`.
- Added issue-ready backlog entries for the managed-asset queue and repo-slimming queue.
- Updated backlog/doc summaries so the new queues are visible from the human entrypoints.
- Updated `scripts/github/create-roadmap-issues.ps1` label mappings for the new task ranges.

## Verification
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`: pass; `issue_seed_version=5.4`, `rendered_tasks=136`, `rendered_issue_creation_tasks=2`, `completed_task_count=134`, `active_task_count=2`.
- After the `GAP-146` follow-up landed in this same branch, the same render command passes with `rendered_issue_creation_tasks=1`, `completed_task_count=135`, `active_task_count=1`; `GAP-151` is the remaining active closeout item.
- `python -m unittest tests.runtime.test_issue_seeding`: pass; `Ran 9 tests`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`: pass; `OK powershell-parse`, `OK issue-seeding-render`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`: pass; `OK python-bytecode`, `OK python-import`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`: pass; `102` test files, `failures=0`, `Completed 102 test files in 104.532s`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`: pass; includes `OK target-repo-rollout-contract`, `OK target-repo-governance-consistency`, `OK agent-rule-sync`, `OK pre-change-review`, and `OK functional-effectiveness`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`: pass; hard checks OK with existing `WARN codex-capability-degraded`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`: pass; includes `OK backlog-yaml-ids`, `OK evidence-recovery-posture`, `OK autonomous-next-work-selection`, and `OK post-closeout-queue-sync`.
- `git diff --check`: pass; CRLF normalization warnings only.

## Compatibility
- GitHub issue rendering continues to read from the existing `issue-seeds.yaml` and `issue-ready-backlog.md` parser contract.
- This metadata sync did not itself claim `GAP-146` or `GAP-151` completion; `GAP-146` is resolved separately by `docs/change-evidence/20260503-gap-146-managed-file-provenance-sidecar.md`, while `GAP-151` remains active until closeout target evidence is recorded.
- This change does not start or promote any `LTP-01..06` heavy-stack package.

## Rollback
- Revert this file and the related changes to `docs/backlog/issue-seeds.yaml`, `docs/backlog/issue-ready-backlog.md`, `docs/backlog/README.md`, and `docs/README.md`.
