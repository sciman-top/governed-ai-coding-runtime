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
- trial runner now supports attached-repo execution loops
- each attachment can run `doctor/posture -> verification -> handoff aggregation`
- optional write probe can be enabled to measure approval friction and write-path readiness
- profile-only summaries remain supported as a compatibility path

## Attached-Repo Loop
For each attached repo, the trial runner executes:
- inspect attachment posture
- validate light pack and repo profile
- run quick verification gates from attached repo commands
- aggregate evidence, verification refs, and handoff refs
- optional write-governance probe (`--execute-write-probe`)

Unhealthy attachment posture is recorded explicitly with:
- `attachment_posture`
- `doctor_status`
- `gate_failures` including `attachment_doctor`
- `replay_quality: insufficient`

## Related
- [Evidence Bundle Spec](../specs/evidence-bundle-spec.md)
- [Eval And Trace Grading Spec](../specs/eval-and-trace-grading-spec.md)
- [Target Repo Attachment Flow](./target-repo-attachment-flow.md)
- [Adapter Capability Tiers](./adapter-capability-tiers.md)
