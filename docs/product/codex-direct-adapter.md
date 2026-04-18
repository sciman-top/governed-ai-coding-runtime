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

The posture event records whether the flow was `direct_adapter`, `process_bridge`, or `manual_handoff`. Manual handoff evidence remains distinguishable from direct adapter evidence.

## Smoke Trial
Use `scripts/run-codex-adapter-trial.py` to run the current Codex adapter smoke trial.

The trial is safe-mode by default:
- it does not require real high-risk writes
- it does not claim native attach unless `--native-attach` is passed
- it emits deterministic trial refs so task, binding, evidence, and verification wiring can be reviewed without private maintainer context

Example:

```powershell
python scripts/run-codex-adapter-trial.py `
  --repo-id "python-service" `
  --task-id "task-codex-trial" `
  --binding-id "binding-python-service"
```

Expected JSON fields:
- `mode`
- `repo_id`
- `task_id`
- `binding_id`
- `adapter_id`
- `adapter_tier`
- `unsupported_capabilities`
- `unsupported_capability_behavior`
- `evidence_refs`
- `verification_refs`
- `handoff_ref`

## Related
- [Codex CLI/App Integration Guide](./codex-cli-app-integration-guide.md)
- [Session Bridge Commands](./session-bridge-commands.md)
- [Adapter Degrade Policy](./adapter-degrade-policy.md)
