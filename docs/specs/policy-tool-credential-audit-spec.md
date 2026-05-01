# Policy Tool Credential Audit Spec

## Status
Draft

## Purpose
Define the fail-closed audit boundary that normalizes tool identity, credential scope, policy basis, host actions, and target-repo override limits without turning the repository into a standalone IAM, gateway, or credential-broker product.

## Required Fields
- schema_version
- audit_id
- status
- reviewed_on
- verification_command
- report_output_ref
- fail_closed_defaults
- entries
- target_repo_override_entries
- rollback_ref

## Tool Entry Fields
Each audit entry must include:
- id
- tool_name
- host_surface
- registry_refs
- credential_scope
- policy_basis_refs
- evidence_refs
- decision
- remediation

## Credential Scope Fields
Each `credential_scope` object must include:
- scope_id
- scope_kind
- resource_boundary
- owner_boundary
- allowed_actions

## Target-Repo Override Fields
Each override entry must include:
- surface_id
- declared_rule
- limitation_note
- basis_refs

Allowed `declared_rule` values:
- tighten_only
- platform_limit_only

## Invariants
- unknown tools must fail closed according to `fail_closed_defaults.unknown_tool`
- overbroad credential scopes must fail closed according to `fail_closed_defaults.overbroad_credential_scope`
- missing policy basis must fail closed according to `fail_closed_defaults.missing_policy_basis`
- every audit output must identify tool, scope, policy basis, decision, evidence, and remediation
- target-repo overrides in this audit boundary may only tighten policy or declare platform limitations
- Codex and Claude Code remain cooperation hosts; credential ownership stays user-owned unless a later bounded contract proves otherwise
- local Codex/Claude/Gemini user configuration may preserve operator convenience settings only when deterministic guard evidence remains present
- plaintext local login tokens are accepted operator-owned state only when credential-bearing config files are denied to agents and are not synchronized into repositories
- MCP server synchronization is acceptable only when credentials remain indirect through environment-variable references rather than expanded token values

## Non-Goals
- full IAM
- credential brokering
- centralized enterprise gateway enforcement
- automatic target-repo policy mutation
