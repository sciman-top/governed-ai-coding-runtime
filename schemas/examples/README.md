# Governed AI Coding Runtime Example Instances

## Purpose
Provide minimal but realistic JSON instances that exercise the repository's current governance schemas.

## Layout
- `hook-contract/`: hook contract examples
- `skill-manifest/`: skill manifest examples
- `knowledge-source/`: knowledge source examples
- `waiver-and-exception/`: waiver record examples
- `provenance-and-attestation/`: provenance and attestation examples
- `controlled-improvement-proposal/`: controlled proposal pipeline examples
- `repo-map-context-shaping/`: repo-map strategy examples
- `repo-profile/`: sample target-repository profiles
- `control-pack/`: sample control-pack metadata
- `policy-decision/`: policy decision examples
- `agent-adapter-contract/`: sample adapter posture examples
- `interaction-signal/`: observable interaction trigger examples
- `response-policy/`: bounded response policy examples
- `teaching-budget/`: explanation and clarification budget examples
- `interaction-evidence/`: interaction-trace evidence examples
- `learning-efficiency-metrics/`: bounded interaction metrics examples

## Example Files
- `control-pack/minimum-governance-kernel.example.json`
- `hook-contract/pre-write-path-guard.example.json`
- `skill-manifest/repo-map-audit.example.json`
- `knowledge-source/docs-index-authoritative.example.json`
- `waiver-and-exception/temporary-gate-waiver.example.json`
- `provenance-and-attestation/schema-bundle-release.example.json`
- `controlled-improvement-proposal/policy-rollout-review-proposal.example.json`
- `repo-map-context-shaping/hybrid-default.example.json`
- `repo-profile/python-service.example.json`
- `repo-profile/typescript-webapp.example.json`
- `repo-profile/target-repo-fast-full-template.example.json`
- `policy-decision/escalate-write.example.json`
- `agent-adapter-contract/manual-handoff.example.json`
- `agent-adapter-contract/process-bridge.example.json`
- `interaction-signal/default-bugfix-gap.example.json`
- `response-policy/guided-clarify.example.json`
- `teaching-budget/default-runtime.example.json`
- `interaction-evidence/checklist-first-bugfix.example.json`
- `learning-efficiency-metrics/baseline.example.json`

## Validation
Each example should validate against its matching schema:

```powershell
Get-Content -Raw 'schemas/examples/control-pack/minimum-governance-kernel.example.json' |
  Test-Json -SchemaFile 'schemas/jsonschema/control-pack.schema.json'

Get-Content -Raw 'schemas/examples/hook-contract/pre-write-path-guard.example.json' |
  Test-Json -SchemaFile 'schemas/jsonschema/hook-contract.schema.json'

Get-Content -Raw 'schemas/examples/skill-manifest/repo-map-audit.example.json' |
  Test-Json -SchemaFile 'schemas/jsonschema/skill-manifest.schema.json'

Get-Content -Raw 'schemas/examples/knowledge-source/docs-index-authoritative.example.json' |
  Test-Json -SchemaFile 'schemas/jsonschema/knowledge-source.schema.json'

Get-Content -Raw 'schemas/examples/waiver-and-exception/temporary-gate-waiver.example.json' |
  Test-Json -SchemaFile 'schemas/jsonschema/waiver-and-exception.schema.json'

Get-Content -Raw 'schemas/examples/provenance-and-attestation/schema-bundle-release.example.json' |
  Test-Json -SchemaFile 'schemas/jsonschema/provenance-and-attestation.schema.json'

Get-Content -Raw 'schemas/examples/repo-map-context-shaping/hybrid-default.example.json' |
  Test-Json -SchemaFile 'schemas/jsonschema/repo-map-context-shaping.schema.json'

Get-Content -Raw 'schemas/examples/repo-profile/python-service.example.json' |
  Test-Json -SchemaFile 'schemas/jsonschema/repo-profile.schema.json'

Get-Content -Raw 'schemas/examples/repo-profile/typescript-webapp.example.json' |
  Test-Json -SchemaFile 'schemas/jsonschema/repo-profile.schema.json'

Get-Content -Raw 'schemas/examples/repo-profile/target-repo-fast-full-template.example.json' |
  Test-Json -SchemaFile 'schemas/jsonschema/repo-profile.schema.json'

Get-Content -Raw 'schemas/examples/policy-decision/escalate-write.example.json' |
  Test-Json -SchemaFile 'schemas/jsonschema/policy-decision.schema.json'

Get-Content -Raw 'schemas/examples/agent-adapter-contract/manual-handoff.example.json' |
  Test-Json -SchemaFile 'schemas/jsonschema/agent-adapter-contract.schema.json'

Get-Content -Raw 'schemas/examples/agent-adapter-contract/process-bridge.example.json' |
  Test-Json -SchemaFile 'schemas/jsonschema/agent-adapter-contract.schema.json'

Get-Content -Raw 'schemas/examples/interaction-signal/default-bugfix-gap.example.json' |
  Test-Json -SchemaFile 'schemas/jsonschema/interaction-signal.schema.json'

Get-Content -Raw 'schemas/examples/response-policy/guided-clarify.example.json' |
  Test-Json -SchemaFile 'schemas/jsonschema/response-policy.schema.json'

Get-Content -Raw 'schemas/examples/teaching-budget/default-runtime.example.json' |
  Test-Json -SchemaFile 'schemas/jsonschema/teaching-budget.schema.json'

Get-Content -Raw 'schemas/examples/interaction-evidence/checklist-first-bugfix.example.json' |
  Test-Json -SchemaFile 'schemas/jsonschema/interaction-evidence.schema.json'

Get-Content -Raw 'schemas/examples/learning-efficiency-metrics/baseline.example.json' |
  Test-Json -SchemaFile 'schemas/jsonschema/learning-efficiency-metrics.schema.json'
```

## Notes
- These examples are intentionally small enough to be easy to audit.
- The repo-profile examples demonstrate `same kernel, different profiles` across Python and TypeScript targets.
- The control-pack example demonstrates bundle metadata; it does not contain executable policy or hook code.
- The adapter examples demonstrate honest fallback posture for non-Codex integrations.
- The interaction-governance examples demonstrate checklist-first bugfix guidance, bounded response policy, and token-budget-aware behavior.
- They are reference assets, not normative defaults for every repository.
