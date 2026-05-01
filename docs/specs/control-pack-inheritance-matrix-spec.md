# Control Pack Inheritance Matrix Spec

## Status
Draft

## Purpose
Define a machine-readable matrix that separates:
- unified governance owned by the hub control pack
- target-repo fields inherited through baseline materialization
- repo-local override points that remain bounded and typed
- forbidden override surfaces that must never be delegated to repo profiles or emitted light packs

## Required Fields
- `schema_version`
- `matrix_id`
- `control_pack_ref`
- `target_baseline_ref`
- `repo_profile_schema_ref`
- `light_pack_ref`
- `unified_governance`
- `target_inherit`
- `target_override`
- `forbidden_override`

## Unified Governance Entries
Each entry must declare:
- `field_path`
- `reason`
- `validation_rule`

These entries identify kernel-owned fields that target repos must not redefine through profile materialization or light-pack emission.

## Target Inherit Entries
Each entry must declare:
- `profile_field`
- `baseline_field`
- `control_pack_reference`
- `schema_path`
- `reason`

These entries identify target-repo fields that the hub is allowed to materialize into repo profiles through `required_profile_overrides`.

## Target Override Entries
Each entry must declare:
- `profile_field`
- `schema_path`
- `override_rule`
- `reason`

These entries identify repo-local fields that remain under target-repo ownership, but only within explicit typed and bounded rules.

Allowed `override_rule` values:
- `bounded_to_schema`
- `strengthen_only`
- `additive_only`
- `repo_local_only`
- `must_remain_true`

## Forbidden Override Entries
Each entry must declare:
- `surface`
- `blocked_field_names`
- `reason`

Optional fields:
- `blocked_in`

These entries identify semantic surfaces that must not appear as override fields in baseline-distributed profiles or emitted light packs.

## Verification
The matrix is valid only if:
- every inherited baseline field is listed exactly once in `target_inherit`
- every inherited or override field resolves to an explicit path in `repo-profile.schema.json`
- unified governance fields exist in the hub control pack and do not appear as repo-profile or light-pack override payload
- forbidden override fields are absent from baseline materialization, repo-local light packs, and any other declared emission surface
- the verifier reports drift through the existing contract verification entrypoint
