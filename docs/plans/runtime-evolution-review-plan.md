# Runtime Evolution Review Plan

## Status
- Created on 2026-05-01 as the planning queue for governed self-evolution.
- Queue: `GAP-120..124`.
- Materialization queue: `GAP-125..129`.
- Current status: dry-run implementation exists through policy, evaluator, operator action, Docs gate, and scheduled workflow; low-risk materialization can write proposal and disabled skill candidate files.
- This plan does not authorize direct policy auto-apply, skill enablement, target repo sync, push, or merge. The only automatic apply currently allowed is candidate file materialization.

## Goal
Make runtime self-evolution repeatable, source-grounded, and safe enough to run on a 30-day cadence.

Self-evolution means:
- refresh official documentation, primary project references, community signals, internal runtime evidence, and lessons from real AI coding work
- normalize findings into candidate actions: `add`, `modify`, `delete`, `defer`, or `no_action`
- decide from evidence, not novelty
- preserve the existing hard-gate floor: `build -> test -> contract/invariant -> hotspot`
- record source, candidate, decision, gate, evidence, and rollback

Self-evolution does not mean:
- open-ended autonomous self-mutation
- blindly following community projects or fashionable infrastructure
- bypassing LTP promotion fences
- replacing Codex, Claude Code, or other upstream hosts
- touching credentials, provider secrets, or target repos without an explicit scope and rollback path

## Architecture Decisions
- The source of truth for evolution policy is `docs/architecture/runtime-evolution-policy.json`.
- The user-facing future entrypoint should be `scripts/operator.ps1 -Action EvolutionReview`.
- The first implementation must be dry-run and produce candidate/evidence artifacts before applying changes.
- Automatic checks may report stale review state after 30 days; automatic apply remains limited by risk class.
- Candidate deletion and retirement are first-class outcomes, not failures of the review.
- AI coding experience is a valid source only when it becomes reviewable evidence, controlled improvement proposals, knowledge-source records, or skill-manifest candidates.
- The AI coding experience dry-run entrypoint is `scripts/operator.ps1 -Action ExperienceReview`; it emits proposals and skill manifest candidates, not installed skills.
- The controlled materialization entrypoint is `scripts/operator.ps1 -Action EvolutionMaterialize`; it writes proposal files, disabled skill candidate files, and a rollback manifest.

## Task List

### GAP-120 Runtime Evolution Policy And Scope Boundary
Define the 30-day self-evolution policy and claim boundary.

Acceptance criteria:
- [x] policy defines 30-day freshness, source priority, candidate actions, risk boundaries, and verification floor
- [x] policy explicitly preserves existing LTP scope fences and host-neutral runtime identity
- [x] docs identify current status as dry-run implementation with automatic mutation disabled

