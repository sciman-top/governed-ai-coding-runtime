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
  - Refreshed all-target daily quick workload evidence through `scripts/runtime-flow-preset.ps1 -AllTargets -FlowMode daily -Mode quick -SkipGovernanceBaselineSync -ExportTargetRepoRuns -Json`, producing a new `20260607231307` target-run batch plus refreshed KPI/effect artifacts.
  - Updated `docs/architecture/planning-status.json` so `updated_on`, `current_decision_gate.as_of`, and `current_decision_gate.proof_ref` now point at the 2026-06-07 refresh.
  - Updated claim/evidence pointers that are explicitly tied to the freshest live-posture guard (`CLM-011`, `CLM-012`, and the host-capability claim-upgrade policy) to cite this 2026-06-07 evidence.
  - Kept the current decision gate unchanged as `wait_for_host_capability_recovery`, because fresh evidence still shows Codex target runs in `process_bridge / degraded` posture.

## Verification
- `python scripts/host-feedback-summary.py --assert-minimum`
  - result: `status=attention`
  - result: `target_run_freshness=fresh`
  - result: latest target runs are now `*-daily-20260607231307.json`
  - result: `degraded_latest_run_count=7`
  - result: all degraded latest runs still require `codex_capability_status=ready` and `adapter_tier=native_attach` before stronger Codex recovery claims are allowed
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -FlowMode daily -Mode quick -SkipGovernanceBaselineSync -ExportTargetRepoRuns -Json`
  - result: `target_count=7`
  - result: `failure_count=0`
  - result: exported fresh target runs:
    - `classroomtoolkit-daily-20260607231307.json`
    - `cockpit-tools-local-daily-20260607231307.json`
    - `github-toolkit-daily-20260607231307.json`
    - `k12-question-graph-daily-20260607231307.json`
    - `self-runtime-daily-20260607231307.json`
    - `skills-manager-daily-20260607231307.json`
    - `vps-ssh-launcher-daily-20260607231307.json`
  - result: refreshed `kpi-latest.json`, `kpi-rolling.json`, and `effect-report-classroomtoolkit.json`
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
- `codex --version`
  - result: `codex-cli 0.137.0`
- `codex --help`
  - result: the top-level command surface no longer exposes `status`
  - result: current CLI surface exposes `doctor`, `app-server`, `exec-server`, `resume`, and `features`
- `codex doctor --json`
  - result: `app_server.status=not running`
  - result: `terminal.env.stdin is terminal=false`
  - result: `network.websocket_reachability.supports websockets=false`
  - implication: command-surface drift exists, but fresh local evidence still does not prove an attached `native_attach` session boundary in the current environment
- `python scripts/verify-planning-status.py`
  - result: `status=pass`
  - result: `current_decision_gate=wait_for_host_capability_recovery`
  - result: `current_live_posture=attention`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  - result: `OK planning-status`
  - result: `OK evidence-recovery-posture`
  - result: `OK host-capability-claim-upgrade-policy`
  - result: `OK claim-evidence-freshness`

## Risks
- This refresh still does not claim Codex target-run `native_attach` recovery.
- The fresh probe confirms that evidence is current, but it also confirms that the bounded host-capability defer remains active.
- The new target-run batch improved target overall pass posture, but did not improve Codex capability posture; governance claims must continue to distinguish workload success from host recovery.
- Local probe investigation found Codex CLI command-surface drift (`status` removed in `0.137.0`), but the same probe also shows no running app-server or interactive attached boundary today; changing the runtime posture claim without new continuity evidence would overstate host capability.
- Future probe refreshes can drift again if `planning-status.json` and the claim evidence pointers are updated without re-running the docs gate.

## Rollback
- Revert `docs/architecture/planning-status.json`, `docs/product/claim-catalog.json`, `docs/architecture/host-capability-claim-upgrade-policy.json`, and this evidence file.
- Re-run:
  - `python scripts/host-feedback-summary.py --assert-minimum`
  - `python scripts/select-next-work.py --as-of 2026-06-07`
  - `python scripts/verify-evidence-recovery-posture.py --as-of 2026-06-07`
  - `python scripts/verify-planning-status.py`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
