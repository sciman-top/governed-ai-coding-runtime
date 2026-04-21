# 20260421 Hybrid Best-State Optimization And Gap Horizons

## Goal
Optimize the hybrid final-state narrative so it is:
- stricter in engineering acceptance
- explicit about near-term vs long-term gap horizons
- executable for roadmap and implementation planning

## Scope
Updated canonical planning documents:
- `docs/architecture/hybrid-final-state-master-outline.md`
- `docs/roadmap/direct-to-hybrid-final-state-roadmap.md`
- `docs/plans/direct-to-hybrid-final-state-implementation-plan.md`

## What Changed
1. Master outline:
- added `Optimized Best-State Definition (2026-04-21)`
- introduced quantified acceptance targets
- separated near-term and long-term gap horizons

2. Roadmap:
- added `Near-Term Gap Lanes (Execution Horizon)`
- added `Long-Term Gap Lanes (North-Star Hardening Horizon)`
- tied each lane to phase dependencies and closure evidence expectations

3. Implementation plan:
- added `Gap Horizon Planning (Optimized Best-State)`
- introduced near-term and long-term gap packages to drive backlog decomposition

## Why
Previous planning artifacts were strong on sequencing, but weaker on:
- measurable closure targets
- explicit horizon split for actionable vs deferred gaps
- direct mapping from optimized end-state definition to executable package lanes

## Verification
- attempted:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
  - result: failed in runtime unit tests due host temp-directory permission errors (`PermissionError` under `%LOCALAPPDATA%\\Temp` during `tempfile.TemporaryDirectory()` cleanup and writes)
- alternative verification for this docs-only change:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs` -> `OK`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts` -> `OK`

### Gate N/A Record
| field | value |
|---|---|
| type | `gate_na` |
| reason | full runtime gate chain is blocked by host temp directory permission failures unrelated to this planning-doc-only change |
| alternative_verification | docs + scripts checks passed (`verify-repo -Check Docs`, `verify-repo -Check Scripts`) |
| evidence_link | this file plus command output captured in current session |
| expires_at | `2026-05-31` |

## Risks
- If lane/package labels are not synchronized to backlog/issue seeds, planning drift can return.
- Quantitative targets require stable evidence freshness policy; otherwise targets become decorative.

## Rollback
- Revert this commit (or this file set) and restore prior versions of the three planning docs.
- No runtime contract/schema/code behavior is changed by this update.
