# Single-Machine Runtime Quickstart

## Purpose
Bootstrap, run, inspect, and clean up the governed runtime on one machine without private maintainer knowledge.

## Scope Boundary
- this quickstart proves the local governed runtime path
- it does not prove a direct Codex CLI/App execution adapter
- the `run-governed-task.py` path below should be read as a runtime smoke task

For current Codex usage guidance, see:
- [Codex CLI/App Integration Guide](../product/codex-cli-app-integration-guide.md)
- [Codex CLI/App 集成指南](../product/codex-cli-app-integration-guide.zh-CN.md)
- [Codex Direct Adapter](../product/codex-direct-adapter.md)
- [Use With An Existing Repo](./use-with-existing-repo.md)

## Run A Codex Adapter Smoke Trial
This is distinct from the existing read-only scripted trial and from the local runtime smoke task.

```powershell
python scripts/run-codex-adapter-trial.py `
  --repo-id "python-service" `
  --task-id "task-codex-trial" `
  --binding-id "binding-python-service"
```

Expected JSON output includes:
- `adapter_tier`
- `task_id`
- `binding_id`
- `evidence_refs`
- `verification_refs`
- `unsupported_capability_behavior`

Interpretation boundary:
- this proves the current direct Codex adapter contract surface is wired
- it does not prove a real high-risk write path
- it does not replace the local runtime smoke task below

## Prerequisites
- Windows with PowerShell 7+
- `python` or `python3` on `PATH`
- Repository checkout with the current `Full Runtime` baseline

## Bootstrap
Run from the repository root:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/bootstrap-runtime.ps1
```

Expected result:
- compatibility runtime roots under `.runtime/` (bootstrap keeps legacy local mode available)
- JSON status output showing `total_tasks`

## Runtime Root Modes
`run-governed-task.py` now resolves runtime roots through one model:
- default: machine-local runtime root (outside repo root)
- compatibility mode: repo-root `.runtime/` via `--compat-runtime-root`
- explicit override: `--runtime-root <path>`

Inspect resolved roots:

```powershell
python scripts/run-governed-task.py status --json
```

## Create And Run A Runtime Smoke Task

```powershell
python scripts/run-governed-task.py create --goal "inspect runtime quickstart"
```

```powershell
python scripts/run-governed-task.py run --json
```

Expected runtime outputs:
- persisted task record under `runtime_roots.tasks_root`
- gate artifacts under `runtime_roots.artifacts_root/<task>/<run>/verification-output/`
- evidence bundle under `runtime_roots.artifacts_root/<task>/<run>/evidence/`
- handoff package under `runtime_roots.artifacts_root/<task>/<run>/handoff/`
- a local runtime smoke result rather than a direct Codex-managed coding run

Run in compatibility mode if you need repo-local `.runtime/`:

```powershell
python scripts/run-governed-task.py --compat-runtime-root run --json
```

## Inspect Runtime Status

```powershell
python scripts/run-governed-task.py status --json
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
```

## Repository Verification

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```

## Cleanup
If you run in compatibility mode and need to reset repo-local runtime state:

```powershell
Remove-Item -Recurse -Force .runtime
```

If you also want to remove managed workspaces:

```powershell
Remove-Item -Recurse -Force .governed-workspaces
```
