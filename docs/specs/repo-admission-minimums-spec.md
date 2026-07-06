# Repo Admission Minimums Spec

## Status
Draft

## Purpose
Define the minimum machine-readable admission and compatibility signals a repository-local governed runtime surface must satisfy before it can enter repo-local verification or host-side governance flows.

## Required Inputs
- repository identifier
- repo profile reference
- working directory or checkout locator
- control pack reference
- allowed read-only tools
- path scope policy
- verification gate commands or explicit `gate_na` records
- knowledge readiness declaration or explicit `not_ready` signal
- eval-trace policy reference or explicit `not_ready` signal
- repo-local runtime status or operator-surface readiness result
- repo override summary

## Admission Checks
1. Repo profile validates against `schemas/jsonschema/repo-profile.schema.json`.
2. Control pack validates against `schemas/jsonschema/control-pack.schema.json`.
3. Path policy defines at least one allowed read scope.
4. Read-only tool references are declared in the repo profile or inherited control pack.
5. `build`, `test`, `contract_or_invariant`, and `hotspot_or_health_check` are either command-backed or have explicit `gate_na` records.
6. Repo-local runtime readiness is recorded as `healthy`, `warning`, or `blocked` instead of being left implicit.
7. Knowledge readiness is recorded as `ready`, `warning`, or `not_ready`.
8. Eval readiness is recorded as `ready`, `warning`, or `not_ready`.
9. Repo overrides may only tighten or extend kernel governance and must never weaken kernel guarantees.

## Compatibility Signal Model
Admission must emit one or more compatibility signals with:
- `signal_id`
- `signal_kind`
- `status`
- `reason`
- `blocking`
- `evidence_refs`

### signal_kind
- `core_contract`
- `knowledge_readiness`
- `eval_readiness`
- `runtime_surface_readiness`
- `override_safety`
- `adapter_compatibility`

### status
- `accept`
- `warn`
- `block`

### Signal Semantics
- `accept` means the repo can enter the governed flow without additional admission work.
- `warn` means the repo is locally usable but has visible follow-up work such as missing knowledge curation, partial eval coverage, or degraded runtime/operator readiness.
- `block` means the repo cannot enter the governed flow until the underlying contract, readiness, or override problem is resolved.

## Failure Behavior
- Missing repo profile: block startup.
- Invalid control pack: block startup.
- Missing path policy: block startup.
- Weakened gate semantics: block startup.
- Missing knowledge readiness declaration: warn only.
- Missing eval readiness declaration: warn only.
- Missing or stale repo-local runtime readiness: block startup.
- Missing optional handoff hints: warn only.

## Invariants
- Admission must be able to describe repo state through explicit `accept`, `warn`, or `block` outputs instead of relying on undocumented operator judgment.
- Knowledge readiness and eval readiness may warn, but they cannot silently default to `ready`.
- Runtime surface readiness may warn only for explicitly degraded but still inspectable states; missing or stale local readiness must block.
- Repo overrides may add stricter local behavior but must never downgrade a `block` to `warn` or `accept`.
- Compatibility signals must stay machine-readable so later rollout, reuse, and proposal tasks can consume them consistently.

## Non-Goals
- running the governed task
- mutating an external repository
- approving write-side tools
- creating runtime UI
