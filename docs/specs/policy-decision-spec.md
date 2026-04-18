# Policy Decision Spec

## Status
Draft

## Purpose
Define the stable local decision interface between host adapters, session bridges, tool runners, approval flow, and verification gates.

This contract exists so the runtime can decide whether an execution-like action should:
- proceed
- pause for approval
- fail closed

without conflating those outcomes with agent-specific frontend behavior.

## Required Fields
- schema_version
- task_id
- action_id
- risk_tier
- subject
- status
- decision_basis
- evidence_ref

## Optional Fields
- required_approval_ref
- remediation_hint

## Enumerations

### risk_tier
- low
- medium
- high

### status
- allow
- escalate
- deny

## Field Semantics

### schema_version
Contract version for the serialized decision payload. The current local contract default is `1.0`.

### task_id
Stable task identifier for the governed workflow that requested the action.

### action_id
Stable identifier for the governed action or execution-like request under evaluation.

### risk_tier
Resolved risk tier for the action at decision time.

### subject
Human-readable and machine-stable subject string describing what is being decided, such as a path-scoped write request, a session command, or an adapter action.

### status
Decision result:
- `allow`: the action may proceed without further approval interruption
- `escalate`: the action may not proceed yet and must wait for approval intent to resolve
- `deny`: the action fails closed and does not become executable

### decision_basis
Non-empty ordered list of reasons or policy facts that explain why the decision was reached.

### evidence_ref
Reference to the auditable evidence or trace record that supports the decision.

### required_approval_ref
Approval request reference associated with `escalate`.

### remediation_hint
Operator or session-facing hint describing how to recover from `deny` or how to convert a blocked action into an allowed path.

## Invariants
- `decision_basis` must contain at least one non-empty entry.
- `evidence_ref` must point to an auditable runtime record.
- `allow` must not require an approval reference.
- `escalate` must carry `required_approval_ref`.
- `escalate` does not make the action executable by itself.
- `deny` fails closed and must not produce an executable action.
- `deny` must not carry an approval reference.
- `deny` must carry a remediation hint.
- PolicyDecision may describe approval intent, but it may not impersonate approval completion.
- PolicyDecision may not alter task lifecycle, verification gate order, or rollback semantics.

## Non-Goals
- implementing a full policy engine
- binding the runtime to OPA or any other external policy product immediately
- replacing adapter contracts or approval contracts
- embedding agent-specific UI or transcript semantics into the decision object
