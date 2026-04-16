# repo-governance-hub Mechanism Adoption Matrix

## Purpose
Upgrade the earlier lightweight borrowing review into a formal adoption decision for mechanisms observed in `repo-governance-hub`.

This document answers three questions:
- which mechanisms should be absorbed into `governed-ai-coding-runtime` now
- which mechanisms should be deferred until the runtime and operator surfaces exist
- which `repo-governance-hub` shapes should remain outside this product boundary

## Decision Rule
Use the following filter order.

### Adopt Now
Adopt now when a mechanism:
- can be specified in docs, schemas, and policies before runtime code exists
- constrains later implementation in a useful way
- strengthens the governance kernel without pulling in multi-repo control-plane machinery

### Defer
Defer when a mechanism:
- depends on runtime services, CI, or real operator flows
- needs a second repository or admission workflow to become meaningful
- needs repeated task history, token telemetry, or recurring failures

### Do Not Adopt
Do not adopt when a mechanism:
- changes the product shape from governed runtime to distribution hub
- mainly exists to manage cross-repo source trees rather than governed task execution
- is PowerShell/distribution infrastructure rather than portable runtime semantics

## Current Boundary
- This repository is still `docs-first / contracts-first`.
- The product target remains `governance kernel + bounded control packs`, not `multi-repo governance distribution`.
- The right borrowing target is the governance kernel semantics, not the `repo-governance-hub` repository shape.

## Source Review Scope
Reviewed areas:
- `config/governance-control-registry.json`
- `config/update-trigger-policy.json`
- `config/target-control-rollout-matrix.json`
- `config/clarification-policy.json`
- `.governance/tracked-files-policy.json`
- `.governance/risk-tier-approval-policy.json`
- `.governance/trace-grading-policy.json`
- `.governance/session-compaction-trigger-policy.json`
- `.governance/external-baseline-policy.json`
- `.governance/failure-replay/policy.json`
- `.governance/failure-replay/replay-cases.json`
- `docs/governance/verification-entrypoints.md`
- `docs/governance/evidence-and-rollback-runbook.md`
- `docs/governance/governance-noise-budget.md`
- `docs/governance/failure-replay-policy.md`
- `docs/governance/cross-repo-compatibility-gate.md`
- `templates/change-evidence.md`
- `tests/clarification-mode.tests.ps1`
- `tests/repo-governance-hub.full-fast.tests.ps1`

## Decision Summary
- `adopt_now`: 5
- `defer`: 5
- `do_not_adopt`: 0 from the ten-item mechanism set below

The absence of `do_not_adopt` inside the ten-item set is intentional. These ten are all worth borrowing as mechanisms. The main question is timing, not value.

