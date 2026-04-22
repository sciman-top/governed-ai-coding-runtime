# Required Canonical Entrypoint Policy Design

## Status
Draft for review

## Goal
- Add one unified policy model that can express three rollout stages for canonical runtime entrypoint enforcement.
- Keep one implementation path while allowing repositories to stop at `advisory`, promote to targeted enforcement, and finally promote to repo-wide enforcement.
- Make entrypoint drift visible in runtime surfaces before it becomes blocking.

## Problem
The repository already has a practical canonical flow shape:
- `scripts/runtime-flow.ps1`
- `scripts/runtime-flow-preset.ps1`

Those scripts already bundle attach-first onboarding and daily governed checks. They are the closest thing to a product-level unified entrypoint today.

At the same time, the runtime still exposes many lower-level entrypoints:
- `scripts/runtime-check.ps1`
- `scripts/run-governed-task.py`
- `scripts/session-bridge.py`
- `scripts/verify-repo.ps1`

This is useful for debugging and composition, but it means:
- canonical flow usage is recommended rather than enforced
- drift is not first-class in runtime status
- repositories cannot explicitly choose when to tighten to stronger entrypoint rules

## Non-Goals
- Do not turn the product into a host replacement.
- Do not remove low-level entrypoints.
- Do not make read-only inspection impossible during enforcement.
- Do not auto-promote repositories through stages without explicit configuration.

## Decision
Implement one repo-level policy object, `required_entrypoint_policy`, with three supported stages:
- `advisory`
- `targeted_enforced`
- `repo_wide_enforced`

All runtime surfaces will evaluate the same policy. Behavior changes by mode, not by separate implementations.

Default rollout posture for this feature should be:
- framework exists everywhere
- default repo posture starts at `advisory`
- promotion to stricter stages is explicit per repo

## Policy Shape
Add `required_entrypoint_policy` to `repo-profile`.

Proposed shape:

```json
{
  "required_entrypoint_policy": {
    "current_mode": "advisory",
    "target_mode": "repo_wide_enforced",
    "canonical_entrypoints": [
      "runtime-flow",
      "runtime-flow-preset"
    ],
    "allow_direct_entrypoints": [
      "run-governed-task.status",
      "session-bridge.inspect_status",
      "session-bridge.inspect_evidence",
      "session-bridge.inspect_handoff",
      "verify-repo"
    ],
    "targeted_enforcement_scopes": [
      "run_quick_gate",
      "run_full_gate",
      "write_request",
      "write_execute"
    ],
    "promotion_condition_ref": "docs/runbooks/entrypoint-policy-promotion.md"
  }
}
```

Field intent:
- `current_mode`: currently active enforcement stage.
- `target_mode`: desired future stage once drift is low enough.
- `canonical_entrypoints`: runtime entrypoint ids considered compliant.
- `allow_direct_entrypoints`: exemptions that remain legal even under stricter policy.
- `targeted_enforcement_scopes`: execution scopes blocked during stage 2 unless they came from a canonical entrypoint.
- `promotion_condition_ref`: explicit repo-owned promotion rule.

## Entrypoint Identity Model
Every relevant runtime caller must identify itself with a stable `entrypoint_id`.

Examples:
- `runtime-flow`
- `runtime-flow-preset`
- `runtime-check`
- `run-governed-task.verify-attachment`
- `run-governed-task.status`
- `session-bridge.request-gate`
- `session-bridge.write-execute`
- `verify-repo`

Canonical wrapper scripts are responsible for passing their identity to lower layers. Lower layers must preserve the original caller identity instead of replacing it with their own local script name.

This is necessary because:
- `runtime-flow-preset` delegates into `runtime-flow`
- `runtime-flow` delegates into `runtime-check`
- drift should be judged by the top-level user path, not by the last internal hop

## Three Stages

### Stage 1: `advisory`
Behavior:
- never blocks execution by itself
- records whether the current request came from a canonical entrypoint
- emits `entrypoint_drift` metadata in status and command results

