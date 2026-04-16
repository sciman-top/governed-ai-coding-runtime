# Governance Boundary Matrix

## Goal
- 明确 `governed-ai-coding-runtime` 中哪些能力应统一治理，哪些由目标仓继承，哪些允许 override，哪些不建议纳入平台。
- 防止平台把所有工程治理问题都吸进中枢。

## Classification Rules

### Unified governance
- 平台必须统一语义，否则跨仓任务无法稳定运行。

### Repository inheritance
- 平台定义 schema，目标仓提供默认值。

### Repository override
- 平台允许受限扩展或收紧，但不允许破坏平台核心保证。

### Not in platform
- 不进入 MVP 平台边界，避免范围膨胀。

## Matrix

| Capability | Default bucket | Why | Override rule |
|---|---|---|---|
| Task object model | Unified governance | 跨仓任务必须有统一状态和字段语义 | not overridable |
| Task lifecycle / state machine | Unified governance | completed / blocked / waiting_approval 语义不能漂移 | not overridable |
| Approval semantics | Unified governance | 风险中断与恢复必须全平台一致 | repos may strengthen triggers, not redefine states |
| Risk taxonomy | Unified governance | risk level 必须跨仓可比较 | repos may map more commands into higher tiers |
| Tool execution contract | Unified governance | tool requests must be validated consistently | repos cannot bypass contract |
| Evidence bundle schema | Unified governance | replay, audit, and review need one evidence language | repos may add extra evidence fields |
| Eval categories | Unified governance | final outcome / trajectory / safety should stay comparable | repos may add repo-specific evals |
| Replay / rollback model | Unified governance | failure recovery must be deterministic | repos may provide extra compensation hooks |
| Repository profile schema | Unified governance | profiles need one contract across repos | repos fill values only in allowed fields |
| Build command | Repository inheritance | command is repo-specific but contract is shared | override through repo profile |
| Test command | Repository inheritance | same as build | override through repo profile |
| Lint / typecheck command | Repository inheritance | same as build | override through repo profile |
| Contract / invariant gate | Repository inheritance | repo-specific checks belong to repo profile | repos may add more strict checks |
| Path scope defaults | Repository inheritance | repo structure differs by project | repos may narrow scope further |
| Allowed tool set | Repository inheritance | tool surface depends on repo needs | repos may remove tools or require more approvals |
| Additional risky command patterns | Repository override | repos know their own risky operations best | can only make policy stricter |
| Blocked paths | Repository override | some repos need stronger local protection | can only add blocked paths |
| Approval escalation thresholds | Repository override | some repos may require stronger review | can only escalate, not weaken platform minimums |
| Context shaping hints / repo map hints | Repository override | repo topology differs and may benefit from hints | allowed if bounded to profile schema |
| Handoff template hints | Repository override | different repos need different review summaries | allowed as additive metadata |
| Repository business logic | Not in platform | belongs to product code, not runtime governance | not applicable |
| Generic enterprise workflow automation | Not in platform | would blur product identity | defer beyond MVP |
| Memory-first personalization stack | Not in platform | weak ROI before evidence/replay/approval are solved | defer |
| Autonomous policy modification | Not in platform | violates governance guarantees | never in MVP |
| Default multi-agent orchestration | Not in platform | too much complexity before single-agent shell is proven | defer |
| Production deployment automation by default | Not in platform | too risky for first platform loop | defer or separate module |

## Practical Reading

### What the platform must own
- runtime truth model
- approvals
- policy enforcement
- tool safety semantics
- evidence language
- validation completion rules

### What repos should own
- their commands
- their path hints
- their stricter local constraints
- their additional repo-specific checks

### What repos must not own
- redefining task lifecycle semantics
- bypassing approvals
- weakening evidence requirements
- weakening core validation semantics

## Related Documents
- `docs/prd/governed-ai-coding-runtime-prd.md`
- `docs/architecture/governed-ai-coding-runtime-target-architecture.md`
- `docs/research/benchmark-and-borrowing-notes.md`


