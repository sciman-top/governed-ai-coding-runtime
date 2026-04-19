# Waiver And Exception Spec

## Status
Draft

## Purpose
Define the minimum record for temporary exceptions to kernel controls, gates, or policy defaults, including expiry handling, recovery gates, and rollback visibility.

## Required Fields
- waiver_id
- subject_type
- subject_ref
- reason
- owner
- approver
- created_at
- expires_at
- recovery_plan
- recovery_gate
- evidence_link
- rollback_ref
- status

## Optional Fields
- repo_id
- control_id
- task_id
- supersedes
- notes

## Enumerations
### subject_type
- control
- gate
- policy
- approval
- repo_profile

### status
- proposed
- active
- expired
- revoked
- superseded
- fulfilled

### recovery_gate
- observe_only
- canary_ready
- enforce_ready

## Invariants
- active waivers must name an approver, expiry, recovery plan, recovery gate, and rollback reference
- waivers may relax enforcement temporarily but may not change the underlying kernel contract definition
- expired waivers must not continue to authorize execution
- waivers must remain temporary and recoverable; silent perpetual waivers are invalid
- evidence link must point to an auditable record explaining why the waiver exists
- `enforce_ready` recovery gates require the waiver to define a concrete recovery plan that removes the exception instead of normalizing it

## Recovery And Expiry Semantics
- `observe_only`: the waived surface may continue as a non-promotable exception while evidence is gathered
- `canary_ready`: the waived surface can advance only into a bounded canary after the recovery plan is satisfied
- `enforce_ready`: the waiver should be removed before full enforcement promotion

Expiry must lead to one of three explicit states:
- `fulfilled`: recovery completed and the waiver is no longer needed
- `revoked`: the waiver was manually canceled
- `expired`: the waiver lapsed without satisfying recovery requirements

## Non-Goals
- granting permanent policy exceptions
- allowing waivers to bypass evidence or rollback requirements
- hiding recovery debt from control promotion decisions
