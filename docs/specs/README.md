# Specs Index

## Purpose
This directory holds the normative contract descriptions that the schema drafts in `schemas/jsonschema/` mirror.

## Contract Families

### Governance kernel
- [Control Registry Spec](./control-registry-spec.md)
- [Control Pack Spec](./control-pack-spec.md)
- [Risk Tier And Approval Spec](./risk-tier-and-approval-spec.md)
- [Task Lifecycle And State Machine Spec](./task-lifecycle-and-state-machine-spec.md)
- [Verification Gates Spec](./verification-gates-spec.md)
- [Evidence Bundle Spec](./evidence-bundle-spec.md)
- [Eval And Trace Grading Spec](./eval-and-trace-grading-spec.md)
- [Waiver And Exception Spec](./waiver-and-exception-spec.md)
- [Provenance And Attestation Spec](./provenance-and-attestation-spec.md)

### Repo and execution inputs
- [Repo Admission Minimums Spec](./repo-admission-minimums-spec.md)
- [Repo Profile Spec](./repo-profile-spec.md)
- [Tool Contract Spec](./tool-contract-spec.md)
- [Hook Contract Spec](./hook-contract-spec.md)
- [Knowledge Source Spec](./knowledge-source-spec.md)
- [Repo Map And Context Shaping Spec](./repo-map-context-shaping-spec.md)
- [Skill Manifest Spec](./skill-manifest-spec.md)

### Agent compatibility
- [Agent Adapter Contract Spec](./agent-adapter-contract-spec.md)

## Reading Order
1. [Task Lifecycle And State Machine Spec](./task-lifecycle-and-state-machine-spec.md)
2. [Risk Tier And Approval Spec](./risk-tier-and-approval-spec.md)
3. [Verification Gates Spec](./verification-gates-spec.md)
4. [Evidence Bundle Spec](./evidence-bundle-spec.md)
5. [Repo Profile Spec](./repo-profile-spec.md)
6. [Tool Contract Spec](./tool-contract-spec.md)
7. [Agent Adapter Contract Spec](./agent-adapter-contract-spec.md)
8. Remaining specs by the contract family you are changing

## Pairing Rule
- `docs/specs/*` defines human-readable semantics.
- `schemas/jsonschema/*` defines the machine-readable draft.
- If one side changes, the matching schema/spec and `schemas/catalog/schema-catalog.yaml` must be checked together.
