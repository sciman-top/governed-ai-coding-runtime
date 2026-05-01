# Control Pack Spec

## Status
Draft

## Purpose
Define the executable contract for a reusable control pack.

A control pack is a versioned bundle of governance references that can be attached to a repo profile or runtime rollout without redefining kernel semantics. The pack must carry runnable or verifiable execution references, explicit kernel-versus-target ownership boundaries, and a controlled materialization path into runtime-consumable pack assets.

## Scope
Control packs may reference:
- control registry entries
- hook contracts
- skill manifests
- knowledge sources
- verification gates
- eval suites
- provenance or attestation records
- memory and evidence review flows
- rollback runbooks or rollback commands

Control packs do not inline executable policy semantics. They bind existing kernel contracts into an auditable package with execution references that prove how each surface is checked or invoked.

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
- field_ownership
- execution_contract
- materialization
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
- `execution_contract` must cover `policy`, `gate`, `hook`, `eval`, `workflow`, `skill`, `knowledge`, `memory`, `evidence`, and `rollback`.
- each execution-contract entry must include a `source_ref`, `runtime_ref`, `verification_ref`, and `mode`.
- a control pack fails closed when any required execution reference or materialization reference is missing.
- a control pack may tighten governance but must not weaken kernel guarantees.
- a pack activated in `enforce` mode must include at least one control reference.
- repo profile gate requirements must use the verification gate canonical names.
- `field_ownership.unified_kernel_fields` and `field_ownership.target_repo_input_fields` must be explicit, non-overlapping, and sufficient to distinguish kernel-owned fields from target-repo supplied fields.
- `materialization` must identify the source template, generated runtime-consumable pack path, apply command, and verification command.
- every active pack must have provenance sufficient to identify its source material.

## Non-Goals
- replacing the control registry
- defining target-repo-specific command values inside the pack
- embedding executable hook code
- creating a skill marketplace or promotion workflow
