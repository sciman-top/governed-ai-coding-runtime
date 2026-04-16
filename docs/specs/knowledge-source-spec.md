# Knowledge Source Spec

## Status
Draft

## Purpose
Define the contract for curated knowledge sources consumed by governed sessions.

## Required Fields
- source_id
- display_name
- source_kind
- location
- trust_tier
- freshness_policy
- owner
- access_policy
- serialization_format

## Optional Fields
- repo_scope
- tags
- cache_ttl_s
- precedence
- notes

## Enumerations
### source_kind
- file
- directory
- web_doc
- schema
- repo_map
- registry
- memory_bridge
- manual

### trust_tier
- authoritative
- reviewed
- reference
- untrusted

### access_policy
- read_only
- approved_read
- restricted

## Invariants
- `source_kind=memory_bridge` must not use `trust_tier=authoritative`
- authoritative sources must identify a stable owner and freshness policy
- knowledge sources may shape context but may not replace evidence, approval, or task state as system-of-record objects
- serialization format must be deterministic enough for replay or diffing

## Non-Goals
- embedding provider configuration
- vector storage implementation details
