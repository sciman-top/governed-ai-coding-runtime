# Repo Map And Context Shaping Spec

## Status
Draft

## Purpose
Define bounded repository mapping and context-shaping rules used to assemble repo-aware session context as a governed knowledge input.

## Required Fields
- strategy_id
- mode
- max_tokens
- ranking_signals
- include_rules
- exclude_rules
- serialization_format
- knowledge_source_refs
- review_status

## Optional Fields
- symbol_kinds
- fallback_files
- freshness_policy
- stop_conditions
- notes

## Enumerations
### mode
- none
- file_graph
- symbol_graph
- hybrid

### ranking_signals
- entrypoint
- import_degree
- test_proximity
- recent_change
- path_priority
- manual_boost

### serialization_format
- file_list
- symbol_outline
- markdown_map
- json_map

### review_status
- draft
- reviewed
- approved
- stale

## Invariants
- context shaping must stay within an explicit token budget
- exclusion rules must win over inclusion rules when both match the same target
- required governance files must remain present in the final artifact even when repo-local include/exclude overrides are tightened
- repo maps may prioritize context but may not bypass repo admission or policy enforcement
- `mode=none` must not emit ranked repository output
- repo-map strategies must point to reviewable `knowledge_source_refs` rather than acting as an implicit hidden agent behavior
- memory-like sources may inform ranking only when they remain non-authoritative and reviewable through linked knowledge-source records

## Effect Metrics
Repo-map artifacts should report at least:

- estimated token cost
- required governance file coverage
- file-selection accuracy
- clarification-reduction proxy or equivalent reviewable signal

## Non-Goals
- IDE-specific navigation behavior
- model-provider-specific prompt templates
- turning repo maps into an implicit memory product
