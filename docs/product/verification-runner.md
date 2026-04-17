# Verification Runner

## Canonical Order
Full verification follows the project gate order:

1. `build`
2. `test`
3. `contract`
4. `doctor`

Quick verification is a shortened preflight and preserves ordering for the active gates it runs:

1. `test`
2. `contract`

## Live Commands
- `build`: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- `test`: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `contract`: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `doctor`: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

## Escalation Conditions
- A quick verification failure requires either full verification or root-cause evidence before delivery.
- A contract/invariant failure blocks delivery.
- A missing required gate blocks delivery unless it has a documented `gate_na` record.

## Evidence Artifact
Verification output must attach to a change evidence file with:

- mode: `quick` or `full`
- gate order
- per-gate result
- evidence link
- escalation conditions
