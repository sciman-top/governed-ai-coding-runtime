# 20260614 Reference Shelf Governance Refresh

## Goal
- current landing: `D:\CODE\governed-ai-coding-runtime`
- target home:
  - `D:\CODE\external\ai-coding-runtime-references`
  - `docs/architecture/reference-basis-policy.json`
  - `docs/architecture/capability-portfolio-classifier.json`
  - `docs/change-evidence/governance-hub-certification-report.json`
  - `docs/research/reference-basis-catalog.json`
  - `docs/research/reference-basis-matrix.md`
  - `docs/research/external-reference-repos-index.md`
  - `docs/research/external-reference-repo-tiering.md`
  - `docs/research/external-reference-repo-one-page-overview.md`
  - `docs/research/runtime-governance-borrowing-matrix.md`
- verification path: refresh the external shelf, then keep repo-owned reference rules and evidence aligned before running quick feedback and the hard gate order

## What Changed
- refreshed the external shelf manifest and local shallow clones for the current reference set
- added `1code`, `openclaw-code-agent`, and `openclaw` to the local shelf
- expanded the repo-owned reference-basis catalog so guarded surfaces can cite the full local shelf ids
- promoted the community execution-loop and context-shaping surface into `reference-basis` enforcement
- refreshed `docs/change-evidence/governance-hub-certification-report.json` so the machine-readable portfolio/outcome counts match the newly classified reference shelf
- clarified that:
  - `openclaw-code-agent` is a Tier 2 managed/background coding-session reference
  - `1code` is a Tier 2 managed/background coding-agent client reference
  - `openclaw` is a Tier 4 observe-only personal-assistant gateway reference
  - `hermes-agent` remains Tier 2 for skills, memory, gateway, runtime backend, scheduling, and trajectory ideas

## Source Review
reference_required_review:
- changed_surface_paths:
  - `docs/architecture/reference-basis-policy.json`
  - `docs/research/reference-basis-catalog.json`
  - `docs/research/reference-basis-matrix.md`
  - `docs/research/external-reference-repos-index.md`
  - `docs/research/external-reference-repo-tiering.md`
  - `docs/research/external-reference-repo-one-page-overview.md`
  - `docs/research/runtime-governance-borrowing-matrix.md`
- official_sources_reviewed:
  - `https://github.com/openai/codex`
  - `https://github.com/openai/openai-agents-python`
  - `https://github.com/openai/openai-agents-js`
  - `https://github.com/modelcontextprotocol/modelcontextprotocol`
  - `https://github.com/microsoft/agent-framework`
- primary_references_reviewed:
  - `D:\CODE\external\ai-coding-runtime-references\references.manifest.json`
  - `D:\CODE\external\ai-coding-runtime-references\README.md`
  - `D:\CODE\external\ai-coding-runtime-references\reports\update-summary-latest.json`
  - `D:\CODE\external\ai-coding-runtime-references\repos\1code`
  - `D:\CODE\external\ai-coding-runtime-references\repos\openclaw-code-agent`
  - `D:\CODE\external\ai-coding-runtime-references\repos\openclaw`
  - `D:\CODE\external\ai-coding-runtime-references\repos\hermes-agent`
- local_runtime_evidence_reviewed:
  - `docs/architecture/reference-required-change-policy.json`
  - `docs/architecture/reference-basis-policy.json`
  - `docs/research/reference-basis-catalog.json`
  - `docs/research/reference-basis-matrix.md`
  - `scripts/verify-reference-required-changes.py`
  - `scripts/verify-reference-basis.py`
  - `scripts/verify-capability-portfolio.py`
- source_decision:
  - Add only the three missing references that answer the current OpenClaw / managed-background-agent question.
  - Keep `openclaw` observe-only and do not promote it into the core community execution-loop requirement set.
  - Use repo-owned `reference-basis` enforcement for community execution-loop and context-shaping surfaces instead of leaving the matrix as prose-only guidance.

reference_basis_review:
- changed_surface_paths:
  - `docs/architecture/reference-basis-policy.json`
  - `docs/architecture/capability-portfolio-classifier.json`
  - `docs/research/runtime-governance-borrowing-matrix.md`
  - `docs/research/external-reference-repos-index.md`
  - `docs/research/external-reference-repo-tiering.md`
  - `docs/research/external-reference-repo-one-page-overview.md`
