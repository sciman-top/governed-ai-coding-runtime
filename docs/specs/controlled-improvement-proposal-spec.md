# Controlled Improvement Proposal Spec

## Status
Draft

## Purpose
Define a structured proposal pipeline that turns evidence-backed signals into human-reviewable improvement proposals without autonomous kernel mutation.

## Required Fields
- proposal_id
- source_refs
- proposal_category
- proposal_scope
- summary
- rationale
- expected_impact
- risk_posture
- human_review
- mutation_guard
- rollback_ref
- status

## Optional Fields
- repo_id
- control_id
- related_task_ids
- proposed_changes
- notes

## Enumerations
### proposal_category
- skill
- hook
- policy
- control
- knowledge
- repo_followup

### proposal_scope
- unified_governance
- repo_specific

### risk_posture
- low
- medium
- high

### status
- proposed
- under_review
- approved_for_implementation
- rejected
- deferred
- archived

## Invariants
- each proposal must link to at least one evidence-backed source reference
- proposals must remain non-executable by default; proposal creation does not mutate policy, controls, or kernel behavior
- `proposal_scope=repo_specific` proposals must not alter unified governance semantics
- `proposal_scope=unified_governance` proposals must include explicit human-review requirements
- every proposal must carry a rollback reference for any later implementation path
- human review is mandatory before any status transition to `approved_for_implementation`

## Non-Goals
- autonomous policy mutation
- direct runtime execution from proposal records
- replacing approval, evidence, or rollback models
