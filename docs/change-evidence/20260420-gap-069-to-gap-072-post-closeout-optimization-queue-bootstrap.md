# 20260420 GAP-069 To GAP-072 Post-Closeout Optimization Queue Bootstrap

## Goal
Bootstrap the next executable optimization queue after governance-lane closeout so the project can keep improving without reopening hybrid final-state closure claims.

## Clarification Trace
- `issue_id`: `gap-069-to-gap-072-queue-bootstrap`
- `attempt_count`: `1`
- `clarification_mode`: `direct_fix`
- `clarification_scenario`: `n/a`
- `clarification_questions`: `[]`
- `clarification_answers`: `[]`

## Scope
- Define `GAP-069` through `GAP-072` in the issue-ready backlog with goals, acceptance criteria, and blockers.
- Sync machine-readable issue seeds and version bump.
- Refresh backlog seed policy and backlog index posture to show the new active queue.
- Keep roadmap and lifecycle posture docs consistent with the new post-closeout queue.
- Extend GitHub seeding script task-label mapping so the new IDs render cleanly.

## What Changed
1. Added a new post-closeout optimization queue:
   - `GAP-069 Host-Neutral Governance Boundary Hardening`
   - `GAP-070 Default-On Onboarding And Auto-Apply Guardrails`
   - `GAP-071 Evidence Replay SLO And Recoverability Hardening`
   - `GAP-072 Claim-Drift Sentinel And Continuous Doc-Runtime Sync`
2. Updated `docs/backlog/issue-seeds.yaml`:
   - `issue_seed_version` from `3.6` to `3.7`
   - inserted `GAP-069` through `GAP-072` with dependency chain `GAP-068 -> GAP-069 -> GAP-070 -> GAP-071 -> GAP-072`
3. Updated backlog posture docs:
   - `docs/backlog/full-lifecycle-backlog-seeds.md`
   - `docs/backlog/README.md`
   - `docs/backlog/issue-ready-backlog.md`
4. Synced roadmap posture docs:
   - `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
   - `docs/roadmap/governance-optimization-lane-roadmap.md`
5. Updated seeding script compatibility:
   - `scripts/github/create-roadmap-issues.ps1` now maps `GAP-069` through `GAP-072` to `phase:governance-optimization` task labels.

## Verification
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
   - `exit_code`: `0`
   - `key_output`: `OK python-bytecode`; `OK python-import`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
   - `exit_code`: `0`
   - `key_output`: `OK runtime-unittest`; `Ran 250 tests`; `OK`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
   - `exit_code`: `0`
   - `key_output`: `OK schema-json-parse`; `OK schema-example-validation`; `OK schema-catalog-pairing`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
   - `exit_code`: `0`
   - `key_output`: `OK runtime-status-surface`; `OK codex-capability-ready`; `OK adapter-posture-visible`
5. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
   - `exit_code`: `0`
   - `key_output`: `OK active-markdown-links`; `OK backlog-yaml-ids`; `OK old-project-name-historical-only`
6. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`
   - `exit_code`: `0`
   - `key_output`: `OK powershell-parse`; `OK issue-seeding-render`
7. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
   - `exit_code`: `0`
   - `key_output`: `issue_seed_version=3.7`; `rendered_issue_creation_tasks=4`; `active_task_count=4`

## Risks
- The new queue currently reuses the governance-optimization phase label family; if future governance work splits into a different epic taxonomy, label mapping and roadmap phase wiring will need another sync.

## Rollback
- Revert:
  - `docs/backlog/issue-ready-backlog.md`
  - `docs/backlog/issue-seeds.yaml`
  - `docs/backlog/full-lifecycle-backlog-seeds.md`
  - `docs/backlog/README.md`
  - `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
  - `docs/roadmap/governance-optimization-lane-roadmap.md`
  - `scripts/github/create-roadmap-issues.ps1`
  - `docs/change-evidence/20260420-gap-069-to-gap-072-post-closeout-optimization-queue-bootstrap.md`
- Re-run:
  1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  5. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  6. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`
