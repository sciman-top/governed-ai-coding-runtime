# 2026-04-17 FinalStateBestPractices Original Mapping Review

## Goal
Deep-review `FinalStateBestPractices（原稿）.md` against the active `governed-ai-coding-runtime` project baseline, then map each original section to:
- current source-of-truth documents
- current coverage status
- remaining gaps
- whether the section should be adopted, adapted, deferred, or rejected for this repository

## Overall Judgment
`FinalStateBestPractices（原稿）.md` is useful as a strong end-state architecture prompt and review checklist, but it is not a safe drop-in source-of-truth for this repository.

Why:
- it is written as a multi-agent system design brief, while this project explicitly starts from a governed single-agent baseline
- it assumes a broader enterprise knowledge-and-execution platform, while this repository is intentionally scoped to governed AI coding
- it is strong on governance mechanics, deterministic boundaries, state machines, risk, and failure modes, which fit this repository well
- it is weak on the repository's current differentiator: agent-product compatibility through capability adapters, especially Codex CLI/App first and future unknown product shapes

Net conclusion:
- treat the original as a `north-star review checklist`
- do not treat it as the active project spec
- selectively absorb the governance structure where it strengthens the current AI-coding-focused kernel

## Mapping Table

| 原稿章节 | 当前覆盖状态 | 当前落点 | 尚缺项 | 建议 |
|---|---|---|---|---|
| 一、任务目标 | `partial` | [PRD](../prd/governed-ai-coding-runtime-prd.md), [Interaction Model](../product/interaction-model.md) | 当前项目没有完整的“为什么不是普通 workflow / RAG / 单 Agent 就够”的成文对照节 | `adapt`。保留“先给 single-agent baseline，再证明是否升级”的结构，但把场景收敛到 AI coding |
| 二、默认前提、设计假设与非目标 | `partial` | [PRD](../prd/governed-ai-coding-runtime-prd.md), [Target Architecture](../architecture/governed-ai-coding-runtime-target-architecture.md) | 当前缺少一页集中化的 assumptions 文档 | `adapt`。保留假设清单写法，但把“企业级知识与执行系统”改成“AI coding runtime” |
| 三、设计总原则 | `partial` | [PRD](../prd/governed-ai-coding-runtime-prd.md), [ADR-0001](../adrs/0001-control-plane-first.md), [ADR-0005](../adrs/0005-governance-kernel-and-control-packs-before-platform-breadth.md), [ADR-0006](../adrs/0006-final-state-best-practice-agent-compatibility.md) | 当前原则散落在多文档，未集中成单页“governance principles” | `adopt`。原则与项目高度吻合，值得在后续汇总成显式原则文档 |
| 四、先做架构选型，再展开细节 | `partial` | [Target Architecture](../architecture/governed-ai-coding-runtime-target-architecture.md), [MVP Stack Vs Target Stack](../architecture/mvp-stack-vs-target-stack.md) | 当前没有“候选架构评分矩阵”文档 | `adapt`。保留选型先于细节的纪律，但不必完整照抄提示词结构 |
| 五、系统总分层（四大平面） | `covered` | [Target Architecture](../architecture/governed-ai-coding-runtime-target-architecture.md) | 当前尚未把每个平面的审批/签名/双重确认写到表格级别 | `adopt`。这是原稿最值得借鉴的部分之一 |
| 六、控制面设计 | `partial` | [Target Architecture](../architecture/governed-ai-coding-runtime-target-architecture.md), [Governance Boundary Matrix](../architecture/governance-boundary-matrix.md), [Verification Gates Spec](../specs/verification-gates-spec.md), [Risk Tier And Approval Spec](../specs/risk-tier-and-approval-spec.md) | 还没有“全方面控制面”统一模板文档 | `adapt`。适合成为后续高级设计文档，而不是当前 MVP 阻塞项 |
| 七、模块 / Agent 体系与权责制衡 | `partial` | [Target Architecture](../architecture/governed-ai-coding-runtime-target-architecture.md), [Compatibility Matrix](../architecture/compatibility-matrix.md), [Agent Adapter Contract Spec](../specs/agent-adapter-contract-spec.md) | 当前缺少完整的“权责—权限—制衡矩阵” | `adapt`。应转写为“模块/服务 + adapter + deterministic boundary”，不要直接写成多 agent 编制表 |
| 八、核心对象模型、生命周期与注册表 | `partial` | [Task Lifecycle And State Machine Spec](../specs/task-lifecycle-and-state-machine-spec.md), [Evidence Bundle Spec](../specs/evidence-bundle-spec.md), [Control Registry Spec](../specs/control-registry-spec.md), [Repo Profile Spec](../specs/repo-profile-spec.md), [Control Pack Spec](../specs/control-pack-spec.md) | 缺少统一对象模型总览，很多对象仍分散在 specs 中 | `adopt`。非常适合后续补一份 canonical domain model |
| 九、系统级状态机与闭环 | `partial` | [Minimum Viable Governance Loop](../architecture/minimum-viable-governance-loop.md), [Task Lifecycle And State Machine Spec](../specs/task-lifecycle-and-state-machine-spec.md) | 还没有覆盖“复盘 / 策略优化 / 知识更新 / 演进回滚”的系统级闭环总图 | `adopt`。但应先围绕 AI coding 最小闭环，而不是一次扩成通用自治闭环 |
| 十、规则分层、优化边界与晋升链 | `partial` | [ADR-0006](../adrs/0006-final-state-best-practice-agent-compatibility.md), [Governance Boundary Matrix](../architecture/governance-boundary-matrix.md), [Waiver And Exception Spec](../specs/waiver-and-exception-spec.md) | 当前没有一页显式的 immutable / configurable / experimental 分层文档 | `adopt`。这是后续治理成熟化的重要输入 |
| 十一、风险、权限、审批与高风险阻断 | `partial` | [Risk Tier And Approval Spec](../specs/risk-tier-and-approval-spec.md), [PRD](../prd/governed-ai-coding-runtime-prd.md), [Target Architecture](../architecture/governed-ai-coding-runtime-target-architecture.md) | 当前风险/权限模型仍偏高层，尚未形成完整操作矩阵 | `adopt`。与项目高度一致，应持续细化 |
| 十二、工程约束、预算与终止条件 | `partial` | [PRD](../prd/governed-ai-coding-runtime-prd.md), [Minimum Viable Governance Loop](../architecture/minimum-viable-governance-loop.md) | 还没有一页“budgets / stop conditions / circuit breakers”统一文档 | `adapt`。值得吸收，但需要改写为 AI coding runtime 的预算模型 |
| 十三、接口、协议、同步异步边界、观测与评估 | `partial` | [Target Architecture](../architecture/governed-ai-coding-runtime-target-architecture.md), [Compatibility Matrix](../architecture/compatibility-matrix.md), [Eval And Trace Grading Spec](../specs/eval-and-trace-grading-spec.md), [Tool Contract Spec](../specs/tool-contract-spec.md), [Agent Adapter Contract Spec](../specs/agent-adapter-contract-spec.md) | 缺少更细的 protocol 文档和指标字典 | `adopt`。尤其是 MCP/A2A/adapter/event bus 分层思路，与当前架构吻合 |
| 十四、分阶段演进路线图 | `covered` | [90-Day Plan](../roadmap/governed-ai-coding-runtime-90-day-plan.md), [MVP Stack Vs Target Stack](../architecture/mvp-stack-vs-target-stack.md) | 当前已覆盖阶段路线，但还没有“ideal end-state checklist”版收束 | `adopt`。项目已经在做，只需持续保持 north-star 和 tracer-bullet 区分 |
| 十五、失控点与失败模式 | `partial` | [PRD](../prd/governed-ai-coding-runtime-prd.md), [ADR-0001](../adrs/0001-control-plane-first.md), [ADR-0005](../adrs/0005-governance-kernel-and-control-packs-before-platform-breadth.md), [ADR-0006](../adrs/0006-final-state-best-practice-agent-compatibility.md) | 还没有专门的 failure-mode / chaos / rollback drill 文档 | `adopt`。这是值得后补的高价值文档 |
| 十六、输出格式（严格执行） | `not_applicable` | 原稿是面向模型的输出约束，不是仓库事实 | 不适合作为项目文档结构强制落地 | `reject_as_spec`。可以当内部分析模板，不应写进项目事实源 |
| 十七、强制输出要求 | `not_applicable` | 同上 | 同上 | `reject_as_spec`。保留为提示词工程资产，而不是产品架构资产 |

