# Governed AI Coding Runtime English Guide

## Current Status
`Foundation / GAP-020` through `GAP-023` are complete, and the active execution queue now starts at `Full Runtime / GAP-024`.

This repository is usable today as a governed runtime contract layer, not as a deployable product service.

Available now:

- Repository verification over docs, schemas, catalog, scripts, and runtime contract tests.
- Foundation-grade build and doctor gates.
- A first scripted read-only trial.
- Python contract primitives for task intake, repo profiles, approvals, write governance, verification, delivery handoff, eval/trace, second-repo pilot checks, and a minimal control-console facade.

Not available yet:

- No production runtime service.
- No database or durable workflow worker.
- No real web console.
- No package build artifact or release pipeline.
- `build` and `hotspot/doctor` now have Foundation-grade live entrypoints, but they are not production packaging or service-health checks yet.

## How To Use

### 1. Verify The Repository
Run from the repository root:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
```

This checks:

- runtime contract tests
- JSON Schema parsing
- schema example validation
- schema catalog pairing
- active Markdown links
- backlog / YAML ID drift
- PowerShell script parsing

Runtime contract tests only:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
```

Direct Python unittest command:

```powershell
python -m unittest discover -s tests/runtime -p "test_*.py" -v
```

### 2. Run The First Read-Only Trial
The current trial is scripted and read-only. It does not invoke Codex directly and does not write to a target repository.

```powershell
python scripts/run-readonly-trial.py `
  --goal "inspect repository" `
  --scope "readonly trial" `
  --acceptance "readonly request accepted" `
  --repo-profile "schemas/examples/repo-profile/python-service.example.json" `
  --target-path "src/service.py" `
  --max-steps 1 `
  --max-minutes 5
```

Expected output is JSON with:

- `repo_id`
- `accepted_count`
- `summary`
- `auth_ownership`
- `unsupported_capability_behavior`

### 3. Use Runtime Contract Primitives
Core code lives in:

```text
packages/contracts/src/governed_ai_coding_runtime_contracts/
```

Important modules:

- `task_intake.py`: task input and lifecycle transition validation
- `repo_profile.py`: repo profile loading and admission minimums
- `tool_runner.py`: read-only tool request governance
- `workspace.py`: isolated workspace allocation and write path validation
- `write_policy.py`: medium/high write policy defaults
- `approval.py`: approval request state and audit trail
- `write_tool_runner.py`: write-side governance and rollback references
- `verification_runner.py`: quick/full verification plans and artifacts
- `delivery_handoff.py`: delivery handoff packages
- `eval_trace.py`: eval baseline and trace grading
- `second_repo_pilot.py`: second repo profile reuse pilot
- `control_console.py`: minimal approval/evidence console facade

Example:

```powershell
$env:PYTHONPATH="packages/contracts/src"
python - <<'PY'
from governed_ai_coding_runtime_contracts.repo_profile import load_repo_profile
from governed_ai_coding_runtime_contracts.write_policy import resolve_write_policy

profile = load_repo_profile("schemas/examples/repo-profile/python-service.example.json")
policy = resolve_write_policy(profile)
print(profile.repo_id)
print(policy.approval_mode("high"))
PY
```

## Reading Order
For tool usage:

1. [This guide](README.en.md)
2. [Docs Index](docs/README.md)
3. [First Read-Only Trial](docs/product/first-readonly-trial.md)
4. [Write Policy Defaults](docs/product/write-policy-defaults.md)
5. [Approval Flow](docs/product/approval-flow.md)
6. [Write-Side Tool Governance](docs/product/write-side-tool-governance.md)
7. [Verification Runner](docs/product/verification-runner.md)
8. [Delivery Handoff](docs/product/delivery-handoff.md)
9. [Runbooks](docs/runbooks/README.md)

For product planning:

1. [90-Day Plan](docs/roadmap/governed-ai-coding-runtime-90-day-plan.md)
2. [Issue-Ready Backlog](docs/backlog/issue-ready-backlog.md)
3. [PRD](docs/prd/governed-ai-coding-runtime-prd.md)
4. [Target Architecture](docs/architecture/governed-ai-coding-runtime-target-architecture.md)

## Completion Level
Completed:

- MVP contract and verification slices through `Phase 4`
- The next active implementation queue is `Full Runtime / GAP-024+`

Current verification baseline:

- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
- `python -m unittest discover -s tests/runtime -p "test_*.py" -v`

## Recommended Next Productization Step
If the project continues toward a deployable runtime, the next slice should likely:

1. Add real Python package metadata and a fuller release build.
2. Add durable storage or a workflow worker.
3. Connect the current `ControlPlaneConsole` facade to a CLI or minimal web UI.
4. Expand the Foundation doctor into a richer runtime health entrypoint.
