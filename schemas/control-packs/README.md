# Control Packs

Runtime-consumable control-pack assets live here.

## Current Assets
- `minimum-governance-kernel.control-pack.json`: executable and verifiable reference pack for the first governed AI coding trial loop.

## Boundaries
- Control packs reference controls, hooks, skills, gates, evals, and knowledge sources.
- Control packs do not embed executable policy code.
- Control packs must carry runnable or verifiable execution references for policy, gate, hook, eval, workflow, skill, knowledge, memory, evidence, and rollback surfaces.
- A pack can tighten governance but must not weaken kernel guarantees.

## Validation
```powershell
python scripts/verify-control-pack-execution.py
python scripts/materialize-control-pack.py
```
