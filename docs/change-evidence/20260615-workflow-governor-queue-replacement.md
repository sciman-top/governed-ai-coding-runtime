# 20260615 Workflow Governor Queue Replacement

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
- keep `planning-status.json` unchanged
- add `GAP-173..180` as a conditional package only
- tighten product wording to workflow governor rather than replacement host

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
- do not delete any current reference repo

## Decision
- keep `docs/architecture/planning-status.json` unchanged
- keep current active queue = `Continuous-Execution`
- keep selector = `defer_ltp_and_refresh_evidence`
- add a conditional follow-on package only: `GAP-173..180`

## Why
- workflow-governor work is real follow-on scope, but it is not the current planning truth
- this package tightens product boundary, value claims, and workflow-governance contracts without pretending the queue is already active

## Queue Definition
- `GAP-173`: workflow-governor 价值审计与产品边界改写
- `GAP-174`: reference shelf 刷新与 workflow reference-basis enforcement
- `GAP-175`: workflow governance contract family
- `GAP-176`: repo-profile / control-pack / adapter contract workflow 扩展
- `GAP-177`: runtime selection 与 operator/target-run workflow 投影
- `GAP-178`: workflow effect metrics 与 effect-report/KPI 整合
- `GAP-179`: 两仓 workflow 比较实证
- `GAP-180`: claim tightening、closeout evidence、conditional package completion

## Claim Boundary
- this queue is a follow-on package
- this queue is not the current active queue
- this queue does not authorize rewriting planning truth
