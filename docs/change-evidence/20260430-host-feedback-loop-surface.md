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
- Added multi-contract catalog sync support so a target repo can receive both its normal contract gate and target-specific policy gates, then used it for `vps-ssh-launcher` `contract:powershell-policy`.
- Added `runtime-flow-preset.ps1 -ExportTargetRepoRuns` and wired `operator.ps1 -Action DailyAll` to export fresh target-run JSON evidence after every all-target daily run.
- Adjusted the runtime doctor test contract to accept explicit `codex-capability-degraded` as a valid host-feedback state while still blocking `codex-capability-blocked`.
- Added a live `claude_workload` feedback dimension backed by `claude_code_adapter` probe/trial helpers so FeedbackReport can distinguish healthy Claude CLI/provider/MCP status from actual Claude Code workload readiness.

## Pre Change Review
- `pre_change_review`: sensitive paths were reviewed before and during the change because this touched `docs/targets/target-repos-catalog.json`, `scripts/apply-target-repo-governance.py`, `scripts/runtime-flow-preset.ps1`, and `scripts/verify-target-repo-governance-consistency.py`.
- `control_repo_manifest_and_rule_sources`: checked the control repo catalog and baseline paths through `docs/targets/target-repos-catalog.json`, `docs/targets/target-repo-governance-baseline.json`, and the existing hard gate contract.
- `user_level_deployed_rule_files`: no user-level rule file content was changed in this patch; `RulesDryRun` remained `changed_count=0` before the catalog/profile fix.
- `target_repo_deployed_rule_files`: no target `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` rule files were changed; the target repo change was limited to managed `.governed-ai/repo-profile.json` gate facts through the governance baseline sync.
- `target_repo_gate_scripts_and_ci`: compared the `vps-ssh-launcher` gate contract with `scripts/run_gates.ps1` and its tests; the missing gate was `contract:powershell-policy` with command `python .governed-ai/verify-powershell-policy.py`.
- `target_repo_repo_profile`: confirmed `D:\CODE\vps-ssh-launcher\.governed-ai\repo-profile.json` lacked the target-specific policy contract before sync and gained `contract:powershell-policy` after `GovernanceBaselineAll`.
- `target_repo_readme_and_operator_docs`: no README/operator usage semantics changed; existing operator entry remains `scripts/operator.ps1 -Action FeedbackReport` and `-Action DailyAll -Mode quick`.
- `current_official_tool_loading_docs`: no Codex/Claude rule-loading semantics were changed in this patch; host feedback reads local snapshots and manifest-backed distribution instead of changing tool loading behavior.
- `drift-integration decision`: source-of-truth fix was made in the control catalog and sync pipeline, then propagated through `GovernanceBaselineAll`; the target repo was not manually edited as the long-term source.

## Verification
- `python scripts/host-feedback-summary.py --assert-minimum`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action FeedbackReport`
- `python -m unittest tests.runtime.test_host_feedback_summary tests.runtime.test_operator_entrypoint tests.runtime.test_operator_ui`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`

Current observed status after hardening:
- `FeedbackReport` exits 0 and writes `.runtime/artifacts/host-feedback-summary/latest.md`.
- Overall report status is `attention`, not `pass`, because Codex local config reports `attention` and latest target-run evidence is stale at roughly 188 hours.
- After multi-contract sync, `vps-ssh-launcher` governance consistency is `drift_count=0`; the remaining daily refresh blocker moved to self-runtime pre-change evidence until this evidence section was added.
- After export wiring, `DailyAll -Mode quick` writes five fresh `*-daily-20260501004238.json` records and `FeedbackReport` returns `target_run_freshness=fresh`.
- Current Codex runtime attachment posture is `process_bridge / fallback_explicit` because native attach status handshake is unavailable; this is now surfaced as host feedback instead of hidden behind stale evidence.
- After Claude workload probe wiring, `FeedbackReport` reports `claude_workload=ok`, `readiness.status=ready`, and `adapter_tier=native_attach` on this host; current overall report status is `attention` only because the Codex local config dimension is still attention.

## Rollback
- Revert `scripts/host-feedback-summary.py`, the operator/UI wiring, the new product docs, and this evidence file if the new summary surface causes regressions or proves too noisy.
