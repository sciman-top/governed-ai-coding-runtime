# 20260617 Workflow Governor Claim Tightening Refresh

## Goal
- current landing: `D:\CODE\governed-ai-coding-runtime`
- target home:
  - `docs/product/interaction-model.md`
  - `docs/README.md`
  - `docs/quickstart/ai-coding-usage-guide.zh-CN.md`
  - `scripts/verify-repo.ps1`
- verification path: align the product-boundary wording with the already-landed `workflow / gate / evidence governance` claim boundary without promoting the conditional `GAP-173..180` package into active work

## Why This Refresh Was Needed
- The repo had already converged on a more careful claim boundary in the root/docs entrypoints and quickstart docs, but `docs/product/interaction-model.md` still described the unproved area using a shorter, more absolute wording.
- The goal here was to tighten wording consistency only: make the product boundary say that a built-in best-workflow auto-executor is not yet proven across repos, hosts, and risk tiers, rather than implying a simpler binary distinction.

## Change Summary
1. Tightened the interaction-model unproved claim boundary
- replaced the more absolute unproved bullets with:
  - not yet proven across repos, hosts, and risk tiers
  - not a replacement host UI or product identity
  - not a default orchestrator that already picks the globally best recipe everywhere

2. Kept the docs index aligned to the same boundary
- updated `docs/README.md` so its proved/unproved summary matches the stronger risk-bounded wording

3. Completed the Chinese quickstart boundary disclosure
- added the Chinese-language `本指南不宣称` section to `docs/quickstart/ai-coding-usage-guide.zh-CN.md`
- aligned it with the English quickstart boundary on:
  - no single best automatic AI coding workflow claim
  - no replacement-host claim
  - no default multi-agent orchestration everywhere claim

4. Extended the host-replacement claim boundary scan
- expanded `scripts/verify-repo.ps1` so `host-replacement-claim-boundary` also scans:
  - `docs/README.md`
  - `docs/product/interaction-model.md`
  - `docs/strategy/current-best-end-state-blueprint.md`
  - `docs/strategy/positioning-and-competitive-layering.md`
- this turns the tightened workflow-governor boundary from a docs-only convention into a wider operator-facing gate

## Verification
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  - result: pass
- `python scripts/verify-planning-status.py`
  - result: pass

## Queue Boundary
- This refresh does **not** implement `GAP-173..180`.
- This refresh does **not** change `planning-status.json`.
- This refresh only tightens wording to stay honest about what is and is not yet proven.

## Risk
- risk_level: `low`
- reason:
  - docs-only wording consistency
  - no queue promotion
  - no contract/runtime mutation

## Rollback
- revert:
  - `docs/product/interaction-model.md`
  - `docs/README.md`
  - `docs/quickstart/ai-coding-usage-guide.zh-CN.md`
  - `scripts/verify-repo.ps1`
- re-run:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  - `python scripts/verify-planning-status.py`
