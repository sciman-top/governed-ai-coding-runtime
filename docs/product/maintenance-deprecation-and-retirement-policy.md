# Maintenance, Deprecation, And Retirement Policy

## Purpose
- define the minimum maintenance boundary for the single-machine governed runtime after lifecycle completion
- make deprecation and retirement traceable instead of ad hoc

## Maintenance Boundary
- maintain the documented local bootstrap, quickstart, package bundle, and operator surfaces
- maintain the canonical gate order `build -> test -> contract/invariant -> hotspot`
- maintain schema/spec/example/catalog alignment for runtime-facing contracts
- maintain explicit adapter posture and fail-closed behavior for unsupported capability surfaces

## Triage Rules
- defects that break bootstrap, governed task execution, verification routing, status visibility, or evidence persistence are `high`
- docs/spec/schema drift that invalidates the quickstart or package bundle is `medium`
- cosmetic issues that do not change operator behavior are `low`
- a maintenance change is not complete until the affected gate or read model is re-verified

## Deprecation Rules
- deprecated capabilities must remain discoverable in docs or evidence until a replacement path exists
- every deprecation notice must name:
  - the deprecated surface
  - the replacement or fallback
  - the earliest retirement point
  - the evidence or migration note that explains the change
- deprecation without replacement is allowed only when the capability is unsafe and explicitly fails closed

## Retirement Rules
- retired capabilities may be removed only after a deprecation or evidence trail exists
- retirement must leave enough traceability to explain:
  - what was removed
  - why it was removed
  - how operators recover old artifacts or historical behavior if needed
- silent disappearance of operator-visible surfaces, policy docs, or persisted identifiers is not allowed

## Review Cadence
- review maintenance policy whenever a change affects adapters, repo profiles, persisted runtime state, or operator-visible schemas
- update the evidence log whenever maintenance policy itself changes

## Exit Signal
- the project stays in steady-state maintenance once compatibility, upgrade, deprecation, and retirement remain explicit in docs, runtime status, and doctor checks
