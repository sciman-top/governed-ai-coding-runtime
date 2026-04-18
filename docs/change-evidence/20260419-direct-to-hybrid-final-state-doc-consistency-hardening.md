# 20260419 Direct-To-Hybrid Final-State Doc Consistency Hardening

## Goal
- 修复“终态总纲 / 直达终态路线图 / 混合终态实施总计划 / 终态任务清单”之间的主线一致性漂移。
- 让 `Phase 4 -> Phase 5` 顺序、活跃队列口径、完成声明边界和入口导航保持同一事实源。

## Basis
- `docs/architecture/hybrid-final-state-master-outline.md`
- `docs/roadmap/direct-to-hybrid-final-state-roadmap.md`
- `docs/plans/direct-to-hybrid-final-state-implementation-plan.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/reviews/2026-04-19-hybrid-final-state-executable-gap-audit.md`
- `AGENTS.md`（项目级：规划/schema/脚本类变更需补 `docs/change-evidence`）

## Changes
1. 顺序一致性修复（核心）：
   - 重排 `direct-to-hybrid-final-state-implementation-plan` 中 Task 10-14 的阶段顺序：
     - Task 10-11 对应服务化提取（Phase 4）
     - Task 12-14 对应硬化收口（Phase 5）
   - 同步更新 checkpoint 分段与风险语句，消除与 roadmap/backlog 的反向依赖。
2. 完成声明边界修复：
   - `issue-ready-backlog` 中 `GAP-039` 增加“第一版产品化切片”限定，并把 external attached-repo 完整闭环明确挂到 `GAP-053`。
   - 将 `GAP-039` 的验收描述改为 profile-based 试运行已完成，避免与可执行缺口审查冲突。
3. 活跃队列口径同步：
   - `docs/backlog/README.md`、`docs/backlog/full-lifecycle-backlog-seeds.md` 从“无 open queue / 018..044”切换到“045..060 为 active queue”。
4. 导航入口同步：
   - 更新 `README.md`、`docs/README.md`、`docs/plans/README.md`、`docs/reviews/README.md`，将 `2026-04-19` 审查与 direct-to-final-state 规划包作为主入口。
   - `docs/product/positioning-roadmap-competitive-layers.zh-CN.md` 的“当前活跃队列”改为 `GAP-045..060`。
5. 证据约束强化：
   - 在 `direct-to-hybrid-final-state-implementation-plan` 增加跨任务证据规则：
     - 修改 planning/spec/schema/script 时，必须新增一条 `docs/change-evidence/<date>-<slug>.md`。

## Changed Files
- `README.md`
- `docs/README.md`
- `docs/backlog/README.md`
- `docs/backlog/full-lifecycle-backlog-seeds.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/plans/README.md`
- `docs/plans/direct-to-hybrid-final-state-implementation-plan.md`
- `docs/product/positioning-roadmap-competitive-layers.zh-CN.md`
- `docs/reviews/README.md`
- `docs/roadmap/direct-to-hybrid-final-state-roadmap.md`

## Commands
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
   - exit `0`
   - key output: `OK python-bytecode`, `OK python-import`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
   - exit `0`
   - key output: `Ran 204 tests ... OK`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
   - exit `0`
   - key output: `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
   - exit `0`
   - key output: `OK gate-command-build/test/contract/doctor`
5. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
   - exit `0`
   - key output: `OK active-markdown-links`, `OK backlog-yaml-ids`
6. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`
   - exit `0`
   - key output: `OK powershell-parse`, `OK issue-seeding-render`
7. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
   - exit `0`
   - key output: `rendered_tasks=43`, `rendered_epics=7`, `rendered_initiative=true`

## Risk
- 低风险（文档与规划口径修复，无 runtime 行为代码变更）。
- 主要风险是历史语义误读；通过“history vs active mainline”显式分层已降低该风险。

## Rollback
- 回滚以下文件到本次改动前版本：
  - `README.md`
  - `docs/README.md`
  - `docs/backlog/README.md`
  - `docs/backlog/full-lifecycle-backlog-seeds.md`
  - `docs/backlog/issue-ready-backlog.md`
  - `docs/plans/README.md`
  - `docs/plans/direct-to-hybrid-final-state-implementation-plan.md`
  - `docs/product/positioning-roadmap-competitive-layers.zh-CN.md`
  - `docs/reviews/README.md`
  - `docs/roadmap/direct-to-hybrid-final-state-roadmap.md`
  - `docs/change-evidence/20260419-direct-to-hybrid-final-state-doc-consistency-hardening.md`
