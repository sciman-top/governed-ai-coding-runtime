# 20260423 Low-Token Interaction Profile Baseline Sync

## Goal
- 将低 token 交互默认策略纳入 active target 治理基线，并确保可一键同步到所有目标仓且通过一致性与硬门禁验证。

## Clarification Trace
- `issue_id=low-token-interaction-profile-baseline-sync`
- `attempt_count=1`
- `clarification_mode=direct_fix`
- `clarification_scenario=acceptance`
- `clarification_questions=[]`
- `clarification_answers=[]`

## Scope
- `.governed-ai/repo-profile.json`
- `docs/targets/target-repo-governance-baseline.json`
- `docs/quickstart/use-with-existing-repo.zh-CN.md`
- `docs/quickstart/use-with-existing-repo.md`
- `docs/change-evidence/20260423-low-token-interaction-profile-baseline-sync.md`
- `docs/change-evidence/README.md`

## Changes
1. 更新治理基线覆盖项
- `sync_revision` 从 `2026-04-23.1` 升级到 `2026-04-23.2`。
- 在 `required_profile_overrides` 新增 `interaction_profile`，默认值为：
  - `default_mode=guided`
  - `term_explain_style=definition_plus_task_role`
  - `default_checklist_kind=bugfix`
  - `compaction_preference=stage_summary`
  - `summary_template=goal-plan-changes-verification-risks`
  - `handoff_teaching_notes` 保持短摘要导向。

2. 同步双语使用说明
- 更新中英文 quickstart 的“Baseline sync behavior”说明，明确默认基线已覆盖低 token `interaction_profile`。

3. 执行全目标仓基线同步
- 运行 `runtime-flow-preset` 的 `-AllTargets -ApplyGovernanceBaselineOnly`。
- 结果：`target_count=5`、`failure_count=0`，5 个 active target 都仅显示 `governance_sync_changed=interaction_profile`。
- 连带结果：当前仓作为 `self-runtime` 目标，其 `.governed-ai/repo-profile.json` 新增同一 `interaction_profile` 块。

## Verification
1. 全目标仓基线同步
- Command:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -ApplyGovernanceBaselineOnly -Json`
- Result:
  - `target_count=5`
  - `failure_count=0`
  - 每个 target 的 `governance_sync_status=pass`，`governance_sync_changed=interaction_profile`

2. 一致性检查
- Command:
  - `python scripts/verify-target-repo-governance-consistency.py`
- Result:
  - `status=pass`
  - `sync_revision=2026-04-23.2`
  - `drift_count=0`

3. Gate order（硬门禁）
- Build:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - key output: `OK python-bytecode`, `OK python-import`
- Test:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - key output: `Ran 353 tests ... OK (skipped=2)`, `Ran 5 tests ... OK`
- Contract/Invariant:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - key output: `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing`, `OK dependency-baseline`, `OK target-repo-governance-consistency`
- Hotspot:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  - key output: `OK gate-command-build`, `OK gate-command-test`, `OK gate-command-contract`, `OK gate-command-doctor`, `OK codex-capability-ready`, `OK adapter-posture-visible`

4. Supporting check
- Docs:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  - key output: `OK active-markdown-links`, `OK claim-drift-sentinel`, `OK claim-evidence-freshness`, `OK post-closeout-queue-sync`

## Risks
- 基线同步是覆盖式的 `required_profile_overrides` 行为；若单个目标仓存在定制 `interaction_profile`，会被本次统一值覆盖。
- 本次同步修改了 5 个 active target 仓库中的 `.governed-ai/repo-profile.json`（仓外变更，不在本仓 git diff 内）。

## Rollback
1. 回滚本仓改动
- `git checkout -- .governed-ai/repo-profile.json`
- `git checkout -- docs/targets/target-repo-governance-baseline.json`
- `git checkout -- docs/quickstart/use-with-existing-repo.zh-CN.md`
- `git checkout -- docs/quickstart/use-with-existing-repo.md`
- `git checkout -- docs/change-evidence/20260423-low-token-interaction-profile-baseline-sync.md`
- `git checkout -- docs/change-evidence/README.md`

2. 回滚已同步目标仓（按需）
- 在每个目标仓执行：`git checkout -- .governed-ai/repo-profile.json`
- 或恢复到旧基线并重跑：
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -ApplyGovernanceBaselineOnly -Json`
