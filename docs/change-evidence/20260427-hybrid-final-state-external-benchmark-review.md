# Hybrid Final-State External Benchmark Review Evidence

## Goal
Validate whether the current hybrid engineering final state remains the best target after checking official docs, community coding-agent projects, and best-practice references.

## Scope
Changed documentation only:
- `docs/architecture/hybrid-final-state-master-outline.md`
- `docs/architecture/mvp-stack-vs-target-stack.md`
- `docs/architecture/governed-ai-coding-runtime-target-architecture.md`
- `docs/roadmap/direct-to-hybrid-final-state-roadmap.md`
- `docs/plans/direct-to-hybrid-final-state-implementation-plan.md`
- `docs/FinalStateBestPractices.md`
- `docs/research/2026-04-27-hybrid-final-state-external-benchmark-review.md`

## Source Basis
External sources reviewed:
- OpenAI Codex AGENTS.md guidance
- OpenAI harness engineering notes
- OpenAI Agents SDK guardrails
- MCP roots and authorization specs
- A2A protocol specification
- LangGraph durable execution docs
- OPA policy-as-code docs
- OpenHands runtime architecture
- SWE-agent architecture
- GitHub Copilot repository custom instructions
- OWASP GenAI Security Project
- SLSA supply-chain framework

## Change Summary
- Kept the canonical hybrid product shape.
- Added explicit execution-containment and protocol-boundary invariants.
- Added sandbox/provenance near-term and long-term planning lanes.
- Clarified that heavy target-state components are trigger-based, not mandatory next steps.
- Split the technology stack into current verified baseline, direct transition stack, and trigger-based final-state candidates.
- Corrected the earlier ambiguity where `Temporal` could be read as a mandatory MVP component.
- Captured the benchmark review in `docs/research/`.

## Verification
Command:
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`

Key output:
- `OK runtime-build`
- `OK runtime-unittest`
- `OK runtime-service-parity`
- `OK schema-json-parse`
- `OK schema-example-validation`
- `OK schema-catalog-pairing`
- `OK dependency-baseline`
- `OK target-repo-rollout-contract`
- `OK target-repo-governance-consistency`
- `OK target-repo-powershell-policy`
- `OK agent-rule-sync`
- `OK runtime-doctor`
- `OK active-markdown-links`
- `OK claim-drift-sentinel`
- `OK powershell-parse`
- `OK issue-seeding-render`
- `Ran 412 tests ... OK (skipped=5)`
- `Ran 10 tests ... OK`
- Post-evidence docs rerun: `OK active-markdown-links`, `OK claim-drift-sentinel`, `OK claim-evidence-freshness`
- Post stack-staging rerun: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All` passed with the same gate family, `Ran 412 tests ... OK (skipped=5)`, and `Ran 10 tests ... OK`

## Risk
- Documentation-only change. No runtime behavior changed.
- The main risk is claim drift if future implementation claims do not satisfy the strengthened containment/provenance criteria.

## Rollback
Use git diff or git history to revert the five documentation changes and this evidence file.
