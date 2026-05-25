# 2026-05-25 Token-Efficient One-Click Rollout Follow-Up

- rules: R1/R6/R8, pre_change_review
- risk: medium
- current_location: `D:\CODE\governed-ai-coding-runtime`
- target_destination: one-click target governance baseline, rule sync manifest, and rollout contract validation

## pre_change_review
- control_repo_manifest_and_rule_sources: reviewed `rules/manifest.json`, `rules/global/**`, and `rules/projects/**`; current manifest contains 24 entries, including Cockpit-Tools-Local project rules.
- user_level_deployed_rule_files: verified with `python scripts/sync-agent-rules.py --scope All --fail-on-change`; after sync, global Codex/Claude/Gemini deployed files match source version `9.53`.
- target_repo_deployed_rule_files: verified target project rule projections through the same sync check; Cockpit-Tools-Local same-version drift was merged by the canonical rule-sync entrypoint.
- target_repo_gate_scripts_and_ci: checked `scripts/runtime-flow-preset.ps1`, `scripts/verify-target-repo-rollout-contract.py`, rollout contract tests, and agent rule sync tests.
- target_repo_repo_profile: no repo-profile schema change was introduced in this follow-up; target selection continues to come from the catalog and manifest.
- target_repo_readme_and_operator_docs: quickstart/operator documentation changes are treated as operator-facing docs only; they do not override manifest, gate, or sync behavior.
- current_official_tool_loading_docs: Codex/Claude/Gemini rule files remain context rules; this follow-up does not add auth/provider/profile writes or process restart behavior.
- drift-integration decision: integrate `.ignore` as a managed baseline file, keep live Codex token config outside one-click ApplyAllFeatures, and synchronize rule-file drift only through `scripts/sync-agent-rules.ps1 -Scope All -Apply`.

## Verification
- `python -m unittest tests.runtime.test_agent_rule_sync`: pass, 8 tests.
- `python scripts/verify-target-repo-rollout-contract.py`: pass, `sync_revision = 2026-05-23.1`, `errors = []`.
- `python -m unittest tests.runtime.test_target_repo_rollout_contract`: pass, 13 tests.
- `python scripts/sync-agent-rules.py --scope All --fail-on-change`: pass, `entry_count = 24`, `changed_count = 0`, `blocked_count = 0`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`: pass with non-blocking `WARN codex-capability-degraded`.

## Rollback
- Revert this follow-up with git for control-repo files.
- Rule sync backups are under `docs/change-evidence/rule-sync-backups/`.
- Re-run `python scripts/sync-agent-rules.py --scope All --fail-on-change` and `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` after rollback.
