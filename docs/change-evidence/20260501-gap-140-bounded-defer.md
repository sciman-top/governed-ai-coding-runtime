# 2026-05-01 GAP-140 Bounded Host-Capability Defer

## Goal
Close `GAP-140` with a bounded defer decision that is grounded in current host facts rather than leaving degraded host posture as an unbounded active queue.

## Root Cause And Changes
- Fresh target-run evidence still shows `codex_capability_status=degraded` and `adapter_tier=process_bridge` for the active targets.
- Current local `codex-cli 0.125.0` exposes `exec`, `resume`, and `fork`, but its top-level command surface does not expose a `status` handshake command.
- This repository's current native-attach contract requires a successful `status` handshake before it will claim `native_attach` for automated target runs.
- Preserved that contract and closed `GAP-140` as a bounded defer instead of weakening the proof standard.
- Added shared remediation-boundary fields so host feedback and effect reports now state the same recovery rule and claim guard.

## Verification
- `codex --version`
  - result: `codex-cli 0.125.0`
- `codex --help`
  - result: command surface includes `exec`, `resume`, `fork`, and related commands, but no top-level `status`
- `python scripts/host-feedback-summary.py`
  - result: `status=attention`
  - result: `target_runs.degraded_latest_runs` populated for the active target set
- `python scripts/build-target-repo-reuse-effect-report.py --target classroomtoolkit`
  - result: `decision=adjust`
  - result: host-capability candidate now includes the explicit recovery boundary and claim guard

## Risks
- This does not restore `native_attach`; it records why the current host cannot satisfy the repository's stronger proof contract.
- If the Codex CLI later exposes a valid status handshake, this bounded defer must be re-opened and replaced by fresh recovery evidence.

## Rollback
Revert the backlog/status/doc updates that mark `GAP-140` complete, and restore it to an active follow-on queue if the bounded-defer interpretation is rejected.
