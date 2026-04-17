# Second-Repo Reuse Pilot

## Pilot Scope
The second-repo pilot uses existing sample repo profiles:

- primary: `python-service-sample`
- second: `typescript-webapp-sample`

The pilot does not access an external repository. It proves that the same kernel semantics can admit a second repo shape through repo-profile values and stricter overrides.

## Kernel Reuse Rule
The second repo may differ in:

- language
- build/test commands
- path policies
- eval suites
- reviewer handoff text

It must not redefine:

- task lifecycle
- approval state machine
- canonical verification order

## Additional Adapter Shape
The pilot also declares a generic non-interactive process CLI adapter. Its logs-only event visibility is tracked as an adapter compatibility gap, not a reason to fork governance-kernel semantics.