Verification:
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`

Dependencies: `GAP-119`

### GAP-121 Evolution Source Collection Design
Design and implement the dry-run source collection contract for official docs, primary projects, community signals, internal runtime evidence, and internal AI coding experience.

Acceptance criteria:
- [x] source categories and priorities are machine-readable
- [x] collected sources record URL/path, checked date, source type, summary, and confidence in dry-run mode
- [x] external content remains candidate evidence only and cannot override repo policy or code facts
- [x] AI coding experience is represented as local, reviewable evidence rather than hidden memory authority

Verification:
- [x] source artifact example validates against the policy fields
- [x] docs explain `platform_na` behavior for unavailable online sources

Dependencies: `GAP-120`

### GAP-122 Evolution Candidate Evaluation Design
Design and implement the dry-run candidate evaluator contract and decision rubric.

Acceptance criteria:
- [x] each candidate can resolve to `add`, `modify`, `delete`, `defer`, or `no_action`
- [x] delete/retire criteria are explicit and evidence-based
- [x] medium/high risk candidates stop at patch plan, scope fence, and rollback plan

Verification:
- [x] example candidates cover defer and no-action outcomes; add/delete remain policy-defined until a real reviewed candidate exists
- [x] candidate decisions include acceptance gates and rollback

Dependencies: `GAP-121`

### GAP-123 Operator EvolutionReview Entrypoint Plan
Implement the operator action with dry-run behavior.

Acceptance criteria:
- [x] planned operator action is documented as `EvolutionReview`
- [x] first executable behavior is dry-run candidate generation
- [x] output artifacts and evidence paths are documented

Verification:
- [x] operator docs link the dry-run action as available
- [x] implementation checklist names required tests before action exposure

Dependencies: `GAP-122`

### GAP-124 Evolution Gate, Evidence, And 30-Day Freshness Plan
Implement the verifier and freshness gate that enforce the 30-day review cadence.

Acceptance criteria:
- [x] gate distinguishes stale review detection from automatic apply
- [x] evidence format records source -> candidate -> decision -> gate -> evidence -> rollback
- [x] stale review has a safe remediation path and does not weaken current hard gates

Verification:
- [x] gate is wired into `verify-repo.ps1 -Check Docs`
- [x] evidence checklist includes N/A fields for unavailable sources

Dependencies: `GAP-123`

## Implementation Order
1. Land policy, plan, backlog tasks, issue seeds, and planning evidence.
2. Implement source collection in dry-run mode.
3. Implement candidate evaluation in dry-run mode.
4. Add `operator.ps1 -Action EvolutionReview` only after source and candidate artifacts are stable.
5. Add Docs/Contract gate coverage for the 30-day freshness policy.
6. Consider low-risk automatic apply only after at least one successful dry-run review cycle.

## AI Coding Experience Extraction
- Input sources: `learning-efficiency-metrics`, `interaction-evidence`, controlled proposal contracts, and skill manifest contracts.
- Scoring: recurrence, time saved, risk reduction, verification strength, reuse scope, maintenance cost, ambiguity, and staleness risk.
- Output assets: advisory controlled improvement proposals and disabled skill manifest candidates.
- Guard: generated records are dry-run artifacts; they cannot install skills, change policy, add hooks, or mutate controls.
- Correctness checks: source refs must exist, scores must be recomputable, proposal and skill thresholds must be respected, proposals must require human review, proposals must be non-mutating, and skill candidates must stay disabled.
- Accuracy checks: low-score signals remain evidence-only; high-score skill candidates must expose source refs, score formula, risk tier, compatibility contracts, and rollback/non-mutation guards.

## Controlled Auto-Apply Materialization
- Allowed automatic writes: controlled proposal JSON, disabled skill candidate `skill-manifest.json`, disabled candidate `SKILL.md`, and materialization manifest.
- Disallowed automatic writes: enabled skills, policy enforcement changes, Codex/Claude/Gemini rules, target repo sync, credentials, provider config, branch push, merge, and release actions.
- Operator entrypoint: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action EvolutionMaterialize`.
- Guard fields: `policy_auto_apply=false`, `skill_auto_enable=false`, `target_repo_sync=false`, and `requires_human_review_before_enable=true`.
- Rollback: delete paths listed in `docs/change-evidence/runtime-evolution-patches/<date>-runtime-evolution-materialization.json`.

## Branch, PR, And Retirement Preparation
- PR preparation entrypoint: `python scripts/prepare-runtime-evolution-pr.py`.
- PR preparation output includes recommended `codex/` branch name, commit message, PR title/body, required gates, and an explicit guard that no branch, commit, push, or PR was created automatically.
- Retirement review entrypoint: `python scripts/review-runtime-evolution-retirements.py`.
- Retirement output is dry-run only: stale disabled candidates become retire proposals; enabled or reviewed assets are not directly deleted.

## Risks And Mitigations
| risk | impact | mitigation |
|---|---|---|
| community examples become instructions | unsafe rule drift | keep community sources as candidate signals only |
| private AI coding memory becomes hidden authority | unverifiable evolution decisions | require interaction evidence, controlled proposals, knowledge-source records, or skill manifests before promotion |
| automatic review becomes automatic mutation | uncontrolled changes | default dry-run and risk-class automation boundaries |
| stale official docs invalidate claims | over-claiming | 30-day freshness gate and current-source compatibility checks |
| feature growth outpaces maintenance | complexity creep | first-class delete/retire criteria |
| heavy stack starts accidentally | unnecessary infrastructure | preserve LTP promotion scope fence |

## Rollback
Revert the `GAP-120..124` planning docs, policy, backlog entries, issue seeds, evidence, and any later implementation files. If a future implementation partially lands, disable the operator action first and keep the current runtime gates active.
