# Knowledge Source Spec

## Status
Draft

## Purpose
Define the contract for curated knowledge sources consumed by governed sessions, including trust, freshness, precedence, and drift posture.

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
- review_status
- precedence
- drift_policy

## Optional Fields
- repo_scope
- tags
- cache_ttl_s
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

### review_status
- draft
- reviewed
- approved
- stale

### drift_policy.mode
- fixed
- review_on_change
- ttl_refresh
- manual_refresh

## Invariants
- `source_kind=memory_bridge` must not use `trust_tier=authoritative`
- authoritative sources must identify a stable owner, freshness policy, and reviewable precedence
- knowledge sources may shape context but may not replace evidence, approval, or task state as system-of-record objects
- serialization format must be deterministic enough for replay or diffing
- stale or untrusted knowledge sources must remain visible as degraded inputs instead of silently inheriting authoritative posture

## Non-Goals
- embedding provider configuration
- vector storage implementation details
- allowing memory-like sources to become hidden runtime truth
