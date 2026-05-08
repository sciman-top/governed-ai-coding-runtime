# Host Feedback Autonomy Loop

## Goal
- Reduce false operator interruptions in the Codex/Claude/Gemini feedback loop.
- Ensure daily all-target runs refresh evidence that `FeedbackReport` actually consumes.
- Keep Codex local model/reasoning choices advisory while preserving hard safety, context, sandbox, and credential checks.

## Root Cause And Changes
- `host-feedback-summary.py` recommended `runtime-flow-preset.ps1 -AllTargets -FlowMode daily -Json` when target-run evidence was missing, but that command does not export `docs/change-evidence/target-repo-runs/*` evidence.
- `host-feedback-summary.py` defaulted to `--max-target-runs=5`, which silently hid the sixth active target repo after the catalog expanded.
- `codex_local.config_health()` treated model and reasoning-effort drift as blocking config health, even though this repo's policy audit treats model/provider choices as implementation preferences under the stable efficiency-first principle.
- Updated the missing-evidence recommendation to include `-ExportTargetRepoRuns`.
- Changed default target-run summary behavior to include all latest target repos unless the caller explicitly sets `--max-target-runs`.
- Split Codex config checks into hard `checks` and non-blocking `advisory_checks`.
- Updated the Codex local optimizer and quickstart docs from the stale `gpt-5.3-codex` baseline to `gpt-5.5 + medium + never`.
- Updated `select-next-work.py`, `autonomous-next-work-selection-policy.json`, runtime evolution, and operator UI host-feedback consumers to use full target-run summaries.
- Corrected the bounded host-capability defer branch so fresh but degraded target-run evidence selects `wait_for_host_capability_recovery` instead of another evidence-refresh loop.

## Verification
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/Optimize-ClaudeLocal.ps1 -Apply`
  - result: `status=ok`, active provider `bigmodel-glm`, config `status=ok`.
- `python scripts/verify-policy-tool-credential-audit.py`
  - result: `status=pass`, `local_agent_config_status=pass`.
- `python scripts/sync-agent-rules.py --scope All --fail-on-change`
  - result: `status=pass`, `changed_count=0`, `blocked_count=0`, `entry_count=21`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -ApplyCodingSpeedProfile -Json -BatchTimeoutSeconds 1800`
  - result: `target_count=6`, `failure_count=0`, `batch_timed_out=false`.
- `python scripts/verify-target-repo-governance-consistency.py`
  - result: `status=pass`, `target_count=6`, `drift_count=0`.
- `python scripts/verify-target-repo-rollout-contract.py`
  - result: `status=pass`, `capability_count=14`, `feature_count=6`, `baseline_field_count=6`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -FlowMode daily -Mode quick -SkipGovernanceBaselineSync -Json -ExportTargetRepoRuns -RuntimeFlowTimeoutSeconds 360 -BatchTimeoutSeconds 1800 -FailFast`
  - result: `target_count=6`, `failure_count=0`, `batch_timed_out=false`, `export_count=6`, `speed_kpi_status=pass`, `effect_reports_status=pass`.
- `python -m unittest tests.runtime.test_host_feedback_summary`
  - result: `Ran 8 tests`, `OK`.
- `python -m unittest tests.runtime.test_codex_local tests.runtime.test_policy_tool_credential_audit`
  - result: `Ran 33 tests`, `OK`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/Optimize-CodexLocal.ps1`
  - result: dry-run shows `model=gpt-5.5`, `model_reasoning_effort=medium`, `approval_policy=never`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action FeedbackReport`
  - result: `dimensions_ok=5`, `dimensions_attention=1`, `latest_target_repos=6`, `codex_host_status=ok`, `claude_workload_status=ready`, `target_run_freshness=fresh`.
- `python -m unittest tests.runtime.test_evidence_recovery_posture tests.runtime.test_autonomous_next_work_selection tests.runtime.test_host_feedback_summary`
  - result: `Ran 18 tests`, `OK`.
- `python scripts/select-next-work.py`
  - result: `next_action=wait_for_host_capability_recovery`, `degraded_latest_run_count=6`, `evidence_blocker=host_capability_degraded_bounded_defer`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - result: `OK python-bytecode`, `OK python-import`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - result: `Completed 105 test files`, `failures=0`, `OK runtime-unittest`, `OK runtime-service-parity`, `OK runtime-service-wrapper-drift-guard`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - result: `OK dependency-baseline`, `OK target-repo-rollout-contract`, `OK target-repo-governance-consistency`, `OK policy-tool-credential-audit`, `OK functional-effectiveness`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  - result: doctor checks passed with expected `WARN codex-capability-degraded`; this warning remains the honest host capability boundary until native attach recovery evidence exists.

## Remaining Attention
- Fresh target-run evidence still reports `codex_capability_status=degraded` and `adapter_tier=process_bridge` for all six target repos.
- Do not claim Codex native attach recovery until fresh target-run evidence reports both `codex_capability_status=ready` and `adapter_tier=native_attach`.

## Rollback
- Revert `scripts/host-feedback-summary.py`.
- Revert `scripts/select-next-work.py`.
- Revert `scripts/evaluate-runtime-evolution.py`.
- Revert `scripts/serve-operator-ui.py`.
- Revert `docs/architecture/autonomous-next-work-selection-policy.json`.
- Revert `scripts/lib/codex_local.py`.
- Revert `scripts/Optimize-CodexLocal.ps1`.
- Revert `tests/runtime/test_host_feedback_summary.py`.
- Revert `tests/runtime/test_codex_local.py`.
- Revert `tests/runtime/test_autonomous_next_work_selection.py`.
- Revert `docs/quickstart/ai-coding-usage-guide.md` and `docs/quickstart/ai-coding-usage-guide.zh-CN.md`.
- Remove this evidence file and regenerate affected reports if the old behavior is intentionally restored.
