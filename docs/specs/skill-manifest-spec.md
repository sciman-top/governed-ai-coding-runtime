# Skill Manifest Spec

## Status
Draft

## Purpose
Define portable metadata for reusable skills that can be enabled inside governed sessions.

## Required Fields
- skill_id
- display_name
- version
- description
- entrypoint
- input_modes
- risk_tier
- capabilities
- provenance
- compatibility

## Optional Fields
- default_enabled
- requires_approval
- repo_scopes
- tool_dependencies
- knowledge_dependencies
- tags
- notes

## Enumerations
### input_modes
- prompt_only
- file_context
- structured_input
- mcp
- shell
- browser
- mixed

### risk_tier
- low
- medium
- high

## Invariants
- high-risk skills must not be enabled by default
- skills that require shell, browser, or MCP access must declare matching dependencies
- provenance metadata must identify the source location and version or digest of the skill package
- compatibility rules must identify the minimum kernel version or contract family version required

## Non-Goals
- skill marketplace workflow
- billing or provider packaging rules
