# 2026-05-01 Post-Core-Principle Evidence Refresh

## Goal
Execute the current `refresh_evidence_first` action after the core-principle update and planning crosswalk, then decide whether implementation code work is justified by fresh evidence.

## Root Cause And Changes
The autonomous selector continued to choose `refresh_evidence_first` because host feedback and target-repo effect evidence were fresh enough to classify the issue but still degraded for Codex target runs.

Changes made:

- Ran the all-target daily evidence refresh through `scripts/operator.ps1 -Action DailyAll -Mode quick`.
- Regenerated five target-run JSON evidence files under `docs/change-evidence/target-repo-runs/` with stamp `20260501200520`.
- Rebuilt `docs/change-evidence/target-repo-runs/effect-report-classroomtoolkit.json`.
- Confirmed the target-repo reuse effect backlog candidates dropped from 2 to 1 because the historical problem trace aged out of the active rolling KPI window.
- Confirmed no broad implementation-code optimization is justified by the refreshed evidence; the remaining candidate is the bounded Codex host capability gap.

## Verification
Completed verification:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action DailyAll -Mode quick
```

Result: pass. Key output: `target_count=5`, `failure_count=0`; exported `classroomtoolkit`, `github-toolkit`, `self-runtime`, `skills-manager`, and `vps-ssh-launcher` daily run files at stamp `20260501200520`.

```powershell
python scripts/build-target-repo-reuse-effect-report.py --target classroomtoolkit --output docs/change-evidence/target-repo-runs/effect-report-classroomtoolkit.json
```

Result: pass. Key output: `after_run_ref=classroomtoolkit-daily-20260501200520.json`, `decision=adjust`, `backlog_candidates` contains only `target-repo-reuse-host-capability-gap`.

```powershell
python scripts/host-feedback-summary.py --assert-minimum --max-target-runs 5
```

Result: attention, not failure. Key output: `dimensions_fail=0`, `dimensions_attention=1`, `target_run_freshness=fresh`; latest target runs remain `codex_capability_status=degraded`, `adapter_tier=process_bridge`, and `flow_kind=process_bridge`.

```powershell
python scripts/verify-target-repo-reuse-effect-report.py
```

Result: pass. Key output: `decision=adjust`, `backlog_candidate_count=1`, `errors=[]`.

```powershell
python scripts/select-next-work.py --as-of 2026-05-01
```

Result: pass. Key output: `next_action=refresh_evidence_first`, `ltp_decision=defer_all`, `evidence_state=stale`.

```powershell
python scripts/verify-evidence-recovery-posture.py
```

Result: pass. Key output: selector, host-feedback target-run posture, and target-repo reuse effect report all agree on the recovery rule `fresh target run with codex_capability_status=ready and adapter_tier=native_attach`.

```powershell
python -m unittest tests.runtime.test_codex_local tests.runtime.test_host_feedback_summary
python -m unittest tests.runtime.test_autonomous_next_work_selection tests.runtime.test_operator_ui
python -m unittest tests.runtime.test_target_repo_reuse_effect_feedback tests.runtime.test_evidence_recovery_posture
```

Result: pass. Key output: `Ran 15 tests OK`, `Ran 13 tests OK`, and `Ran 5 tests OK`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
```

Result: pass. Key output: `OK python-bytecode`, `OK python-import`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs
```

Result: pass. Key output includes `OK host-feedback-surface`, `OK evidence-recovery-posture`, `OK core-principles`, `OK autonomous-next-work-selection`, `OK core-principle-change-materialization`, and `OK post-closeout-queue-sync`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
```

Result: pass. Key output includes `OK target-repo-reuse-effect-feedback`, `OK governance-hub-certification`, `OK agent-rule-sync`, `OK pre-change-review`, and `OK functional-effectiveness`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
```

Result: pass. Key output: `Completed 94 test files`, `failures=0`, `OK runtime-unittest`, `OK runtime-service-parity`, and `OK runtime-service-wrapper-drift-guard`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
```

Result: pass with the expected bounded host warning. Key output includes `OK runtime-status-surface`, `WARN codex-capability-degraded`, and `OK adapter-posture-visible`.

```powershell
codex --version
codex --help
codex status
codex exec resume --help
```

Result: `codex --version` returns `codex-cli 0.125.0`; `codex --help` has no top-level `status` subcommand; `codex status` still fails in this non-interactive context with `stdin is not a terminal`; `codex exec resume --help` exists but is supporting evidence only, not the required native attach status handshake.

## Decision
Do not start broad implementation-code optimization from this evidence refresh. The refreshed evidence supports only the existing bounded host-capability gap:

- target daily runs: pass for all 5 active targets
- host feedback: attention because Codex target runs remain degraded to `process_bridge`
- effect report: `adjust` with one candidate
- selector: `refresh_evidence_first`
- LTP promotion: still `defer_all`

## Rollback
Remove this evidence file, the `20260501200520` target-run JSON files, and the regenerated `effect-report-classroomtoolkit.json`, then rerun `python scripts/host-feedback-summary.py --assert-minimum --max-target-runs 5` and `python scripts/select-next-work.py --as-of 2026-05-01` to confirm the prior evidence posture.
