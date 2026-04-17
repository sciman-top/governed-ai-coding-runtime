# Delivery Handoff

## Package Contents
A delivery handoff package is generated per completed task and contains:

- task id
- changed files
- verification artifact
- validation status
- risk notes
- replay references

## Validation Status
- `fully_validated`: full verification ran and all full gates passed.
- `partially_validated`: quick verification, `gate_na`, missing gates, or any non-full verification path.

## Replay References
Failed, interrupted, or not-run paths require replay references. A replay reference can be a command, evidence file, failure log, or recovery instruction that lets the next operator reproduce or continue the path.
