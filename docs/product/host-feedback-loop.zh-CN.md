# Codex / Claude 功能反馈闭环

## 目的
说明怎样系统性获得本项目在 `Codex` 与 `Claude Code` 环境中的真实功能反馈，而不是只看单次命令输出。

## 核心原则
- 对宿主默认值相关决策，最高层规则始终是“综合效率优先”：少打扰、自动连续执行、节省 token / 成本、高效率。
- 具体模型组合、推理档位、compact 阈值、provider 选择都只是这条规则下的阶段性实现，不应反客为主。
- 先区分宿主问题、规则漂移、runtime 降级、目标仓治理失败，不把所有异常混成“项目没生效”。
- 先看机器证据，再做主观判断；任何“优化建议”都应能回指到具体 `status`、`adapter_tier`、`closure_state`、`write_status`、`evidence refs`。
- 反馈闭环必须固定入口、固定维度、固定证据位置，否则每次排查都会重新发明流程。

## AI 推荐闭环
1. 生成本仓 readiness 与交互面板：
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action Readiness -OpenUi`
2. 检查规则同步面：
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action RulesDryRun`
3. 生成宿主反馈汇总：
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action FeedbackReport`
4. 跑真实目标仓 daily：
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action DailyAll -Mode quick -OpenUi`
5. 最后按 full gate 收口：
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`

理由：这条链能把本机宿主状态、规则分发、runtime 能力、真实目标仓效果和最终门禁统一到一个闭环里，而不是分别看零散脚本输出。

## 统一反馈维度

| 维度 | 主要问题 | 关键字段/证据 |
|---|---|---|
| 宿主入口 | 现在调用的到底是不是预期的 `codex` / `claude` | 可执行入口、`config`/`settings` 状态、账号或 provider 状态 |
| 规则生效 | 规则是不是只改了源文件，没有同步到用户目录/目标仓 | `rules/manifest.json`、`RulesDryRun`、全局目标副本 |
| 能力姿态 | 当前是 `native_attach`、`process_bridge` 还是 `manual_handoff` | `adapter_tier`、`flow_kind`、`unsupported_capabilities` |
| Claude workload probe | `Claude Code` 是否真的暴露本仓编码所需的 settings/hooks、session/resume 和结构化证据能力 | `claude_workload.readiness`、`probe_commands`、trial refs |
| 门禁执行 | 是不是只跑了局部 quick slice | `build -> test -> contract/invariant -> hotspot` |
| 写流治理 | 高风险改动是否真的进入 request/approve/execute 闭环 | `approval_status`、`write_status`、handoff/replay refs |
| 证据可解释性 | 输出能不能解释“为什么通过/为什么降级/为什么阻断” | `evidence_link`、`artifact_refs`、`verification_refs` |
| 双宿主一致性 | `Codex` 与 `Claude` 是否达到相同治理结果 | parity matrix、latest target runs、host feedback summary |
| 批量稳定性 | 多目标仓一键执行后是否还能保持一致 | `target-repo-runs/*.json`、governance consistency 检查 |

## 统一报告入口

### 一键生成反馈报告
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action FeedbackReport
```

它会调用：

```powershell
python scripts/host-feedback-summary.py --assert-minimum --write-markdown .runtime/artifacts/host-feedback-summary/latest.md
```

输出包括：
- 本机 `Codex` 状态摘要
- 本机 `Claude` 状态摘要
- live `Claude Code` workload adapter readiness
- 规则 manifest 与全局副本同步面
- `Codex` / `Claude` parity 文档面
- 最新目标仓 run evidence 摘要
- 下一步推荐动作

Markdown 报告固定落在：
- `.runtime/artifacts/host-feedback-summary/latest.md`

## 怎样判读

### 情况 1：宿主状态异常，但目标仓 run 仍正常
优先判断为宿主本机配置问题，而不是 runtime 代码问题。

### 情况 1.5：当前默认组合显得过时，但闭环仍然有效
应先更新具体默认实现，再继续保持“综合效率优先”这条更高层规则，不要把原则写死成某一代模型组合。

### 情况 2：规则 manifest 正常，但全局副本缺失
优先运行：
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -Apply
```

### 情况 3：`adapter_tier` 降级但 gate 仍通过
说明治理结果可用，但宿主能力没达到最佳态；此时应优化宿主接入，不应误报“功能整体失效”。

### 情况 3.5：Claude 宿主健康，但 `claude_workload` 降级或阻断
说明 `claude` CLI/provider/MCP 层可能正常，但真实编码 workload 路径还不完整。此时按 `claude_workload.readiness.status`、`adapter_tier`、`unsupported_capabilities`、`probe_commands` 判断缺的是 managed settings/hooks、session/resume 参数，还是 structured hook-event evidence。

### 情况 4：target run evidence 缺失
说明你没有真实 workload 反馈，只能算“本仓静态健康”，不能据此判断 Codex/Claude 的真实效果。

### 情况 5：target run evidence 存在但过期
`host-feedback-summary.py` 会优先选每个目标仓最新的 `daily*` / `onboard` 证据，并在同时间戳下优先使用 `daily`，因为 `daily` 才代表真实 workload 反馈。若最新证据超过 168 小时，报告会显示 `target_runs=attention` 与 `freshness_status=stale`。

此时不能回答“当前真实效果已经清楚”；只能回答“闭环入口可用，但真实 workload 证据需要刷新”。

## 最低验收
以下四项同时满足，才算“已经拿到可用于优化决策的反馈闭环”：
- `FeedbackReport` 可成功生成
- `RulesDryRun` 无未预期漂移
- `claude_workload.readiness.status` 不是 `blocked`
- `target_runs.freshness_status=fresh`，且 latest runs 来自最新 `daily` 实跑证据
- `verify-repo.ps1 -Check All` 通过

## 相关文件
- [Adapter Conformance Parity Matrix](./adapter-conformance-parity-matrix.md)
- [AI 编码使用指南](../quickstart/ai-coding-usage-guide.zh-CN.md)
- [Codex CLI/App 集成指南](./codex-cli-app-integration-guide.zh-CN.md)
