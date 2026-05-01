# Knowledge Memory Lifecycle Spec

## Status
Draft

## Purpose
Define the governed lifecycle that turns AI coding experience into reviewable knowledge candidates, pattern candidates, memory records, and retirement records without granting hidden authority to memory.

## Required Fields
- lifecycle_id
- as_of
- source_policy_ref
- promotion_requirements
- usefulness_filter
- knowledge_candidates
- pattern_candidates
- memory_records
- retirement_records
- rollback_ref

## Promotion Requirements
- source evidence must be attached before a knowledge or pattern candidate can be promoted
- verification references must be attached before a knowledge or pattern candidate can be promoted
- human review remains mandatory before any downstream executable asset is enabled

## Usefulness Filter
The lifecycle must score candidate usefulness with explicit, reviewable dimensions:

- recurrence
- transferability
- verification strength
- freshness
- blast-radius reduction

## Memory Record Requirements
Each memory record must include:

- scope
- provenance
- confidence
- expiry
- retrieval evidence

## Retirement Requirements
- stale or low-value knowledge must be able to move to a retired state
- retirement must preserve audit history
- retirement must not delete active evidence history as part of the review record

## Invariants
- experience extraction remains evidence-backed and non-mutating by default
- memory records may inform later retrieval, but they may not become hidden system-of-record truth
- promotion decisions must remain traceable through source evidence, verification references, review, and rollback
- retirement records must keep archive references so future re-evaluation is possible

## Non-Goals
- vector database implementation
- hidden personalization state
- autonomous policy or skill enablement from memory records
