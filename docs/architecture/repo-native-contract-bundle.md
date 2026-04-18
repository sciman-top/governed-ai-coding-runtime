# Repo-Native Contract Bundle

## Purpose
Define how the hybrid final state turns this repository's source-of-truth authoring structure into a runtime-consumable attachment surface for target repositories.

This document fixes one boundary:

- the repo-native contract bundle is an attachment and packaging boundary
- it is not a replacement for the governance kernel
- it is not a replacement for this repository's authoring structure under `docs/`, `schemas/`, and `packages/contracts/`

## Decision
The final product shape is:

`Repo-native Contract Bundle + Host Adapters + Policy Decision Interface + Verification and Delivery Plane`

For this repository, that means:

1. `docs/` remains the human-readable source of truth for strategy, architecture, specs, product semantics, and plans.
2. `schemas/` remains the machine-readable source of truth for stable contract drafts and examples.
3. `packages/contracts/` remains the executable local kernel baseline for contract-aligned runtime primitives.
4. The repo-native contract bundle is a materialized, runtime-consumable attachment surface derived from those stable inputs.

## Source-Of-Truth Inputs

### Human-readable inputs
- strategy, product, and architecture documents in `docs/`
- normative contract specs in `docs/specs/`
- runbooks and recovery guidance in `docs/runbooks/`

### Machine-readable inputs
- schema drafts in `schemas/jsonschema/`
- schema catalog in `schemas/catalog/schema-catalog.yaml`
- example payloads in `schemas/examples/`
- reference control packs in `schemas/control-packs/`

### Executable kernel inputs
- runtime contract helpers in `packages/contracts/src/governed_ai_coding_runtime_contracts/`
- gate and operator entrypoints in `scripts/`

These inputs are authored here. The bundle is derived from them for target-repo attachment and runtime consumption.

## Runtime Bundle Outputs
The bundle should contain only the repo-local declarations that the runtime needs to attach honestly to a target repository.

### Required bundle contents
- repo profile
- gate command mapping
- write policy defaults
- approval policy defaults
- adapter preference or capability hints
- policy-decision output references or expected contract version
- evidence, handoff, and rollback reference targets
- optional onboarding metadata needed to bind the repo to a machine-local runtime

### Explicit non-contents
- task store
- approval ledger state
- artifact payloads
- replay payloads
- long-lived execution worker code
- copied governance kernel logic

## Placement Rules

### Repo-local declarations
Keep in the attached repository:
- repo-scoped policy inputs
- gate command declarations
- adapter preference hints
- stable references to evidence or rollback destinations

These files should stay light, portable, and reviewable as repository metadata.

### Machine-local runtime state
Keep outside the target repository:
- task and run state
- approval state
- evidence payloads
- artifact payloads
- replay bundles
- operator snapshots
- adapter session state

This preserves one durable runtime per machine or workspace environment instead of copying mutable state into every target repository.

## Bundle Materialization Modes

### 1. Authoring mode
Inside this repository, humans and agents edit `docs/`, `schemas/`, and `packages/contracts/`.

### 2. Attachment mode
For a target repository, the runtime generates or validates a repo-native bundle or light pack from the stable source inputs.

### 3. Verification mode
Local runtime checks and CI both consume the same declared contract shape, even if they materialize it differently.

The key rule is that authoring structure and runtime bundle shape are related, but not identical.

## Mapping To Existing Contracts
| Bundle item | Existing source-of-truth inputs |
|---|---|
| repo profile | `docs/specs/repo-profile-spec.md`, `schemas/jsonschema/repo-profile.schema.json` |
| gate command mapping | `docs/specs/verification-gates-spec.md`, `schemas/jsonschema/verification-gates.schema.json`, `scripts/verify-repo.ps1` |
| write policy defaults | `docs/product/write-policy-defaults.md`, `packages/contracts/src/governed_ai_coding_runtime_contracts/write_policy.py` |
| approval policy defaults | `docs/specs/risk-tier-and-approval-spec.md`, `packages/contracts/src/governed_ai_coding_runtime_contracts/approval.py` |
| adapter capabilities and preference | `docs/specs/agent-adapter-contract-spec.md`, `schemas/jsonschema/agent-adapter-contract.schema.json`, `docs/product/adapter-degrade-policy.md` |
| policy-decision outputs | `docs/specs/policy-decision-spec.md`, `schemas/jsonschema/policy-decision.schema.json`, `packages/contracts/src/governed_ai_coding_runtime_contracts/policy_decision.py` |
| evidence and handoff references | `docs/specs/evidence-bundle-spec.md`, `packages/contracts/src/governed_ai_coding_runtime_contracts/evidence.py`, `packages/contracts/src/governed_ai_coding_runtime_contracts/delivery_handoff.py` |
| rollback references | `docs/runbooks/control-rollback.md`, task or handoff records emitted by runtime primitives |

## Local And CI Consumption

### Local runtime consumption
The local runtime can:
- validate bundle inputs before binding a target repo
- load repo policy and adapter hints before session attachment
- emit evidence and handoff aligned to the declared bundle contract

### CI consumption
CI can:
- validate bundle declarations and schema/spec pairings
- run declared verification gates
- confirm that evidence and delivery references remain compatible with the declared contract

Local and CI should use the same contract semantics even if one path runs inside an interactive session and the other runs in non-interactive automation.

## Relationship To Current Baseline
The current repository still runs a local baseline with repo-root `.runtime/` state and CLI-first operator entrypoints.

That baseline remains valid for:
- bootstrap
- smoke verification
- recovery
- packaging
- contract development

It must not be confused with the final target-repo attachment boundary. The repo-native contract bundle is the bridge from the current baseline to the hybrid final state.

## Acceptance Boundary
This document is complete only when the following remain true together:
- the bundle is described as a runtime-consumable output or attachment surface
- source-of-truth authoring remains in `docs/`, `schemas/`, and `packages/contracts/`
- repo-local declarations stay light
- mutable runtime state stays machine-local
- local and CI are both described as consumers of the same contract semantics

## Related Documents
- [Generic Target-Repo Attachment Blueprint](./generic-target-repo-attachment-blueprint.md)
- [Local Baseline To Hybrid Final-State Migration Matrix](./local-baseline-to-hybrid-final-state-migration-matrix.md)
- [Governed AI Coding Runtime Target Architecture](./governed-ai-coding-runtime-target-architecture.md)
- [Governance Runtime Strategy Alignment Plan](../plans/governance-runtime-strategy-alignment-plan.md)
