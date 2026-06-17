# 20260617 Self-Evolution Promotion Review And Defer

## Goal
- current landing: `D:\CODE\governed-ai-coding-runtime`
- target home:
  - `docs/change-evidence/20260617-self-evolution-promotion-review-and-defer.md`
  - `docs/change-evidence/README.md`
- verification path: keep the current promotion-controller recommendation reviewable without enabling policy mutation, skill enablement, target sync, push, or merge

## Scope Boundary
- This slice is review-only.
- It does not materialize policy mutations, enable skills, sync target repos, push, merge, or convert any promotion lane into active behavior.
- It stays aligned with the current selector result `defer_ltp_and_refresh_evidence`.

## Inputs Reviewed
- `docs/change-evidence/self-evolution-recommendations/20260617-self-evolution-recommendations.json`
- `docs/change-evidence/self-evolution-promotions/20260617-self-evolution-promotion-controller.json`
- `docs/change-evidence/self-evolution-variant-evaluations/20260617-self-evolution-variant-evaluation.json`
- `docs/architecture/planning-status.json`
- `scripts/select-next-work.py`

## Review Result
- selector posture remains `defer_ltp_and_refresh_evidence`
- recommendation posture remains `review_candidate_variants`
- promotion controller posture remains `ready_for_review`
- every effective-change lane remains review-gated:
  - `automatic_policy_mutation=false`
  - `automatic_skill_enablement=false`
  - `automatic_target_repo_sync=false`
  - `automatic_push_or_merge=false`
  - `effective_change_allowed=false`

## Lane Audit
1. `policy_mutation`
   - status: `review_required`
   - next action: `attach_promotion_evidence_and_review`
   - reason: any policy mutation still needs human review plus full gates before it can become active
2. `skill_enablement`
   - status: `review_required`
   - next action: `attach_promotion_evidence_and_review`
   - reason: disabled skill candidates remain bounded until explicit promotion evidence and rollback refs exist
3. `target_repo_sync`
   - status: `review_required`
   - next action: `attach_promotion_evidence_and_review`
   - reason: target sync is still limited to explicit operator actions instead of unattended carry-through
4. `push_or_merge`
   - status: `review_required`
   - next action: `attach_promotion_evidence_and_review`
   - reason: push and merge remain human-reviewed release actions, not a side effect of self-evolution materialization

## Decision
- Keep the promotion controller in `review_required` state.
- Do not override the controller into any automatic lane while the selector still says `defer_ltp_and_refresh_evidence`.
- Treat `review_promotion_evidence_before_effective_change` as a documentation and operator-readiness recommendation only, not as permission for unattended follow-through.

## Why No Further Mutation
- the selector still chooses bounded evidence upkeep rather than a safer promotion window
- the recommendation report still says `mutation_allowed=false`
- the promotion controller explicitly keeps all four effective-change lanes at `review_required`
- the variant review ordering already favors the checklist-first proposal/skill pair, but that ranking still does not satisfy the human-review requirement

## Verification
- `python scripts/select-next-work.py`
  - result: pass; `next_action=defer_ltp_and_refresh_evidence`
- `python scripts/plan-self-evolution-promotion.py --as-of 2026-06-17 --write-artifacts`
  - result: pass; `status=ready_for_review`, `effective_change_allowed=false`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  - result: pass

## Risk
- risk_level: `low`
- reason: evidence-only review closeout; it records the current guarded promotion boundary without changing runtime behavior or enabling any effective-change lane

## Rollback
- remove:
  - `docs/change-evidence/20260617-self-evolution-promotion-review-and-defer.md`
  - the matching entry in `docs/change-evidence/README.md`
- re-run Docs verification after rollback
