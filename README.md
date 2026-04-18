# Governed AI Coding Runtime

## Language / 语言
- 中文说明: [README.zh-CN.md](README.zh-CN.md)
- English guide: [README.en.md](README.en.md)
- Documentation index / 文档索引: [docs/README.md](docs/README.md)

## 中文快速结论
本项目已完成 `Foundation / GAP-020` 到 `GAP-023`。当前活跃执行队列已切到 `Full Runtime / GAP-024` 及后续阶段。现在可以使用的是“治理运行时契约层”以及已落地的 Foundation build/doctor 门禁，不是可部署的完整 SaaS / Web 服务。

当前可用能力：
- 运行仓库完整验证：文档、Schema、Catalog、脚本、runtime contract tests。
- 运行 Foundation build 门禁与 doctor 门禁。
- 运行第一个只读 trial 脚本。
- 在 Python 中复用 `packages/contracts` 下的任务、repo profile、审批、写侧治理、验证、handoff、eval/trace 等契约原语。

不能误解为已经完成的能力：
- 还没有生产级 runtime service。
- 还没有持久化 worker、数据库、Web 控制台、部署目标。
- `build` 与 `hotspot/doctor` 已有 Foundation 级真实入口，但还不是生产发布构建或服务级健康检查。

最常用命令：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
```

```powershell
python scripts/run-readonly-trial.py `
  --goal "inspect repository" `
  --scope "readonly trial" `
  --acceptance "readonly request accepted" `
  --repo-profile "schemas/examples/repo-profile/python-service.example.json" `
  --target-path "src/service.py" `
  --max-steps 1 `
  --max-minutes 5
```

## English Quick Answer
`Foundation / GAP-020` through `GAP-023` are complete. The active execution queue now starts at `Full Runtime / GAP-024`. The usable artifact is a governed runtime contract layer plus repository verification tooling and the landed Foundation build/doctor gates, not a deployable SaaS or web service yet.

Available now:
- Run full repository verification over docs, schemas, catalog, scripts, and runtime contract tests.
- Run Foundation build and doctor gates.
- Run the first read-only scripted trial.
- Reuse Python contract primitives under `packages/contracts` for task intake, repo profiles, approvals, write governance, verification, handoff, eval/trace, pilot checks, and console facade.

Not available yet:
- No production runtime service.
- No durable worker, database, web console, or deployment target.
- `build` and `hotspot/doctor` now have Foundation-grade live commands, but they are not production packaging or service-health entrypoints yet.

Primary command:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```

## Current Working Set / 当前工作入口
- Lifecycle roadmap: [docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md](docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md)
- Active execution plan: [docs/plans/full-runtime-implementation-plan.md](docs/plans/full-runtime-implementation-plan.md)
- Execution backlog: [docs/backlog/issue-ready-backlog.md](docs/backlog/issue-ready-backlog.md)
- Latest deep audit review: [docs/reviews/2026-04-18-full-repo-deep-audit-and-planning-refresh.md](docs/reviews/2026-04-18-full-repo-deep-audit-and-planning-refresh.md)
- Latest audit evidence: [docs/change-evidence/20260418-full-repo-deep-audit-and-planning-refresh.md](docs/change-evidence/20260418-full-repo-deep-audit-and-planning-refresh.md)


