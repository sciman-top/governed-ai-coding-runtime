# Codex Direct Adapter

## Purpose
Define the Codex-first adapter contract without making the runtime Codex-only.

This contract records what the runtime knows about a Codex CLI/App integration posture and how it should degrade when full native attach capability is unavailable.

## Adapter Identity
- adapter id: `codex-cli`
- auth ownership: `user_owned_upstream_auth`
- workspace control: `external_workspace`
- mutation model: `direct_workspace_write`

## Capability Fields
- tool visibility
- resume behavior
- evidence export capability
- adapter tier
- probe source
- posture reason
- unsupported capabilities
- unsupported capability behavior

## Adapter Tiers

### native_attach
Use only when live session attachment capability is available.

### process_bridge
Use when native attach is unavailable but a process boundary can be launched and captured.

### manual_handoff
Use when neither native attach nor process bridge capability is available.

## Degrade Rules
- Missing native attach must be recorded as unsupported; it must not be implied.
- Missing structured event visibility degrades evidence quality to logs, transcript, or manual summary.
- Missing resume id support must be recorded as manual resume behavior.
- Missing structured evidence export must be recorded as manual summary evidence capability.
- Process bridge and manual handoff are compatibility paths, not native attach.

## Live Probe And Handshake
The runtime now supports a real Codex surface probe and handshake path:
- `codex --version` confirms whether Codex CLI is reachable.
- `codex --help` is used to discover the available command surface.
- `codex exec --help` is used to infer JSONL event visibility and evidence export hints.
- `codex status` is treated as the live attach handshake signal only when that command exists in the current Codex build.
- if `status` is absent but `resume` is present, native attach capability is inferred from the resume command surface.

When `codex status` cannot complete (for example non-interactive `stdin is not a terminal`), posture degrades to `process_bridge` while keeping the failure reason explicit.
When `status` is not exposed by the installed Codex build and `resume` is also unavailable, native attach is marked unavailable explicitly while process bridge remains available.

Live probe command resolution supports:
- explicit CLI flag: `--codex-bin "<path-or-command>"`
- environment variable fallback: `GOVERNED_RUNTIME_CODEX_BIN` (then `CODEX_BIN`)

Live probe output now includes:
- `failure_stage` (`codex_command_unavailable`, `live_attach_probe_unsupported_status_command_missing`, `live_attach_unavailable_non_interactive`, `codex_status_probe_failed`, or `null`)
- `remediation_hint` with executable next checks
- `probe_attempts` (`>=1`) to show whether degraded posture triggered automatic re-probing
- `stability_state` (`single_pass`, `stabilized`, `degraded_after_retry`)

Stability behavior:
- degraded capability posture now triggers automatic probe retry (`max_probe_attempts=2` by default)
- transient failures can self-recover in one runtime call instead of sticking to stale degrade posture
- cached degraded probe results are not kept sticky across repeated status calls

Codex session identity is carried in the runtime task model as:
- `session_id`
- `resume_id`
- `continuation_id`
- `flow_kind` (`live_attach` / `process_bridge` / `manual_handoff`)

## Runtime Boundary
The Codex adapter may classify Codex capability posture and evidence expectations. It may not:
- own upstream Codex authentication
- redefine task lifecycle
- weaken approval requirements
- change canonical gate order
- make a weak capability look like full native attach

## Evidence Mapping
Codex session evidence maps into the runtime evidence timeline by governed task id:
- file changes -> `adapter_file_change`
- tool calls -> `adapter_tool_call`
- gate runs -> `adapter_gate_run`
- approval events -> `adapter_approval_event`
- handoff references -> `adapter_handoff`

The posture event records whether the flow was `live_attach`, `process_bridge`, or `manual_handoff`. Manual handoff evidence remains distinguishable from live attach evidence.

## Smoke Trial
Use `scripts/run-codex-adapter-trial.py` to run the current Codex adapter smoke trial.

The trial is safe-mode by default:
- it does not require real high-risk writes
- it does not claim native attach unless `--native-attach` is passed
- it emits deterministic trial refs so task, binding, evidence, and verification wiring can be reviewed without private maintainer context
- it can optionally derive posture from a live probe with `--probe-live`

Example:

```powershell
python scripts/run-codex-adapter-trial.py `
  --repo-id "python-service" `
  --task-id "task-codex-trial" `
  --binding-id "binding-python-service" `
  --probe-live
```

Use a custom executable or shim:

```powershell
python scripts/run-codex-adapter-trial.py `
  --repo-id "python-service" `
  --task-id "task-codex-trial" `
  --binding-id "binding-python-service" `
  --probe-live `
  --codex-bin "codex.cmd"
```

On Windows, do not hard-code the exact `.exe` executable name unless that file has been verified on the target machine. Prefer `codex`, `codex.cmd`, or a configurable `--codex-bin` / `GOVERNED_RUNTIME_CODEX_BIN` value.

Expected JSON fields:
- `mode`
- `repo_id`
- `task_id`
- `binding_id`
- `adapter_id`
- `adapter_tier`
- `unsupported_capabilities`
- `unsupported_capability_behavior`
- `flow_kind`
- `session_id`
- `resume_id`
- `continuation_id`
- `probe_source`
- `live_probe.failure_stage`
- `live_probe.remediation_hint`
- `evidence_refs`
- `verification_refs`
- `handoff_ref`

## Related
- [Codex CLI/App Integration Guide](./codex-cli-app-integration-guide.md)
- [Session Bridge Commands](./session-bridge-commands.md)
- [Adapter Degrade Policy](./adapter-degrade-policy.md)
