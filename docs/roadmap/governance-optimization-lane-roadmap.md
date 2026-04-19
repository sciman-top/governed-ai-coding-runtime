# Governance Optimization Lane Roadmap

## Status
- This roadmap defines the next governance-optimization lane that follows the current direct-to-hybrid-final-state mainline.
- It does not replace:
  - `docs/roadmap/direct-to-hybrid-final-state-roadmap.md`
  - `docs/plans/direct-to-hybrid-final-state-implementation-plan.md`
  - `docs/backlog/issue-ready-backlog.md`
- `GAP-060` closeout evidence activated the lane, and `GAP-061` through `GAP-068` are complete on the current branch baseline.
- The lane is now closed with explicit claim discipline and rollback-linked evidence.

## Goal
Define the governed follow-on work that should start after hybrid final-state closure so the runtime can improve through auditable traces, structured postmortems, controlled rollout, and rollback-safe optimization loops.

## Why This Lane Exists
The direct-to-hybrid-final-state queue closes the executable runtime truth:
- governed execution
- live adapter reality
- multi-repo and machine-local sidecar reality
- service-shaped runtime boundaries
- hardening and operator completion

That queue does not yet make the following fully operational as a continuous optimization loop:
- trace-grading-driven improvement
- compatibility and admission hardening for reused target repos
- control promotion and rollback discipline
- knowledge-source freshness and repo-map curation
- provenance and attestation for governance assets
- controlled improvement proposals

This lane exists to close those gaps without changing the product identity from governed runtime into a memory-first or wrapper-first agent platform.

## Roadmap Principles
1. Evidence before optimization.
2. Controlled improvement before autonomous mutation.
3. Promotion only with rollback.
4. Reuse cross-repo signals without collapsing repo-specific constraints into the kernel.
5. Keep memory optional, non-authoritative, and auditable.
6. Do not broaden the product into default multi-agent orchestration, messaging gateways, or generic enterprise automation.

## Dependency Line
`GAP-060 -> GAP-061 -> GAP-062 -> GAP-063 -> GAP-064 -> GAP-065 -> GAP-066 -> GAP-067 -> GAP-068`

## Milestone Overview
| milestone | closes | outcome |
|---|---|---|
| `GOM-0` | lane planning ambiguity | governance-optimization lane has canonical planning assets |
| `GOM-1` | trace and postmortem baseline | traces can drive repeatable improvement proposals |
| `GOM-2` | repo reuse admission gaps | attached repos have stronger compatibility and admission signals |
| `GOM-3` | control promotion ambiguity | observe-to-enforce and waiver recovery are explicit |
| `GOM-4` | knowledge drift | curated knowledge and repo-map inputs become versioned governance assets |
| `GOM-5` | provenance gaps | governance assets can carry provenance and attestation records |
| `GOM-6` | uncontrolled self-improvement risk | the runtime can emit controlled improvement proposals without mutating itself |
| `GOM-7` | lane closeout ambiguity | optimization claims are evidence-backed and rollback-aware |

## Phase 6: Governance Optimization Lane

### Status
- closed governance-optimization lane after completed `GAP-068`
- rendered as a distinct follow-on epic chain under the existing lifecycle initiative

### Goal
- package the governance-only follow-on work into one explicit phase after hybrid final-state closure
- keep optimization work visible without letting it masquerade as the closure queue itself

### Scope
- `GAP-061` through `GAP-068`
- trace grading, repo admission, control rollout, knowledge governance, provenance, controlled proposals, and lane closeout
- dedicated GitHub issue rendering support for this governance follow-on phase

### Exit Criteria
- the governance lane can be rendered as a dedicated epic after `Phase 5`
- `GAP-061` through `GAP-068` are complete on the current branch baseline
- the lane remains visibly follow-on rather than a replacement for direct-to-hybrid closure

### GAP-061 Governance Optimization Lane Canonicalization
#### Goal
Create the canonical planning package for the governance-optimization lane.

#### Scope
- create this roadmap
- create a companion implementation plan
- create a shared acceptance and rollback template
- align indexes, backlog, seeds, and planning evidence
- add dedicated epic-rendering support for the governance lane

#### Exit Criteria
- the lane has a canonical roadmap, implementation plan, backlog entries, issue seeds, and evidence
- future work can reference `GAP-061` through `GAP-068` without ambiguity

### GAP-062 Trace Grading And Improvement Baseline
#### Goal
Promote traces from passive records into the first optimization-grade governance signal.

#### Scope
- strengthen trace grading requirements
- define postmortem-ready trace completeness thresholds
- define how failed runs and reviewer feedback map into improvement inputs

#### Exit Criteria
- traces can distinguish missing evidence, poor outcome, policy misses, and replay-readiness gaps
- postmortem and improvement inputs are reproducible rather than anecdotal

### GAP-063 Repo Admission And Compatibility Signal Hardening
#### Goal
Make cross-repo reuse safer by tightening repo admission and compatibility signals.

