# 20260427 Hybrid Final-State Current Source Refresh

## Goal
- Re-check the current hybrid final-state posture against official documentation, mature community coding-agent projects, and supply-chain best practices after the `GAP-111` certification.
- Decide whether the latest external sources require a stack or architecture pivot.
- Keep any change limited to planning/claim boundaries unless evidence justifies a new implementation queue.

## Sources Reviewed
- OpenAI Codex `AGENTS.md` guidance: https://developers.openai.com/codex/guides/agents-md
- OpenAI Agents SDK sandbox guidance: https://developers.openai.com/api/docs/guides/agents/sandboxes
- OpenAI Agents SDK guardrails: https://openai.github.io/openai-agents-python/guardrails/
- OpenAI harness engineering notes: https://openai.com/index/harness-engineering/
- MCP roots: https://modelcontextprotocol.io/specification/2025-06-18/client/roots
- A2A latest specification: https://a2a-protocol.org/latest/specification/
- OpenHands runtime architecture: https://docs.openhands.dev/openhands/usage/architecture/runtime
- SWE-agent architecture: https://swe-agent.com/0.7/background/architecture/
- Temporal durable execution: https://docs.temporal.io/temporal
- OPA policy-as-code: https://www.openpolicyagent.org/docs
- OpenTelemetry docs: https://opentelemetry.io/docs/
- FastAPI features: https://fastapi.tiangolo.com/features/
- SLSA provenance: https://slsa.dev/spec/v1.2/provenance

## Decision
No architecture pivot is required.

The current best hybrid target remains:

`repo-local contract bundle + machine-local durable governance kernel + attach-first host adapters + same-contract verification/delivery plane`

The refresh strengthens these boundaries:
- MCP roots are adapter scope inputs that the runtime must revalidate; they are not the only enforcement boundary.
- A2A 1.0.0 integration, if selected after `GAP-111`, must include version negotiation, authorization scoping, and in-task authorization mapping into the runtime-owned approval model.
- Host or SDK guardrails remain defense-in-depth because built-in execution tools are not fully covered by function-tool guardrails.
- Sandbox/process containment remains a certification freshness condition for broad executable tool coverage.
- SLSA-style provenance remains trigger-based for external signing and artifact promotion, but provenance-or-waiver evidence is required for generated runtime packages, control packs, and target-repo light packs that support release claims.

## Changed Files
- `docs/research/2026-04-27-hybrid-final-state-external-benchmark-review.md`
- `docs/architecture/hybrid-final-state-master-outline.md`
- `docs/roadmap/optimized-hybrid-final-state-long-term-roadmap.md`
- `docs/README.md`
- `docs/change-evidence/README.md`
- `docs/change-evidence/20260427-hybrid-final-state-current-source-refresh.md`

## Verification
Run after this change:
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`

## Rollback
- Revert the documentation and evidence files listed above.
- Re-run issue rendering, docs verification, and full repo verification.
