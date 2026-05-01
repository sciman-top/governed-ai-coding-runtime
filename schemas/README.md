# Governed AI Coding Runtime Schemas

## Purpose
Machine-readable schema drafts and example instances for the platform's core governance contracts.

## JSON Schema Drafts
- `jsonschema/control-registry.schema.json`
- `jsonschema/control-pack.schema.json`
- `jsonschema/capability-portfolio-classifier.schema.json`
- `jsonschema/repo-profile.schema.json`
- `jsonschema/repo-admission-minimums.schema.json`
- `jsonschema/tool-contract.schema.json`
- `jsonschema/agent-adapter-contract.schema.json`
- `jsonschema/hook-contract.schema.json`
- `jsonschema/skill-manifest.schema.json`
- `jsonschema/knowledge-source.schema.json`
- `jsonschema/waiver-and-exception.schema.json`
- `jsonschema/provenance-and-attestation.schema.json`
- `jsonschema/repo-map-context-shaping.schema.json`
- `jsonschema/risk-tier-approval-policy.schema.json`
- `jsonschema/task-lifecycle.schema.json`
- `jsonschema/evidence-bundle.schema.json`
- `jsonschema/verification-gates.schema.json`
- `jsonschema/eval-trace-policy.schema.json`

## Catalog
- `catalog/schema-catalog.yaml`

## Runtime-Consumable Metadata
- `control-packs/README.md`
- `control-packs/minimum-governance-kernel.control-pack.json`

## Example Instances
- `examples/README.md`
- `examples/control-pack/minimum-governance-kernel.example.json`
- `examples/capability-portfolio-classifier/default-governance-hub.example.json`
- `examples/hook-contract/pre-write-path-guard.example.json`
- `examples/skill-manifest/repo-map-audit.example.json`
- `examples/knowledge-source/docs-index-authoritative.example.json`
- `examples/waiver-and-exception/temporary-gate-waiver.example.json`
- `examples/provenance-and-attestation/schema-bundle-release.example.json`
- `examples/repo-map-context-shaping/hybrid-default.example.json`
- `examples/repo-profile/python-service.example.json`
- `examples/repo-profile/typescript-webapp.example.json`

## Notes
- These are initial drafts aligned with `docs/specs/*`.
- They define contract shape, not storage or transport implementation.
- Example instances are intentionally minimal and should validate against their matching schema.
- The control-pack example is metadata only; it is not an executable runtime control pack yet.
- `schemas/control-packs/` is the stable location for runtime-consumable metadata references derived from the validated examples.
- They should be revised once the first runtime package exists.
