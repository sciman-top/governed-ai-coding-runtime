# Benchmark and Borrowing Notes

## Goal
- 记录 `governed-agent-platform` 在 AI coding 场景下应借鉴哪些官方资料和社区项目。
- 明确“借什么、不借什么”，避免文档和架构被流行项目带偏。

## Borrowing Rules
- 优先借机制，不复制产品身份。
- 官方文档定义语义边界，社区项目提供实现启发。
- 任何借鉴都必须回到本项目目标：`governed AI coding runtime`
- 若某能力不能增强可治理、可验证、可审计、可回滚，就不优先进入 MVP。

## Official Sources

### OpenAI Cookbook and official platform docs
**Worth borrowing**
- structured outputs
- tool use patterns
- eval and grader mindset
- stateful execution and conversation-state ideas
- safety-first tool approval thinking

**Do not copy directly**
- notebook/tutorial structure as product architecture
- example-specific workflow assumptions

**Why**
- 官方资料更适合定义 runtime 语义和评测方法，不适合直接当成产品模块图。

## Community Projects

### LangGraph
**Worth borrowing**
- durable execution
- interrupt-based human review
- resumable state model

**Do not copy directly**
- graph-first identity for the whole product
- framework lock-in in the architecture narrative

**Why**
- 本项目需要 workflow durability 和 HITL，但不需要把“graph”作为系统中心概念。

### OpenHands
**Worth borrowing**
- sandbox-centered runtime isolation
- long-running coding task execution environment
- separation between agent reasoning and action execution

**Do not copy directly**
- IDE/runtime product shape
- broad agent shell assumptions that exceed MVP scope

**Why**
- 对本项目最有价值的是隔离执行环境，而不是整套产品 UX。

### SWE-agent
**Worth borrowing**
- issue/task-driven coding loop
- repository-grounded repair and validation thinking
- task-focused coding automation discipline

**Do not copy directly**
- benchmark-first prioritization
- open-ended autonomous search as default runtime posture

**Why**
- 本项目重视“任务闭环”，但不应让 benchmark 目标压过治理目标。

### Aider repo map
**Worth borrowing**
- compact repository map
- symbol-level or structure-level context shaping
- relevance-first codebase summary instead of full-repo stuffing

**Do not copy directly**
- chat-transcript-centric UX assumptions
- direct coupling to one coding interaction style

**Why**
- 本项目需要 repo-aware execution，但上下文塑形应作为 platform capability，而不是单一聊天模式的副产物。

### Cline
**Worth borrowing**
- fine-grained approval ergonomics
- explicit permission surfaces
- path/tool-aware approval model

**Do not copy directly**
- permissive auto-approve defaults
- IDE-centric interaction model as system architecture

**Why**
- Cline 对“权限不是一句 prompt，而是一套操作面”这一点很有启发。

### Letta
**Worth borrowing**
- stateful agent framing
- memory layering vocabulary
- distinction between in-context state and longer-lived state

**Do not copy directly**
- memory-first product architecture
- stateful memory as MVP center of gravity

**Why**
- 对本项目来说，memory 现在是辅助能力，不应先于 approval/evidence/verification。

### Mem0
**Worth borrowing**
- memory as a separable layer
- memory lifecycle thinking
- multi-level memory language

**Do not copy directly**
- universal memory layer positioning for MVP
- self-improving memory claims as early product priority

**Why**
- 本项目在 MVP 阶段更需要 evidence, replay, and repo profile than a rich memory platform.

## Net Recommendation

### Borrow aggressively
- durable execution
- human approval interrupts
- sandbox isolation
- repo-aware context shaping
- explicit tool permissions
- eval-driven iteration

### Borrow cautiously
- memory layering ideas
- stateful agent abstractions
- benchmark task loops

### Do not prioritize in MVP
- multi-agent default orchestration
- memory-first architecture
- federation-first architecture
- generalized enterprise automation breadth

## How This Affects The Docs
- PRD 应强调 `governed coding runtime`，不是“万能 agent 平台”。
- Architecture 文档应突出 `minimum viable governance loop`。
- Roadmap 应先强化 `approval / workflow / verification / evidence`。
- Boundary matrix 应明确 memory、multi-agent、federation 属于延后项或非 MVP。
