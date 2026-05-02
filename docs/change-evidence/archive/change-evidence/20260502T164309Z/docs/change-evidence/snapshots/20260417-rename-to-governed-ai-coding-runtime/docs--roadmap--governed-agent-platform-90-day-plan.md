# Governed Agent Platform 90-Day Plan

## Execution Inputs

This plan assumes the following documents are the active design inputs:
- PRD:
  - `docs/prd/governed-agent-platform-ai-coding-prd.md`
- MVP loop:
  - `docs/architecture/minimum-viable-governance-loop.md`
- ADRs:
  - `docs/adrs/0001-control-plane-first.md`
  - `docs/adrs/0002-no-multi-repo-distribution-in-mvp.md`
  - `docs/adrs/0003-single-agent-baseline-first.md`
- Specs:
  - `docs/specs/control-registry-spec.md`
  - `docs/specs/repo-profile-spec.md`
  - `docs/specs/tool-contract-spec.md`
  - `docs/specs/risk-tier-and-approval-spec.md`
  - `docs/specs/task-lifecycle-and-state-machine-spec.md`
  - `docs/specs/evidence-bundle-spec.md`
  - `docs/specs/verification-gates-spec.md`
  - `docs/specs/eval-and-trace-grading-spec.md`
- Backlog seeds:
  - `docs/backlog/mvp-backlog-seeds.md`

## Current Baseline
- `docs/`, `schemas/`, and `scripts/github/create-roadmap-issues.ps1` already exist.
- Root `README.md` and project `AGENTS.md` now exist as repo entry contracts.
- The repository is still `docs-first / contracts-first`; `apps/`, `packages/`, `infra/`, and `tests/` have not been bootstrapped yet.
- Phase 1 should therefore start from implementation skeleton and verification entrypoints, not from re-authoring strategy documents.

## Goal
- 在 90 天内交付 `governed-agent-platform` 的 MVP。
- 范围聚焦：`single-agent baseline + deterministic guardrails + durable workflow + approval + audit + eval + console`
- 不追求 90 天内完成 fully distributed multi-agent。

## Scope

### In Scope
- Control Plane v1
- Policy / Risk / Approval v1
- Durable Workflow Runtime v1
- Single-Agent Baseline v1
- Tool Runner / Sandbox v1
- Validation / Evidence / Console v1
- Production Hardening v1

### Out of Scope
- 多 Agent 自治协商
- 全量 A2A 生产化
- 自动策略晋升
- 自动规则修改
- 多区域多活
- 独立 memory 微服务

## Roadmap Principles

- 先建立最小可行治理闭环，再扩平台宽度。
- 优先强化 `task / approval / policy / verification / evidence`，而不是先扩 memory 或 multi-agent。
- 统一治理只覆盖必须统一的 runtime 语义；repo-specific 内容通过 profile 继承或 override。
- 借鉴社区项目时优先拿“机制”，不照搬产品形态。

## What To Add / What To Weaken / What To Defer

### Add now
- repository profile
- tool governance contract
- approval-first risky action handling
- evidence bundle model
- replay / rollback model
- benchmark-informed repo context shaping

### Weaken intentionally
- broad automation claims
- memory-first positioning
- multi-agent positioning
- deployment automation as default path

### Defer explicitly
- A2A federation
- long-term adaptive memory platform
- autonomous policy promotion
- generalized enterprise workflow automation
- organization-scale tenancy and RBAC complexity

## Phases

### Phase 1: Foundation (Week 1-4)
- 建立 monorepo、契约、基础设施、控制面骨架

**Expected benefit**
- 固定任务模型、repo profile、基础设施和控制面边界，避免后续返工。

**Primary risk**
- 过早铺太多基础设施，但没有尽快打通完整治理闭环。

### Phase 2: Execution (Week 5-8)
- 建立 deterministic guardrails、审批闭环、durable workflow、single-agent baseline

**Expected benefit**
- 尽快证明“AI coding in governed shell”可用，而不是停留在设计图。

**Primary risk**
- 在 agent 与 tool 层投入太快，导致审批和 evidence 质量不足。

### Phase 3: Hardening (Week 9-13)
- 打通工具与沙箱、补齐 eval、管理台、异步化和上线硬化

**Expected benefit**
- 把 MVP 从“能跑”升级成“可运营、可回放、可灰度”。

