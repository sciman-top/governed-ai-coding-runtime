# 20260617 Active Queue Evidence-Upkeep Refresh

## Goal
- current landing: `D:\CODE\governed-ai-coding-runtime`
- target home:
  - `docs/architecture/planning-status.json`
  - `README.md`
  - `README.en.md`
  - `README.zh-CN.md`
  - `docs/README.md`
  - `docs/change-evidence/README.md`
  - `docs/change-evidence/20260617-active-queue-evidence-upkeep-refresh.md`
  - `docs/change-evidence/repo-map-context-artifact.json`
  - `docs/change-evidence/runtime-test-speed-latest.json`
- verification path: rerun the active bounded loop, refresh target-run and host-feedback evidence, and then update the planning source of truth without promoting a new implementation queue

## Why This Refresh Was Needed
- The 2026-06-17 selector initially returned `next_action=refresh_evidence_first` because the latest target-run evidence had aged past the freshness window.
- `planning-status.json` and the operator-facing entry docs still described the recovered `fresh` / `native_attach` posture from the earlier 2026-06-09 batch, so the truthful next move was to refresh evidence first instead of inferring new implementation permission.
- Once fresh target-run evidence returned, the selector should fall back to the normal conservative posture `defer_ltp_and_refresh_evidence` and the planning truth should point at that fresh proof.

## Change Summary
1. Refreshed active-loop target-run evidence
- ran `DailyAll` in `quick` mode and exported fresh `daily` run artifacts for all 7 configured targets at `20260617190800`
- refreshed:
  - `docs/change-evidence/target-repo-runs/classroomtoolkit-daily-20260617190800.json`
  - `docs/change-evidence/target-repo-runs/cockpit-tools-local-daily-20260617190800.json`
  - `docs/change-evidence/target-repo-runs/github-toolkit-daily-20260617190800.json`
  - `docs/change-evidence/target-repo-runs/k12-question-graph-daily-20260617190800.json`
  - `docs/change-evidence/target-repo-runs/self-runtime-daily-20260617190800.json`
  - `docs/change-evidence/target-repo-runs/skills-manager-daily-20260617190800.json`
  - `docs/change-evidence/target-repo-runs/vps-ssh-launcher-daily-20260617190800.json`
  - `docs/change-evidence/target-repo-runs/kpi-latest.json`
  - `docs/change-evidence/target-repo-runs/kpi-rolling.json`
  - `docs/change-evidence/target-repo-runs/effect-report-classroomtoolkit.json`

2. Refreshed host-feedback and selector truth
- reran `python scripts/host-feedback-summary.py --assert-minimum --write-markdown .runtime/artifacts/host-feedback-summary/latest.md`
- confirmed fresh target-run evidence for all 7 repos with:
  - `target_runs.status=ok`
  - `target_runs.freshness_status=fresh`
  - `codex_capability_status=ready`
  - `adapter_tier=native_attach`
- reran selector and recovery-posture verification so the bounded loop now truthfully returns:
  - `next_action=defer_ltp_and_refresh_evidence`
  - `evidence_state=fresh`
  - `ltp_decision=defer_all`

3. Refreshed planning truth and operator-facing navigation
- updated `docs/architecture/planning-status.json` to `updated_on=2026-06-17`
- moved the decision-gate proof pointer to this evidence file while keeping:
  - active queue = `Continuous-Execution`
  - selector = `defer_ltp_and_refresh_evidence`
  - live posture = `ready`
- refreshed root/docs guides so their latest bounded-loop proof points at this 2026-06-17 upkeep slice instead of stopping at older proof entries

4. Recorded supporting machine-readable gate side effects
- refreshed `docs/change-evidence/runtime-test-speed-latest.json` from the latest passing Runtime gate
- refreshed `docs/change-evidence/repo-map-context-artifact.json`
  - current derived delta: `excluded_archive_candidate_count=254`
  - this remains a bounded context-shaping artifact, not an active behavior change

## Verification
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action DailyAll -Mode quick`
  - result: pass
  - result: `operator-preflight next_action=refresh_evidence_first`
  - result: `failure_count=0`
  - result: exported 7 fresh target-run `daily` artifacts at `20260617190800`
- `python scripts/host-feedback-summary.py --assert-minimum --write-markdown .runtime/artifacts/host-feedback-summary/latest.md`
  - result: pass
  - result: overall `status=attention` because host snapshots still carry non-blocking local config attention
  - result: `target_runs.status=ok`
  - result: `target_runs.freshness_status=fresh`
- `python scripts/select-next-work.py`
  - result: pass
  - result: `next_action=defer_ltp_and_refresh_evidence`
  - result: `evidence_state=fresh`
  - result: `ltp_decision=defer_all`
- `python scripts/verify-evidence-recovery-posture.py`
  - result: pass
  - result: selector, host-feedback target runs, and effect feedback all agree on the recovered bounded-defer posture
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
  - result: pass
  - result: refreshed `runtime-test-speed-latest.json`
  - result: refreshed `repo-map-context-artifact.json`

## Queue Boundary
- This refresh keeps `Continuous-Execution` active as a bounded evidence-and-gates loop.
- This refresh does **not** promote `GAP-173..180` or any later follow-on queue into current active work.
- This refresh does **not** authorize heavy `LTP-01..06` implementation.
- This refresh does **not** turn review-only self-evolution artifacts into effective policy, skill, target-sync, push, or merge changes.

## Risk
- risk_level: `low`
- reason:
  - evidence refresh and source-of-truth refresh only
  - no production contract broadening
  - no queue promotion
  - no effective mutation lane enabled

## Rollback
- revert:
  - `docs/architecture/planning-status.json`
  - `README.md`
  - `README.en.md`
  - `README.zh-CN.md`
  - `docs/README.md`
  - `docs/change-evidence/README.md`
  - `docs/change-evidence/20260617-active-queue-evidence-upkeep-refresh.md`
- retain or remove separately as desired:
  - the refreshed `20260617190800` target-run artifacts
  - refreshed `kpi-latest.json`, `kpi-rolling.json`, and `effect-report-classroomtoolkit.json`
- re-run:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action DailyAll -Mode quick`
  - `python scripts/host-feedback-summary.py --assert-minimum --write-markdown .runtime/artifacts/host-feedback-summary/latest.md`
  - `python scripts/select-next-work.py`
  - `python scripts/verify-evidence-recovery-posture.py`
  - `python scripts/verify-planning-status.py`
