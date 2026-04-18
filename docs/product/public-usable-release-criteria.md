# Public Usable Release Criteria

## Goal
Define the minimum bar for calling the local governed runtime publicly usable on one machine.

## Required Capabilities
- a new user can bootstrap the runtime with `scripts/bootstrap-runtime.ps1`
- a governed task can be created and run through `scripts/run-governed-task.py`
- `build -> test -> contract/invariant -> hotspot` can run locally from documented commands
- runtime artifacts, evidence, verification, and handoff outputs are inspectable from local paths
- the richer local operator surface can be generated through `scripts/serve-operator-ui.py`
- a package bundle can be assembled through `scripts/package-runtime.ps1`
- at least one sample repo profile can follow the documented runtime path

## Required Commands

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/bootstrap-runtime.ps1
```

```powershell
python scripts/run-governed-task.py run --json
```

```powershell
python scripts/serve-operator-ui.py
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/package-runtime.ps1
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```

## Exit Rule
`Public Usable Release / GAP-029` through `GAP-032` are complete only when all required commands succeed and the resulting docs, artifacts, packaging output, and compatibility posture agree with each other.

## Boundary Note
The `scripts/run-governed-task.py` command proves the local governed runtime path. It should not be interpreted as proof that Codex CLI/App is already directly invoked through a managed runtime adapter.
