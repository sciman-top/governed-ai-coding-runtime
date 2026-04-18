# Session Bridge Commands

## Purpose
Define the first interactive command surface that host adapters can use to call governed runtime actions from an active AI coding session.

## Commands
- `bind_task`
- `show_repo_posture`
- `request_approval`
- `run_quick_gate`
- `run_full_gate`
- `write_request`
- `write_approve`
- `write_execute`
- `write_status`
- `inspect_evidence`
- `inspect_handoff`
- `inspect_status`

## Required Context
Every command carries:
- task id
- repo binding id
- adapter id
- risk tier
- structured payload

Execution-like commands also carry a PolicyDecision reference.

## Execution Semantics
- Read-only commands use `execution_mode = read_only`.
- Allowed quick/full gate commands use `execution_mode = execute`.
- Escalated quick/full gate commands use `execution_mode = requires_approval` and carry escalation context.
- Denied quick/full gate commands fail closed and do not become executable commands.

## PolicyDecision Boundary
The session bridge does not make policy decisions by itself. It consumes a PolicyDecision result and normalizes the command posture:
- `allow` becomes executable
- `escalate` becomes approval-required
- `deny` fails closed

## Local Entrypoint
The local bridge entrypoint is:

```powershell
python scripts/session-bridge.py --help
```

Supported local subcommands:
- `bind-task`
- `repo-posture`
- `status`
- `request-gate`
- `inspect-evidence`
- `inspect-handoff`
- `write-request`
- `write-approve`
- `write-execute`
- `write-status`
- `launch`

The local entrypoint returns structured JSON. Unsupported commands or adapter capabilities return an explicit degraded result with `unsupported_capability_behavior = manual_handoff`.

## Gate Requests
`request-gate` creates a verification request through the existing verification runner plan path:
- `quick` maps to `test -> contract`
- `full` maps to `build -> test -> contract -> doctor`
- when `attachment_root` and `attachment_runtime_state_root` are supplied, the gate commands come from the attached target repo light pack / repo profile instead of the local runtime repo defaults

The local bridge does not silently execute a denied PolicyDecision. Denied execution-like commands fail closed before a gate request is exposed.

## Write Flow
The local session bridge now exposes the first governed write command surface:
- `write-request` returns the governance posture for a proposed write, including approval-required state when needed
- `write-approve` records the approval decision for a pending write request
- `write-execute` attempts the actual write after policy and approval checks
- `write-status` reports the current approval or execution posture for a write flow

Write-flow results include a stable `execution_id` so later approval, execution, and inspection calls can stay on one runtime-owned thread.

## Evidence And Handoff Inspection
- `inspect-evidence` returns task-level evidence refs, verification refs, artifact refs, approval ids, transition evidence refs, and rollback refs
- `inspect-handoff` returns known handoff refs and related rollback refs for a task or run

## Launch-Second Fallback
Launch mode is explicit. It is never presented as native attach.

`launch` uses process bridge posture when a process boundary is available. The result captures:
- launch mode
- adapter tier
- process exit code
- stdout
- stderr
- changed files
- verification references

If process bridge is unavailable, the bridge returns manual handoff with explicit degrade behavior.

## Write Governance Normalization
Existing local write governance decisions are normalized to PolicyDecision before the bridge exposes execution-like outcomes:
- allowed write governance result -> `allow`
- paused write governance result -> `escalate`
- blocked or invalid write request -> `deny`

## Related
- [Session Bridge Command Spec](../specs/session-bridge-command-spec.md)
- [Policy Decision Spec](../specs/policy-decision-spec.md)
- [Target Repo Attachment Flow](./target-repo-attachment-flow.md)
