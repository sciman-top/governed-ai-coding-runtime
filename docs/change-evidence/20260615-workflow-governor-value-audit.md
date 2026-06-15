# 20260615 Workflow Governor Value Audit

reference_required_review
reference_basis_review

changed_surface_paths
- docs/architecture/reference-basis-policy.json
- docs/plans/workflow-governor-governance-plan.md
- docs/roadmap/workflow-governor-governance-roadmap.md
- docs/research/external-reference-repo-one-page-overview.md
- docs/research/external-reference-repo-tiering.md
- docs/research/external-reference-repos-index.md
- docs/research/reference-basis-catalog.json
- docs/research/reference-basis-matrix.md
- docs/specs/agent-adapter-contract-spec.md
- docs/specs/control-pack-spec.md
- docs/specs/controlled-improvement-proposal-spec.md
- docs/specs/repo-profile-spec.md
- docs/specs/workflow-effect-metrics-spec.md
- docs/specs/workflow-governance-spec.md
- docs/strategy/current-best-end-state-blueprint.md
- schemas/examples/workflow-effect-metrics/default.example.json
- schemas/examples/workflow-governance/default-workflow-governor.example.json
- schemas/jsonschema/workflow-effect-metrics.schema.json
- schemas/jsonschema/workflow-governance.schema.json

official_sources_reviewed
- openai-codex
- anthropic-claude-code
- anthropic-claude-code-monitoring-guide

primary_references_reviewed
- github-spec-kit
- obra-superpowers
- 1code
- openclaw-code-agent
- aider
- swe-agent

local_runtime_evidence_reviewed
- docs/architecture/planning-status.json
- docs/change-evidence/20260614-reference-shelf-governance-refresh.md
- docs/change-evidence/20260615-continuous-execution-active-loop-reconciliation.md

source_decision
- proved value remains workflow / gate / evidence governance
- unproved value remains general best-workflow auto-execution
- workflow governor is an intended evolution target, not a current replacement-host claim

reference_basis_surface_ids
- host-and-adapter-boundaries
- workflow-governance-and-spec-driven-delivery
- reference-basis-and-release-preflight
- protocol-and-mcp-boundaries

required_local_reference_ids_reviewed
- openai-codex
- anthropic-claude-code
- github-spec-kit
- obra-superpowers
- 1code
- openclaw-code-agent
- aider
- swe-agent
- mcp-specification
- mcp-typescript-sdk
- mcp-python-sdk
- github-mcp-server
- openai-agents-python
- openai-agents-js
- google-antigravity-cli
- github-copilot-cli
- a2aproject-A2A
- mcp-inspector

reference_adoption_decision
- keep existing reference shelf
- add workflow-governance reference basis surface
- keep `anthropic-claude-code-monitoring-guide` as Tier 2 / Keep for ROI measurement

## Scope
- audit target: `governed-ai-coding-runtime`
- current active queue truth: `Continuous-Execution`
- current selector truth: `defer_ltp_and_refresh_evidence`
- product-boundary target: `AI coding workflow governor`

## 已证明价值

### target-repo baseline
- 本仓已经能把目标仓 baseline 下发成 repo-owned profile / managed file / governance contract。
- 可量化表现：
  - target repo profile baseline 已有稳定 materialization 路径
  - `ApplyGovernanceBaselineOnly` / `ApplyAllFeatures` 已有可执行脚本与 JSON 输出

### entrypoint enforcement
- 本仓已经能把 canonical entrypoint policy 下发到目标仓 profile，并通过 runtime flow 路径持续执行。
- 可量化表现：
  - `required_entrypoint_policy` 已进入 target governance baseline
  - `runtime-flow` / `runtime-flow-preset` 是被证明存在的统一入口

### gate orchestration
- 本仓已经能把 `build -> test -> contract/invariant -> hotspot` 收敛成可重放、可导出的 gate orchestration。
- 可量化表现：
  - `verify-repo.ps1`
  - `preflight.ps1`
  - target-side quick/full gate projection

### target-run evidence
- 本仓已经能把 target run 输出收敛成结构化 evidence，而不是只剩聊天记录。
- 可量化表现：
  - `docs/change-evidence/target-repo-runs/*.json`
  - effect report / KPI / handoff / replay refs 已存在

### KPI
- 本仓已经能导出 target-repo speed KPI，并把 deny/fallback/problem recovery 变成结构化指标。
- 可量化表现：
  - `target_repo_speed_kpi`
  - `deny_to_success_retries`
  - `fallback_rate`
  - `problem_run_rate`

### effect report
- 本仓已经能把 target-run 前后差异收口成 effect report，而不是只报 pass/fail。
- 可量化表现：
  - `effect-report-<target>.json`
  - decision / backlog_candidates / rolling KPI 对齐验证已存在

## 未证明价值

### 直接业务开发加速
- 当前没有足够 fresh evidence 证明本仓已经稳定提升目标仓真实业务功能开发速度。

### 显著节省人工时间
- 当前没有足够 fresh evidence 证明人工介入次数已显著下降，或维护时间已有稳定、可重复的下降幅度。

### 通用最佳 workflow 自动执行
- 当前没有足够证据证明本仓已经内建并自动执行“最佳 AI 编程工作流”。
- 尤其未证明：
  - 多 subagent
  - 多 worktree
  - spec-first + review-heavy
  - background automation
  - 这些模式在不同 host 上都已被真实执行并量化优于其他模式

## 继续投资门槛

### time_saved
- 需要把 workflow mode 与节省时间联系起来，而不是只证明“脚本存在”。

### manual_intervention_count
- 需要证明人工确认、人工修补、人工 rerun 的次数下降。

### problem_run_rate
- 需要证明 workflow-governance 引入后，problem run rate 可解释下降，而不是只是被记录得更好。

## Audit Conclusion
- 当前项目的已证价值主要是 `workflow / gate / evidence governance`。
- 当前项目尚未证明“最佳自动 AI 编程工作流”已经内建完成。
- 因此对外应收敛为：
  - `AI coding workflow governor`
  - not replacement host
  - not default multi-agent orchestrator
  - not fixed single best workflow executor
