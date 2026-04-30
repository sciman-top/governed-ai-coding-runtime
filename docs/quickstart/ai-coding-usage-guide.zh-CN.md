# AI 编码使用指南

## 目的
说明如何把本运行时与 Codex/Claude Code 等 AI 编码宿主配合使用，并明确它在真实编码流程中的具体辅助作用。

## 根本原则
- 本项目面向宿主工作流的根本原则是“综合效率优先”。
- 落到执行上，就是：少打扰、自动连续执行、节省 token / 成本、高效率。
- 当前默认组合如 `gpt-5.4 + medium + never` 只是这个原则下的暂行实现，不是更高层规则。
- 以后如果模型、推理档位、compact 阈值或宿主工具更迭，应先保持这条原则；只有在安全与门禁不退化时，才替换当前实现。

## 推荐使用模式

### 总入口速记
- 操作者聚合入口：`scripts/operator.ps1`
- 宿主反馈汇总：`scripts/operator.ps1 -Action FeedbackReport`
- 目标仓日常运行/批量一键应用：`scripts/runtime-flow-preset.ps1`
- 全局/项目级 AI 规则同步：`scripts/sync-agent-rules.ps1`
- 本仓完整自检：`scripts/verify-repo.ps1 -Check All`

常用一键命令：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action Help

pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action Readiness

pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action OperatorUi -OpenUi

pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action OperatorUi -OpenUi -UiLanguage en

pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action FeedbackReport

pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -ListTargets

pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 `
  -AllTargets `
  -ApplyGovernanceBaselineOnly `
  -Json

pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 `
  -AllTargets `
  -ApplyAllFeatures `
  -FlowMode "daily" `
  -MilestoneTag "milestone" `
  -Json

pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -Apply
```

### Operator UI
默认中文打开交互控制台：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action OperatorUi -OpenUi
```

英文版打开交互控制台：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action OperatorUi -OpenUi -UiLanguage en
```

这个 UI 在 `127.0.0.1` 上运行本地常驻交互服务，后续可直接访问 `http://127.0.0.1:8770/?lang=zh-CN`；状态/停止/重启使用 `scripts/operator-ui-service.ps1 -Action Status|Stop|Restart`。可点击执行 allowlist 内的 readiness、目标仓列表、规则漂移检查、规则同步、治理基线下发、daily 和全部功能应用；可选择全部目标仓或单个目标仓，也可调整语言、验证模式、并发、fail-fast、只预演与里程碑标签；执行结果会写入输出区和本地浏览器执行历史，并可点击 evidence/artifact/verification refs 查看文件内容。若只想生成只读快照，去掉 `-OpenUi`，输出位于 `.runtime/artifacts/operator-ui/index.html`。
`Codex` 页签会把“综合效率优先”单独作为长期原则展示，而把当前模型组合只当作暂行实现，这样以后默认模型更新时，不会把更高层原则一起改没。

### 宿主反馈汇总
如果你想系统性判断“功能在 Codex 和 Claude 里是否真的生效、异常属于宿主还是 runtime、下一步该优化哪里”，直接生成统一反馈报告，而不是只读单次日志：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action FeedbackReport
```

报告会汇总：
- 本机 `Codex` 状态摘要
- 本机 `Claude` 状态摘要
- 规则 manifest 与全局副本同步面
- 最新 target repo run evidence 摘要
- 推荐的下一步动作

Markdown 报告落在：
- `.runtime/artifacts/host-feedback-summary/latest.md`

### 模式 A：治理侧车（阻力最低）
继续按原方式使用宿主工具，把本运行时用于 readiness、verification 和证据留痕。

1. 初始化与健康检查：
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/bootstrap-runtime.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/install-repo-hooks.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```
2. 查看 runtime/Codex 能力姿态：
```powershell
python scripts/run-governed-task.py status --json
```

### 模式 B：Attach-First 日常流（外部仓推荐）
先把目标仓接入，再跑一键日常治理链。

