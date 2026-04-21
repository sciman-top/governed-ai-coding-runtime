# 20260422 教学式协作与低 Token 治理总设计

## Goal
将“外层 AI 更会纠偏、更会教学、同时更省 token”的目标，收敛为一份可复用、可拆分、可留痕的顶层设计文档，并与本仓现有 task/evidence/trace/governance 语义对齐。

## Scope
- `docs/superpowers/specs/2026-04-22-teaching-collaboration-and-low-token-governance-design.md`
- `docs/change-evidence/20260422-teaching-collaboration-low-token-governance-design.md`
- `docs/change-evidence/README.md`

## Changes
1. 新增教学式协作与低 token 治理总设计
- 在 `docs/superpowers/specs/2026-04-22-teaching-collaboration-and-low-token-governance-design.md` 落一份中文总设计。
- 设计范围只覆盖两个子系统：
  - `教学式协作与认知纠偏`
  - `低 token 预算、压缩与高效教学`
- 设计明确不做心理诊断、不做 memory-first personalization、不替代现有主执行链。

2. 明确共享对象模型与触发链
- 统一定义五类共享对象：
  - `InteractionSignal`
  - `ResponsePolicy`
  - `TeachingBudget`
  - `InteractionEvidence`
  - `LearningEfficiencyMetrics`
- 明确 interaction posture、触发优先级、任务复述策略、压缩/降级/停机规则。

3. 明确与现有治理链的接法
- 设计把新能力挂接到：
  - task intake/runtime
  - evidence bundle
  - eval and trace grading
  - repo profile / operator surface
- 明确不新增平行状态机，不改 canonical gate order。

4. 同步 evidence 索引
- 在 `docs/change-evidence/README.md` 增加本次记录入口，保证后续可检索。

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
- 当前只是顶层设计，不含 schema/example/runtime code，因此还不能直接宣称这些能力已经产品化落地。
- 如果后续直接实现而不先拆成更窄 spec，容易把 interaction signals、budget 和 evidence 字段耦合过深。
- 教学收益与 token 成本的最优平衡仍需要真实 governed session telemetry 验证。

## Rollback
Revert:
- `docs/superpowers/specs/2026-04-22-teaching-collaboration-and-low-token-governance-design.md`
- `docs/change-evidence/20260422-teaching-collaboration-low-token-governance-design.md`
- `docs/change-evidence/README.md`
