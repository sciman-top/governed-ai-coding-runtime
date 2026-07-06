# Governed AI Coding Runtime Schemas

## Purpose
This directory stores the machine-readable contract surface for the runtime:
- JSON Schemas under `schemas/jsonschema/`
- example instances under `schemas/examples/`
- runtime-consumable metadata under `schemas/control-packs/`
- the authoritative pairing catalog at `schemas/catalog/schema-catalog.yaml`

## Sync Rule
- `docs/specs/*` defines the human-readable contract meaning.
- `schemas/jsonschema/*` defines the machine-readable contract shape.
- `schemas/catalog/schema-catalog.yaml` is the authoritative pairing list.
- If you change one side, verify the other two in the same diff.

## Current Schema Families
- Governance and control packs:
  - `control-registry`, `control-pack`, `control-pack-inheritance-matrix`, `capability-portfolio-classifier`
- Repo, host, and repo-local runtime surfaces:
  - `repo-profile`, `repo-admission-minimums`, `agent-adapter-contract`, `runtime-operator-surface`
- Policy, interaction, and evidence:
  - `tool-contract`, `hook-contract`, `policy-decision`, `response-policy`, `risk-tier-approval-policy`, `verification-gates`, `evidence-bundle`, `provenance-and-attestation`, `waiver-and-exception`, `interaction-signal`, `interaction-evidence`
- Runtime flow and task semantics:
  - `task-lifecycle`, `teaching-budget`, `clarification-protocol`, `transition-stack-convergence`
- Knowledge, continuity, and controlled evolution:
  - `knowledge-source`, `knowledge-memory-lifecycle`, `agent-continuity-record`, `promotion-lifecycle`, `self-evolution-promotion-controller`, `learning-efficiency-metrics`, `controlled-improvement-proposal`, `core-principles`, `core-principle-change-proposal`, `core-principle-change-manifest`, `core-principle-change-report`
- Skill and governed rollout support:
  - `skill-manifest`

## Examples And Runtime Metadata
- `examples/README.md` describes the example-instance layout.
- `control-packs/minimum-governance-kernel.control-pack.json` is the current checked-in runtime-consumable pack surface.
- Example instances should stay intentionally minimal while remaining valid against their matching schemas.

## Verification
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```
