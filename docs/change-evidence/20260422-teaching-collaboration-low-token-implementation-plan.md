# 20260422 教学式协作与低 Token 治理实现计划

## Goal
把已确认的《教学式协作与低 Token 治理总设计》进一步收敛为可执行实现计划，明确依赖顺序、文件落点、验收标准与门禁要求，避免后续实现直接把总设计硬塞进 runtime。

## Scope
- `docs/plans/teaching-collaboration-and-low-token-governance-implementation-plan.md`
- `docs/plans/README.md`
- `docs/change-evidence/20260422-teaching-collaboration-low-token-implementation-plan.md`
- `docs/change-evidence/README.md`

## Changes
1. 新增 bounded follow-on implementation plan
- 新增 `docs/plans/teaching-collaboration-and-low-token-governance-implementation-plan.md`。
- 计划只覆盖 interaction governance 的 design-to-contract lane，不替代已完成的 direct-to-hybrid 与 governance-optimization 主线历史。

2. 明确 dependency order
- 将实现拆成 9 个窄任务：
  - interaction core specs
  - schema/example/catalog wiring
  - Python primitives
  - evidence bundle interaction trace
  - trace/postmortem interaction inputs
  - task intake defaults
  - operator/runtime read-model projection
  - repo-profile defaults
  - metrics baseline and closeout evidence

3. 同步计划索引与 evidence 索引
- 在 `docs/plans/README.md` 增加本计划入口。
- 在 `docs/change-evidence/README.md` 增加本记录入口。

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
- 该计划是新的 bounded follow-on lane；如果后续不更新 backlog/roadmap，就不应把它表述为仓库唯一 active mainline。
- interaction governance 任务跨越 spec/schema/Python/evidence/read-model，多点联动时容易产生字段漂移。
- 如果没有真实 governed session telemetry，后续 metrics baseline 只能先做到 contract-ready，而不是 product-proof。

## Rollback
Revert:
- `docs/plans/teaching-collaboration-and-low-token-governance-implementation-plan.md`
- `docs/plans/README.md`
- `docs/change-evidence/20260422-teaching-collaboration-low-token-implementation-plan.md`
- `docs/change-evidence/README.md`
