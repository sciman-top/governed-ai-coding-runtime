# Codex Config Baseline And Target-Run Refresh

## Goal
- Execute the `refresh_evidence_first` action after `GAP-142`.
- Remove the local Codex config baseline drift caused by the repository still expecting `gpt-5.4` while the live machine config uses `gpt-5.5`.
- Refresh all active target-repo daily evidence and preserve the remaining `process_bridge/degraded` posture as a bounded host capability limitation.

## Commands
- `python scripts/select-next-work.py --as-of 2026-05-01`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action DailyAll -Mode quick`
- `python scripts/host-feedback-summary.py --assert-minimum --max-target-runs 5`
- `python scripts/build-target-repo-reuse-effect-report.py --target classroomtoolkit --output docs/change-evidence/target-repo-runs/effect-report-classroomtoolkit.json`
- `python scripts/verify-target-repo-reuse-effect-report.py`
- `python -m unittest tests.runtime.test_codex_local tests.runtime.test_host_feedback_summary tests.runtime.test_autonomous_next_work_selection tests.runtime.test_operator_ui`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
- `codex --version`
- `codex --help`
- `codex status`
- `codex exec resume --help`

## Key Output
- `DailyAll` exported fresh target runs for `classroomtoolkit`, `github-toolkit`, `self-runtime`, `skills-manager`, and `vps-ssh-launcher` at stamp `20260501182923`; all exported run statuses were `pass`.
- Codex config health is now `ok`; the expected and actual `model` are both `gpt-5.5`.
- Host feedback now has `hosts.status=ok` and only `target_runs.status=attention`.
- Remaining target-run posture is still `codex_capability_status=degraded`, `adapter_tier=process_bridge`, `flow_kind=process_bridge`.
- The fresh target-run root cause is `live_attach_probe_unsupported_status_command_missing`; native attach still requires a Codex build exposing a status handshake command.
- Effect report verification is back to `pass` with `decision=adjust` and `backlog_candidate_count=2`.
- Docs verification passed through `OK host-feedback-surface`, `OK autonomous-next-work-selection`, `OK claim-drift-sentinel`, and `OK post-closeout-queue-sync`.
- Contract verification passed through `OK target-repo-reuse-effect-feedback`, `OK governance-hub-certification`, and `OK functional-effectiveness`.
- Runtime verification completed 93 test files with `failures=0`.
- Doctor verification passed and intentionally still reports `WARN codex-capability-degraded`.
- Codex CLI diagnostics:
  - `codex --version` returns `codex-cli 0.125.0`.
  - `codex --help` has no top-level `status` subcommand.
  - `codex status` fails in this non-interactive context with `stdin is not a terminal`.
  - `codex exec resume --help` exists and is supporting evidence only, not the required native attach status handshake.

## Compatibility
- This change updates the active recommended Codex default from `gpt-5.4 + medium + never` to `gpt-5.5 + medium + never`.
- The long-lived principle remains `efficiency_first`; model choice remains a temporary implementation detail.
- Historical evidence files that recorded the old `gpt-5.4` baseline were intentionally left unchanged.

## Rollback
- Revert the `gpt-5.5` active baseline updates, regenerated target-run evidence, KPI/effect report refresh, and this evidence file.
- If rollback is used, rerun `python scripts/host-feedback-summary.py --assert-minimum --max-target-runs 5` and `python scripts/select-next-work.py --as-of 2026-05-01` to restore the prior evidence posture.
