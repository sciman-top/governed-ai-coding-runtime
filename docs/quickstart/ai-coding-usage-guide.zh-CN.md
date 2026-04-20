# AI 编码使用指南

## 目的
说明如何把本运行时与 Codex/Claude Code 等 AI 编码宿主配合使用，并明确它在真实编码流程中的具体辅助作用。

## 推荐使用模式

### 模式 A：治理侧车（阻力最低）
继续按原方式使用宿主工具，把本运行时用于 readiness、verification 和证据留痕。

1. 初始化与健康检查：
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/bootstrap-runtime.ps1
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
