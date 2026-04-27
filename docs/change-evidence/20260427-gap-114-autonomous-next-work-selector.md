# GAP-114 Autonomous Next-Work Selector

## Goal
Turn the `GAP-113` promotion result into an autonomous next-work selector.

The selector answers what to do next after complete hybrid final-state certification and LTP promotion evaluation. Current expected output is `defer_ltp_and_refresh_evidence`, not heavy LTP implementation.

## Scope
- Added a machine-readable autonomous next-work selection policy.
- Added `scripts/select-next-work.py` to consume `scripts/evaluate-ltp-promotion.py` output.
- Added runtime tests for current defer posture, gate-first priority, stale evidence priority, one-package LTP promotion, and Docs gate wiring.
- Wired the selector into `verify-repo.ps1 -Check Docs`.
- Updated roadmap, implementation plan, backlog, issue seeds, docs index, master outline, claim catalog, and evidence index.

## Decision
The correct current next action is `defer_ltp_and_refresh_evidence`.

Why:
- The repository is already certified through `GAP-111` on the current branch baseline.
- `GAP-112` keeps current-source assumptions machine-checkable.
- `GAP-113` returns `defer_all` for `LTP-01..06`.
- Therefore autonomous continuation should not start hidden heavy-stack work. It should keep the certification fresh through gates, source review, claim drift checks, and evidence refresh until a higher-priority signal appears.

Selection priority:
1. `repair_gate_first` when gate state is failing.
2. `refresh_evidence_first` when source or evidence state is stale.
3. `promote_ltp` when exactly one LTP package is selected by the promotion evaluator.
4. `owner_directed_scope_required` when the user explicitly directs heavy-stack work.
5. `defer_ltp_and_refresh_evidence` when no LTP package is triggered.

## Verification
- `python scripts/select-next-work.py --as-of 2026-04-27`
  - `status=pass`
  - `ltp_decision=defer_all`
  - `next_action=defer_ltp_and_refresh_evidence`
  - `selected_package=null`
  - `missing_refs=[]`
  - `missing_required_doc_text=[]`
  - `invalid_reasons=[]`
- `python -m unittest tests.runtime.test_autonomous_next_work_selection -v`
  - `Ran 6 tests ... OK`
- `python -m unittest tests.runtime.test_ltp_autonomous_promotion tests.runtime.test_autonomous_next_work_selection -v`
  - `Ran 11 tests ... OK`
- `python -m py_compile scripts/select-next-work.py`
  - pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
  - `issue_seed_version=4.7`
  - `rendered_tasks=92`
  - `completed_task_count=92`
  - `active_task_count=0`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  - `OK current-source-compatibility`
  - `OK ltp-autonomous-promotion`
  - `OK autonomous-next-work-selection`
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
  - `OK autonomous-next-work-selection`
  - `Ran 444 tests ... OK (skipped=5)`
  - `Ran 12 tests ... OK`

## Residual Risks
- The selector does not run expensive gates by itself; it records selection semantics and is enforced by the existing verifier chain.
- The current selector output intentionally defers heavy LTP work. Future promotion still needs fresh trigger evidence, one package, scope fence, full gate reference, and rollback.
- Owner-directed work remains possible, but it must stay explicitly labeled and scoped.

## Rollback
Revert the next-work selection policy, selector, tests, gate wiring, planning updates, claim-catalog entry, and this evidence file. If rollback happens, fall back to `scripts/evaluate-ltp-promotion.py` as the only autonomous continuation decision.
