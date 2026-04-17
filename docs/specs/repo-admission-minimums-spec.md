# Repo Admission Minimums Spec

## Status
Draft

## Purpose
Define the minimum checks a target repository must satisfy before it can enter the first governed AI coding trial slice.

## Required Inputs
- repository identifier
- repo profile reference
- working directory or checkout locator
- control pack reference
- allowed read-only tools
- path scope policy
- verification gate commands or explicit `gate_na` records

## Admission Checks
1. Repo profile validates against `schemas/jsonschema/repo-profile.schema.json`.
2. Control pack validates against `schemas/jsonschema/control-pack.schema.json`.
3. Path policy defines at least one allowed read scope.
4. Read-only tool references are declared in the repo profile or inherited control pack.
5. `build`, `test`, `contract_or_invariant`, and `hotspot_or_health_check` are either command-backed or have explicit `gate_na` records.
6. Repo overrides only tighten or extend kernel governance.

## Failure Behavior
- Missing repo profile: block startup.
- Invalid control pack: block startup.
- Missing path policy: block startup.
- Weakened gate semantics: block startup.
- Missing optional handoff hints: warn only.

## Non-Goals
- running the governed task
- mutating the target repository
- approving write-side tools
- creating runtime UI
