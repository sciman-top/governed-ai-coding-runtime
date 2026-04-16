# Risk Tier And Approval Spec

## Status
Draft

## Purpose
Define how runtime actions are classified and when approval interrupts execution.

## Tiers
### low
- read-only or clearly reversible operations
- may auto execute

### medium
- repository write operations or remote write actions with bounded scope
- may require pre-publish confirmation depending on repo profile

### high
- irreversible actions
- broad-scope writes
- privileged or production state changes
- must require explicit user approval

## Required Evidence By Tier
### low
- issue_id
- risk_tier
- command_or_tool

### medium
- issue_id
- risk_tier
- decision_basis
- rollback_trigger

### high
- issue_id
- risk_tier
- approval_reference
- rollback_trigger
- hard_guard_hits
- impacted_scope

## Approval States
- pending
- approved
- rejected
- expired
- cancelled

## Approval Interrupt Rules
- the workflow must pause before execution of a high-risk step
- approval decisions must be written to the evidence bundle
- expired approvals must not be reused implicitly

## Open Questions
- whether medium-tier repo writes should default to approval in Phase 1 or Phase 2
