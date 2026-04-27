# 20260427 GAP-112 Current Source Compatibility Guard

## Goal
- Continue post-`GAP-111` realization by converting the current-source compatibility review into an executable guard.
- This file is the closeout record for the current-source compatibility guard.
- Prevent A2A, MCP, Codex sandbox, host guardrail, or supply-chain provenance assumptions from silently strengthening final-state claims.
- Keep the complete hybrid final-state claim evidence-bound without importing untriggered heavyweight infrastructure.

## Scope
- Added a machine-readable current-source compatibility policy.
- Added a verifier for review expiry, source metadata, protocol-boundary mappings, required doc text, evidence refs, and forbidden active-doc patterns.
- Wired the verifier into `verify-repo.ps1 -Check Docs`.
- Added runtime tests, backlog/seeds, claim-catalog, docs index, roadmap, and plan updates for `GAP-112`.

## Changed Files
- `docs/architecture/current-source-compatibility-policy.json`
- `scripts/verify-current-source-compatibility.py`
- `tests/runtime/test_current_source_compatibility.py`
- `scripts/verify-repo.ps1`
- `scripts/github/create-roadmap-issues.ps1`
- `docs/README.md`
- `docs/backlog/README.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/issue-seeds.yaml`
- `docs/roadmap/optimized-hybrid-final-state-long-term-roadmap.md`
- `docs/plans/optimized-hybrid-final-state-long-term-implementation-plan.md`
- `docs/product/claim-catalog.json`
- `docs/change-evidence/README.md`
- `docs/change-evidence/20260427-gap-112-current-source-compatibility-guard.md`

## Verification
- `python scripts/verify-current-source-compatibility.py --as-of 2026-04-27`
  - `status=pass`
  - `policy_id=default-current-source-compatibility`
  - `review_expires_at=2026-07-26`
  - `protocol_ids=mcp_roots,a2a_1_0_0,codex_sandbox_and_guardrails,slsa_provenance`
- `python -m unittest tests.runtime.test_current_source_compatibility`
  - `Ran 4 tests ... OK`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
  - `issue_seed_version=4.5`
  - `rendered_tasks=90`
  - `active_task_count=0`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  - includes `OK current-source-compatibility`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
  - includes `OK current-source-compatibility`
  - `Ran 433 tests ... OK (skipped=5)`
  - `Ran 12 tests ... OK`

## Residual Risks
- The guard records reviewed external sources and expiry; it does not live-fetch external websites during normal repo gates.
- If external protocol semantics change before the expiry date, claim owners still need to trigger a manual refresh and rerun the gate.
- New LTP implementation remains blocked unless a post-`GAP-111` scope fence selects it.

## Rollback
- Revert this policy/verifier/test/planning/claim-catalog/evidence slice.
- Remove `GAP-112` from backlog and issue seeds.
- Downgrade any final-state wording that relies on current-source compatibility checks.
- Re-run issue rendering, Docs gate, and full repo verification before re-certifying.
