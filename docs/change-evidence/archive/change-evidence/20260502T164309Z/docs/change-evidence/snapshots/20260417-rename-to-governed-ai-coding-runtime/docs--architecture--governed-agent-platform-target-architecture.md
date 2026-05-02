# Governed Agent Platform Target Architecture

## Document Map
- PRD:
  - `docs/prd/governed-agent-platform-ai-coding-prd.md`
- MVP loop:
  - `docs/architecture/minimum-viable-governance-loop.md`
- Boundary classification:
  - `docs/architecture/governance-boundary-matrix.md`
- Research:
  - `docs/research/benchmark-and-borrowing-notes.md`
  - `docs/research/repo-governance-hub-borrowing-review.md`
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

## Goal
- 为 `governed-agent-platform` 提供一份从零开始可落地的终态架构说明。
- 明确控制面、执行面、数据/知识面、观测/保证面的边界。
- 固定 `MCP`、`A2A`、状态机、事件总线、审批、审计之间的职责分工。

## Non-Goals
- 不把本文档写成产品需求文档。
- 不把“多 Agent”当作默认上线形态。
- 不把事件驱动或某个框架当成完整系统答案。

## Design Premises
- 场景：企业级知识与执行系统，允许长链、多阶段、跨工具任务。
- 风险：中高风险混合，真实写操作默认受限。
- 权限：默认最小权限，高风险写操作必须审批。
- 约束：成本预算、时延预算、上下文窗口、人工审批频率都有限。
- 目标：优先得到可治理、可验证、可审计、可回滚的系统，不追求无限自治。

## Core Position
默认首选：

`Hybrid architecture = control-plane-first + durable workflow orchestration + event-driven observability + governed agent execution`

一句话解释：
- `single-agent + tools` 作为 baseline 必须先存在，但不能承担最终治理职责。
- 真正的“终态最佳实践”不是让 Agent 更自由，而是让治理、审批、回滚、验证更确定。

## Architecture Overview

```text
                           +----------------------+
                           |   User / API / UI    |
                           | Web / Chat / Ticket  |
                           +----------+-----------+
                                      |
                                      v
                        +-------------+--------------+
                        |     API Gateway / BFF      |
                        | AuthN / Rate Limit / Audit |
                        +-------------+--------------+
                                      |
          +---------------------------+---------------------------+
          |                           |                           |
          v                           v                           v
+---------+---------+     +-----------+-----------+     +---------+---------+
|   Control Plane   |     |   Execution Plane     |     | Assurance Plane   |
| Goal / Scope      |---->| Durable Workflows     |---->| Trace / Metrics    |
| Policy / Risk     |     | Task State Machines   |     | Logs / Alerts      |
| Approval / AuthZ  |     | Agent Workers         |     | Eval / Red-team    |
| Registry / Change |     | Tool Runners          |     | Audit Analytics    |
+---------+---------+     | Sandbox Executors     |     +--------------------+
          |               | Rollback / Compensate |
          |               +-----------+-----------+
          |                           |
          v                           v
+---------+---------------------------------------------------------------+
|                        Data / Knowledge Plane                           |
| PostgreSQL | pgvector | Redis | Object Storage | Event Bus | Registries|
| Goals      | Memory   | Cache | Evidence       | NATS/JS   | Tools      |
| Plans      | KB       | Locks | Artifacts      |           | Policies   |
| Approvals  | Lessons  |       | Snapshots      |           | Agents     |
+-------------------------------------------------------------------------+
          |
          v
+-------------------------------------------------------------------------+
|                  Integration / Adapter Boundary                         |
| MCP Clients | A2A Gateway | SaaS Connectors | Browser | Shell | RPA     |
+-------------------------------------------------------------------------+
```

## Four Planes

### 1. Control Plane
职责：
- 目标建模与范围锁定
- 权限、策略、风险判定
- 审批与授权
- 变更治理、注册表、版本控制

必须 deterministic 的能力：
- 身份认证
- 权限校验
- 风险分级
- 审批状态合法性
- 状态迁移门禁

### 2. Execution Plane
职责：
- Durable workflow 编排
- 任务状态机
- Agent 受限执行
- 工具调用与补偿/回滚
- 沙箱执行与资源控制

允许 LLM 参与但不能放权的能力：
- 需求澄清
- 子计划草拟
- 工具选择建议
- 低风险重试建议
- 受限局部优化

### 3. Data / Knowledge Plane
职责：
- 任务、计划、审批、证据、审计等持久化
- 记忆与知识条目版本化
- 经验沉淀与回滚
- 对象存储与快照管理

