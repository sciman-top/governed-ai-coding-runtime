# Adapter Degrade Policy

## Goal
Make adapter compatibility posture explicit, especially when upstream capability surfaces are weaker than full governed enforcement expects.

## Baseline
- Codex remains the first adapter priority.
- The runtime is honest about weak capability surfaces.
- Unsupported capabilities do not silently degrade into a posture that looks fully governed.
- Generic adapter posture is expressed through `native_attach`, `process_bridge`, and `manual_handoff`.

## Rules
- `full_support` preserves the requested posture when the repo also supports it.
- `partial_support` must include an explicit `degrade_to` target and a reason.
- `unsupported` without an explicit `degrade_to` is treated as fail-closed.
- `unsupported` with `degrade_to: fail_closed` is blocked.
- `unsupported` with an explicit weaker posture is allowed only when the runtime can still explain the exact loss of enforcement.

## Operator Visibility
- docs must explain the degrade behavior
- sample repo profiles must carry compatibility signals
- `doctor-runtime.ps1` must report that adapter posture is visible

## Current Public Usable Release Posture
- Codex-first compatibility is explicit.
- Structured upstream event visibility is still partial.
- The local runtime compensates with artifact-backed status, verification, evidence, and replay outputs.

## Launch-Second Fallback
- Native attach remains the preferred posture when available.
- Process bridge launch mode is explicit and must not be described as native attach.
- Process bridge results must capture process output, exit code, changed-file discovery, and verification references.
- When process bridge is unavailable, the runtime degrades to manual handoff instead of pretending execution is governed through a stronger adapter tier.

## Tier Guarantees
- `native_attach` guarantees an attached session boundary plus same-contract verification.
- `process_bridge` guarantees a captured process boundary plus same-contract verification.
- `manual_handoff` guarantees explicit handoff posture plus same-contract verification.
- Tier guarantees must be documented and machine-readable on the adapter contract surface.
