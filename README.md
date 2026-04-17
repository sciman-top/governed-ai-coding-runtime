# Governed AI Coding Runtime

## Language / 语言
- 中文说明: [README.zh-CN.md](README.zh-CN.md)
- English guide: [README.en.md](README.en.md)
- Documentation index / 文档索引: [docs/README.md](docs/README.md)

## 中文快速结论
本项目当前计划任务已经完成到 `Phase 4 / GAP-017`。现在可以使用的是“治理运行时契约层”和配套验证工具，不是可部署的完整 SaaS / Web 服务。

当前可用能力：
- 运行仓库完整验证：文档、Schema、Catalog、脚本、runtime contract tests。
- 运行第一个只读 trial 脚本。
- 在 Python 中复用 `packages/contracts` 下的任务、repo profile、审批、写侧治理、验证、handoff、eval/trace 等契约原语。

不能误解为已经完成的能力：
- 还没有生产级 runtime service。
- 还没有持久化 worker、数据库、Web 控制台、部署目标。
- `build` 和 `hotspot/doctor` 仍是 `gate_na`，因为还没有真实包构建和健康检查入口。

最常用命令：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
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
The current planned backlog is complete through `Phase 4 / GAP-017`. The usable artifact is a governed runtime contract layer plus repository verification tooling, not a deployable SaaS or web service yet.

Available now:
- Run full repository verification over docs, schemas, catalog, scripts, and runtime contract tests.
- Run the first read-only scripted trial.
- Reuse Python contract primitives under `packages/contracts` for task intake, repo profiles, approvals, write governance, verification, handoff, eval/trace, pilot checks, and console facade.

Not available yet:
- No production runtime service.
- No durable worker, database, web console, or deployment target.
- `build` and `hotspot/doctor` remain `gate_na` until real package build and health-check entrypoints exist.

Primary command:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```


