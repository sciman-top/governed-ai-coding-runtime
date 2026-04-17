# Eval And Trace Baseline

## Eval Baseline
The runtime records required eval suites from the repo profile. For the current sample profile, this includes:

- `python-service-smoke`
- `api-regression`

## Required Trace Fields
Each trace record emits:

- task id
- evidence link
- validation status
- outcome quality

## Trace Grading
Trace grading separates evidence completeness from outcome quality:

- `missing_evidence`: evidence link is absent.
- `poor_outcome_quality`: evidence exists, but the outcome quality failed.
- `pass`: evidence exists and outcome quality passed.