**Primary risk**
- 提前引入过多异步化和分布式复杂度，稀释 MVP 重点。

## Weekly Plan

### Week 1
**Goal**
- 初始化实现骨架和仓库入口契约

**Tasks**
- 创建 `apps/`、`packages/`、`infra/`、`tests/`
- 在实现骨架落地时保持根 `README.md` 和项目级 `AGENTS.md` 同步
- 初始化 Python workspace、前端 workspace、统一 lint/test/schema 命令
- 建立基础 CI：lint、unit test、schema check
- 建立 ADR 模板和开发脚本

**Acceptance**
- 新成员能通过根 `README.md` 和 `docs/README.md` 快速理解仓库
- 本地 bootstrap/verification 入口已定义
- CI 能跑通基础检查
- 实现骨架结构固定

### Week 2
**Goal**
- 固定核心对象模型和契约

**Tasks**
- 定义 `Goal`、`Task`、`Plan`、`ApprovalRequest`、`RiskEvent`
- 定义 `ToolCall`、`Evidence`、`ValidationResult`、`RollbackPoint`
- 建立 `jsonschema / OpenAPI / protobuf` 第一版
- 定义状态枚举、不可变字段、审计字段

**Acceptance**
- 核心对象模型完成 v1
- schema 校验可自动执行
- 关键对象状态和版本字段固定

### Week 3
**Goal**
- 打通开发基础设施

**Tasks**
- 部署本地 `PostgreSQL`、`Redis`、`Temporal`
- 接入 `OpenTelemetry`、`Prometheus`、`Grafana`
- 建立对象存储开发环境
- 固定 config / secret 加载和 migration 流程

**Acceptance**
- 本地一键启动核心基础设施
- 服务可写 trace / logs
- migration 可执行可回滚

### Week 4
**Goal**
- 建立控制面骨架

**Tasks**
- 创建 `api-gateway`
- 创建 `control-plane`
- 实现基础 auth 和 tenant context
- 搭建 `Registry` 初版
- 搭建 `Audit / Evidence` 初版

**Acceptance**
- 可创建/查询 Goal / Task 基础对象
- 所有 API 调用写入审计日志
- Gateway 和 Control Plane 职责分离

### Week 5
**Goal**
- 固定权限和风险模型

**Tasks**
- 接入 `OPA`
- 定义权限等级：`read / suggest / simulate / execute / policy-change / rollback`
- 定义风险等级：`low / medium / high / critical`
- 建立 tool side-effect catalog
- 建立高风险默认阻断规则

**Acceptance**
- 工具调用前可完成权限和风险判定
- 高风险默认阻断
- 策略具备版本化能力

### Week 6
**Goal**
- 建立审批闭环

**Tasks**
- 实现审批请求对象和状态机
- 实现批准、拒绝、撤回、超时
- 接入通知链路
- 审批结果回写任务状态

**Acceptance**
- 高风险任务可发起审批并等待
- 审批结果可驱动后续状态变化
- 审批全链路可审计

### Week 7
**Goal**
- 跑通 durable workflow 主链路

**Tasks**
- 创建 `workflow-worker`
- 定义主任务状态机
- 实现 `pause / resume / timeout / retry`
- 接入审批插点
- 定义补偿接口

**Acceptance**
- 主 workflow 可完整跑通
- 审批能暂停并恢复 workflow
- 失败能进入补偿或人工接管

### Week 8
**Goal**
- 跑通受控 single-agent baseline

**Tasks**
- 创建 `agent-worker`
- 集成模型调用和上下文装配
- 定义 Agent 输入输出 schema
- 实现受限推理能力
- 建立 token / cost / wall-clock budget

**Acceptance**
- Agent 可在 workflow 中执行
- Agent 无法绕过策略直接调用高风险工具
- budget 超限会停止并落证据

### Week 9
**Goal**
- 打通首批工具

**Tasks**
- 建立 Tool SDK
- 接入首批 3-5 个工具
- 实现 schema 校验、timeout、retry budget、idempotency key
- 建立 tool call 审计记录

**Recommended first tools**
- GitHub
- HTTP fetch
- PostgreSQL read
- file read/write
- notifications

**Acceptance**
- 至少 3 个工具可在主任务链中使用
- 所有工具调用都经 Tool Runner
- 工具失败可归因、可阻断、可重试

### Week 10
**Goal**
- 建立写能力和沙箱隔离

