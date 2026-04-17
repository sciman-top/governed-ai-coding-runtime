# Control Packs

Runtime-consumable control-pack metadata lives here.

## Current Assets
- `minimum-governance-kernel.control-pack.json`: reference metadata pack for the first governed AI coding trial loop.

## Boundaries
- Control packs reference controls, hooks, skills, gates, evals, and knowledge sources.
- Control packs do not embed executable policy code.
- A pack can tighten governance but must not weaken kernel guarantees.

## Validation
```powershell
Get-Content -Raw 'schemas/control-packs/minimum-governance-kernel.control-pack.json' |
  Test-Json -SchemaFile 'schemas/jsonschema/control-pack.schema.json'
```