1. 接入或校验目标仓 light-pack：
```powershell
python scripts/attach-target-repo.py `
  --target-repo "<target-repo-root>" `
  --runtime-state-root "<machine-local-runtime-state-root>" `
  --repo-id "<repo-id>" `
  --primary-language "<language>" `
  --build-command "<build>" `
  --test-command "<test>" `
  --contract-command "<contract>" `
  --adapter-preference "native_attach"
```
2. 运行 daily 治理链：
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow.ps1 `
  -FlowMode "daily" `
  -AttachmentRoot "<target-repo-root>" `
  -AttachmentRuntimeStateRoot "<machine-local-runtime-state-root>" `
  -Mode "quick"
```

### 模式 C：受治理写入流（中高风险改动）
对 medium/high 风险写入使用 runtime-managed 的 request/approve/execute 流程。

1. 评估写治理姿态：
```powershell
python scripts/run-governed-task.py govern-attachment-write `
  --attachment-root "<target-repo-root>" `
  --attachment-runtime-state-root "<machine-local-runtime-state-root>" `
  --task-id "<task-id>" `
  --tool-name "apply_patch" `
  --target-path "<target-path>" `
  --tier "medium" `
  --rollback-reference "<rollback-ref>" `
  --json
```
2. 升级请求审批并执行：
```powershell
python scripts/run-governed-task.py decide-attachment-write `
  --attachment-runtime-state-root "<machine-local-runtime-state-root>" `
  --approval-id "<approval-id>" `
  --decision "approve" `
  --decided-by "operator" `
  --json

python scripts/run-governed-task.py execute-attachment-write `
  --attachment-root "<target-repo-root>" `
  --attachment-runtime-state-root "<machine-local-runtime-state-root>" `
  --task-id "<task-id>" `
  --tool-name "write_file" `
  --target-path "<target-path>" `
  --tier "medium" `
  --rollback-reference "<rollback-ref>" `
  --approval-id "<approval-id>" `
  --content "<content>" `
  --json
```

## 对 AI 编码的具体辅助作用

| AI 编码阶段 | 运行时辅助能力 | 实际价值 |
|---|---|---|
| 会话就绪检查 | `status`/`doctor` 暴露 Codex capability readiness 与 adapter tier | 在执行前提前发现降级姿态，避免误判能力 |
| 仓库接入 | attach-first light-pack 生成/校验 | 给宿主会话提供一致的仓库策略与 gate 元数据 |
| 规则同步 | `sync-agent-rules.ps1` 按 manifest 下发 `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` | 降低多宿主、多仓规则漂移 |
| 重复故障预防 | governance baseline 下发 Windows 进程环境、统一入口、low-token、fast/full gate 等策略 | 把反复问题固化到目标仓，而不是依赖提示 |
| 效率优先默认值 | 保持一套稳定默认配置，只在必要时手动升档 | 兼顾连续执行、低 token 成本与升级路径 |
| 验证执行 | runtime-managed gate 流（`build -> test -> contract/invariant -> hotspot`） | 验收链稳定且可复现 |
| 高风险写入 | medium/high 风险策略、审批、fail-closed | 防止越权或无审批高风险改动 |
| 交付与审计 | evidence/handoff/replay refs 与 task/run 绑定 | 交付可追溯、回滚路径清晰 |
| 多仓运维 | preset/daily flow 与 multi-repo trial surface | 多仓治理姿态可以重复执行并横向对齐 |

## 边界说明
- 本项目是上游宿主之上的治理/运行时层，不是替代宿主 UI 的新执行宿主。
- `native_attach` 受环境影响，可能降级到 `process_bridge` 或 `manual_handoff`。
- 不应宣称“所有仓库、所有环境、所有高风险流程都已被本项目完全接管”。

## 相关文档
- [Use With An Existing Repo](./use-with-existing-repo.md)
- [在现有仓库中使用](./use-with-existing-repo.zh-CN.md)
- [Codex CLI/App Integration Guide](../product/codex-cli-app-integration-guide.md)
- [Codex CLI/App 集成指南](../product/codex-cli-app-integration-guide.zh-CN.md)
- [Codex / Claude 功能反馈闭环](../product/host-feedback-loop.zh-CN.md)
