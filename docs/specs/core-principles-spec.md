# Core Principles Spec

## Status
Draft

## Purpose
Define the non-negotiable project principles that must be enforceable by repository verification, not only by agent-readable prose.

## Required Fields
- schema_version
- policy_id
- status
- principles
- capability_portfolio_outcomes
- outer_ai_evolution_controls
- required_doc_refs
- forbidden_active_patterns
- evidence_refs
- rollback_ref

## Principle Requirements
Every principle must include:

- principle_id
- category
- summary
- required
- enforcement_level
- machine_gate
- rollback_ref

## Required Principle Set
- efficiency_first
- codex_claude_cooperation_hosts
- no_host_competition
- claude_third_party_provider_boundary
- external_mechanism_selective_absorption
- governance_hub_reusable_contract_final_state
- controlled_evolution_portfolio_lifecycle
- automation_first_outer_ai_intelligent_evolution
- no_automatic_mutation_without_review
- evidence_and_rollback_required
- context_budget_and_instruction_minimalism
- least_privilege_tool_credential_boundary
- measured_effect_feedback_over_claims
- hard_gate_order

## Capability Portfolio Outcomes
Controlled evolution must classify both proposed mechanisms and existing capabilities with one of:

- add
- keep
- improve
- merge
- deprecate
- retire
- delete_candidate

## Outer AI Evolution Controls
Automation-first, outer-AI-assisted, gate-controlled evolution is a required core posture.

The project may automatically trigger outer AI for intelligent review, experience extraction, knowledge and skill candidate generation, evolution proposal generation, candidate evaluation, and effect feedback analysis.

The project must not let outer AI output become effective policy, enabled skills, target-repo sync, push, merge, reviewed evidence deletion, or active gate deletion without the configured risk gate, machine gate, evidence, rollback, and human review boundary for high-risk work.

The policy must declare:

- automatic_trigger_allowed
- allowed_automatic_actions
- forbidden_automatic_effective_actions
- required_controls

## Invariants
- Codex and Claude Code are cooperation hosts, not products this repository should compete with.
- Claude Code support assumes local third-party Anthropic-compatible provider usage such as GLM or DeepSeek, not official subscription entitlement.
- Hermes Agent, OpenHands, SWE-agent, Letta, Mem0, LangGraph, Aider, Cline, OPA, MCP gateways, and similar projects are mechanism sources only.
- The best engineering final state is Governance Hub + Reusable Contract + Controlled Evolution loop + outer AI intelligent review/generation capability.
- Context budget and instruction minimalism are first-class constraints: core rules, instruction files, repo maps, and memory artifacts must stay bounded, concise, and verifiable.
- Tool permissions, sandbox scope, credentials, provider secrets, mounted paths, and network access must be least-privilege and auditable.
- Capability completion claims must be backed by fresh target-run evidence, eval traces, effect feedback, verification commands, and rollback paths.
- Controlled evolution must evaluate additions, retention, improvement, merge, deprecation, retirement, and deletion candidates.
- Deterministic governance automation should run inside this project; outer AI may be automatically triggered for high-intelligence analysis and proposal generation, but effective changes remain gate-controlled.
- Automatic policy mutation, skill enablement, target-repo sync, push, and merge remain disallowed unless a later reviewed implementation explicitly changes the guard.
- Documentation claims must not outgrow implementation, evidence, and rollback.
- Deletion must be proposal-backed, path-bounded, rollbackable, and must not remove reviewed policy, enabled skills, active gates, target-repo declarations, or evidence history automatically.

## Non-Goals
- replacing Codex or Claude Code host UI
- requiring official Claude subscription state
- adopting external agent product identity
- treating natural-language rules as sufficient enforcement
- letting outer AI bypass structured candidates, risk gates, evidence, and rollback