#### Scope
- strengthen repo-admission minimums
- define compatibility signals for knowledge readiness, eval readiness, and attachment hygiene
- keep repo overrides restricted to stricter local behavior

#### Exit Criteria
- attachable repos can be accepted, warned, or blocked using explicit machine-readable criteria
- compatibility drift becomes visible before governed execution starts

### GAP-064 Control Rollout Matrix And Waiver Recovery
#### Goal
Make control promotion, rollback, and waiver recovery explicit.

#### Scope
- add rollout-state semantics for `observe`, `canary`, `enforce`, and rollback
- tighten control-lifecycle metadata
- link waivers to recovery and promotion gates

#### Exit Criteria
- progressive controls can move from observe to enforce with evidence
- waivers cannot remain active without expiry and recovery visibility

### GAP-065 Knowledge Registry And Repo-Map Context Shaping
#### Goal
Turn curated knowledge and repo-map inputs into governed runtime assets instead of informal context hints.

#### Scope
- formalize trust, freshness, precedence, and drift handling for knowledge sources
- align repo-map inputs with the knowledge-source contract
- keep knowledge shaping separate from system-of-record runtime state

#### Exit Criteria
- knowledge sources are versioned, typed, and reviewable
- repo-map context shaping is reusable across repos without becoming an implicit memory product

### GAP-066 Provenance And Attestation For Governance Assets
#### Goal
Extend provenance and attestation coverage to governance assets.

#### Scope
- define provenance minimums for control packs, schema bundles, and release-adjacent governance artifacts
- align provenance with verification status and rollback visibility
- keep attestation additive to evidence rather than a replacement for evidence

#### Exit Criteria
- governance assets can carry provenance records with verifiable references
- promotion decisions can reference attested governance artifacts when present

### GAP-067 Controlled Improvement Proposal Pipeline
#### Goal
Allow the runtime to propose improvements without directly mutating policy or kernel behavior.

#### Scope
- define improvement proposal inputs from traces, postmortems, reviewer feedback, and repeated failures
- classify proposals into skill, hook, policy, control, knowledge, and repo-follow-up buckets
- require human review before activation or rollout

#### Exit Criteria
- the runtime can emit structured improvement proposals
- no proposal path can silently modify kernel policy or approval semantics

### GAP-068 Governance Optimization Lane Closeout And Claim Discipline
#### Goal
Close the lane with explicit optimization claims, acceptance criteria, and rollback notes.

#### Scope
- define final lane closeout criteria
- record residual risks and deferred items
- align roadmap, plan, backlog, and evidence one last time

#### Exit Criteria
- governance-optimization claims are backed by evidence, not aspiration
- deferred non-goals remain explicit
- closeout references verification and rollback-linked evidence for every lane slice from `GAP-061` through `GAP-067`

## Claim Discipline
The repository should not claim:
- autonomous policy mutation
- memory-first self-evolution
- default multi-agent governance orchestration
- full self-healing runtime behavior

The repository may claim narrower truths as the lane exits:
1. after `GAP-061`: the optimization lane is canonicalized
2. after `GAP-062`: traces can drive repeatable postmortem and grading
3. after `GAP-063`: repo reuse admission is stronger and more explicit
4. after `GAP-064`: control promotion and waiver recovery are governed
5. after `GAP-065`: knowledge shaping is versioned and reviewable
6. after `GAP-066`: governance assets can carry provenance records
7. after `GAP-067`: the runtime can emit controlled improvement proposals
8. after `GAP-068`: the lane is closed with evidence-backed claim discipline

## Non-Goals
- replacing the direct-to-hybrid-final-state mainline
- introducing a memory-first product identity
- turning the runtime into a wrapper-first orchestrator
- allowing autonomous policy mutation
- making default multi-agent orchestration part of the kernel baseline
- building a marketplace for skills, hooks, or control packs in this lane

## Companion Deliverables
This roadmap is paired with:
1. `docs/plans/governance-optimization-lane-implementation-plan.md`
2. `docs/backlog/issue-ready-backlog.md`
3. `docs/backlog/issue-seeds.yaml`
4. `scripts/github/create-roadmap-issues.ps1`
5. `docs/templates/governance-gap-acceptance-and-rollback-template.md`
6. `docs/change-evidence/20260419-governance-optimization-lane-planning.md`

## Source References
- `docs/architecture/minimum-viable-governance-loop.md`
- `docs/architecture/governance-boundary-matrix.md`
- `docs/specs/control-registry-spec.md`
- `docs/specs/eval-and-trace-grading-spec.md`
- `docs/specs/knowledge-source-spec.md`
- `docs/specs/repo-admission-minimums-spec.md`
- `docs/specs/provenance-and-attestation-spec.md`
- `docs/specs/waiver-and-exception-spec.md`
- `docs/product/maintenance-deprecation-and-retirement-policy.md`
- `docs/roadmap/direct-to-hybrid-final-state-roadmap.md`
