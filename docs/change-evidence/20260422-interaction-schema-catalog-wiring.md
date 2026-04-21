# 20260422 Interaction Schema And Catalog Wiring

## Goal
执行《Teaching Collaboration And Low-Token Governance Implementation Plan》的 Task 2，为 Task 1 新增的 5 份 interaction core specs 补齐 schema、example 和 catalog wiring，使 contract gate 恢复闭合。

## Scope
- `schemas/jsonschema/interaction-signal.schema.json`
- `schemas/jsonschema/response-policy.schema.json`
- `schemas/jsonschema/teaching-budget.schema.json`
- `schemas/jsonschema/interaction-evidence.schema.json`
- `schemas/jsonschema/learning-efficiency-metrics.schema.json`
- `schemas/examples/interaction-signal/default-bugfix-gap.example.json`
- `schemas/examples/response-policy/guided-clarify.example.json`
- `schemas/examples/teaching-budget/default-runtime.example.json`
- `schemas/examples/interaction-evidence/checklist-first-bugfix.example.json`
- `schemas/examples/learning-efficiency-metrics/baseline.example.json`
- `schemas/examples/README.md`
- `schemas/catalog/schema-catalog.yaml`
- `docs/plans/teaching-collaboration-and-low-token-governance-implementation-plan.md`
- `docs/change-evidence/20260422-interaction-schema-catalog-wiring.md`
- `docs/change-evidence/README.md`

## Changes
1. 新增 5 份 interaction governance schemas
- 为 Task 1 的 5 份 spec 各自补齐 machine-readable schema。
- schema 覆盖 required fields、enum values 与关键边界。

2. 新增 5 个 example instances
- 新增 bugfix/checklist-first、guided clarify、default runtime budget 等最小示例。
- examples 目录与 schema basename 一一对应，满足现有 example validation 约束。

3. 恢复 catalog pairing
- 在 `schemas/catalog/schema-catalog.yaml` 增加 5 条新的 spec/schema pairing。
- 在 `schemas/examples/README.md` 增加新目录、新示例与验证命令说明。

4. 同步计划与 evidence 索引
- 在实现计划中把 Task 2 的 acceptance criteria 与 verification 勾为完成。
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
- 当前只完成到 Task 2；Python primitives 还未落地，因此 interaction governance 仍是 docs/schema-ready，而不是 runtime-ready。
- examples 以“最小可审计”为目标，不代表生产默认值或最终 telemetry 粒度。

## Rollback
Revert:
- `schemas/jsonschema/interaction-signal.schema.json`
- `schemas/jsonschema/response-policy.schema.json`
- `schemas/jsonschema/teaching-budget.schema.json`
- `schemas/jsonschema/interaction-evidence.schema.json`
- `schemas/jsonschema/learning-efficiency-metrics.schema.json`
- `schemas/examples/interaction-signal/default-bugfix-gap.example.json`
- `schemas/examples/response-policy/guided-clarify.example.json`
- `schemas/examples/teaching-budget/default-runtime.example.json`
- `schemas/examples/interaction-evidence/checklist-first-bugfix.example.json`
- `schemas/examples/learning-efficiency-metrics/baseline.example.json`
- `schemas/examples/README.md`
- `schemas/catalog/schema-catalog.yaml`
- `docs/plans/teaching-collaboration-and-low-token-governance-implementation-plan.md`
- `docs/change-evidence/20260422-interaction-schema-catalog-wiring.md`
- `docs/change-evidence/README.md`
