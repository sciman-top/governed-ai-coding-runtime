# 20260606 Live Posture Refresh

## Goal
- Refresh the repository planning truth so the active decision gate and live posture match real 2026-06-06 evidence instead of the earlier stale-evidence snapshot.
- Refresh the runtime evolution review window only after a new 2026-06-06 review artifact exists.

## Root Cause And Changes
- Root cause:
  - `planning-status.json` and the linked README/docs summary still described the earlier `refresh_evidence_first` plus `target_run_freshness=stale` posture.
  - `runtime-evolution-policy.json` was expired at `2026-05-31`, which forced `source_state=stale` even after fresh target-run evidence had been generated.
- Changes:
  - Updated `docs/architecture/planning-status.json` to reflect `wait_for_host_capability_recovery` with `target_run_freshness=fresh`.
  - Updated README/doc summary surfaces to align with the new live posture.
  - Refreshed `docs/architecture/runtime-evolution-policy.json` review window to `reviewed_on=2026-06-06` and `review_expires_at=2026-07-06`.
  - Kept the current Codex claim boundary evidence-bound: latest target runs are fresh, but recovery is still blocked by degraded `process_bridge` posture rather than missing evidence.

## Verification
- `python scripts/host-feedback-summary.py --assert-minimum`
  - result: `status=attention`
  - result: `target_run_freshness=fresh`
  - result: latest target runs are `*-daily-20260606200228.json`
  - result: degraded latest runs still require `codex_capability_status=ready` and `adapter_tier=native_attach`
- `python scripts/select-next-work.py --as-of 2026-06-06`
  - expected result after refresh: `next_action=wait_for_host_capability_recovery`
  - expected result after refresh: `source_state=fresh`
  - expected result after refresh: `evidence_state=stale`
  - expected result after refresh: `evidence_blocker=host_capability_degraded_bounded_defer`
- `python scripts/verify-evidence-recovery-posture.py --as-of 2026-06-06`
  - expected result after refresh: `status=pass`
- `python scripts/verify-planning-status.py`
  - expected result after refresh: `status=pass`
- `python scripts/verify-governance-hub-certification.py`
  - expected result after refresh: `status=pass`

## Risks
- This refresh does not claim Codex target-run `native_attach` recovery.
- Future doc summaries can drift again if `planning-status.json` changes without re-running the docs gate.

## Rollback
- Revert `docs/architecture/planning-status.json`, `docs/architecture/runtime-evolution-policy.json`, the linked README/doc wording, regenerated review artifacts, and this evidence file.
