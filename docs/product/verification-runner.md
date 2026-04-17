# Verification Runner

## Canonical Order
Full verification follows the project gate order:

1. `build`
2. `test`
3. `contract/invariant`
4. `hotspot`

Quick verification is a shortened preflight and preserves ordering for the active gates it runs:

1. `test`
2. `contract/invariant`

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
