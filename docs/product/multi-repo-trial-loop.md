# Multi-Repo Trial Loop

## Purpose
Capture onboarding and adapter feedback as structured product evidence instead of informal notes.

## Trial Record Shape
A multi-repo trial record should capture:
- `trial_id`
- `repo_id`
- `repo_binding_id`
- `adapter_id`
- `adapter_tier`
- `unsupported_capabilities`
- `approval_friction`
- `gate_failures`
- `replay_quality`
- `evidence_refs`
- `handoff_refs`
- `follow_ups`

## Follow-Up Categories
Every follow-up item must be classified as one of:
- `repo_specific`
- `onboarding_generic`
- `adapter_generic`
- `contract_generic`

This prevents trial learning from collapsing into a pile of vague notes.

## Evidence Linkage
Trial records should link back to:
- evidence bundles
- delivery handoff refs
- replay-quality assessment

When a governed task is part of a trial, its evidence bundle may include a `trial_feedback` object with the trial id, repo id, adapter tier, and follow-up categories.

## Replay Quality
Use explicit replay-quality values:
- `replay_ready`
- `needs_follow_up`
- `insufficient`

## Current Boundary
- this model records trial evidence
- it does not yet run multi-repo trials by itself
- the runner and onboarding kit belong to the next task

## Related
- [Evidence Bundle Spec](../specs/evidence-bundle-spec.md)
- [Eval And Trace Grading Spec](../specs/eval-and-trace-grading-spec.md)
- [Target Repo Attachment Flow](./target-repo-attachment-flow.md)
- [Adapter Capability Tiers](./adapter-capability-tiers.md)
