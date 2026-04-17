# Write Policy Defaults

## Decision
The MVP write policy is conservative by default:

- `low` tier writes may run without human approval after path-scope validation.
- `medium` tier writes require approval by default.
- `high` tier writes always require explicit approval.

## Runtime Contract
The default policy is resolved from each repo profile:

- `risk_defaults.default_write_tier` defines the default tier when a task does not declare one.
- `approval_defaults.medium_write_requires_approval` controls medium-tier behavior and defaults to `true`.
- `approval_defaults.high_requires_explicit_approval` must be `true`; a profile that disables it is invalid.

## Downstream Implementation Notes
- Approval service work must treat `high` as fail-closed until an explicit approval decision exists.
- Tool governance work may auto-run only `low` tier writes, and only after workspace and path policy checks pass.
- Any future relaxation of `medium` behavior must be recorded as a policy change with evidence and rollback notes.
