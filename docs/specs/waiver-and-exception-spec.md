# Waiver And Exception Spec

## Status
Draft

## Purpose
Define the minimum record for temporary exceptions to kernel controls, gates, or policy defaults.

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
- evidence_link
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

## Invariants
- active waivers must name an approver, expiry, and recovery plan
- waivers may relax enforcement temporarily but may not change the underlying kernel contract definition
- expired waivers must not continue to authorize execution
- evidence link must point to an auditable record explaining why the waiver exists
