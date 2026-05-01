# 2026-05-01 Native Attach Claim Boundary Doc Sync

## Goal
Remove stale planning-language that could be read as claiming current `native_attach` recovery while the latest target-run evidence still reports degraded Codex workload posture.

## Decision
AI recommendation: update documentation only. Do not modify implementation code, create `GAP-144+`, or promote an `LTP-01..06` package.

The latest target-run and effect-feedback evidence is fresh and passing, but it still reports `codex_capability_status=degraded`, `adapter_tier=process_bridge`, and `flow_kind=process_bridge` for active target repos. Documentation may continue to claim Codex and Claude Code are dual first-class governance entrypoints, but adapter-tier recovery claims must remain evidence-bound.

## Changes
- Updated `docs/backlog/README.md` to distinguish governance-result parity from adapter-tier recovery.
- Updated `docs/backlog/issue-ready-backlog.md` current baseline with the same degraded target-run recovery boundary.
- Updated `docs/roadmap/optimized-hybrid-final-state-long-term-roadmap.md` so roadmap success/failure wording does not imply recovered `native_attach`.
- Updated `docs/architecture/hybrid-final-state-master-outline.md` so the master outline does not claim degraded Codex target-run posture has recovered.

## Non-Changes
- No runtime, package, script, schema, verifier, policy, issue seed, or target repo was changed.
- No `native_attach` recovery claim was made.
- No `GAP-144+` work was created.
- No `LTP-01..06` package was selected or promoted.

## Verification
Completed verification:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll
```

Result: pass. Key output: `rendered_tasks=121`, `completed_task_count=121`, and `active_task_count=0`.

```powershell
python scripts/select-next-work.py --as-of 2026-05-01
```

Result: pass. Key output: `next_action=refresh_evidence_first`, `host_feedback.status=attention`, `degraded_latest_run_count=5`, and `ltp_decision=defer_all`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs
```

Result: pass. Key output includes `OK host-feedback-surface`, `OK evidence-recovery-posture`, `OK autonomous-next-work-selection`, `OK claim-drift-sentinel`, and `OK post-closeout-queue-sync`.

```powershell
git diff --check
```

Result: no whitespace errors; Git reported only existing LF-to-CRLF working-copy warnings.

## Rollback
Revert this evidence file plus the matching documentation changes in `docs/backlog/README.md`, `docs/backlog/issue-ready-backlog.md`, `docs/roadmap/optimized-hybrid-final-state-long-term-roadmap.md`, and `docs/architecture/hybrid-final-state-master-outline.md`.