Purpose:
- make drift visible
- establish migration evidence
- avoid breaking current multi-entrypoint usage

### Stage 2: `targeted_enforced`
Behavior:
- blocks only execution-critical scopes listed in `targeted_enforcement_scopes`
- keeps read-only inspection and selected direct tools available
- returns explicit denial or degraded status with remediation

Initial target scopes:
- gate execution
- write-governance request
- write execution

Purpose:
- tighten the highest-value governed paths first
- keep debugging and inspection usable

### Stage 3: `repo_wide_enforced`
Behavior:
- all governed execution paths must originate from a canonical entrypoint unless explicitly exempted
- read-only status and inspection remain available
- direct low-level execution tools become policy violations by default

Purpose:
- turn the canonical flow into the real operational contract for that repo

## Enforcement Boundaries
The policy should be checked at two layers:

### 1. Runtime orchestration surfaces
Primary enforcement points:
- `scripts/runtime-check.ps1`
- `packages/contracts/.../session_bridge.py`

Reason:
- these are where the runtime already makes execution decisions
- they can emit structured drift and remediation details

### 2. Canonical wrapper surfaces
Primary identity injectors:
- `scripts/runtime-flow.ps1`
- `scripts/runtime-flow-preset.ps1`

Reason:
- they define the user-facing canonical path
- they must stamp the request with the right `entrypoint_id`

Low-level direct tools should not each invent independent policy logic. They should report their identity and let the shared runtime evaluator decide.

## Runtime Behavior

### Shared evaluator
Introduce one shared evaluator that receives:
- `entrypoint_id`
- `required_entrypoint_policy`
- requested execution scope

It returns:
- `compliant`
- `drift_detected`
- `blocked`
- `reason`
- `remediation_hint`

### Status surfaces
Expose the following:
- policy mode
- active entrypoint id
- whether request is canonical
- whether drift was observed
- whether current scope would be blocked in the active mode

Minimum surfaces:
- `runtime-check` summary
- session bridge results for gate and write flows
- runtime status snapshot where practical

### Remediation
When blocked, the runtime should return the exact canonical rerun path when it can derive one, for example:
- rerun through `runtime-flow.ps1`
- rerun through `runtime-flow-preset.ps1 -Target <x>`

## Failure Handling
- `advisory` never fails the command.
- `targeted_enforced` and `repo_wide_enforced` fail closed only for governed execution scopes.
- status and evidence inspection remain callable even under strict mode.
- missing or malformed policy configuration should degrade to `advisory`, not silently behave as enforced.

## Testing
Minimum tests:
- repo-profile schema and loader accept the new policy object
- canonical wrapper scripts pass `entrypoint_id`
- direct non-canonical execution in `advisory` reports drift but does not fail
- direct non-canonical execution in `targeted_enforced` fails for gate and write scopes
- direct non-canonical read-only inspection remains allowed in `targeted_enforced`
- `repo_wide_enforced` blocks non-exempt governed execution scopes
- result payloads expose entrypoint compliance fields consistently

## Rollout
Implementation should land as one framework in one pass:
- schema and repo-profile support
- wrapper identity propagation
- shared evaluator
- status/result exposure for all stages

Default shipped presets and generated repo profiles should start with:
- `current_mode = advisory`

Promotion should remain configuration-driven rather than automatic.

## Risks
- If entrypoint identity is not propagated from the top-level wrapper, enforcement will be noisy and misclassify compliant flows as drift.
- If strict mode blocks read-only inspection, recovery and debugging will become harder.
- If every script implements enforcement separately, behavior will drift and quickly become unmaintainable.

## Acceptance
- A repo can stay at `advisory` without behavior breakage.
- The same repo can switch to `targeted_enforced` by config only.
- The same repo can switch to `repo_wide_enforced` by config only.
- Canonical flow compliance is visible in runtime outputs.
- Non-canonical execution receives explicit remediation instead of ambiguous failure.
