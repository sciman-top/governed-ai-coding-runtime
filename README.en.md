# Governed AI Coding Runtime English Guide

## Current Status
`Foundation / GAP-020` through `GAP-023`, `Full Runtime / GAP-024` through `GAP-028`, `Public Usable Release / GAP-029` through `GAP-032`, and `Maintenance Baseline / GAP-033` through `GAP-034` are complete.

That means the local single-machine runtime baseline is landed. It does not mean the final product boundary is complete.

This repository is usable today as a local governed runtime baseline with explicit maintenance policy. The active next-step queue is now `Interactive Session Productization / GAP-035..039`.

Available now:

- Repository verification over docs, schemas, catalog, scripts, and runtime contract tests.
- Foundation-grade build and doctor gates.
- A first scripted read-only trial.
- A CLI-first governed runtime smoke path with persisted artifacts, verification outputs, evidence bundles, handoff packages, replay references, and runtime status.
- Python contract primitives for task intake, repo profiles, approvals, write governance, execution runtime, artifact/replay persistence, verification, delivery handoff, eval/trace, second-repo pilot checks, and a minimal control-console facade.

Not available yet:

- No database or multi-machine workflow worker.
- The package bundle is a local distribution directory, not an installer or published channel.
- The richer operator UI is a local HTML surface, not a long-running web service.
- No direct Codex adapter yet; Codex CLI/App remains a compatible current-state boundary rather than a fully runtime-owned coding backend.
- No generic target-repo attachment pack or attach-first session bridge yet.

## How To Use

### 1. Verify The Repository
Run from the repository root:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/bootstrap-runtime.ps1
```

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

Quickstart:
- [Single-Machine Runtime Quickstart](docs/quickstart/single-machine-runtime-quickstart.md)
- [Codex CLI/App Integration Guide](docs/product/codex-cli-app-integration-guide.md)
- [Codex CLI/App 集成指南](docs/product/codex-cli-app-integration-guide.zh-CN.md)

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

### 3. Run One Governed Task End To End
The `run-governed-task.py` path below should currently be read as a runtime smoke path, not as direct Codex-driven coding execution.

```powershell
python scripts/run-governed-task.py status --json
```

```powershell
python scripts/run-governed-task.py run --json
```

Expected output includes:

- `task_id`
- `state`
- `active_run_id`
- `verification_refs`
- `evidence_refs`
- `artifact_refs`

### 4. Use Runtime Contract Primitives
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
- `execution_runtime.py`: local task-to-run orchestration
- `worker.py`: synchronous single-machine worker interface
- `artifact_store.py`: local artifact persistence and risk classification
- `replay.py`: failure signatures and replay references
- `verification_runner.py`: quick/full verification plans and artifacts
- `delivery_handoff.py`: delivery handoff packages
- `eval_trace.py`: eval baseline and trace grading
- `second_repo_pilot.py`: second repo profile reuse pilot
- `runtime_status.py`: CLI-first operator read model
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
5. [Generic Target-Repo Attachment Blueprint](docs/architecture/generic-target-repo-attachment-blueprint.md)
6. [Interactive Session Productization Plan](docs/plans/interactive-session-productization-plan.md)

## Completion Level
Completed:

- MVP contract and verification slices through `Phase 4`
- `Full Runtime / GAP-024` through `GAP-028`
- `Public Usable Release / GAP-029` through `GAP-032`
- `Maintenance Baseline / GAP-033` through `GAP-034`

Active next queue:

- `Interactive Session Productization / GAP-035` through `GAP-039`

Current verification baseline:

- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
- `python -m unittest discover -s tests/runtime -p "test_*.py" -v`

## Maintenance Policy
- [Codex CLI/App Integration Guide](docs/product/codex-cli-app-integration-guide.md)
- [Codex CLI/App 集成指南](docs/product/codex-cli-app-integration-guide.zh-CN.md)
- [Runtime Compatibility And Upgrade Policy](docs/product/runtime-compatibility-and-upgrade-policy.md)
- [Maintenance, Deprecation, And Retirement Policy](docs/product/maintenance-deprecation-and-retirement-policy.md)
