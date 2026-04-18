# Contracts

Hand-maintained runtime contracts and domain models live here.

## Current Status
The current repository baseline exposes pure Python runtime contracts and domain models for:
- task intake validation
- lifecycle transition validation
- repo profile loading and resolution
- read-only governed tool request validation
- evidence timeline and task output primitives
- scripted read-only trial entrypoint
- isolated workspace allocation and write-path policy validation
- write policy default resolution
- approval request state handling, interruption state, and audit trail primitives
- write-side tool governance decisions with rollback references
- quick and full verification runner plans with live build/test/contract/doctor commands and evidence artifacts
- delivery handoff packages with validation status and replay references
- eval baseline records and trace grading primitives
- second-repo reuse pilot checks and generic process adapter compatibility gaps
- local operator HTML rendering from the runtime read model
- maintenance policy visibility in the runtime status surface
- minimal approval and evidence control console facade

These models are intentionally runtime-only and do not imply API, database, or workflow runtime selection yet.

Not landed yet:
- execution worker or managed runtime loop
- artifact store and replay pipeline
- stable runtime status surface beyond scripts and the minimal facade
