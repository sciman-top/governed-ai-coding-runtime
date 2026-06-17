# 20260617 Self-Evolution Variant Review And Defer

## Goal
- current landing: `D:\CODE\governed-ai-coding-runtime`
- target home:
  - `docs/change-evidence/20260617-self-evolution-variant-review-and-defer.md`
  - `docs/change-evidence/README.md`
- verification path: keep the current `review_candidate_variants` lane reviewable without turning it into an automatic effective change

## Scope Boundary
- This slice is review-only.
- It does not materialize policy mutations, enable skills, sync target repos, push, merge, or promote any self-evolution artifact into active behavior.
- It stays aligned with the current selector result `defer_ltp_and_refresh_evidence`.

## Inputs Reviewed
- `docs/change-evidence/self-evolution-readiness/20260617-self-evolution-readiness.json`
- `docs/change-evidence/self-evolution-recommendations/20260617-self-evolution-recommendations.json`
- `docs/change-evidence/self-evolution-variants/20260617-self-evolution-variants.json`
- `docs/change-evidence/self-evolution-variant-evaluations/20260617-self-evolution-variant-evaluation.json`
- `docs/change-evidence/self-evolution-promotions/20260617-self-evolution-promotion-controller.json`
- `docs/architecture/planning-status.json`
- `scripts/select-next-work.py`

## Review Result
- selector posture remains `defer_ltp_and_refresh_evidence`
- recommendation posture remains `review_candidate_variants`
- promotion controller posture remains `ready_for_review`
- effective-change boundary remains fail-closed:
  - `mutation_allowed=false`
  - `effective_change_allowed=false`
  - `requires_human_review_before_effective_change=true`

## Ranked Review Candidates
1. `variant.skill.checklist-first-bugfix`
   - score: `11`
   - risk: `low`
   - reason: carries three verification refs, preserves `default_enabled=false`, and already encodes the cleanest review-to-promotion path
2. `variant.proposal.checklist-first-bugfix`
   - score: `10`
   - risk: `low`
   - reason: already carries explicit verification refs and stays proposal-only with rollback preserved
3. `variant.candidate.evol-host-feedback`
   - score: `8`
   - risk: `low`
   - reason: bounded runtime-evolution candidate, but still has `verification_refs=0`
4. `variant.candidate.evol-ai-experience`
   - score: `8`
   - risk: `low`
   - reason: bounded runtime-evolution candidate, but still has `verification_refs=0`
5. `variant.candidate.evol-effect-feedback`
   - score: `8`
   - risk: `medium`
   - reason: effect-feedback driven candidate without attached verification refs, so its review value exists but promotion confidence remains lower
6. `variant.candidate.evol-source-collector`
   - score: `8`
   - risk: `medium`
   - reason: source-collector candidate without attached verification refs, so it should not outrank the checklist-first proposal/skill pair

## Decision
- Keep all six variants in `review_candidate` state.
- Do not auto-materialize any of them while the selector still says `defer_ltp_and_refresh_evidence`.
- If a later owner-reviewed promotion window opens, prefer the `checklist-first-bugfix` proposal/skill pair before the four runtime-evolution candidates because the pair already carries explicit verification refs and lower review ambiguity.

## Why No Further Mutation
- the selector does not choose a heavy package or safer autonomous continuation beyond bounded evidence upkeep
- the recommendation report explicitly keeps `mutation_allowed=false`
- the promotion controller explicitly keeps every effective-change lane blocked or review-gated
- the four runtime-evolution candidates still have `verification_refs=0`, so turning them into active changes would weaken review quality

## Verification
- `python scripts/select-next-work.py`
  - result: pass; `next_action=defer_ltp_and_refresh_evidence`
- `python scripts/evaluate-runtime-evolution-variant.py --as-of 2026-06-17 --write-artifacts`
  - result: pass; six variants remain `review_candidate`
- `python scripts/plan-self-evolution-promotion.py --as-of 2026-06-17 --write-artifacts`
  - result: pass; `status=ready_for_review`, `effective_change_allowed=false`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  - result: pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/governance/preflight.ps1 -DisableAutoCommit`
  - result: pass

## Risk
- risk_level: `low`
- reason: evidence-only review closeout; it records current guarded state and review ordering without changing active runtime behavior

## Rollback
- remove:
  - `docs/change-evidence/20260617-self-evolution-variant-review-and-defer.md`
  - the matching entry in `docs/change-evidence/README.md`
- re-run Docs and preflight verification after rollback
