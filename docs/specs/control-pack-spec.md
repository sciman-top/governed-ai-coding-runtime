# Control Pack Spec

## Status
Draft

## Purpose
Define the metadata contract for a reusable control pack.

A control pack is a versioned bundle of governance references that can be attached to a repo profile or runtime rollout without redefining kernel semantics.

## Scope
Control packs may reference:
- control registry entries
- hook contracts
- skill manifests
- knowledge sources
- verification gates
- eval suites
- provenance or attestation records

Control packs do not inline executable policy semantics. They bind existing kernel contracts into an auditable package.

## Required Fields
- schema_version
- pack_id
- display_name
- version
- owner
- lifecycle_status
- scope
- activation
- includes
- compatibility
- provenance

## Enumerations
### lifecycle_status
- draft
- active
- deprecated
- retired

### scope
- kernel
- repository
- organization

### activation.default_mode
- observe
- enforce
- advisory

## Invariants
- `pack_id` must be stable and version-independent.
- `version` must use semantic versioning.
- referenced controls, hooks, skills, knowledge sources, gates, and eval suites must point to separately governed artifacts.
- a control pack may tighten governance but must not weaken kernel guarantees.
- a pack activated in `enforce` mode must include at least one control reference.
- repo profile gate requirements must use the verification gate canonical names.
- every active pack must have provenance sufficient to identify its source material.

## Non-Goals
- replacing the control registry
- defining repository-specific command values
- embedding executable hook code
- creating a skill marketplace or promotion workflow
