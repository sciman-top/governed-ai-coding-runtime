# 2026-04-30 Host Feedback Loop Surface

## Goal
- Land a repeatable Codex/Claude host feedback loop so this repository can judge real feature effect from one unified report instead of scattered logs.

## Root Cause And Changes
- Added `scripts/host-feedback-summary.py` to summarize local Codex status, local Claude status, manifest-backed rule distribution, parity docs, and latest target-repo run evidence.
- Added `scripts/operator.ps1 -Action FeedbackReport` and wired the same action into the interactive operator UI allowlist.
- Added bilingual product guidance for the feedback loop and linked it from the main README, docs index, and AI coding usage guides.
- Added `verify-repo.ps1 -Check Docs` coverage for the minimum host feedback surface, plus runtime tests for the script and operator wiring.
- Hardened the summary so host config/CLI/MCP attention no longer reports as overall pass, and latest target-run selection prefers the newest `daily*` workload evidence over older `onboard` snapshots.
- Added target-run freshness detection: evidence older than 168 hours now reports `target_runs=attention` with `freshness_status=stale`, preventing stale run artifacts from being used as current Codex/Claude effect feedback.

## Verification
- `python scripts/host-feedback-summary.py --assert-minimum`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action FeedbackReport`
- `python -m unittest tests.runtime.test_host_feedback_summary tests.runtime.test_operator_entrypoint tests.runtime.test_operator_ui`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`

Current observed status after hardening:
- `FeedbackReport` exits 0 and writes `.runtime/artifacts/host-feedback-summary/latest.md`.
- Overall report status is `attention`, not `pass`, because Codex local config reports `attention` and latest target-run evidence is stale at roughly 188 hours.

## Rollback
- Revert `scripts/host-feedback-summary.py`, the operator/UI wiring, the new product docs, and this evidence file if the new summary surface causes regressions or proves too noisy.
