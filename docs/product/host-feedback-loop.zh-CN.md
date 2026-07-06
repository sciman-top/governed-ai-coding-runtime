# 功能反馈闭环

## 目的
为本仓提供一条固定的、repo-local 的反馈闭环，用来判断宿主健康、规则漂移、门禁状态以及下一步 bounded maintenance 动作。

## 当前边界
- 反馈汇总现在是 host-only、repo-local
- 不再依赖 target-repo daily runs
- 不再依赖 attachment posture 或 session-bridge 证据
- 仍然坚持 evidence-first 和 fail-closed

## 推荐闭环
1. 跑 readiness：
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action Readiness -OpenUi`
2. 检查全局规则漂移：
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action RulesDryRun`
3. 生成统一反馈报告：
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action FeedbackReport`
4. 用 full repo gate 收口：
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`

## 报告应回答的问题
- 当前 Codex / Claude 的本机状态是否足以支撑当前工作负载？
- `rules/manifest.json` 与用户目录全局副本是否同步？
- 本仓硬门禁链是否通过？
- 自演化当前是 blocked、review_required，还是可以做 bounded materialization？
- `select-next-work` 给出的下一步安全动作是什么？

## 主要证据
- `.runtime/artifacts/host-feedback-summary/latest.md`
- 最新 self-evolution recommendation artifact
- 最新 self-evolution promotion artifact
- `scripts/verify-repo.ps1 -Check All`

## 最低验收
- `FeedbackReport` 成功
- `RulesDryRun` 没有未预期漂移
- `verify-repo.ps1 -Check All` 通过
- 报告能给出明确的 next action，而不是只能靠人工猜测

## 相关文档
- [AI 编码使用指南](../quickstart/ai-coding-usage-guide.zh-CN.md)
- [共享上下文连续性指南](./agent-continuity.zh-CN.md)
