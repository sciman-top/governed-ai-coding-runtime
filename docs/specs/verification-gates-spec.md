# Verification Gates Spec

## Status
Draft

## Purpose
Define the layered verification model (`l1/l2/l3`) for governed AI coding while preserving `quick/full` compatibility aliases.

## Gate Levels
### l1
- intended for inner-loop feedback
- may skip expensive checks
- must not weaken high-risk pre-delivery requirements
- uses the live `test` and `contract` gate ids

### l2
- intended for target-repo daily flow where delivery confidence must include build + runtime + contract checks
- uses the live gate ids `build`, `test`, and `contract`

### l3
- required before delivery of medium/high-risk changes
- required after explicit approval paths
- must run the canonical order
- uses the live gate ids `build`, `test`, `contract`, and `doctor`

### Compatibility Aliases
- `quick` is an alias of `l1`
- `full` is an alias of `l3`
- `fast-check.ps1` remains the compatibility entrypoint for `l1`
- `full-check.ps1` remains the compatibility entrypoint for `l3`
- `level-check.ps1 -Level l1|l2|l3` is the explicit layered target-repo entrypoint

## Canonical Order
1. build
2. test
3. contract_or_invariant
4. hotspot_or_health_check

## Live Gate Bindings
- `build` -> `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- `test` -> `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `contract` -> `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `doctor` -> `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

## Escalation Rules
L3/full gate must run when:
- a high-risk file scope is touched
- a high-risk tool is used
- delivery is requested
- l1/quick gate reports escalation reasons

## Required Output
- task_id
- run_id
- gate_level
- gate_id
- canonical_name
- command
- status
- duration_ms
- failed_steps
- reason_codes
- artifact_refs
- risky_artifact_refs
- timeout_seconds
- blocking

## Runtime Binding
- `quick/full/l1/l2/l3` verification may bind to a persisted `task_id` and `run_id`
- gate outputs should persist as artifact-backed records under the runtime artifact store
- the canonical gate order remains `build -> test -> contract/invariant -> hotspot`
- local target-repo gate runners may stop after the first blocking failure unless diagnostic mode explicitly requests continue-on-error

## Execution Contexts

### local
- runs inside the local runtime, operator workflow, or interactive recovery path
- may be triggered from CLI, session bridge, or operator console helpers
- consumes the same declared repo contract inputs that CI consumes
- provides first-line feedback before delivery

### ci
- runs in non-interactive automation after code leaves the local operator path
- consumes the same declared repo contract inputs as local verification
- must not invent CI-only contract semantics that drift from local verification
- acts as the last line of defense when hooks, wrappers, adapters, or session controls are bypassed

## Same-Contract Inputs
Local and CI verification must read the same declared contract classes:
- repo profile and repo-local attachment declarations
- verification gate definitions and canonical order
- policy and approval references that influence verification or delivery interpretation
- evidence, handoff, and rollback reference expectations

Differences between local and CI should come from execution context, not from different contract semantics.

## Non-Goals
- CI provider implementation details
- language-specific test framework rules