## What Fits Especially Well
The original is especially aligned with this repository on these points:

1. governance must be mechanism-backed, not prompt-backed
2. deterministic boundaries must be explicit
3. state machines matter more than chat transcripts
4. approvals, audit, rollback, recovery, and verification are first-class runtime concerns
5. a single-agent baseline should be proven before upgrading to richer coordination models

Current project documents already reflect these themes:
- [Target Architecture](../architecture/governed-ai-coding-runtime-target-architecture.md)
- [PRD](../prd/governed-ai-coding-runtime-prd.md)
- [ADR-0001](../adrs/0001-control-plane-first.md)
- [ADR-0003](../adrs/0003-single-agent-baseline-first.md)
- [ADR-0005](../adrs/0005-governance-kernel-and-control-packs-before-platform-breadth.md)

## What Does Not Fit Directly
The original does not fit directly in these areas:

1. It is multi-agent-first in framing, while the repository is intentionally single-agent-first in execution proof.
2. It frames the problem as a general enterprise knowledge-and-execution system, while this repository is scoped to governed AI coding.
3. It does not cover the repository's current differentiator: agent-product compatibility through capability adapters, especially Codex CLI/App first and future unknown agent shapes.
4. It is written as a very strong output-spec prompt for an LLM, not as a maintainable repository fact source.

