# Hook Contract Spec

## Status
Draft

## Purpose
Define the contract for lifecycle hooks that observe or block governed execution at well-defined checkpoints.

## Required Fields
- hook_id
- display_name
- stage
- mode
- handler_ref
- timeout_ms
- failure_policy
- sandbox_boundary
- input_schema_ref
- output_schema_ref
- observability_fields

## Optional Fields
- repo_selector
- control_ids
- approval_on_failure
- retry_policy
- notes

## Enumerations
### stage
- before_session_start
- after_session_start
- before_tool_request
- after_tool_result
- before_write
- after_write
- before_verification
- after_verification
- before_delivery
- after_delivery

### mode
- advisory
- blocking
- emitting

### failure_policy
- fail_closed
- fail_open
- warn_only

## Invariants
- hooks may observe or block execution but may not redefine task lifecycle semantics
- blocking hooks must declare deterministic input and output schemas
- hooks attached to write-related stages must execute inside a declared sandbox boundary
- `mode=blocking` must not use `failure_policy=warn_only`

## Non-Goals
- hook implementation runtime details
- shell-specific or provider-specific plugin APIs
