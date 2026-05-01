# Governance Hub Certification Spec

## Status
Draft

## Purpose
Define the certification package that proves the governance hub, reusable contract, controlled evolution loop, and target-repo effect feedback are executable together and remain bounded by current-source compatibility.

## Required Fields
- schema_version
- certification_id
- status
- reviewed_on
- verification_command
- report_output_ref
- portfolio_ref
- effect_feedback_ref
- policy_audit_ref
- required_artifact_refs
- required_outcomes
- required_loop_ids
- host_statement_refs
- rollback_ref

## Invariants
- certification must include real target-repo effect evidence, not only plan or schema files
- all required lifecycle outcomes must be present in the capability portfolio review
- `review_loop`, `knowledge_loop`, `capability_upgrade_loop`, `capability_cleanup_loop`, `controlled_evolution_loop`, and `self_improvement_loop` must each resolve to executable evidence
- Codex and Claude Code must remain cooperation hosts, not competitor products
- any deferred or unimplemented capability must remain fenced by future-trigger evidence rather than upgraded to a live claim
- current-source compatibility must pass before certification claims are emitted

## Non-Goals
- automatic host replacement
- automatic push or merge
- automatic skill enablement
- automatic target-repo synchronization
