# 在现有仓库中使用

## 短答案
不能再通过本仓旧的一键 rollout 路径来做。

从 2026-07-06 起，本仓不再 attach 外部目标仓，不再向外部仓写治理基线，也不再暴露 attachment、session-bridge 或 apply-all 流程。

## 仍然保留的能力
- `~/.codex`、`~/.claude` 的全局规则同步
- 对采用 `AGENTS.md` 共同主体 + `CLAUDE.md` thin wrapper 的目标仓做项目规则协同审计
- 本仓自己的验证与 operator 工作流
- 通过 `scripts/run-governed-task.py` 生成 repo-local task/status/evidence
- host feedback、自演化、continuity、portable packaging

## 如果另一仓库也需要治理
直接在那一仓库内维护。

推荐做法：
1. 在目标仓根 `AGENTS.md` 记录 `**项目契约**: 2.0`、`**全局规则复核**: 9.56`、当前落点、目标归宿、仓库事实、真实门禁、证据和回滚。
2. 保持 `AGENTS.md` 宿主中立，不复制全局 R/E 或平台加载教程；固定门禁仍是 `build -> test -> contract/invariant -> hotspot`。
3. 目标仓 `CLAUDE.md` 第一物理行写裸文本 `@AGENTS.md`，无 BOM；没有真实仓库级差异时文件只保留这一行。
4. 在 `rules/target-project-rule-coordination.json` 显式登记目标，并填写 `github_repository` 与 `ci_workflow_path`；控制仓只审计，不保存或盲覆盖目标正文。
5. 将已审查的 `rules/templates/github/agent-rule-contract.yml` 字节复制到目标仓声明的 workflow 路径，并在 `AGENTS.md` 引用该路径；本地 workflow 只验证规则契约，绝不替代产品门禁。
6. rollout evidence 与验收证明留在目标仓；全局同步备份、聚合 CI 证据与加载探针证据留在控制仓。

当前 allowlist：`ai-content-delivery-studio`、`classroom-answer-toolkit`、`ClassroomToolkit`、`github-toolkit`、`k12-question-graph`、`local-ai-dev-orchestrator`、`qq-codex-bot`、`skills-manager`、`vps-ssh-launcher`。发布审计会将该清单与 `D:\CODE` 直接子 Git 根动态发现结果对账；发现本身不会自动纳管。其他相邻目录仍受用户级全局规则影响，但不接受本轮项目规则审计或写入。

## 在本仓仍应使用的命令
```powershell
python scripts/verify-agent-rule-family.py
python scripts/verify-target-project-rules.py --require-all
python scripts/export-target-rule-ci-matrix.py
python scripts/sync-agent-rules.py --scope All --fail-on-change
```

上述静态检查通过后，才执行 `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -Apply`；随后做零漂移复核和新的 Codex/Claude 加载探针。

回滚必须分层：全局副本使用同步备份加回退后的源版本；每个目标仓只回滚本仓 `AGENTS.md / CLAUDE.md / rollout evidence`；不得恢复无关脏工作树。

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action Readiness -OpenUi
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action FeedbackReport
```

```powershell
python scripts/run-governed-task.py status --json
```

## 已退役命令
以下名称已明确退役，现在都会 fail-closed 返回退休提示：
- `runtime-flow-preset`
- `runtime-flow`
- `attach-target-repo`
- `session-bridge`
- `verify-attachment`
- `govern-attachment-write`
- `decide-attachment-write`
- `execute-attachment-write`
- `ApplyAllFeatures`
- `DailyAll`
- `GovernanceBaselineAll`
- `CleanupTargets`
- `UninstallGovernance`

## 相关文档
- [单机 Runtime 快速开始](./single-machine-runtime-quickstart.zh-CN.md)
- [AI 编码使用指南](./ai-coding-usage-guide.zh-CN.md)
- [功能反馈闭环](../product/host-feedback-loop.zh-CN.md)
