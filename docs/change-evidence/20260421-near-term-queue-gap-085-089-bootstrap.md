# 20260421 Near-Term Queue GAP-085-089 Bootstrap

## Goal
在保持 `GAP-080..084` 已完成历史不回滚的前提下，创建下一段近端执行队列 `GAP-085..089`，并同步 backlog、issue seeds、文档姿态和 GitHub issue 渲染映射，支持自动连续执行。

## Scope
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/issue-seeds.yaml`
- `docs/backlog/README.md`
- `docs/backlog/full-lifecycle-backlog-seeds.md`
- `docs/README.md`
- `scripts/github/create-roadmap-issues.ps1`

## Changes
1. 新增 queue 项：`GAP-085..089`（NTP-06..NTP-10），包含依赖链、类型、user stories、what-to-build、acceptance criteria。
2. 更新机器种子版本：`issue_seed_version` 从 `3.9` 升级到 `4.0`。
3. 更新 near-term 姿态文案：
   - `GAP-080..084` 仍为 completed history。
   - `GAP-085..089` 成为 active execution-horizon queue。
4. 扩展 issue 渲染标签映射：`create-roadmap-issues.ps1` 将 near-term 标签范围从 `GAP-080..084` 扩展为 `GAP-080..089`。

## Verification
### Gate order
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
   - result: `OK python-bytecode`, `OK python-import`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
   - result: `Ran 268 tests ... OK`, `Ran 5 tests ... OK`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
   - result: `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
   - result: doctor checks all `OK` including gate command surfaces and adapter posture

### Supporting checks
5. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
   - result: docs drift and claim checks all `OK`
6. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`
   - result: `OK powershell-parse`, `OK issue-seeding-render`
7. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
   - result: `{"issue_seed_version":"4.0","rendered_tasks":67,"rendered_issue_creation_tasks":5,"rendered_epics":14,"rendered_initiative":true,"completed_task_count":62,"active_task_count":5}`

## Risks
- 新队列仅完成规划与渲染接线，尚未落地 runtime 行为；若将“active queue”误读为“已实现”，会导致对交付状态的过度声明。
- 若后续再扩展 `GAP-09x`，需继续保持 backlog、seeds、脚本映射和姿态文档同步。

## Rollback
Revert:
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/issue-seeds.yaml`
- `docs/backlog/README.md`
- `docs/backlog/full-lifecycle-backlog-seeds.md`
- `docs/README.md`
- `scripts/github/create-roadmap-issues.ps1`
- `docs/change-evidence/20260421-near-term-queue-gap-085-089-bootstrap.md`
