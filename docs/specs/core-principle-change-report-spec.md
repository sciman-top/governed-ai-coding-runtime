# Core Principle Change Dry-Run Report Spec

## Status
Draft

## Purpose
Define an optional audit-only dry-run report for core-principle change candidates. Report writing is explicit and separate from proposal/manifest materialization.

## Required Fields
- schema_version
- generated_on
- mode
- source_command
- proposal_id
- proposal_path
- manifest_path
- operations
- guard
- rollback

## Invariants
- `mode` must be `dry_run_report`
- report writing must not write proposal or manifest artifacts
- report writing must not mutate active core-principle policy, specs, verifier code, skills, target repos, push state, or merge state
- each operation must include its planned path, risk, content hash, overwrite behavior, and pre-write existence state
- rollback must describe how to delete the report without affecting proposal, manifest, or active policy files

## Non-Goals
- replacing explicit proposal write confirmation
- active implementation apply
- automatic policy edit
