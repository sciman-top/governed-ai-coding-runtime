# GAP-142 Degraded Fresh Evidence Next-Work Guard

## Goal
- Close the next low-risk governance gap after `GAP-141`: fresh target-run evidence must not be treated as healthy when the latest host capability posture is still degraded.
- Preserve the `LTP-01..06` heavy-stack defer boundary while making the autonomous selector choose evidence refresh/remediation before implementation work.

## Risk
- Risk level: low.
- Change type: host-feedback classification, autonomous next-work input interpretation, tests, backlog/claim/evidence docs.
- Compatibility: existing `pass/fail/attention` status vocabulary is preserved; degraded latest target runs now correctly use the existing `attention` state.

## Commands
- `python -m unittest tests.runtime.test_host_feedback_summary tests.runtime.test_autonomous_next_work_selection`
- `python scripts/host-feedback-summary.py --assert-minimum --max-target-runs 5`
- `python scripts/select-next-work.py --as-of 2026-05-01`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

## Key Output
- Host feedback now reports `target_runs.status=attention` with summary `fresh target-run evidence is degraded for 5 repos`.
- `select-next-work.py --as-of 2026-05-01` now returns:
  - `gate_state=pass`
  - `source_state=fresh`
  - `evidence_state=stale`
  - `next_action=refresh_evidence_first`
  - `ltp_decision=defer_all`
  - `degraded_latest_run_count=5`
- Roadmap rendering returns `issue_seed_version=5.2`, `rendered_tasks=120`, `completed_task_count=120`, `active_task_count=0`.
- Runtime verification returns `Completed 93 test files ... failures=0`.
- Contract and Docs verification return `OK autonomous-next-work-selection`, `OK host-feedback-surface`, `OK claim-drift-sentinel`, and `OK post-closeout-queue-sync`.
- Doctor returns `OK adapter-posture-visible` and keeps `WARN codex-capability-degraded`, matching the bounded defer posture.

## Evidence
- `scripts/host-feedback-summary.py` makes degraded latest target runs an `attention` signal.
- `scripts/select-next-work.py` treats degraded latest target runs as stale evidence posture.
- `scripts/operator.ps1` allows `DailyAll` to run when the selector says `refresh_evidence_first`, because `DailyAll` is the evidence refresh action; higher-impact implementation actions remain blocked.
- `tests/runtime/test_host_feedback_summary.py` verifies fresh degraded target runs are not `ok`.
- `tests/runtime/test_autonomous_next_work_selection.py` verifies the live selector chooses `refresh_evidence_first` for the current degraded target-run evidence.
- `docs/backlog/issue-ready-backlog.md` and `docs/backlog/issue-seeds.yaml` define `GAP-142`.
- `docs/product/claim-catalog.json` adds `CLM-011` so the claim remains drift-checked.

## Rollback
- Revert the `GAP-142` code, tests, backlog/seed, claim-catalog, roadmap, README, and this evidence file.
- After rollback, run `python scripts/host-feedback-summary.py --assert-minimum` and `python scripts/select-next-work.py --as-of 2026-05-01` to confirm the previous selector behavior is restored.
