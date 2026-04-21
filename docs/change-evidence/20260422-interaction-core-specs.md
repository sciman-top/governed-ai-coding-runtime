# 20260422 Interaction Core Specs

## Goal
执行《Teaching Collaboration And Low-Token Governance Implementation Plan》的 Task 1，先把 interaction governance 的核心 contract 家族正式落为 reviewable specs，再进入 schema、example 和 runtime wiring。

## Scope
- `docs/specs/interaction-signal-spec.md`
- `docs/specs/response-policy-spec.md`
- `docs/specs/teaching-budget-spec.md`
- `docs/specs/interaction-evidence-spec.md`
- `docs/specs/learning-efficiency-metrics-spec.md`
- `docs/specs/README.md`
- `docs/plans/teaching-collaboration-and-low-token-governance-implementation-plan.md`
- `docs/change-evidence/20260422-interaction-core-specs.md`
- `docs/change-evidence/README.md`

## Changes
1. 新增 5 份 interaction core specs
- `Interaction Signal Spec`
- `Response Policy Spec`
- `Teaching Budget Spec`
- `Interaction Evidence Spec`
- `Learning Efficiency Metrics Spec`

2. 明确 Task 1 contract 边界
- 所有 spec 都采用现有仓库一致的 `Purpose / Required Fields / Optional Fields / Enumerations / Invariants / Notes` 结构。
- 明确这些对象都是 reviewable governance assets，而不是隐藏的 prompt 习惯或心理推断系统。

3. 同步索引与计划进度
- 在 `docs/specs/README.md` 增加新的 interaction-governance contract family。
- 在实现计划中把 Task 1 的 acceptance criteria 与 verification 勾为完成。
- 在 `docs/change-evidence/README.md` 增加本次记录入口。

## Verification
### Gate order
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
- result: all pass
- key output:
  - build: `OK python-bytecode`, `OK python-import`
  - runtime: `OK runtime-unittest`, `OK runtime-service-parity`, `OK runtime-service-wrapper-drift-guard`
  - contract: `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing`
  - hotspot/doctor: `OK runtime-policy-compatibility`, `OK runtime-policy-maintenance`, `OK codex-capability-ready`, `OK adapter-posture-visible`

### Supporting checks
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- result: pass
- key output:
  - `OK active-markdown-links`
  - `OK claim-drift-sentinel`
  - `OK claim-evidence-freshness`
  - `OK post-closeout-queue-sync`

## Risks
- 当前只完成 Task 1；schema/example/catalog 尚未落地，因此还不能宣称 interaction governance 已 machine-readable。
- 这些 spec 先定义为新的 contract family；如果 Task 2 不及时跟进，spec/schema pairing 会暂时只停留在设计侧。

## Rollback
Revert:
- `docs/specs/interaction-signal-spec.md`
- `docs/specs/response-policy-spec.md`
- `docs/specs/teaching-budget-spec.md`
- `docs/specs/interaction-evidence-spec.md`
- `docs/specs/learning-efficiency-metrics-spec.md`
- `docs/specs/README.md`
- `docs/plans/teaching-collaboration-and-low-token-governance-implementation-plan.md`
- `docs/change-evidence/20260422-interaction-core-specs.md`
- `docs/change-evidence/README.md`
