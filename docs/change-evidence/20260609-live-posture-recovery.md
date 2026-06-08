# 20260609 Live Posture Recovery

## Goal
- Refresh the repository planning truth from the 2026-06-07 bounded-defer snapshot to the fresh 2026-06-09 recovery posture.
- Record the exact evidence that now proves Codex target-run recovery at `codex_capability_status=ready` and `adapter_tier=native_attach`, while keeping non-blocking host snapshot attention separate from the recovered live target-run claim.

## Root Cause And Changes
- Root cause:
  - `planning-status.json`, `claim-catalog.json`, and the recovery verifier still encoded the older `wait_for_host_capability_recovery` posture after a fresher target-run batch (`20260609000223`) had already landed and proven `ready/native_attach/live_attach`.
  - The repo therefore held contradictory truths: fresh runtime evidence had recovered, but the planning source of truth and machine checks still described a degraded wait state.
- Changes:
  - Added this 2026-06-09 recovery evidence file to anchor the recovered live-posture claim.
  - Updated `docs/architecture/planning-status.json` to point at the 2026-06-09 proof, switch the current decision gate to `defer_ltp_and_refresh_evidence`, and mark the current live posture as recovered `native_attach / ready`.
  - Updated `docs/product/claim-catalog.json` (`CLM-011`, `CLM-012`) and `docs/architecture/host-capability-claim-upgrade-policy.json` to cite the new recovery evidence instead of the older bounded-defer snapshot.
  - Updated `scripts/verify-evidence-recovery-posture.py` and the live posture tests so the machine-checked contract now expects:
    - selector `next_action=defer_ltp_and_refresh_evidence`
    - fresh target-run posture `status=ok`
    - effect feedback `decision=promote`
    - no remaining `target-repo-reuse-host-capability-gap` backlog candidate
  - Refreshed the operator-facing planning docs and READMEs so they match the recovered posture and no longer describe Codex target runs as `process_bridge / degraded`.

## Verification
- `python scripts/host-feedback-summary.py --assert-minimum`
  - result: overall `status=attention`
  - result: `target_runs.status=ok`
  - result: `target_runs.freshness_status=fresh`
  - result: `degraded_latest_runs=[]`
  - result: latest batch is `*-daily-20260609000223.json`
  - result: all 7 latest target runs report `codex_capability_status=ready`, `adapter_tier=native_attach`, and `flow_kind=live_attach`
- `python scripts/select-next-work.py --as-of 2026-06-09`
  - result: `status=pass`
  - result: `next_action=defer_ltp_and_refresh_evidence`
  - result: `source_state=fresh`
  - result: `evidence_state=fresh`
  - result: `evidence_blocker=null`
  - result: `ltp_decision=defer_all`
- `python scripts/verify-evidence-recovery-posture.py --as-of 2026-06-09`
  - result: `status=pass`
  - result: `target_runs.status=ok`
  - result: `target_runs.degraded_latest_run_count=0`
  - result: `effect_report.decision=promote`
  - result: `effect_report.host_capability_candidate_present=false`
- `python scripts/verify-planning-status.py`
  - result: `status=pass`
  - result: `current_decision_gate=defer_ltp_and_refresh_evidence`
  - result: `current_live_posture=ready`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  - result: `OK planning-status`
  - result: `OK evidence-recovery-posture`
  - result: `OK host-capability-claim-upgrade-policy`
  - result: `OK claim-evidence-freshness`

## Risks
- `host-feedback-summary.py --assert-minimum` still returns overall `attention` because the host snapshot surface retains a non-blocking Codex config attention state; this recovery only proves the live target-run and selector posture has recovered.
- Stronger live-host claims remain evidence-bound to fresh target-run batches. If a later batch falls back to degraded `process_bridge`, the planner and claims must immediately drop back with it.
- `defer_ltp_and_refresh_evidence` is not a green light for heavy LTP implementation; it only means the bounded host-capability wait blocker is closed and the repo is back to its normal conservative defer posture.

## Rollback
- Revert `docs/architecture/planning-status.json`, `docs/product/claim-catalog.json`, `docs/architecture/host-capability-claim-upgrade-policy.json`, the updated planning docs/READMEs, the recovery verifier/tests, and this evidence file.
- Re-run:
  - `python scripts/host-feedback-summary.py --assert-minimum`
  - `python scripts/select-next-work.py --as-of 2026-06-09`
  - `python scripts/verify-evidence-recovery-posture.py --as-of 2026-06-09`
  - `python scripts/verify-planning-status.py`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
