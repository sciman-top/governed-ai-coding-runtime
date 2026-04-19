# Session Bridge Command Spec

## Status
Draft

## Purpose
Define the stable command contract for governed actions callable from an active AI coding session.

The session bridge is the boundary between a host adapter and the machine-local governance runtime. It must expose useful interactive commands without letting host-specific behavior bypass PolicyDecision, approval, evidence, or verification semantics.

## Required Fields
- schema_version
- command_id
- command_type
- task_id
- repo_binding_id
- adapter_id
- risk_tier
- execution_mode
- payload

## Optional Fields
- policy_decision_ref
- escalation_context

For `run_quick_gate` and `run_full_gate`, `payload` may carry:
- `run_id` (string): stable run identity for verification artifacts
- `plan_only` (boolean): return the executable gate plan without running commands
- `execution_id` (string, optional override): stable execution identity
- `continuation_id` (string, optional override): stable continuation identity

For `write_request` and `write_execute`:
- file-write path: `tool_name`, `target_path`, `tier`, `rollback_reference`, and `content` (execute only)
- governed tool path: `tool_name` in `shell | git | package`, bounded `command`, `rollback_reference`, and optional `approval_id`

## Enumerations

### command_type
- bind_task
- show_repo_posture
- request_approval
- run_quick_gate
- run_full_gate
- write_request
- write_approve
- write_execute
- write_status
- inspect_evidence
- inspect_handoff
- inspect_status

### risk_tier
- low
- medium
- high

### execution_mode
- read_only
- execute
- requires_approval

## Field Semantics

### schema_version
Contract version for serialized command payloads. The current local contract default is `1.0`.

### command_id
Stable identifier for this session bridge command.

### command_type
The governed action requested by the active session.

### task_id
Governed task id that scopes the command.

### repo_binding_id
Attachment binding id for the target repository.

### adapter_id
Host adapter id that originated or will handle the command.

### risk_tier
Risk tier resolved for this command.

### execution_mode
Execution posture after policy evaluation:
- `read_only`: command only inspects or binds state
- `execute`: command may proceed
- `requires_approval`: command must pause and carry escalation context

### payload
Command-specific structured payload.

### policy_decision_ref
Reference to the PolicyDecision evidence or record used to authorize an execution-like command.

### escalation_context
Context needed to pause for human approval rather than execute.

## Invariants
- Every command must carry task id, repo binding id, adapter id, and risk tier.
- `run_quick_gate`, `run_full_gate`, and `write_execute` must carry `policy_decision_ref`.
- `write_request` creates or returns the effective PolicyDecision posture for a governed write flow.
- Execution commands require a matching PolicyDecision or stable `policy_decision_ref` before they become executable.
- A `deny` PolicyDecision must fail closed and must not create an executable command.
- An `escalate` PolicyDecision must produce `execution_mode = requires_approval` and carry escalation context.
- `request_approval` must carry escalation context.
- Read-only commands must not require PolicyDecision.

## Command Notes
- `write_request` collects the governance posture for a proposed write and may return approval-required state.
- `write_approve` records the human decision for a pending write approval request.
- `write_execute` attempts the actual governed write after policy and approval checks.
- `write_status` reports the current write-flow posture using execution id, approval id, and related refs when available.
- for governed tool execution, `write_request`/`write_execute` keeps the same approval and identity model while enforcing bounded command coverage.
- `run_quick_gate` and `run_full_gate` execute the verification flow through runtime-managed lifecycle by default, and return stable execution/continuation ids plus artifact refs. Set `payload.plan_only = true` to request plan-only output.
- `inspect_evidence` returns task-level evidence, verification, approval, artifact, and rollback refs.
- `inspect_handoff` returns known handoff refs and related rollback refs for a task or run.

## Non-Goals
- implementing the session bridge CLI
- launching or attaching a host AI tool
- replacing PolicyDecision, approval, verification, evidence, or adapter contracts
