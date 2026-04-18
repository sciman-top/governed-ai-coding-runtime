# Task Lifecycle And State Machine Spec

## Status
Draft

## Purpose
Define the canonical state machine for AI coding tasks.

## Core States
- created
- scoped
- planned
- awaiting_approval
- executing
- paused
- verifying
- delivered
- failed
- rolled_back
- cancelled

## Required Transitions
- created -> scoped
- scoped -> planned
- planned -> executing
- planned -> awaiting_approval
- planned -> cancelled
- awaiting_approval -> executing
- awaiting_approval -> cancelled
- executing -> verifying
- executing -> paused
- verifying -> delivered
- verifying -> paused
- executing -> failed
- verifying -> failed
- paused -> executing
- paused -> verifying
- paused -> cancelled
- failed -> planned
- failed -> rolled_back

## State Metadata
Each state transition should capture:
- task_id
- previous_state
- next_state
- actor_type
- actor_id
- reason
- evidence_ref
- timestamp

Persistent task records must also capture:
- current_state
- transition_history
- retry_count
- timeout_at
- last_failure_reason
- resume_state
- current_attempt_id
- active_run_id
- workspace_root
- rollback_ref
- run_history

Each persisted run in `run_history` must capture:
- run_id
- attempt_id
- worker_id
- status
- workspace_root
- started_at
- finished_at
- summary
- evidence_refs
- approval_ids
- artifact_refs
- verification_refs
- rollback_ref
- failure_reason

## Invariants
- execution cannot begin without a scoped task
- high-risk execution cannot skip `awaiting_approval`
- delivery cannot occur before verification
- rollback cannot occur without a failure or explicit cancellation path
- pause must preserve the deterministic state the workflow should resume into
- retry must increment persisted retry metadata instead of creating a fresh anonymous task
- each execution attempt must bind one active run id and one workspace root
