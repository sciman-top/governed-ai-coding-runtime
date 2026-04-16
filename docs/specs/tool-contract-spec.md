# Tool Contract Spec

## Status
Draft

## Purpose
Define the minimum contract every runtime tool must satisfy.

## Required Fields
- tool_name
- description
- risk_class
- approval_policy
- side_effect_class
- timeout_ms
- retry_policy
- idempotency_expectation
- sandbox_boundary
- trace_fields
- input_schema_ref
- output_schema_ref

## Risk Classes
- low
- medium
- high

## Side Effect Classes
- none
- filesystem_read
- filesystem_write
- process_spawn
- network_read
- network_write
- external_state_change

## Approval Policy Values
- auto_execute
- auto_if_reversible
- pre_publish_confirmation
- explicit_user_approval

## Invariants
- tools with `risk_class=high` must not use `approval_policy=auto_execute`
- tools with write side effects must declare rollback guidance or compensating action type
- every tool must emit required trace fields

## Non-Goals
- plugin marketplace definition
- provider-specific SDK implementation details
