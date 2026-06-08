# Codex CLI/App 集成指南

## 目的
说明当前仓库如何与 Codex CLI/App 协同，并以“当前可执行能力边界”为准，不夸大、不降级。

## 当前状态
- 本项目仍是 **Codex-compatible first**，并保持上游 Codex 认证由用户持有（`user_owned_upstream_auth`）。
- 运行时已提供 direct Codex adapter 的能力探测与会话身份握手面（capability probe + session identity handshake）。
- session bridge 已可在 Codex 身份下执行受治理命令面：`run_quick_gate`、`run_full_gate`、`write_request`、`write_approve`、`write_execute`、`write_status`。
- 能力姿态是环境相关的，并按规则显式降级：`native_attach -> process_bridge -> manual_handoff`。

## 今天已经可用的方式

### 1. 能力就绪与降级可见性
现在可以通过 runtime status/doctor 直接看到 Codex 能力就绪状态：
- adapter tier（`native_attach` / `process_bridge` / `manual_handoff`）
- flow kind（`live_attach` / `process_bridge` / `manual_handoff`）
- unsupported capabilities 与降级原因
- remediation 提示与 probe 稳定性信息

对 Codex 而言，当前被承认的强 attached-session boundary 已经分成两条：
- `codex status` 成功时，仍然是强 live handshake。
- 如果 `status` 不可用，但 `codex app-server` 的协议 schema 同时暴露 `thread.sessionId`、`thread/resume`，以及 running-thread rejoin 或 session tree 语义，它也可以构成强 thread boundary。
- `remote-control` 和 `doctor` 仍然只是健康或 daemon supporting surfaces；它们单独不会把 Codex 升格为 `native_attach`。

### 2. Runtime 托管的 Session Bridge 命令面
本地 session bridge 已可执行受治理 gate/write 闭环，并附带 Codex 身份元数据：
- `run_quick_gate` / `run_full_gate` 默认执行验证（仍支持 `plan_only`）
- `write_request` / `write_approve` / `write_execute` / `write_status` 执行策略与审批约束
- 输出 `continuation_id`、evidence/handoff/replay refs
- 写流与 gate 流都会产出 adapter evidence 映射

### 3. Codex Adapter Smoke Trial
`scripts/run-codex-adapter-trial.py` 仍保留为确定性探针入口：
- 默认 safe-mode
- `--probe-live` 可从实时能力面推导姿态

对应文档：
- [First Read-Only Trial](./first-readonly-trial.md)
- [Adapter Degrade Policy](./adapter-degrade-policy.md)
- [Codex Direct Adapter](./codex-direct-adapter.md)

### 3. Runtime Smoke Task
`python scripts/run-governed-task.py run --json` 证明的是本地 governed runtime 路径已经闭环：
- task persistence
- workspace allocation
- gate execution
- evidence 与 handoff 生成
- runtime status 投影

它应当被理解为 **runtime smoke task**，不是 direct Codex coding integration。

## 当前推荐工作流

### 方案 A：Attach-First 受治理执行流（推荐）
适合希望由 runtime 管理 attachment posture、gate 执行与写入治理的场景。

1. 先执行：
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/bootstrap-runtime.ps1`
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
2. 对目标仓执行 attach 或校验 light-pack。
3. 用一键 daily flow 运行治理链：
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow.ps1 -FlowMode "daily" ...`
4. 需要全量门禁时执行：
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
5. 需要查看治理证据与状态时执行：
   - `python scripts/run-governed-task.py status --json`
   - `python scripts/serve-operator-ui.py`

### 方案 B：Codex 原生会话 + Governance Sidecar
适合希望保持原有 Codex 习惯，按需插入治理动作的场景。

1. 仍以 Codex CLI/App 为主会话入口。
2. 用本仓库做 readiness、verification、evidence/handoff/replay 侧的治理留痕。
3. 需要边界化治理时，再用 session-bridge 命令面执行。

## 本机 Cockpit API 互操作边界
Cockpit Tools 拥有 Codex 登录、provider 切换和 launch-on-switch 行为。本仓不得安装后台 guard、SQLite trigger、no-op launcher、restart wrapper、no-restart shim 或 CLI preflight wrapper 去拦截这些行为。

唯一写入例外是显式 current-account API projection：

Codex/Cockpit Direct OAuth、Direct API 和 Cockpit API service 往返切换已回到 Cockpit Tools 原生实现。本仓不再提供 interop checker、projection smoke、repair action、LiteLLM gateway 管理、history bucket 修复或 launcher 包装；只保留旧 shim 清理与缺席验证，避免历史 guard/wrapper 回归。

## 当前还没实现的部分
- 还没有“替代上游 Codex 宿主 UI”的 runtime-owned 全接管形态
- 仍不拥有上游 Codex 认证（设计上保持 user-owned）
- 还没有把上游 Codex 全量 prompt/edit/tool-call 流作为一等 runtime 事件长期编排
- 不能保证所有宿主环境/所有 Codex 构建都具备 `native_attach`
- 不能把当前状态表述为“外部仓一切高风险流程已在所有环境被 runtime 全面接管”

## 未来 Direct Codex Adapter 的边界
如果以后要补 direct Codex adapter，至少应满足这些约束：
- 必须保持为 adapter-owned，不能把 Codex 私有语义泄漏进 kernel
- 除非单独接受新集成决策，否则仍保持用户自持的上游认证
- 必须输出足够的 run-level evidence，让 approval、artifact、verification、rollback 都可追溯
- 当 Codex 的能力面弱于 full governed enforcement 时，必须显式 degrade
- 必须保留规范 gate 顺序：`build -> test -> contract/invariant -> hotspot`

这部分只是未来边界说明，不代表已经承诺实现时间。

## 结论
今天最适合把这个仓库理解为：
- 单机本地 governed runtime substrate
- 在 Codex 工作流上可执行的受治理运行时层（带 adapter tier 与 degrade 规则）
- 在不替换上游宿主前提下的 governance sidecar

不应把它描述成“runtime 已在所有环境下完全替代 Codex 宿主执行”。