- reference_basis_surface_ids:
  - `host-and-adapter-boundaries`
  - `protocol-and-mcp-boundaries`
  - `community-execution-loop-and-context-shaping`
- required_local_reference_ids_reviewed:
  - `openai-codex`
  - `openai-agents-python`
  - `openai-agents-js`
  - `anthropic-claude-code`
  - `github-copilot-cli`
  - `google-antigravity-cli`
  - `mcp-specification`
  - `mcp-typescript-sdk`
  - `mcp-python-sdk`
  - `github-mcp-server`
  - `mcp-inspector`
  - `a2aproject-A2A`
  - `aider`
  - `swe-agent`
  - `mini-swe-agent`
  - `openhands`
  - `opencode`
  - `goose`
  - `cline`
  - `1code`
  - `openclaw-code-agent`
  - `hermes-agent`
  - `langgraph`
  - `semantic-kernel`
  - `microsoft-agent-framework`
- reference_adoption_decision:
  - Treat `openclaw-code-agent` and `1code` as Tier 2 references for managed/background coding-agent lifecycle design.
  - Treat `openclaw` as Tier 4 observe-only because its main value is personal-assistant gateway and remote-exposure posture, not coding-runtime governance.
  - Keep `hermes-agent` as Tier 2 but constrain adoption to mechanisms, not assistant identity.

## External Shelf Evidence
- `D:\CODE\external\ai-coding-runtime-references\reports\update-summary-latest.json`
  - `generated_at`: `2026-06-14T23:46:35`
  - `repo_count`: `35`
  - `updated_count`: `35`
  - `changed_count`: `25`
  - `failed_count`: `0`
- New or newly classified local reference heads:
  - `1code`: `9f1bc76`
  - `openclaw-code-agent`: `98ee59b`
  - `openclaw`: `2e240e77`

## Verification
- `python -m json.tool docs\architecture\reference-basis-policy.json`
  - result: pass
- `python -m json.tool docs\research\reference-basis-catalog.json`
  - result: pass
- `python -m json.tool docs\architecture\capability-portfolio-classifier.json`
  - result: pass
- `python scripts\verify-reference-required-changes.py`
  - result: pass; matched this evidence file
- `python scripts\verify-reference-basis.py`
  - result: pass; matched this evidence file
- `python scripts\verify-capability-portfolio.py`
  - result: pass; `entry_count=28`
- `python -m unittest tests.runtime.test_reference_basis tests.runtime.test_reference_required_changes tests.runtime.test_capability_portfolio_classifier -v`
  - result: pass; 11 tests passed
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - result: pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - result: pass; 118 test files passed
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - first result: fail because the new `community-execution-loop-and-context-shaping` matcher used broad `path_contains` tokens and unintentionally matched generated `docs/change-evidence/self-evolution-*` JSON evidence
  - fix: limited that surface to architecture/research/product/spec/plans/backlog prefixes so generated evidence JSON is not treated as a guarded source surface
  - final result: pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  - result: pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/governance/preflight.ps1 -DisableAutoCommit`
  - result: pass; build, Runtime, Contract, Doctor, Docs, Scripts, issue rendering, and `git diff --check` completed
- `git diff --check`
  - result: pass; Git emitted CRLF normalization warnings only

## Risk
- risk_level: `low`
- reason: reference shelf and documentation governance only; no host auth, provider state, target repo sync, process restart, push, or merge
- compatibility: existing hard gate order remains unchanged; this slice only expands the named reference ids and same-diff evidence requirement for community execution-loop surfaces

## Rollback
- Revert:
  - `docs/architecture/reference-basis-policy.json`
  - `docs/architecture/capability-portfolio-classifier.json`
  - `docs/change-evidence/governance-hub-certification-report.json`
  - `docs/research/reference-basis-catalog.json`
  - `docs/research/reference-basis-matrix.md`
  - `docs/research/external-reference-repos-index.md`
  - `docs/research/external-reference-repo-tiering.md`
  - `docs/research/external-reference-repo-one-page-overview.md`
  - `docs/research/runtime-governance-borrowing-matrix.md`
  - `docs/change-evidence/20260614-reference-shelf-governance-refresh.md`
  - `docs/change-evidence/README.md`
- External shelf rollback: remove the three optional reference paths and restore the previous `D:\CODE\external\ai-coding-runtime-references\references.manifest.json` from backup or git history if needed.
