# Governed AI Coding Runtime

## Language / 语言
- 中文说明: [README.zh-CN.md](README.zh-CN.md)
- English guide: [README.en.md](README.en.md)
- Documentation index / 文档索引: [docs/README.md](docs/README.md)

## 中文快速结论
本项目已经完成 `Foundation / GAP-020` 到 `GAP-023`、`Full Runtime / GAP-024` 到 `GAP-028`、`Public Usable Release / GAP-029` 到 `GAP-032`、`Maintenance Baseline / GAP-033` 到 `GAP-034`。这表示“本地单机运行时基线”已经落地，不表示“最终产品边界”已经完成。

当前仓库的正确理解是：
- 已完成一个可运行、可验证、可留痕的本地治理运行时基线
- 当前活跃下一阶段是 `Interactive Session Productization / GAP-035..039`
- 终态目标是“通用、可迁移、交互式会话优先、attach-first”的 governed AI coding runtime

当前可用能力：
- 运行仓库完整验证：文档、Schema、Catalog、脚本、runtime contract tests
- 运行本地 baseline 的 `build` 与 `doctor` 门禁
- 运行第一个只读 trial 脚本
- 运行 CLI-first runtime smoke path：创建任务、执行本地 worker、跑 `build -> test -> contract -> doctor`、写 evidence/handoff/replay、查询 runtime status
- 在 Python 中复用 `packages/contracts` 下的任务、repo profile、审批、执行运行时、artifact/replay、验证、handoff、eval/trace 等契约原语

当前仍在实现中的终态能力：
- 通用 target-repo 接入包与 attach flow
- attach-first 的会话桥接层
- direct Codex adapter
- capability-tiered 的多 AI 工具适配
- 多仓快速试验与反馈采集

最常用命令：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/bootstrap-runtime.ps1
```

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
python scripts/run-governed-task.py status --json
```

```powershell
python scripts/run-governed-task.py run --json
```

快速上手文档：
- [Single-Machine Runtime Quickstart](docs/quickstart/single-machine-runtime-quickstart.md)
- [Codex CLI/App Integration Guide](docs/product/codex-cli-app-integration-guide.md)
- [Codex CLI/App 集成指南](docs/product/codex-cli-app-integration-guide.zh-CN.md)
- [Generic Target-Repo Attachment Blueprint](docs/architecture/generic-target-repo-attachment-blueprint.md)
- [Interactive Session Productization Plan](docs/plans/interactive-session-productization-plan.md)

## English Quick Answer
`Foundation / GAP-020` through `GAP-023`, `Full Runtime / GAP-024` through `GAP-028`, `Public Usable Release / GAP-029` through `GAP-032`, and `Maintenance Baseline / GAP-033` through `GAP-034` are complete. That means the local single-machine runtime baseline is landed. It does not mean the final product boundary is complete.

The active next-step queue is now `Interactive Session Productization / GAP-035..039`.

Available now:
- Full repository verification over docs, schemas, catalog, scripts, and runtime contract tests
- Local baseline `build` and `doctor` gates
- The first read-only scripted trial
- A CLI-first governed runtime smoke path with persisted evidence, handoff, replay, and runtime status
- Python contract primitives under `packages/contracts`

Still in progress as the true end-state:
- generic target-repo onboarding and attachment
- attach-first session bridge
- direct Codex adapter
- capability-tiered non-Codex adapters
- multi-repo trial feedback loop

Primary docs:
- [Single-Machine Runtime Quickstart](docs/quickstart/single-machine-runtime-quickstart.md)
- [Codex CLI/App Integration Guide](docs/product/codex-cli-app-integration-guide.md)
- [Generic Target-Repo Attachment Blueprint](docs/architecture/generic-target-repo-attachment-blueprint.md)
- [Interactive Session Productization Plan](docs/plans/interactive-session-productization-plan.md)
