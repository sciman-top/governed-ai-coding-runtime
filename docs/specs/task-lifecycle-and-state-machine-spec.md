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
- awaiting_approval -> executing
- executing -> verifying
- verifying -> delivered
- executing -> failed
- verifying -> failed
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

## Invariants
- execution cannot begin without a scoped task
- high-risk execution cannot skip `awaiting_approval`
- delivery cannot occur before verification
- rollback cannot occur without a failure or explicit cancellation path