约束：
- `memory` 不是事实源
- 业务状态、审计记录、证据对象才是系统事实源

### 4. Assurance Plane
职责：
- trace / metrics / logs
- outcome / trajectory / regression / safety eval
- 告警、回放、红队、混沌演练
- 运行态可视化与发布门禁

约束：
- 观测独立于执行链路，不允许执行链篡改审计结果

## Protocol Boundaries

### MCP
- 用途：Agent 到工具、资源、提示模板的接入层。
- 不负责：Agent 之间的协作协议。

### A2A
- 用途：跨 Agent / 跨系统协作、能力发现、任务生命周期桥接。
- 不负责：本地控制面裁决、审批、审计。

### Event Bus
- 用途：异步传播和解耦，适合通知、观测、非关键事件。
- 不负责：替代审批流、状态机、业务事实源。

### State Machine / Durable Workflow
- 用途：关键状态流转、暂停、恢复、超时、重试、补偿、人工接管。
- 必须 deterministic，不能交给 LLM 自由决定。

## Recommended Stack

### Backend
- `Python 3.12+`
- `FastAPI`
- `Pydantic v2`
- `PydanticAI` or equivalent typed agent runtime
- `Temporal`

### Data
- `PostgreSQL`
- `pgvector`
- `Redis`
- `S3-compatible object storage`

### Policy / Security
- `OPA/Rego`
- `Vault` or cloud-native `KMS/Secrets Manager`

### Messaging / Async
- `NATS JetStream`
- 若组织已有标准化消息平台，可替换为 `Kafka`

### Observability
- `OpenTelemetry`
- `Prometheus`
- `Grafana`
- `Loki`
- `Tempo` or `Jaeger`
- `Langfuse` or equivalent LLM trace/eval platform

### Frontend
- `Next.js`
- `TypeScript`
- `Tailwind CSS`

### Protocols
- External APIs: `REST + Webhook`
- Internal service-to-service: `gRPC`
- Tool / context integration: `MCP`
- Cross-agent collaboration: `A2A`

## Why This Stack
- `Python`：AI/runtime/tooling 生态成熟，跨平台友好。
- `Temporal`：把暂停、恢复、审批、补偿从应用代码中抽出。
- `PostgreSQL + pgvector`：在一致性、通用性、运维复杂度之间最平衡。
- `OPA`：让权限和风险判定脱离 prompt 与业务代码。
- `OpenTelemetry`：统一 trace、metrics、event 字段，降低观测漂移。
- `Next.js`：管理台、审批页、回放页和审计页的开发效率高。

## Minimum Viable Governance Loop

终态不能只给大图，必须先给最小闭环。对 `AI coding` MVP，最小闭环是：

1. Task intake
   - 用户创建一个针对具体仓库的编码任务。
   - 任务对象固定：`goal / scope / acceptance / repo / risk / budgets`
2. Repo profile resolution
   - 平台读取目标仓的 profile。
   - 注入 build/test/lint/typecheck/contract/invariant 等命令。
3. Governed session startup
   - 平台创建受控工作目录或 worktree。
   - 为 agent 注入工具权限、路径范围、预算和上下文。
4. Governed execution
   - agent 只通过 Tool Runner 请求能力。
   - Risk / Policy Engine 决定是允许、审批还是阻断。
5. Approval interruption
   - 高风险动作暂停 workflow。
   - 人类批准、拒绝、撤回或超时。
6. Verification
   - 必须经过 build/test/lint/typecheck 以及 repo-specific gates。
7. Evidence and handoff
   - 输出 evidence bundle、summary、risk note、rollback point、handoff package。

没有上述闭环，就不应扩展到 multi-agent、memory-first 或 federation。

Detailed loop spec:
- `docs/architecture/minimum-viable-governance-loop.md`
- `docs/specs/task-lifecycle-and-state-machine-spec.md`
- `docs/specs/evidence-bundle-spec.md`
- `docs/specs/verification-gates-spec.md`

## Deterministic vs LLM Boundary

| Capability | Recommended implementation | LLM decision allowed | Failure protection |
|---|---|---|---|
| Authentication | deterministic service | no | reject request |
| Authorization | deterministic policy engine | no | deny by default |
| Risk classification | deterministic policy engine | no | block and request approval |
| State transition validation | workflow/state machine | no | reject illegal transition |
| Tool schema validation | deterministic validator | no | fail closed |
| Timeout/retry/budget | workflow runtime + runner | no | stop execution |
| Approval requests | approval service | no | freeze task |
| Task clarification | agent worker | limited | handoff to user |
| Plan drafting | agent worker | limited | require validation |
| Tool suggestion | agent worker | limited | policy pre-check |
| Local optimization in sandbox | agent worker + sandbox | limited | rollback / discard |