## Formal Decision Matrix
| ID | Mechanism | Decision | Why | GAP landing zone |
|---|---|---|---|---|
| M01 | Control inventory lifecycle metadata | `adopt_now` | The control registry should track not only control definition but also operational status, observability quality, and retirement candidates. This is already hinted by the open question in the current control registry spec. | `docs/specs/control-registry-spec.md`, `schemas/jsonschema/control-registry.schema.json`, future recurring review artifact |
| M02 | Control rollout matrix and promotion policy | `adopt_now` | Progressive controls need repo-scoped rollout state, observe windows, and rollback conditions before second-repo proof is attempted. The current schema already supports `observe_to_enforce`, but the repo-level rollout plane is missing. | new rollout matrix spec/schema, `docs/specs/control-registry-spec.md`, `docs/specs/repo-profile-spec.md` |
| M03 | Clarification protocol | `adopt_now` | Clarification is already a named runtime capability in the architecture, but not yet a formal policy contract. AI coding failure loops will be expensive if this remains implicit. | task lifecycle spec, evidence bundle spec, new clarification policy/spec |
| M04 | Compatibility gate and repo admission check | `adopt_now` | The roadmap and backlog already depend on second-repo compatibility proof. This should be a first-class machine-readable gate instead of a roadmap sentence. | `docs/backlog/issue-ready-backlog.md`, `docs/backlog/mvp-backlog-seeds.md`, new compatibility signal spec/schema |
| M05 | Evidence template and completeness checker | `adopt_now` | The runtime needs both machine evidence bundles and operator-facing evidence records. A template plus completeness checker will keep early governance work reviewable before full services exist. | `docs/change-evidence/`, `docs/specs/evidence-bundle-spec.md`, future evidence completeness checker |
| M06 | Failure replay catalog | `defer` | The current schemas already reserve `failure_signature` and `replay_case_ref`, but a useful replay catalog needs repeated failure history and real run traces. | evidence bundle writer, eval pipeline, replay store |
| M07 | Quick/full gate operational entrypoints | `defer` | Quick/full gate semantics already belong in the runtime, but practical entrypoints need real build/test/hotspot commands and a gate runner beyond docs-only placeholders. | `docs/specs/verification-gates-spec.md`, repo profile commands, future runtime gate runner |
| M08 | Tracked-files and artifact classification policy | `defer` | This is highly relevant to AI coding, but the real payoff starts once the runtime creates writable artifacts and delivery bundles in actual repos. | repo profile delivery policy, future git-aware packaging policy, task delivery bundle |
| M09 | Noise budget and session compaction thresholds | `defer` | This is valuable product thinking, but it depends on token, latency, clarification, and rework telemetry from real governed sessions. | task metrics, runtime telemetry, eval/reporting layer |
| M10 | External baseline observe policy | `defer` | External baselines such as SBOM, Scorecard, and Codeowners are useful once CI and dependency surfaces exist. Today they would mostly be placeholders because `E5` is still `gate_na`. | future supply-chain baseline spec, repo profile CI and artifact policy |

## Recommended Implementation Order
### Phase 1: Adopt Now
1. Clarification protocol
2. Control rollout matrix and promotion policy
3. Compatibility gate and repo admission checks
4. Evidence template and completeness checker
5. Control inventory lifecycle metadata

### Phase 2: Defer Until Runtime Bootstrap
1. Quick/full gate operational entrypoints
2. Tracked-files and artifact classification policy
3. External baseline observe policy

### Phase 3: Defer Until Historical Signals Exist
1. Failure replay catalog
2. Noise budget and session compaction thresholds

## Why These Five Are First
The first five shape the governance kernel itself:
- they do not require multi-repo distribution
- they constrain future runtime behavior before code lands
- they improve task correctness, approval discipline, compatibility, and evidence quality

The deferred items are still important, but they are downstream of actual runtime execution and operator telemetry.

## Boundary Exclusions
The following items remain outside MVP absorption even though they are important inside `repo-governance-hub`:
- multi-repo source-of-truth distribution
- backflow and mirrored source trees
- skills promotion lifecycle
- cross-repo template sync machinery
- PowerShell-first runtime architecture
- AGENTS / CLAUDE / GEMINI distribution machinery

These are repository governance-hub concerns, not governed-runtime kernel concerns.

## Impact On Existing GAP Assets
This review sharpens, rather than replaces, the current direction in:
- `docs/architecture/minimum-viable-governance-loop.md`
- `docs/specs/control-registry-spec.md`
- `docs/specs/repo-profile-spec.md`
- `docs/specs/evidence-bundle-spec.md`
- `docs/specs/verification-gates-spec.md`
- `docs/specs/eval-and-trace-grading-spec.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/mvp-backlog-seeds.md`

## Follow-On Document Targets
The next documentation wave should create or extend:
- a clarification protocol spec
- a control rollout matrix spec and schema
- a compatibility signal or repo admission spec and schema
- an evidence template plus evidence completeness policy
- a recurring review output or control retirement policy

## Final Boundary Decision
`governed-ai-coding-runtime` should absorb the governance kernel mechanisms from `repo-governance-hub`, but should not absorb the `repo-governance-hub` repository operating model itself.

