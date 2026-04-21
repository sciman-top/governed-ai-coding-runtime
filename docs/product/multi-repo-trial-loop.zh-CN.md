# 多仓试运行循环

## Purpose
把 onboarding 和 adapter 反馈记录为结构化产品证据，而不是散乱备注。

## Trial Record 结构
multi-repo trial record 应至少包含：
- `trial_id`
- `repo_id`
- `repo_binding_id`
- `adapter_id`
- `adapter_tier`
- `unsupported_capabilities`
- `approval_friction`
- `gate_failures`
- `replay_quality`
- `evidence_refs`
- `handoff_refs`
- `follow_ups`

## Follow-Up 分类
每个 follow-up 必须归入以下之一：
- `repo_specific`
- `onboarding_generic`
- `adapter_generic`
- `contract_generic`

这样可以避免 trial 学习结果退化成一堆模糊备注。

## Evidence Linkage
trial records 应回链到：
- evidence bundles
- delivery handoff refs
- replay quality assessment

当一个 governed task 属于某次 trial 时，它的 evidence bundle 可以包含 `trial_feedback`，记录 trial id、repo id、adapter tier、follow-up categories。

## Replay Quality
使用明确的 replay quality 值：
- `replay_ready`
- `needs_follow_up`
- `insufficient`

## 当前边界
- trial runner 已支持 attached-repo execution loop
- 每个 attachment 可执行 `doctor/posture -> verification -> handoff` 聚合
- 可选 write probe 可用于测量 approval friction 和 write-path readiness
- profile-only summary 仍保留为兼容路径
- 可通过 `python scripts/export-target-repo-speed-kpi.py` 从 `docs/change-evidence/target-repo-runs` 导出 speed KPI 快照
- speed 相关对外表述必须引用 `kpi-latest.json` 或 `kpi-rolling.json` 的 measured window，不能使用 anecdotal 体感描述

## Related
- [Evidence Bundle Spec](../specs/evidence-bundle-spec.md)
- [Eval And Trace Grading Spec](../specs/eval-and-trace-grading-spec.md)
- [Target Repo Speed KPI Spec](../specs/target-repo-speed-kpi-spec.md)
- [Target Repo 接入流程](./target-repo-attachment-flow.zh-CN.md)
- [Adapter Capability Tiers](./adapter-capability-tiers.md)
- [English Version](./multi-repo-trial-loop.md)
