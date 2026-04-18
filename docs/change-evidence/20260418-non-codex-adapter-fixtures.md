# 20260418 Non-Codex Adapter Fixtures

## Purpose
Record `GAP-038 Task 11`, adding non-Codex manual-handoff and process-bridge fixtures so the generic adapter contract is exercised beyond Codex.

## Basis
- `docs/plans/interactive-session-productization-implementation-plan.md` Task 11
- `docs/product/adapter-capability-tiers.md`
- `schemas/jsonschema/agent-adapter-contract.schema.json`

## Changes
- `schemas/examples/agent-adapter-contract/manual-handoff.example.json`
  - added a generic manual-handoff fixture
- `schemas/examples/agent-adapter-contract/process-bridge.example.json`
  - added a generic process-bridge fixture
- `schemas/examples/README.md`
  - documented the new example directory and validation commands
- `tests/runtime/test_adapter_registry.py`
  - added fixture existence and tier assertions
- `docs/product/adapter-capability-tiers.md`
  - linked the generic fixture examples

## Commands
1. `python -m unittest tests.runtime.test_adapter_registry -v`
   - exit `0`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
   - exit `0`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
   - exit `0`

## Result
- at least one non-Codex `manual_handoff` fixture now validates
- at least one non-Codex `process_bridge` fixture now validates
- degrade posture examples are generic and honest about weaker capability tiers

## Risks
- fixtures are still illustrative examples, not executable adapter implementations
- more vendor-specific examples remain future work if the generic contract expands

## Rollback
- remove the new `agent-adapter-contract` example files
- revert README/doc references to the example fixtures
