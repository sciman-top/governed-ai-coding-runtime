# Verification Gates Spec

## Status
Draft

## Purpose
Define the quick and full verification model for governed AI coding.

## Gate Levels
### quick
- intended for inner-loop feedback
- may skip expensive checks
- must not weaken high-risk pre-delivery requirements
- uses the live `test` and `contract` gate ids

### full
- required before delivery of medium/high-risk changes
- required after explicit approval paths
- must run the canonical order
- uses the live gate ids `build`, `test`, `contract`, and `doctor`

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
Full gate must run when:
- a high-risk file scope is touched
- a high-risk tool is used
- delivery is requested
- quick gate reports escalation reasons

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

## Runtime Binding
- quick and full verification may bind to a persisted `task_id` and `run_id`
- gate outputs should persist as artifact-backed records under the runtime artifact store
- the canonical gate order remains `build -> test -> contract/invariant -> hotspot`

## Non-Goals
- CI provider implementation details
- language-specific test framework rules
