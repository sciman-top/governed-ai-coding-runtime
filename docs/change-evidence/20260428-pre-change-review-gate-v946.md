# Pre-change Review Gate v9.46 Evidence

## Goal
- 将“先核查本机用户目录全局规则、目标仓项目规则与目标仓真实门禁/profile/CI/script/README 差异，再参考官方文档和社区实践合并修改”从口头执行习惯提升为规则、baseline、测试和同步门禁。

## Changes
- 规则族升级到 `9.46`，`rules/manifest.json` `sync_revision=2026-04-28.2`。
- 全局与项目规则中的前置检查从“规则文件修改前”扩展为“规则文件、门禁、profile、baseline 或同步脚本修改前”。
- `docs/targets/target-repo-governance-baseline.json` 增加 `rule_file_coordination_policy.pre_change_review_gate`。
- `pre_change_review_gate` 覆盖 `rule_file_changes`、`gate_command_changes`、`repo_profile_changes`、`governance_baseline_changes`、`sync_script_changes`。
- required inputs 明确包含控制仓源文件、用户目录分发副本、目标仓分发副本、目标仓 gate scripts / CI、repo-profile、README/operator docs、当前官方工具加载文档，以及不改变工具语义时可参考的可信社区实践。
- 测试更新：`tests/runtime/test_target_repo_governance_consistency.py` 断言该 gate 的输入、阻断行为和证据要求。
- 新增执行门禁脚本：`scripts/verify-pre-change-review.py`。当 diff 涉及规则、门禁、profile、baseline 或同步脚本时，必须在本次 `docs/change-evidence/*.md` 中找到结构化 `pre_change_review` 证据。
- `scripts/verify-repo.ps1 -Check Contract` 已接入 `Invoke-PreChangeReviewChecks`，通过后输出 `OK pre-change-review`。
- 新增测试：`tests/runtime/test_pre_change_review.py` 覆盖敏感改动无证据失败、有结构化证据通过。

## pre_change_review
- `control_repo_manifest_and_rule_sources`: checked `rules/manifest.json` and managed rule source files before updating rule family version and wording.
- `user_level_deployed_rule_files`: checked by `python scripts/sync-agent-rules.py --scope All --fail-on-change`; deployed user files were synchronized through manifest apply.
- `target_repo_deployed_rule_files`: checked by `python scripts/sync-agent-rules.py --scope All --fail-on-change`; 15 target project rule files were synchronized through manifest apply.
- `target_repo_gate_scripts_and_ci`: checked current target governance consistency and existing gate/profile propagation paths before changing the baseline contract.
- `target_repo_repo_profile`: checked through `python scripts/verify-target-repo-governance-consistency.py` and `runtime-flow-preset.ps1 -AllTargets -ApplyGovernanceBaselineOnly -Json`.
- `target_repo_readme_and_operator_docs`: no direct README/operator-doc rewrite in this step; rule change requires future gate/profile/baseline edits to read target README/operator docs before changing commands.
- `current_official_tool_loading_docs`: inherited from the v9.45 source review evidence for Codex AGENTS.md, Claude Code memory/settings, and Gemini CLI GEMINI.md/context behavior; no new tool-loading semantics were changed in v9.46.
- `credible_community_practice_when_tool_semantics_are_not_changed`: used only as implementation-shape signal for concrete, checkable, evidence-backed rules.
- `drift-integration decision`: no uncontrolled same-version drift was accepted; rule family moved to `9.46` and synchronized through the manifest after dry-run showed `blocked_count=0`.

## Verification
- Dry-run before apply: `python scripts/sync-agent-rules.py --scope All --fail-on-change` -> `status=dry_run_changes`, `changed_count=18`, `blocked_count=0`.
- Focused tests: `python -m unittest tests.runtime.test_target_repo_governance_consistency.TargetRepoGovernanceConsistencyTests.test_default_baseline_requires_windows_process_environment_policy tests.runtime.test_agent_rule_sync.AgentRuleSyncTests.test_default_manifest_covers_global_and_project_rule_sources` -> pass.
- Rule sync apply: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -Apply` -> `status=applied`, `changed_count=18`, `blocked_count=0`; backup root `docs/change-evidence/rule-sync-backups/20260428-003004/`.
- Target governance baseline apply: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -ApplyGovernanceBaselineOnly -Json` -> `target_count=5`, `failure_count=0`.
- Final sync check: `python scripts/sync-agent-rules.py --scope All --fail-on-change` -> `status=pass`, `changed_count=0`, `blocked_count=0`.
- Target governance consistency: `python scripts/verify-target-repo-governance-consistency.py` -> `status=pass`, `sync_revision=2026-04-28.2`, `drift_count=0`.
- Format check: `git diff --check` -> pass.
- Build: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1` -> `OK python-bytecode`, `OK python-import`.
- Focused execution-gate tests: `python -m unittest tests.runtime.test_pre_change_review tests.runtime.test_target_repo_governance_consistency.TargetRepoGovernanceConsistencyTests.test_default_baseline_requires_windows_process_environment_policy` -> pass.
- Direct pre-change gate: `python scripts/verify-pre-change-review.py` -> `status=pass`, matched evidence `docs/change-evidence/20260428-pre-change-review-gate-v946.md`.
- Runtime test: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` -> `Completed 75 test files`, `failures=0`.
- Contract: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` -> `OK agent-rule-sync`, `OK pre-change-review`, `OK functional-effectiveness`.
- Hotspot: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1` -> all checks `OK`.

## Rollback
- Preferred rollback: git restore/revert the rule source, baseline, test, and evidence changes, then rerun `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -Apply`.
- Backup rollback: restore distributed rule files from `docs/change-evidence/rule-sync-backups/20260428-003004/`.
