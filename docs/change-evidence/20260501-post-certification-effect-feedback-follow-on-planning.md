# 2026-05-01 Post-Certification Effect-Feedback Follow-On Planning

## Goal
Turn the two live `adjust` candidates from `docs/change-evidence/target-repo-runs/effect-report-classroomtoolkit.json` into bounded post-certification follow-on work instead of leaving them as report-only signals.

## Root Cause And Changes
- The repository had already closed `GAP-130..139`, but the latest verifier-backed effect report still emitted:
  - `target-repo-reuse-host-capability-gap`
  - `target-repo-reuse-historical-problem-trace`
- Normalized `GAP-125..127` status text in the backlog so the issue renderer now recognizes those completed items as complete.
- Added `GAP-140` for host-capability recovery or explicit bounded defer with fresh evidence.
- Added `GAP-141` for historical problem-trace retention and closure rules, separate from current pass-state claims.
- Updated queue summaries, backlog, issue seeds, plan text, and repository status docs so the new follow-on queue is machine-renderable and visibly downstream of `GAP-139`.

## Verification
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
  - result after status normalization: `completed_task_count=117`, `active_task_count=0`
  - result after adding `GAP-140..141`: issue rendering remains valid and the new follow-on queue is renderable
- `python scripts/evaluate-runtime-evolution.py`
  - confirms `candidate_count=4`
  - includes `EVOL-EFFECT-FEEDBACK`
  - shows `backlog_candidate_count=2`
- `docs/change-evidence/target-repo-runs/effect-report-classroomtoolkit.json`
  - confirms `decision=adjust`
  - confirms the two candidate ids that justified `GAP-140..141`

## Risks
- This change is planning-only. It does not resolve degraded host capability posture by itself.
- `GAP-140` must not claim restored `native_attach` or equivalent host posture until a fresh target repo run proves it.
- `GAP-141` must keep historical problem evidence visible enough for audit without collapsing it into current health claims.

## Rollback
Revert the backlog, issue seed, plan, README, and docs index updates that mention `GAP-140..141`, and delete this evidence file if the follow-on queue is superseded.
