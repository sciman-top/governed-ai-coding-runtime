# 20260613 README And Index Refresh

## Goal
- current landing: `D:\CODE\governed-ai-coding-runtime`
- target home:
  - `README.md`
  - `README.zh-CN.md`
  - `README.en.md`
  - `docs/README.md`
  - `packages/README.md`
  - `packages/contracts/README.md`
  - `schemas/README.md`
  - `tests/README.md`
  - `docs/change-evidence/README.md`
- verification path: keep the docs entrypoints aligned with current script, planning, package, schema, and release-preflight truth, then verify with fresh repo commands

## What Changed
- rewrote the root README set into current-state entry guides centered on:
  - `planning-status.json`
  - `GAP-159..164` as the active queue
  - `GAP-169..172` as the latest completed hardening slice
  - repo-owned `reference-basis`
  - release-style `preflight`
- refreshed `docs/README.md` so the docs index now points to the current entrypoints, gate surfaces, bilingual operator docs, and latest evidence
- refreshed `packages/README.md` and `packages/contracts/README.md` to match the actual package layout and current reusable contract surface
- refreshed `schemas/README.md` to match the current schema families and pairing rules
- refreshed `tests/README.md` to match the current gate surfaces and notable current test clusters

## Source Review
reference_required_review:
- changed_surface_paths:
  - `README.md`
  - `README.zh-CN.md`
  - `README.en.md`
  - `docs/README.md`
  - `packages/README.md`
  - `packages/contracts/README.md`
  - `schemas/README.md`
  - `tests/README.md`
  - `docs/change-evidence/README.md`
  - `docs/change-evidence/20260613-readme-and-index-refresh.md`
- official_sources_reviewed:
  - `https://developers.openai.com/codex/guides/agents-md`
  - `https://docs.anthropic.com/en/docs/claude-code/settings`
- primary_references_reviewed:
  - `docs/architecture/planning-status.json`
  - `docs/architecture/reference-required-change-policy.json`
  - `docs/architecture/reference-basis-policy.json`
  - `docs/research/reference-basis-matrix.md`
  - `docs/change-evidence/20260609-reference-basis-and-preflight-hardening.md`
- local_runtime_evidence_reviewed:
  - `run.ps1`
  - `scripts/operator.ps1`
  - `scripts/verify-repo.ps1`
  - `scripts/governance/preflight.ps1`
  - `.github/workflows/verify.yml`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/`
  - `schemas/catalog/schema-catalog.yaml`
- source_decision:
  - Keep the entry docs concise and current-truth oriented instead of repeating long historical narratives.
  - Prefer repo-owned scripts, planning truth, and checked-in evidence as the source of documentation truth for this refresh.

reference_basis_review:
- changed_surface_paths:
  - `README.md`
  - `README.zh-CN.md`
  - `README.en.md`
  - `docs/README.md`
  - `tests/README.md`
- reference_basis_surface_ids:
  - `host-and-adapter-boundaries`
  - `release-gate-and-ci-boundaries`
- required_local_reference_ids_reviewed:
  - `openai-codex`
  - `anthropic-claude-code`
  - `anthropic-claude-code-action`
  - `github-copilot-cli`
- reference_adoption_decision:
  - Keep the docs refresh anchored to the already-checked-in `reference-basis` matrix and current repo scripts, instead of re-expanding host and gate claims from memory.

## Verification
- `python -m unittest tests.runtime.test_governance_hub_certification -v`
  - result: pass; refreshed `docs/change-evidence/governance-hub-certification-report.json` back to `status=pass`
- `python -m unittest tests.runtime.test_codex_cockpit_policy_contract -v`
  - result: pass; confirmed the slimmed README set still carries the retired Codex/Cockpit shim boundary tokens
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  - result: pass; planning, claim, evidence, and docs sentinels returned `OK`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check DocsLinks`
  - result: pass; active markdown links returned `OK`
- `python scripts/verify-reference-basis.py`
  - result: pass; no current `reference-basis` guarded runtime surface changed
- `python scripts/verify-reference-required-changes.py`
  - result: pass; no current `reference-required` guarded runtime surface changed
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check RuntimeQuick`
  - result: pass; 57 quick-slice tests passed
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - result: pass; schema, dependency, governance, sync, source-review, and reference guards returned `OK`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - result: pass; 118 runtime/service test files passed and `runtime-test-speed-latest.json` now records `failure_count=0`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/governance/preflight.ps1 -DisableAutoCommit`
  - result: pass; build, Runtime, Contract, Doctor, Docs, Scripts, and `git diff --check` completed; only CRLF normalization warnings were emitted
- `python scripts/select-next-work.py`
  - result: pass; `next_action=defer_ltp_and_refresh_evidence`, with `gate_state=pass`, `evidence_state=fresh`, and no selected LTP package

## Risk
- risk_level: `low`
- reason: documentation-only refresh that aligns entry docs and indices with the current repo truth; no runtime behavior, provider state, target-repo state, or host-local auth flow is mutated
- compatibility: preserves the current active queue, current decision gate, current live posture, and current host-boundary posture already encoded in repo sources

## Rollback
- revert:
  - `README.md`
  - `README.zh-CN.md`
  - `README.en.md`
  - `docs/README.md`
  - `packages/README.md`
  - `packages/contracts/README.md`
  - `schemas/README.md`
  - `tests/README.md`
  - `docs/change-evidence/README.md`
  - `docs/change-evidence/20260613-readme-and-index-refresh.md`
- re-run the documentation and preflight verification commands after rollback
