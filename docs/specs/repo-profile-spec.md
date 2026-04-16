# Repo Profile Spec

## Status
Draft

## Purpose
Define the per-repository configuration inherited by governed sessions.

## Required Fields
- repo_id
- display_name
- primary_language
- repo_root_locator
- build_commands
- test_commands
- lint_commands
- typecheck_commands
- risk_defaults
- approval_defaults
- tool_allowlist
- path_policies
- branch_policy
- delivery_format

## Optional Fields
- repo_map_strategy
- quick_gate_commands
- full_gate_commands
- extra_eval_suites
- context_files
- reviewer_handoff_template

## Inheritance Model
1. platform defaults
2. repo profile inherited values
3. bounded repo override

## Override Rules
Repo profiles may override:
- command entrypoints
- timeouts
- allowed low-risk tools
- optional eval suites
- delivery templates

Repo profiles may not override:
- evidence minimum fields
- high-risk approval requirements
- control registry semantics
- rollback reference requirement

## Verification
A repo profile is valid only if:
- all required commands are present or explicitly marked not applicable
- all path policies compile into deterministic allow/deny checks
- quick and full gates have unambiguous command order
