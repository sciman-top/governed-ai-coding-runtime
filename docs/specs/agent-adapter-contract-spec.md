# Agent Adapter Contract Spec

## Status
Draft

## Purpose
Define how an AI coding product is admitted as an execution frontend without changing governance-kernel semantics.

The contract describes capabilities, not vendor identity. Codex CLI/App, Claude Code, OpenClaw, Hermes, IDE plugins, cloud coding workers, browser-driven tools, and future products should all map into this shape when possible.

## Required Fields
- adapter_id
- display_name
- product_family
- lifecycle_status
- invocation_mode
- auth_ownership
- workspace_control
- event_visibility
- mutation_model
- continuation_model
- evidence_model
- supported_governance_modes
- minimum_required_runtime_controls
- unsupported_capability_behavior

## Optional Fields
- command_template
- mcp_server_ref
- app_server_ref
- ide_bridge_ref
- browser_automation_ref
- output_schema_ref
- known_limitations
- recommended_default_mode
- compatibility_notes

## Enumerations

### lifecycle_status
- experimental
- supported
- deprecated

### invocation_mode
- interactive_cli
- non_interactive_cli
- mcp
- app_server
- ide_bridge
- cloud_agent
- browser_ui
- manual_handoff

### auth_ownership
- user_owned_upstream_auth
- service_owned_auth
- delegated_token
- unsupported

### workspace_control
- managed_worktree
- managed_workspace
- upstream_sandbox
- external_workspace
- read_only
- unknown

### event_visibility
- structured_jsonl
- mcp_events
- app_protocol_events
- logs_only
- transcript_only
- none

### mutation_model
- direct_workspace_write
- patch_output
- git_diff
- pull_request
- handoff_only
- read_only

### continuation_model
- resume_id
- fork_id
- session_id
- stateless
- manual

### evidence_model
- structured_trace
- command_log
- transcript
- diff_artifact
- external_artifact
- manual_summary

### supported_governance_modes
- observe_only
- advisory
- enforced
- strict

### unsupported_capability_behavior
- fail_closed
- degrade_to_observe_only
- degrade_to_advisory
- degrade_to_manual_handoff

## Invariants
- Agent adapters may not redefine task lifecycle states.
- Agent adapters may not weaken approval requirements for high-risk actions.
- Agent adapters may not change canonical verification gate order.
- User-owned upstream authentication, such as Codex CLI/App login, must remain outside platform credential ownership unless a separate explicit integration decision is accepted.
- If event visibility is weak, the runtime must compensate with stricter post-run diff, gate, and evidence checks or degrade the adapter mode.
- Unsupported capabilities must degrade explicitly rather than silently pretending full enforcement exists.

## Non-Goals
- Defining one universal agent protocol.
- Replacing upstream agent user interfaces.
- Owning all upstream agent authentication.
- Guaranteeing deep compatibility with every AI coding product in the MVP.
