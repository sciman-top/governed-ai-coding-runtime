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

### full
- required before delivery of medium/high-risk changes
- required after explicit approval paths
- must run the canonical order

## Canonical Order
1. build
2. test
3. contract_or_invariant
4. hotspot_or_health_check

## Escalation Rules
Full gate must run when:
- a high-risk file scope is touched
- a high-risk tool is used
- delivery is requested
- quick gate reports escalation reasons

## Required Output
- gate_level
- status
- duration_ms
- failed_steps
- reason_codes
- artifact_refs

## Non-Goals
- CI provider implementation details
- language-specific test framework rules
