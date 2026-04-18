# 20260418 Adapter Capability Tiers

## Purpose
Record `GAP-038 Task 10`, generalizing the adapter registry so Codex posture projects through the same generic adapter-tier contract used for future adapters.

## Basis
- `docs/plans/interactive-session-productization-implementation-plan.md` Task 10
- `docs/specs/agent-adapter-contract-spec.md`
- `schemas/jsonschema/agent-adapter-contract.schema.json`
- `docs/product/adapter-degrade-policy.md`

## Changes
- `packages/contracts/src/governed_ai_coding_runtime_contracts/adapter_registry.py`
  - added `AdapterContract`
  - added `build_adapter_contract(...)`
  - added `project_codex_profile_to_adapter_contract(...)`
  - added explicit per-tier governance guarantees and default runtime controls
- `packages/contracts/src/governed_ai_coding_runtime_contracts/__init__.py`
  - exported the generic adapter contract helpers
- `tests/runtime/test_adapter_registry.py`
  - added tier and Codex projection coverage
- `docs/specs/agent-adapter-contract-spec.md`
  - made `adapter_tier` and `governance_guarantees` explicit
- `schemas/jsonschema/agent-adapter-contract.schema.json`
  - required `adapter_tier`
  - required `governance_guarantees`
- `schemas/catalog/schema-catalog.yaml`
  - bumped schema catalog version to `1.6`
- `docs/product/adapter-capability-tiers.md`
  - added public tier definitions and guarantees
- `docs/product/adapter-degrade-policy.md`
  - linked degrade rules to generic adapter tiers
- `docs/README.md`
  - linked the new product doc

## Commands
1. `python -m unittest tests.runtime.test_adapter_registry tests.runtime.test_codex_adapter -v`
   - exit `0`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
   - exit `0`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
   - exit `0`
   - `Ran 180 tests`

## Result
- adapter posture is now represented through the generic tiers `native_attach`, `process_bridge`, and `manual_handoff`
- each tier carries explicit governance guarantees
- Codex posture can now project into the same generic adapter contract instead of staying adapter-specific only

## Risks
- example instances for `agent-adapter-contract` are not added in this task; they remain the next step in Task 11
- current generic contract is still intentionally small and centered on posture, not end-to-end invocation semantics

## Rollback
- revert `adapter_registry.py` generic contract additions
- revert `agent-adapter-contract` spec/schema changes
- revert the new product doc and doc index entries
