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
- Runtime selection output must include `requested_tier`, `degraded`, and `degrade_reason` when attachment preference cannot be satisfied by detected host capability.

## Operator Visibility
- docs must explain the degrade behavior
- sample repo profiles must carry compatibility signals
- `doctor-runtime.ps1` must report that adapter posture is visible

## Current Public Usable Release Posture
- Codex and Claude Code are dual first-class entrypoints in governance result.
- Current live probe posture is host-dependent and must be re-probed; do not classify Codex as `native_attach` from resume/help surface alone when no status handshake exists.
- Claude Code `native_attach` is evidence-backed by session/resume identity, `stream-json` output, hook-event visibility, and managed settings/hooks; it is not a claim that Claude Code exposes the same host API as Codex.
- Structured upstream event visibility remains host-specific and must be re-probed after host upgrades.
- The local runtime compensates with artifact-backed status, verification, evidence, and replay outputs.

## Launch-Second Fallback
- Native attach remains the preferred posture when available.
- If either Codex or Claude Code loses required live attach evidence, runtime selection must degrade explicitly to `process_bridge` or `manual_handoff`.
- Process bridge launch mode is explicit and must not be described as native attach.
- Process bridge results must capture process output, exit code, changed-file discovery, and verification references.
- When process bridge is unavailable, the runtime degrades to manual handoff instead of pretending execution is governed through a stronger adapter tier.

## Tier Guarantees
- `native_attach` guarantees an attached session boundary plus same-contract verification.
- `process_bridge` guarantees a captured process boundary plus same-contract verification.
- `manual_handoff` guarantees explicit handoff posture plus same-contract verification.
- Tier guarantees must be documented and machine-readable on the adapter contract surface.

## Runtime-Selection Payload
When adapter contracts declare `runtime_selection`, runtime-managed delegation exposes:
- `fallback_chain`
- `delegation_mode`
- `degrade_policy_ref`

This keeps degrade behavior executable and auditable from the runtime interface.