**Tasks**
- 创建 `sandbox-runner`
- 建立写审批 gate
- 实现 rollback point 登记
- 建立补偿动作骨架
- 建立资源限制和清理机制

**Acceptance**
- 至少 2 类写操作支持审批后执行
- 每次高风险写操作有 rollback point
- 沙箱失败不污染控制面

### Week 11
**Goal**
- 把“能跑”升级成“能验证”

**Tasks**
- 创建 `eval-worker`
- 建立 outcome / trajectory / regression / safety eval
- 准备最小 regression dataset
- 将 eval 接入 CI

**Acceptance**
- 关键变更可跑最小评测集
- 结果和轨迹都可评分
- 具备最小安全回归能力

### Week 12
**Goal**
- 建立运营与排障入口

**Tasks**
- 创建 Console 审批页
- 创建任务详情页和证据页
- 创建审计回放页
- 展示 prompt / policy / tool 版本
- 暴露人工接管入口

**Acceptance**
- 管理员可通过 Web 界面完成审批
- 可查看任务轨迹、证据、审计
- 可定位失败任务并决定接管

### Week 13
**Goal**
- 上线前硬化

**Tasks**
- 引入 `NATS JetStream` 处理非关键异步事件
- worker 分池和限流
- canary rollout
- chaos drill
- backup / restore drill
- red-team 最小场景
- 上线和回滚 runbook

**Acceptance**
- 完成至少 1 次恢复演练
- 完成至少 1 次灰度演练
- 关键失败模式有 runbook
- 满足灰度上线门槛

## Suggested Initial Backlog

### First 8 tasks
1. Initialize implementation skeleton and keep repo entry docs aligned
2. Add CI for lint, unit test, and schema validation
3. Define Goal, Task, Plan, ApprovalRequest schemas
4. Provision local PostgreSQL, Redis, Temporal, and OTel stack
5. Create api-gateway skeleton with auth and tenant context
6. Integrate OPA for permission and risk checks
7. Implement approval state machine and notification flow
8. Implement Temporal workflow for task lifecycle

Seed backlog document:
- `docs/backlog/mvp-backlog-seeds.md`

## Phase Decision Matrix

| Phase | Strengthen | Keep minimal | Defer | Exit check |
|---|---|---|---|---|
| Phase 1 | task model, repo profile, control plane, contracts | UI polish | multi-agent, memory, federation | repo-aware task object + local infra + control plane skeleton |
| Phase 2 | approval, workflow, single-agent shell, tool governance | advanced console | adaptive optimization | governed coding task can run end-to-end |
| Phase 3 | eval, evidence, replay, hardening, canary | broad tool catalog | org-scale tenancy | evidence-complete validated task can be replayed and reviewed |

## Release Criteria
- Single-agent baseline 跑通
- 高风险写操作必须审批
- 主 workflow 支持暂停、恢复、超时、重试、补偿/人工接管
- 关键链路具备 trace、审计、证据
- 最小 eval / regression / safety 基线可运行
- 至少完成一次 canary 和一次恢复演练

## Supporting Documents
- `docs/prd/governed-agent-platform-ai-coding-prd.md`
- `docs/architecture/governed-agent-platform-target-architecture.md`
- `docs/architecture/governance-boundary-matrix.md`
- `docs/architecture/minimum-viable-governance-loop.md`
- `docs/research/benchmark-and-borrowing-notes.md`
- `docs/research/repo-governance-hub-borrowing-review.md`
- `docs/adrs/0001-control-plane-first.md`
- `docs/adrs/0002-no-multi-repo-distribution-in-mvp.md`
- `docs/adrs/0003-single-agent-baseline-first.md`
- `docs/specs/control-registry-spec.md`
- `docs/specs/repo-profile-spec.md`
- `docs/specs/tool-contract-spec.md`
- `docs/specs/risk-tier-and-approval-spec.md`
- `docs/specs/task-lifecycle-and-state-machine-spec.md`
- `docs/specs/evidence-bundle-spec.md`
- `docs/specs/verification-gates-spec.md`
- `docs/specs/eval-and-trace-grading-spec.md`
- `docs/backlog/mvp-backlog-seeds.md`

## References
- `docs/architecture/governed-agent-platform-target-architecture.md`
- `scripts/github/create-roadmap-issues.ps1`
- `docs/FinalStateBestPractices.md`
