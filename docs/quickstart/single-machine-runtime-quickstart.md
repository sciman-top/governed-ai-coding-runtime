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
- `.runtime/tasks`
- `.runtime/artifacts`
- `.runtime/replay`
- JSON status output showing `total_tasks`

## Create And Run A Runtime Smoke Task

```powershell
python scripts/run-governed-task.py create --goal "inspect runtime quickstart"
```

```powershell
python scripts/run-governed-task.py run --json
```

Expected runtime outputs:
- persisted task record under `.runtime/tasks`
- gate artifacts under `.runtime/artifacts/<task>/<run>/verification-output/`
- evidence bundle under `.runtime/artifacts/<task>/<run>/evidence/`
- handoff package under `.runtime/artifacts/<task>/<run>/handoff/`
- a local runtime smoke result rather than a direct Codex-managed coding run

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
If you need to reset only local runtime state:

```powershell
Remove-Item -Recurse -Force .runtime
```

If you also want to remove managed workspaces:

```powershell
Remove-Item -Recurse -Force .governed-workspaces
```
