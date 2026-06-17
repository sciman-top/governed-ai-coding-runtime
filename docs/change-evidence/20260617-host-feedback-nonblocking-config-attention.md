# 20260617 Host Feedback Nonblocking Config Attention

## Goal
- current landing: `D:\CODE\governed-ai-coding-runtime`
- target home:
  - `scripts/host-feedback-summary.py`
  - `tests/runtime/test_host_feedback_summary.py`
  - `docs/product/host-feedback-loop.md`
  - `docs/product/host-feedback-loop.zh-CN.md`
  - `docs/change-evidence/README.md`
  - `docs/change-evidence/20260617-host-feedback-nonblocking-config-attention.md`
  - `docs/change-evidence/governance-hub-certification-report.json`
  - `docs/change-evidence/self-evolution-readiness/20260617-self-evolution-readiness.json`
  - `docs/change-evidence/runtime-test-speed-latest.json`
- verification path: keep host-config drift visible in detail, but stop treating already-accepted non-blocking local config differences as overall host-feedback failure signals when entrypoints, workload readiness, and target runs are healthy

## Why This Slice Was Needed
- After the 2026-06-17 evidence refresh, `host-feedback-summary.py --assert-minimum` still returned overall `status=attention`.
- The only remaining attention source was host config drift:
  - Codex local config differs from the repo's reference defaults
  - Claude local config misses at least one recommended env knob
- The repository already documents that this is a non-blocking host snapshot signal, not a contradiction of the recovered live target-run posture.
- Leaving that signal at overall `attention` made the summary noisier than the repo's own truth boundary.

## Root Cause
- `scripts/host-feedback-summary.py` treated any host `config.status=attention` as host `health=attention`.
- The aggregate status then promoted the whole feedback report to overall `attention`, even when:
  - host entrypoints were usable
  - Claude workload readiness was `ready/native_attach`
  - latest target-run evidence was `fresh`
  - no degraded target runs remained

## Change Summary
1. Narrowed host-health aggregation
- `scripts/host-feedback-summary.py` now distinguishes:
  - effective host health for the summary
  - detailed `config_status`
  - explicit `nonblocking_config_attention`
- When the only host issue is config drift already treated as non-blocking, the `hosts` dimension stays `ok` and the overall report may stay `pass`.

2. Added regression coverage
- Updated `tests/runtime/test_host_feedback_summary.py` so the host dimension and overall payload stay green when the only remaining signal is non-blocking config attention.
- Preserved degraded workload and stale/degraded target-run tests as real `attention` cases.

3. Synced operator-facing guidance
- Updated the bilingual host-feedback loop docs so operators read host config drift as a detail signal rather than a report-level failure when real workload evidence is healthy.

4. Refreshed dependent bounded-loop artifacts
- Re-ran the repo verification surfaces that consume host feedback.
- This slice therefore also updated:
  - `docs/change-evidence/governance-hub-certification-report.json`
  - `docs/change-evidence/self-evolution-readiness/20260617-self-evolution-readiness.json`
  - `docs/change-evidence/runtime-test-speed-latest.json`
- The key derived truth change is:
  - `runtime_evolution.candidate_count` shrank from `3` to `2`
  - `EVOL-HOST-FEEDBACK` dropped out of the current runtime-evolution candidate set
  - `host_feedback.status` inside the certification verifier moved from `attention` to `pass`
  - `host_feedback.recommendation_count` shrank from `3` to `1`
  - self-evolution readiness now records `candidate_count=2`

## Reference Required Review
reference_required_review:
- changed_surface_paths:
  - `scripts/host-feedback-summary.py`
  - `docs/product/host-feedback-loop.md`
  - `docs/product/host-feedback-loop.zh-CN.md`
- official_sources_reviewed:
  - `docs/change-evidence/20260609-reference-required-change-enforcement.md`
- primary_references_reviewed:
  - `docs/change-evidence/20260609-live-posture-recovery.md`
  - `docs/change-evidence/20260617-active-queue-evidence-upkeep-refresh.md`
  - `docs/architecture/planning-status.json`
- local_runtime_evidence_reviewed:
  - `python -m unittest tests.runtime.test_host_feedback_summary -v`
  - `python scripts/host-feedback-summary.py --assert-minimum`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- source_decision:
  - Keep the recovered live target-run posture as the source of truth, while treating accepted host config drift as a non-blocking detail signal in the summary and docs.

## Verification
- `python -m unittest tests.runtime.test_host_feedback_summary.HostFeedbackSummaryTests.test_host_dimension_keeps_config_attention_nonblocking -v`
  - result: pass
- `python -m unittest tests.runtime.test_host_feedback_summary -v`
  - result: pass
- `python scripts/host-feedback-summary.py --assert-minimum`
  - result: pass
  - result: overall `status=pass`
  - result: `hosts.status=ok`
  - result: both host detail records still keep `config_status=attention` plus `nonblocking_config_attention=true`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - result: pass
  - result: refreshed `docs/change-evidence/runtime-test-speed-latest.json`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - result: pass
  - result: refreshed `docs/change-evidence/governance-hub-certification-report.json`
  - result: refreshed `docs/change-evidence/self-evolution-readiness/20260617-self-evolution-readiness.json`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/governance/preflight.ps1 -DisableAutoCommit`
  - result: pass

## Risk
- risk_level: `low`
- reason:
  - no runtime behavior, target-run semantics, or minimum-surface gate was broadened
  - degraded workload and stale/degraded target-run cases still surface as real `attention`
  - accepted local preference drift remains visible in detail instead of being hidden

## Rollback
- revert:
  - `scripts/host-feedback-summary.py`
  - `tests/runtime/test_host_feedback_summary.py`
  - `docs/product/host-feedback-loop.md`
  - `docs/product/host-feedback-loop.zh-CN.md`
  - `docs/change-evidence/README.md`
  - `docs/change-evidence/20260617-host-feedback-nonblocking-config-attention.md`
  - `docs/change-evidence/governance-hub-certification-report.json`
  - `docs/change-evidence/self-evolution-readiness/20260617-self-evolution-readiness.json`
  - `docs/change-evidence/runtime-test-speed-latest.json`
- re-run:
  - `python -m unittest tests.runtime.test_host_feedback_summary -v`
  - `python scripts/host-feedback-summary.py --assert-minimum`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
