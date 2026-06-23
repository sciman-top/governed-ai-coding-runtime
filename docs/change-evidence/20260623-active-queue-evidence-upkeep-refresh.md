# 20260623 Active Queue Evidence-Upkeep Refresh

## Goal
- current landing: `D:\CODE\governed-ai-coding-runtime`
- target home:
  - `docs/architecture/planning-status.json`
  - `README.md`
  - `README.en.md`
  - `README.zh-CN.md`
  - `docs/README.md`
  - `docs/change-evidence/README.md`
  - `docs/change-evidence/evidence-index.json`
  - `docs/change-evidence/20260623-active-queue-evidence-upkeep-refresh.md`
  - `docs/change-evidence/20260623-self-evolution-review-refresh.md`
  - `docs/change-evidence/governance-hub-certification-report.json`
  - `docs/change-evidence/policy-tool-credential-audit-report.json`
  - `docs/change-evidence/runtime-test-speed-latest.json`
- verification path: rerun the full release-style upkeep path, refresh current-day runtime/contract/doctor/docs/scripts outputs, and advance the planning proof anchor to the current day without promoting a new implementation queue

## Why This Refresh Was Needed
- `planning-status.json` and the main repo entrypoints still pointed at the 2026-06-20 bounded upkeep proof.
- On 2026-06-23, the repository completed a fresh `build -> runtime -> contract -> doctor` hard-gate chain, `Docs`, `Scripts`, and a release-style `preflight` pass with `-DisableAutoCommit`.
- The selector still reported `defer_ltp_and_refresh_evidence`, so the truthful next move was to refresh the active-loop proof anchor to today instead of leaving the source of truth behind the actual bounded upkeep state.

## Change Summary
1. Refreshed full release-style upkeep evidence for the active loop
- ran `scripts/build-runtime.ps1`
- ran `scripts/verify-repo.ps1 -Check Runtime`
- ran `scripts/verify-repo.ps1 -Check Contract`
- ran `scripts/doctor-runtime.ps1`
- ran `scripts/verify-repo.ps1 -Check Docs`
- ran `scripts/verify-repo.ps1 -Check Scripts`
- ran `scripts/governance/preflight.ps1 -DisableAutoCommit`
- confirmed the release-style upkeep path completed with the hard-gate floor preserved and no queue promotion

2. Refreshed runtime, audit, and selector byproducts
- refreshed `docs/change-evidence/runtime-test-speed-latest.json`
- refreshed `docs/change-evidence/governance-hub-certification-report.json`
- refreshed `docs/change-evidence/policy-tool-credential-audit-report.json`
- re-ran `python scripts/select-next-work.py`
- confirmed the selector still reports:
  - `status=pass`
  - `next_action=defer_ltp_and_refresh_evidence`
  - `gate_state=pass`
  - `evidence_state=fresh`

3. Refreshed planning truth and operator-facing entrypoints
- updated `docs/architecture/planning-status.json` to:
  - `updated_on=2026-06-23`
  - `current_decision_gate.as_of=2026-06-23`
  - `current_decision_gate.proof_ref=docs/change-evidence/20260623-active-queue-evidence-upkeep-refresh.md`
  - current live posture summary anchored to fresh 2026-06-23 upkeep evidence
- refreshed root/docs/evidence entrypoints so the latest bounded-loop proof points at the 2026-06-23 slice

## Verification
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - result: pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - result: pass
  - result: completed 118 runtime test files with `failures=0`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - result: pass
  - result: `agent-rule-sync`, `reference-required-changes`, `reference-basis`, and `functional-effectiveness` all passed
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  - result: pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  - result: pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`
  - result: pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/governance/preflight.ps1 -DisableAutoCommit`
  - result: pass
  - result: build, Runtime, Contract, Doctor, Docs, Scripts, and release-style closeout completed with `auto_commit: status=skipped, reason=disabled_by_caller`
- `python scripts/select-next-work.py`
  - result: pass
  - result: `next_action=defer_ltp_and_refresh_evidence`
- `python scripts/verify-planning-status.py`
  - result: pending final doc refresh verification in this same diff; rerun after entrypoint updates

## Queue Boundary
- This refresh keeps `Continuous-Execution` active as a bounded evidence-and-gates loop.
- This refresh does **not** promote `GAP-173..180` or any later follow-on queue into current active work.
- This refresh does **not** authorize heavy `LTP-01..06` implementation.
- This refresh does **not** turn review-only self-evolution artifacts into effective policy, skill, target-sync, push, or merge changes.

## Risk
- risk_level: `low`
- reason:
  - evidence refresh and source-of-truth refresh only
  - no contract broadening
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
  - `docs/change-evidence/evidence-index.json`
  - `docs/change-evidence/20260623-active-queue-evidence-upkeep-refresh.md`
  - `docs/change-evidence/20260623-self-evolution-review-refresh.md`
  - `docs/change-evidence/governance-hub-certification-report.json`
  - `docs/change-evidence/policy-tool-credential-audit-report.json`
  - `docs/change-evidence/runtime-test-speed-latest.json`
- retain or remove separately as desired:
  - the 2026-06-23 self-evolution, promotion, recommendation, variant, eval, and readiness artifacts
- re-run:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/governance/preflight.ps1 -DisableAutoCommit`
  - `python scripts/select-next-work.py`
  - `python scripts/verify-planning-status.py`