## Governance Boundary Summary

平台不应把所有事情都统一进中枢，而应严格区分：

### Unified governance
- task schema and lifecycle
- approval semantics
- risk taxonomy
- tool execution contract
- evidence and audit schema
- replay / rollback semantics
- eval categories

### Repository inheritance
- repo build/test/lint/typecheck commands
- contract/invariant commands
- repo path scope
- default tool set by repo profile
- repo handoff hints

### Repository override
- additional risky command patterns
- stricter blocked paths
- stronger approval requirements
- repo-specific context shaping hints
- repo-specific extra gates

### Not in the hub
- repository business logic
- self-modifying policy logic
- memory-first personalization stack in MVP
- full deployment governance in MVP

Detailed matrix:
- `docs/architecture/governance-boundary-matrix.md`

## Borrowing Strategy

The architecture should borrow mechanisms, not copy product identity.

### Worth borrowing
- `LangGraph`: interrupts and resumable execution
- `OpenHands`: sandbox-centered runtime isolation
- `SWE-agent`: repository-grounded issue/task loop
- `Aider repo map`: compact repo context shaping
- `Cline`: fine-grained permissions and approval surfaces
- `OpenAI Cookbook` and official docs: structured outputs, evals, tool use, safety, state semantics

### Not worth copying directly
- graph-first mental model as the system identity
- IDE-centric UX as the product core
- memory-first architecture for MVP
- open-ended autonomous multi-agent orchestration
- benchmark-optimized but weakly governed execution loops

Detailed notes:
- `docs/research/benchmark-and-borrowing-notes.md`

## Repository Profile Placement

`Repo profile` is a first-class architecture concept.

It should define:
- repo metadata
- working directory / branch / workspace policy
- build/test/lint/typecheck commands
- contract/invariant commands
- tool allowlist / denylist
- risky path patterns
- approval escalation rules
- handoff / summary template hints

The profile belongs to the control plane, but its content is loaded into execution-time decisions.

Related specs:
- `docs/specs/repo-profile-spec.md`
- `docs/specs/tool-contract-spec.md`
- `docs/specs/risk-tier-and-approval-spec.md`

The platform owns:
- profile schema
- allowed override points
- validation rules

The repository owns:
- the actual repo-specific values within those allowed fields

## Repository Shape

```text
governed-agent-platform/
├── apps/
│   ├── api-gateway/
│   ├── console-web/
│   ├── control-plane/
│   ├── workflow-worker/
│   ├── agent-worker/
│   ├── tool-runner/
│   ├── sandbox-runner/
│   ├── eval-worker/
│   └── a2a-gateway/
├── packages/
│   ├── contracts/
│   ├── domain/
│   ├── policy/
│   ├── agent-runtime/
│   ├── tool-sdk/
│   ├── observability/
│   └── testkit/
├── infra/
├── schemas/
├── docs/
├── tests/
└── scripts/
```

建议：
- 用 `monorepo` 起步，先统一契约和工具链。
- 按逻辑模块切边界，按压力点再拆物理部署。

## Deployment Position
- 生产环境：`Linux + Docker + Kubernetes`
- 开发环境：兼容 `Windows / macOS / Linux`
- 桌面自动化、RPA、Shell、Browser 这类平台差异能力，应封装到独立 worker 中。

## Evolution Path

### Stage 1: Minimum governed baseline
- Control Plane v1
- Approval v1
- Durable workflow v1
- Single-agent baseline v1
- Tool runner v1

### Stage 2: Scalable execution
- Worker pools
- Event bus for non-critical async flows
- Console + eval + evidence
- Sandbox isolation

### Stage 3: Full target state
- A2A gateway
- Multi-tenant governance
- Policy rollout / canary
- Red-team / chaos drill automation

## Red Lines
1. `LLM` 不能直接决定权限、审批、状态合法性。
2. 事件总线不能替代状态机和审批流。
3. `memory` 不能作为系统事实源。
4. 任何高风险写操作必须有审批和 rollback point。
5. 策略/规则变更不能由执行链直接生效。

## References
- `docs/FinalStateBestPractices.md`
- `docs/architecture/governance-boundary-matrix.md`
- `docs/research/benchmark-and-borrowing-notes.md`
- `docs/research/repo-governance-hub-borrowing-review.md`
- `docs/architecture/minimum-viable-governance-loop.md`
- `docs/roadmap/governed-agent-platform-90-day-plan.md`
- `scripts/github/create-roadmap-issues.ps1`
