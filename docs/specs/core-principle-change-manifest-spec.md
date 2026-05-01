# Core Principle Change Manifest Spec

## Status
Draft

## Purpose
Define the audit manifest produced when a reviewed core-principle change proposal is materialized as evidence files.

## Required Fields
- schema_version
- generated_on
- source_command
- operation_paths
- guard
- rollback

## Optional Fields
- existing_file_behavior
- operation_artifacts

## Enumerations
### existing_file_behavior
- overwrite_same_candidate
- fail_if_exists

## Invariants
- all operation paths must stay under `docs/change-evidence/core-principle-change-*`
- manifests may reference proposal, patch, or report JSON artifacts only
- manifest creation must not mutate active core-principle policy, specs, verifier code, skills, target repos, push state, or merge state
- when present, operation artifact hashes must be SHA-256 hex strings
- rollback must describe how to delete generated evidence files without affecting active policy

## Non-Goals
- active implementation apply
- automatic policy edit
- automatic remote synchronization
