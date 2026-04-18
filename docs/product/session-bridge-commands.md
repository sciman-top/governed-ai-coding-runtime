# Session Bridge Commands

## Purpose
Define the first interactive command surface that host adapters can use to call governed runtime actions from an active AI coding session.

## Commands
- `bind_task`
- `show_repo_posture`
- `request_approval`
- `run_quick_gate`
- `run_full_gate`
- `inspect_evidence`
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
- `launch`

The local entrypoint returns structured JSON. Unsupported commands or adapter capabilities return an explicit degraded result with `unsupported_capability_behavior = manual_handoff`.

## Gate Requests
`request-gate` creates a verification request through the existing verification runner plan path:
- `quick` maps to `test -> contract`
- `full` maps to `build -> test -> contract -> doctor`
- when `attachment_root` and `attachment_runtime_state_root` are supplied, the gate commands come from the attached target repo light pack / repo profile instead of the local runtime repo defaults

The local bridge does not silently execute a denied PolicyDecision. Denied execution-like commands fail closed before a gate request is exposed.

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
