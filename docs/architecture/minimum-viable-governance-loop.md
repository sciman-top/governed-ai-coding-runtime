# Minimum Viable Governance Loop

## Goal
Define the smallest governance loop that makes AI coding execution controllable, auditable, and rollbackable.

## Loop
1. Intake task
- normalize goal
- lock repository scope
- define acceptance criteria

2. Classify risk
- identify tool risk tier
- identify write scope
- determine approval requirement

3. Start governed session
- attach repo profile
- set tool allowlist
- set budget and timeout policy

4. Execute bounded work
- read, plan, patch, verify
- record evidence at each checkpoint

5. Pause for approval when required
- emit approval request
- persist rationale and rollback trigger
- wait for human decision

6. Run verification gates
- quick gate for low-risk iteration
- full gate for high-risk or pre-delivery actions

7. Produce delivery bundle
- summary
- files changed
- verification results
- rollback reference
- open questions

8. Persist evidence
- task snapshot
- commands run
- tool calls
- approvals
- final result

9. Grade the trace
- score evidence completeness, workflow correctness, replay readiness, and outcome quality
- classify failures as missing evidence, policy miss, replay gap, poor outcome quality, reviewer disagreement, or repeated failure signature
- keep the grade linked to immutable runtime evidence rather than overwriting it

10. Capture postmortem inputs
- normalize failed runs, reviewer feedback, and repeated failure signatures
- link every input back to evidence refs and affected grading dimensions
- preserve repo-specific follow-ups separately from kernel or adapter follow-ups

11. Generate controlled improvement inputs
- prepare proposal-ready signals only after evidence and trace grading exist
- keep proposal generation human-reviewed and non-mutating
- hand later governance tasks structured inputs instead of anecdotal summaries

## Required Building Blocks
- task object
- repo profile
- control registry
- control pack metadata
- risk tier model
- approval model
- evidence bundle
- verification gate runner

## Out of Scope For This Loop
- multi-repo distribution
- autonomous policy mutation
- cross-organization federation
- durable memory product features

## Success Criteria
- a high-risk action cannot execute without an explicit path
- a task can be replayed from evidence
- a failed run can point to a rollback trigger
- a repo can override bounded runtime settings without breaking kernel rules
- trace grading can distinguish missing evidence, policy misses, replay gaps, and poor outcome quality
- postmortem inputs can be reproduced from failed runs or reviewer feedback without reinterpreting the original trace
