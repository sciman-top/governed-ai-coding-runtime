# Codex CLI/App 集成指南

## 目的
说明当前这个仓库怎样与 Codex CLI/App 配合使用，同时避免把现状说成“已经直接接管 Codex 编码执行”。

## 当前状态
- 本项目当前是 **Codex CLI/App compatible first**，但**还不是 direct Codex execution adapter**。
- 当前运行时已经能做：bootstrap 本地状态、加载 repo profile、管理任务、执行 governed verification gates、持久化 evidence/replay artifact、暴露 runtime status。
- 当前运行时**还不能**通过受管 adapter worker 直接调用 Codex 去完成真实编码工作。
- 当前已经有 Codex adapter contract 用来分类能力姿态，但它本身不等于 live native attach 或 managed Codex execution 已经可用。

## 工程态（2026-04-21）
- 过渡服务路径已落地：真实 FastAPI control-plane 入口 + 可选 Postgres metadata（`verification_runs`、`adapter_events`）。
- Codex adapter event 现可规范化并写入 durable sink，operator 读侧可查询。
- Codex 仍是 direct-adapter 产品化深度的第一优先。
- Claude Code 当前仍处于通用 adapter contract 兼容边界内，但本切片尚未把它做成 first-class direct adapter。

## 今天已经可用的方式

### 1. 作为 Codex 外围的治理层
可以把本仓库当成 Codex 编码会话外层的 governance sidecar：
- 用 repo profile 约束仓库预期
- 用 `bootstrap`、`doctor`、`verify-repo` 做本地 readiness 与 gate 检查
- 用 runtime status/operator UI 看本地治理状态
- 为 runtime-managed task 保留 evidence、verification、replay artifact

### 2. Codex-Compatible 只读 Trial
当前第一个与 Codex 有关的入口是保守模式：
- 只把 Codex 建模成 adapter declaration
- 保持上游 Codex 身份认证仍由用户自己持有
- 落在 manual handoff + read-only 模式

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

### 方案 A：Codex 正常工作，本仓库作为治理侧车
这是现在最推荐的方式，阻力最小。

1. 先执行：
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/bootstrap-runtime.ps1`
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
2. 按你原来的方式使用 Codex CLI/App 编码。
3. 把本仓库的文档、repo profile、gate 规则当成治理基线。
4. 完成后执行：
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
5. 如果你还想查看 runtime 侧状态和产物，再执行：
   - `python scripts/run-governed-task.py status --json`
   - `python scripts/serve-operator-ui.py`

### 方案 B：Codex 前后都经过 Manual Handoff
适合你想给一个边界明确的任务加治理外壳。

1. 先用只读 trial 验证 repo profile 和 adapter posture。
2. 真实编码部分仍然手动在 Codex CLI/App 中执行。
3. 用本仓库的 verification、evidence、operator surface 检查本地治理结果。

## 当前还没实现的部分
- `scripts/run-governed-task.py` 里还没有直接执行 `codex` 命令
- 还没有 managed adapter worker 去捕获 Codex prompt、edit、tool call、diff 等一等事件
- 还没有把长时间运行的 Codex 会话编排进本 runtime
- 不能把当前 smoke task 说成“Codex 已经在 runtime 内产生真实代码修改”
- 不能把 Codex adapter contract 说成“所有宿主环境都已经具备 native attach”

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
- 围绕 Codex 工作流的 governance sidecar
- 为未来 deeper Codex integration 预先定义好的 compatibility boundary

不应把它描述成“Codex 已经被这个 runtime 直接接管并执行真实编码”。
