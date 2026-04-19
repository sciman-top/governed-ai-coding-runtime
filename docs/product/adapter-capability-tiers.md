# Adapter Capability Tiers

## Purpose
Define the generic adapter tiers used to classify AI coding host integrations without overstating governance strength.

## Tiers

### native_attach
- strongest tier
- an attached session boundary is available
- the runtime can reason about adapter posture without pretending a fallback is native

Governance guarantees:
- attached session boundary
- runtime-visible adapter posture
- same-contract verification required

### process_bridge
- fallback tier when native attach is unavailable
- the runtime can launch and capture a process boundary

Governance guarantees:
- captured process boundary
- runtime-visible adapter posture
- same-contract verification required

### manual_handoff
- lowest supported tier
- no native attach and no process bridge are available
- execution is handed off explicitly instead of being described as fully governed

Governance guarantees:
- explicit manual handoff
- runtime-visible adapter posture
- same-contract verification required

## Honest Degrade Rule
- native attach may degrade to process bridge
- process bridge may degrade to manual handoff
- unsupported capability behavior must be explicit and machine-readable
- weaker tiers must never be described as stronger ones

## Runtime Registry Interface
Adapter tier selection is now exposed as a runtime interface, not only static documentation:
- register adapter contracts
- discover adapters by family or tier
- probe host capability
- select tier using attachment preference plus probe result
- delegate execution with structured degrade metadata (`requested_tier`, `degraded`, `degrade_reason`)

## Codex Projection
Codex remains the first direct adapter target, but its posture is projected through the same tier contract:
- `native_attach` when live attachment is available
- `process_bridge` when launch capture exists without attach
- `manual_handoff` when neither path is available

## Example Fixtures
Reference examples now live under `schemas/examples/agent-adapter-contract/`:
- `manual-handoff.example.json`
- `process-bridge.example.json`

They are intentionally non-Codex fixtures so degrade posture stays generic instead of Codex-only.

## Related
- [Agent Adapter Contract Spec](../specs/agent-adapter-contract-spec.md)
- [Adapter Degrade Policy](./adapter-degrade-policy.md)
- [Codex Direct Adapter](./codex-direct-adapter.md)