## Recommended Borrowing Strategy

### Adopt now
- four-plane decomposition
- deterministic vs LLM boundary matrix thinking
- system-level state-machine discipline
- rules layering and promotion-chain thinking
- failure-mode and rollback-oriented review style

### Adapt before use
- module / agent responsibility matrix
- object model and registry model
- protocol and interface boundary model
- engineering budgets and stop-condition model

### Defer
- full multi-agent collaboration design
- graph-style orchestration as an active implementation obligation
- broad enterprise knowledge-system assumptions

### Reject as active project spec
- strict prompt-output sections
- prompt-only “must answer in this order” constraints
- any wording that recasts the repository as a generic multi-agent enterprise platform

## Suggested Next Docs To Add
If the repository wants to absorb the best parts of the original without losing scope discipline, the highest-value missing documents are:

1. `docs/architecture/governance-principles-and-boundaries.md`
2. `docs/specs/core-object-model-and-registries.md`
3. `docs/architecture/failure-modes-and-recovery.md`
4. `docs/architecture/rule-layering-and-controlled-optimization.md`

These would capture the original's strongest governance structure without changing the product identity.

## Final Recommendation
Keep `FinalStateBestPractices（原稿）.md` as a source artifact and review checklist.

Do not promote it to source-of-truth.

Use it to pressure-test whether the repository is missing:
- deterministic boundaries
- state machines
- risk and approval semantics
- rollback and recovery discipline
- failure-mode analysis

But continue to let the repository's active source-of-truth remain:
- [PRD](../prd/governed-ai-coding-runtime-prd.md)
- [Target Architecture](../architecture/governed-ai-coding-runtime-target-architecture.md)
- [MVP Stack Vs Target Stack](../architecture/mvp-stack-vs-target-stack.md)
- [Compatibility Matrix](../architecture/compatibility-matrix.md)
- [90-Day Plan](../roadmap/governed-ai-coding-runtime-90-day-plan.md)
