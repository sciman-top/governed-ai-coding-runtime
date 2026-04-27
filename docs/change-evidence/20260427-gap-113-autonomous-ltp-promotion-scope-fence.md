# GAP-113 Autonomous LTP Promotion Scope Fence

## Goal
Answer how to advance, whether to advance, why to advance, and whether autonomous advancement is allowed after complete hybrid final-state certification.

The result is an autonomous LTP promotion scope fence: the runtime can continue without asking when no package is ready, and can promote exactly one `LTP-01..06` package only when the policy has trigger evidence, scope, full gate reference, rollback, and one vertical slice.

## Scope
- Added a machine-readable LTP promotion policy for `LTP-01..06`.
- Added an evaluator that reports `defer_all`, `auto_select`, or `owner_directed_scope_required`.
- Wired the evaluator into `verify-repo.ps1 -Check Docs`.
- Added runtime tests for current defer posture, one-package auto selection, multiple-selection rejection, required text drift, and Docs gate wiring.
- Updated roadmap, implementation plan, backlog, issue seeds, docs index, claim catalog, and evidence index.

## Changed Files
- `docs/architecture/ltp-autonomous-promotion-policy.json`
- `docs/adrs/0008-autonomous-ltp-promotion-scope-fence.md`
- `scripts/evaluate-ltp-promotion.py`
- `tests/runtime/test_ltp_autonomous_promotion.py`
- `scripts/verify-repo.ps1`
- `scripts/github/create-roadmap-issues.ps1`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/issue-seeds.yaml`
- `docs/backlog/README.md`
- `docs/roadmap/optimized-hybrid-final-state-long-term-roadmap.md`
- `docs/plans/optimized-hybrid-final-state-long-term-implementation-plan.md`
- `docs/architecture/hybrid-final-state-master-outline.md`
- `docs/README.md`
- `docs/product/claim-catalog.json`
- `docs/change-evidence/README.md`

## Decision
The correct current action is `defer_all`.

Why:
- `GAP-111` already certifies the complete hybrid final state on the current branch baseline.
- `GAP-112` keeps external source assumptions machine-checkable.
- No `LTP-01..06` package currently has trigger evidence proving that the certified transition stack is insufficient.
- Force-implementing Temporal, OPA/Rego, event streaming, object-store promotion, A2A gateway, full observability, or external signing now would add operational cost without current trigger evidence.

Autonomous promotion is allowed when:
- exactly one package is `auto_selected`
- that package is `triggered` or `candidate`
- `scope_fence_ref` exists
- `full_gate_ref` exists
- rollback and one vertical slice are part of the package requirements
- `verify-repo.ps1 -Check All` remains the acceptance floor

Owner-directed heavy-stack work remains allowed, but must be labeled `owner_directed_selected` and cannot be misreported as evidence-triggered autonomous promotion.

## Verification
- `python scripts/evaluate-ltp-promotion.py --as-of 2026-04-27`
  - `status=pass`
  - `decision=defer_all`
  - `should_promote=false`
  - `auto_selected_count=0`
  - `missing_refs=[]`
  - `missing_required_doc_text=[]`
  - `invalid_selection_reasons=[]`
- `python -m unittest tests.runtime.test_ltp_autonomous_promotion -v`
  - `Ran 5 tests ... OK`
- `python -m py_compile scripts/evaluate-ltp-promotion.py`
  - pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
  - `issue_seed_version=4.6`
  - `rendered_tasks=91`
  - `completed_task_count=91`
  - `active_task_count=0`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  - `OK current-source-compatibility`
  - `OK ltp-autonomous-promotion`
  - `OK claim-drift-sentinel`
  - `OK post-closeout-queue-sync`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`
  - `OK powershell-parse`
  - `OK issue-seeding-render`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
  - `OK runtime-build`
  - `OK runtime-unittest`
  - `OK runtime-service-parity`
  - `OK schema-json-parse`
  - `OK schema-example-validation`
  - `OK schema-catalog-pairing`
  - `OK dependency-baseline`
  - `OK runtime-doctor`
  - `OK ltp-autonomous-promotion`
  - `Ran 438 tests ... OK (skipped=5)`
  - `Ran 12 tests ... OK`

## Residual Risks
- The current policy intentionally does not implement any heavy `LTP` package; it only defines the safe autonomous promotion boundary.
- Future owner-directed work can still force a package forward, but it must remain explicitly labeled and evidence-bound.
- Trigger evidence may become stale; the policy has `review_expires_at` so the Docs gate fails when the review window expires.

## Rollback
Revert the LTP promotion policy, ADR, evaluator, tests, gate wiring, planning updates, claim-catalog entry, and this evidence file. If rollback happens, keep `LTP-01..06` in defer/watch posture until a replacement promotion policy is accepted.
