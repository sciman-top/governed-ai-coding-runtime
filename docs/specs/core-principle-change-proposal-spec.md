# Core Principle Change Proposal Spec

## Status
Draft

## Purpose
Define a reviewable proposal record for adding, updating, deprecating, retiring, or deleting a core-principle candidate without changing active policy, specs, verifiers, skills, target repos, or remote branches.

## Required Fields
- schema_version
- generated_on
- change_id
- change_action
- principle_id
- category
- summary
- rationale
- source_refs
- target_active_files
- required_controls
- guard
- rollback

## Enumerations
### change_action
- add
- update
- deprecate
- retire
- delete_candidate

### category
- positioning
- automation
- safety
- governance
- compatibility
- lifecycle

## Invariants
- proposal generation must not mutate active core-principle policy, specs, verifier code, skills, target repos, push state, or merge state
- `guard.requires_human_review_before_effective_change` must be true
- all automatic mutation flags in `guard` must be false
- source references and active target files must be explicit
- rollback must describe how to remove the proposal artifact without affecting active policy

## Non-Goals
- active policy mutation
- automatic verifier update
- automatic skill enablement
- target repo synchronization
- remote push or merge
