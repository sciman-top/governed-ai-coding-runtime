# 20260607 Live Posture Refresh

## Goal
- Refresh the repository planning truth so the active decision gate and live posture point at fresh 2026-06-07 evidence instead of yesterday's probe snapshot.
- Preserve the current bounded-defer posture honestly: refresh the evidence, but do not claim Codex `native_attach` recovery unless the fresh target-run posture actually proves it.

## Root Cause And Changes
- Root cause:
  - `planning-status.json`, `claim-catalog.json`, and the host-capability claim-upgrade policy still pointed at `20260606-live-posture-refresh.md` even after a fresh 2026-06-07 host feedback probe had been collected.
  - The current gate remained correct, but the latest proof reference was one day behind the freshest read-only posture evidence.
- Changes:
  - Added this 2026-06-07 live-posture refresh evidence file using the latest host feedback, selector, and evidence-recovery outputs.
  - Updated `docs/architecture/planning-status.json` so `updated_on`, `current_decision_gate.as_of`, and `current_decision_gate.proof_ref` now point at the 2026-06-07 refresh.
  - Updated claim/evidence pointers that are explicitly tied to the freshest live-posture guard (`CLM-011`, `CLM-012`, and the host-capability claim-upgrade policy) to cite this 2026-06-07 evidence.
  - Kept the current decision gate unchanged as `wait_for_host_capability_recovery`, because fresh evidence still shows Codex target runs in `process_bridge / degraded` posture.

## Verification
- `python scripts/host-feedback-summary.py --assert-minimum`
  - result: `status=attention`
  - result: `target_run_freshness=fresh`
  - result: latest target runs are still `*-daily-20260606200228.json`
  - result: `degraded_latest_run_count=7`
  - result: all degraded latest runs still require `codex_capability_status=ready` and `adapter_tier=native_attach` before stronger Codex recovery claims are allowed
- `python scripts/select-next-work.py --as-of 2026-06-07`
  - result: `status=pass`
  - result: `next_action=wait_for_host_capability_recovery`
  - result: `source_state=fresh`
  - result: `evidence_state=stale`
  - result: `evidence_blocker=host_capability_degraded_bounded_defer`
- `python scripts/verify-evidence-recovery-posture.py --as-of 2026-06-07`
  - result: `status=pass`
  - result: `target_runs.status=attention`
  - result: `target_runs.freshness_status=fresh`
  - result: `effect_report.decision=adjust`
- `python scripts/verify-planning-status.py`
  - expected result after refresh: `status=pass`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  - expected result after refresh: includes `OK planning-status`, `OK evidence-recovery-posture`, `OK host-capability-claim-upgrade-policy`, `OK claim-evidence-freshness`

## Risks
- This refresh still does not claim Codex target-run `native_attach` recovery.
- The fresh probe confirms that evidence is current, but it also confirms that the bounded host-capability defer remains active.
- Future probe refreshes can drift again if `planning-status.json` and the claim evidence pointers are updated without re-running the docs gate.

## Rollback
- Revert `docs/architecture/planning-status.json`, `docs/product/claim-catalog.json`, `docs/architecture/host-capability-claim-upgrade-policy.json`, and this evidence file.
- Re-run:
  - `python scripts/host-feedback-summary.py --assert-minimum`
  - `python scripts/select-next-work.py --as-of 2026-06-07`
  - `python scripts/verify-evidence-recovery-posture.py --as-of 2026-06-07`
  - `python scripts/verify-planning-status.py`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
