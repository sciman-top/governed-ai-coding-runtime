# Agent Adapter Contract Spec

## Status
Draft

## Purpose
Define how an AI coding product is admitted as an execution frontend without changing governance-kernel semantics.

The contract describes capabilities, not vendor identity. Codex CLI/App, Claude Code, IDE plugins, cloud coding workers, browser-driven tools, and future products should all map into this shape when possible.

## Required Fields
- adapter_id
- display_name
- product_family
- capability_surface
- lifecycle_status
- adapter_tier
- rollout_posture
- invocation_mode
- auth_ownership
- workspace_control
- event_visibility
- mutation_model
- continuation_model
- evidence_model
- supported_governance_modes
- minimum_required_runtime_controls
- governance_guarantees
- unsupported_capability_behavior

## Optional Fields
- command_template
- runtime_selection
- posture_resolution_order
- mcp_server_ref
- app_server_ref
- ide_bridge_ref
- browser_automation_ref
- output_schema_ref
- known_limitations
- recommended_default_mode
- compatibility_notes
- compatibility_signals

## Canonical Capability Surface
Every adapter contract must also declare a canonical `capability_surface` object. This is the host-capability shape that future operator, claim, adapter, and verification surfaces must expose when the runtime talks about live host posture.

### capability_surface required fields
- `host_family`
- `surface_class`
- `attach_mode`
- `adapter_tier`
- `degrade_reason`
- `verification_refs`
- `evidence_refs`

### capability_surface intent
- `product_family` remains the adapter or implementation identity already used by runtime internals.
- `capability_surface.host_family` is the claim-facing host-family identity used for posture statements and cross-host comparisons.
- `capability_surface.surface_class` expresses where the host surface lives (`terminal`, `desktop`, `ide`, `web`, `cloud_worker`, `browser_automation`, or `manual_handoff`).
- `capability_surface.attach_mode` expresses the continuity and execution-attachment posture that the runtime is actually claiming (`native_attach`, `process_bridge`, `manual_handoff`, or `import_only`).
- `capability_surface.degrade_reason` must be explicit whenever the declared attach mode or tier is weaker than the preferred or strongest posture. A `null` value is allowed only when no degradation is being claimed.
- `capability_surface.verification_refs` and `capability_surface.evidence_refs` make the declaration auditable instead of narrative-only. They may point to docs, artifacts, trials, or runtime-owned evidence locations, but they must not be omitted.

## Enumerations

### lifecycle_status
- experimental
- supported
- deprecated

### adapter_tier
- native_attach
- process_bridge
- manual_handoff

### rollout_posture.current_mode / target_mode
- observe
- advisory
- enforced

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

### runtime_selection.delegation_mode
- runtime_registry
- manual_only

### compatibility_signals.status
- full_support
- partial_support
- unsupported

### capability_surface.host_family
- codex_family
- claude_family
- antigravity_family
- gemini_legacy_bridge
- generic_family

### capability_surface.surface_class
- terminal
- desktop
- ide
- web
- cloud_worker
- browser_automation
- manual_handoff

### capability_surface.attach_mode
- native_attach
- process_bridge
- manual_handoff
- import_only

## Invariants
- adapter tier must be one of `native_attach`, `process_bridge`, or `manual_handoff`
- Agent adapters may not redefine task lifecycle states.
- Agent adapters may not weaken approval requirements for high-risk actions.
- Agent adapters may not change canonical verification gate order.
- User-owned upstream authentication, such as Codex CLI/App login, must remain outside platform credential ownership unless a separate explicit integration decision is accepted.
- If event visibility is weak, the runtime must compensate with stricter post-run diff, gate, and evidence checks or degrade the adapter mode.
- Unsupported capabilities must degrade explicitly rather than silently pretending full enforcement exists.
- runtime selection and fallback chain must be machine-readable when delegation is runtime-managed.
- governance guarantees must explain what the runtime can still honestly promise at the declared adapter tier
- rollout posture must make the current and target enforcement level machine-readable
- compatibility signals must describe the degrade behavior that preserves honest execution semantics when full support is absent
- managed workspace or managed worktree adapters must leave enough run-level evidence for the runtime status surface to project approvals, verification, and artifact links honestly
- `capability_surface` is the canonical host-capability declaration for operator, claim, adapter, and verification surfaces; older fields such as `product_family` or `invocation_mode` must not be treated as sufficient substitutes when the runtime makes live host claims
- missing `capability_surface.host_family`, `surface_class`, `attach_mode`, `adapter_tier`, `verification_refs`, or `evidence_refs` is fail-closed for claim-strengthening and operator posture surfaces
- historical certification alone must not be used as an implicit `verification_ref` or `evidence_ref` for a stronger current live-host claim

## Non-Goals
- Defining one universal agent protocol.
- Replacing upstream agent user interfaces.
- Owning all upstream agent authentication.
- Guaranteeing deep compatibility with every AI coding product in the MVP.
