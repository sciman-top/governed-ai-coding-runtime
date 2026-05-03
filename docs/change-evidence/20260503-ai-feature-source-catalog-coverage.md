# 20260503 AI Feature Source Catalog Coverage

## Goal
- current landing: `D:\CODE\governed-ai-coding-runtime`
- target home: `docs/architecture/runtime-evolution-policy.json`, `scripts/evaluate-runtime-evolution.py`, and `tests/runtime/test_runtime_evolution.py`
- verification path: strengthen the existing runtime-evolution dry-run gate, then close with `build -> test -> contract/invariant -> hotspot`

## Source Review
- OpenAI official sources:
  - `https://openai.com/index/the-next-evolution-of-the-agents-sdk/`
  - `https://developers.openai.com/api/docs/guides/agents/sandboxes`
  - `https://developers.openai.com/api/docs/guides/agents/guardrails-approvals`
  - `https://developers.openai.com/codex/concepts/subagents`
  - `https://developers.openai.com/codex/concepts/sandboxing`
- Claude Code official sources:
  - `https://docs.anthropic.com/en/docs/claude-code/settings`
  - `https://docs.anthropic.com/en/docs/claude-code/hooks`
- Gemini CLI official sources:
  - `https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/settings.md`
  - `https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/plan-mode.md`
  - `https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html`
- MCP official source:
  - `https://modelcontextprotocol.io/specification/2025-11-25/basic/security_best_practices`
- Primary project / reference signals:
  - `https://docs.openhands.dev/openhands/usage/runtimes/overview`
  - `https://aider.chat/docs/repomap.html`
  - `https://swe-agent.com/latest/`

## Decision
- Use the external review to improve the controlled source catalog and gate coverage.
- Do not treat community or primary-project examples as executable instructions.
- Do not replace Codex, Claude Code, Gemini CLI, provider configuration, credentials, target repos, or host permissions.
- Convert the best-practice signal into a deterministic minimum source coverage contract so future runtime-evolution reviews cannot silently regress to stale or narrow sources.

## Changes
- Expanded `source_catalog` with current official and primary-reference AI coding sources covering sandboxes, guardrails, subagents, hooks, plan mode, MCP, repo maps, and agent-computer-interface workflows.
- Added fail-closed validation for `source_priority`, duplicate source IDs, source-type drift, non-HTTPS external refs, and mandatory source IDs.
- Added tests that pin the mandatory source set and prove the evaluator fails when a required source is removed.
- Updated the runtime-evolution plan to mark minimum AI feature source coverage as part of `GAP-121`.

## Verification
- `python -m unittest tests.runtime.test_runtime_evolution`
  - result: `pass`
  - key output: `Ran 9 tests in 32.261s`, `OK`
- `python scripts/evaluate-runtime-evolution.py --as-of 2026-05-03`
  - result: `pass`
  - key output: `source_count=30`, `candidate_count=4`, `invalid_reasons=[]`, `missing_required_refs=[]`
- `python scripts/evaluate-runtime-evolution.py --as-of 2026-05-03 --online-source-check --write-artifacts`
  - result: `pass`
  - artifact_refs:
    - `.runtime/artifacts/runtime-evolution/20260503-runtime-evolution-review.json`
    - `.runtime/artifacts/runtime-evolution/20260503-runtime-evolution-review.md`
  - key output: `source_count=30`, `candidate_count=3`, `online_source_check=true`, `invalid_reasons=[]`, `missing_required_refs=[]`
  - online probe note: `openai-agents-sdk-evolution` returned `HTTP 403`; other external probes returned `200`. The source remains in the required catalog because it was reviewed through browser-backed external research and the probe failure is a fetch restriction, not a policy authorization.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - result: `pass`
  - key output: `OK python-bytecode`, `OK python-import`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - result: `pass`
  - key output: `Completed 103 test files in 116.204s; failures=0`, `OK runtime-unittest`, `OK runtime-service-parity`, `OK runtime-service-wrapper-drift-guard`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - result: `pass`
  - key output: `OK dependency-baseline`, `OK target-repo-governance-consistency`, `OK agent-rule-sync`, `OK functional-effectiveness`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  - result: `pass_with_existing_warning`
  - key output: `OK runtime-policy-compatibility`, `OK runtime-status-surface`, `WARN codex-capability-degraded`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  - result: `pass`
  - key output: `OK runtime-evolution-review`, `OK ai-coding-experience-review`, `OK claim-evidence-freshness`

## Risk
- risk_level: `low`
- reason: policy, docs, evidence, and verifier/test-only change; no target repo sync, provider mutation, credential mutation, automatic apply, push, or merge.
- compatibility: existing dry-run behavior remains; online source failures remain recorded as source evidence and do not authorize mutation.

## Rollback
- Revert:
  - `docs/architecture/runtime-evolution-policy.json`
  - `scripts/evaluate-runtime-evolution.py`
  - `tests/runtime/test_runtime_evolution.py`
  - `docs/plans/runtime-evolution-review-plan.md`
  - `docs/change-evidence/20260503-ai-feature-source-catalog-coverage.md`
  - `docs/change-evidence/README.md`
- Run the hard-gate order again after rollback.
