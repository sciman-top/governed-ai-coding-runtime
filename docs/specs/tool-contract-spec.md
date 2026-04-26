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
- containment_profile

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

## Containment Profile
Every governed executable tool must declare a `containment_profile`. The profile is the shared runtime boundary for tool families that can mutate files, spawn processes, change external state, or bridge into another tool runtime.

Required fields:
- tool_family
- workspace_root
- allowed_path_roots
- environment_policy
- network_posture
- timeout_ms
- approval_class
- evidence_refs
- rollback_refs

Supported `tool_family` values:
- file_write
- shell
- git
- package_manager
- browser_automation
- mcp_tool_bridge

Supported `environment_policy` values:
- minimal
- sanitized_inherited
- repo_profile_declared

Supported `network_posture` values:
- deny
- read_only
- declared_by_tool
- allowlist_required

Supported `approval_class` values:
- auto_execute
- auto_if_reversible
- explicit_user_approval
- deny

## Invariants
- tools with `risk_class=high` must not use `approval_policy=auto_execute`
- tools with write side effects must declare rollback guidance or compensating action type
- every tool must emit required trace fields
- unclassified executable tool families must fail closed unless an explicit waiver is recorded
- execution evidence must include containment metadata and rollback metadata

## Non-Goals
- plugin marketplace definition
- provider-specific SDK implementation details
