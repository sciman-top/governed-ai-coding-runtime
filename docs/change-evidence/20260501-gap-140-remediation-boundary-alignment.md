# 2026-05-01 GAP-140 Remediation Boundary Alignment

## Goal
Make the post-certification host-capability follow-on queue executable by aligning `host-feedback-summary` and `target-repo reuse effect feedback` on the same degraded-posture and recovery-evidence boundary.

## Root Cause And Changes
- `GAP-140` was added as the next bounded follow-on queue, but the runtime still expressed degraded host posture in two different places without one shared recovery rule.
- Updated `scripts/host-feedback-summary.py` so the `target_runs` dimension now emits `degraded_latest_runs` with:
  - current degraded posture
  - the recovery evidence rule
  - the claim guard that blocks premature `native_attach` claims
- Updated `scripts/build-target-repo-reuse-effect-report.py` so backlog candidates now carry:
  - `current_posture`
  - `remediation_boundary`
  - `closure_boundary` for historical problem traces
- Added targeted unit coverage for both surfaces.

## Verification
- `python -m unittest tests.runtime.test_host_feedback_summary tests.runtime.test_target_repo_reuse_effect_feedback`
  - result: `OK`
- `python scripts/build-target-repo-reuse-effect-report.py --target classroomtoolkit`
  - result: `decision=adjust`
  - result: `target-repo-reuse-host-capability-gap` now includes `current_posture` and `remediation_boundary`
  - result: `target-repo-reuse-historical-problem-trace` now includes `closure_boundary`
- `python scripts/host-feedback-summary.py`
  - result: `status=attention`
  - result: `target_runs.degraded_latest_runs` present for the current five active targets
  - result: recommendation now explicitly requires fresh evidence returning to `codex_capability_status=ready` and `adapter_tier=native_attach` before claiming recovery

## Risks
- This does not recover host capability by itself; it only makes the recovery boundary explicit and shared.
- Current evidence still shows `process_bridge` across the latest daily target runs, so `GAP-140` remains open.

## Rollback
Revert the `host-feedback-summary` and `build-target-repo-reuse-effect-report` changes, remove the new unit assertions, and delete this evidence file if the shared remediation boundary is replaced by a different contract.
