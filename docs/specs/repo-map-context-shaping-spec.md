# Repo Map And Context Shaping Spec

## Status
Draft

## Purpose
Define bounded repository mapping and context-shaping rules used to assemble repo-aware session context.

## Required Fields
- strategy_id
- mode
- max_tokens
- ranking_signals
- include_rules
- exclude_rules
- serialization_format

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

## Invariants
- context shaping must stay within an explicit token budget
- exclusion rules must win over inclusion rules when both match the same target
- repo maps may prioritize context but may not bypass repo admission or policy enforcement
- `mode=none` must not emit ranked repository output

## Non-Goals
- IDE-specific navigation behavior
- model-provider-specific prompt templates
