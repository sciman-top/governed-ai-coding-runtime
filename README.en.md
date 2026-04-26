# Governed AI Coding Runtime English Guide

## Current Status
`Foundation / GAP-020` through `GAP-023`, `Full Runtime / GAP-024` through `GAP-028`, `Public Usable Release / GAP-029` through `GAP-032`, `Maintenance Baseline / GAP-033` through `GAP-034`, and `Interactive Session Productization / GAP-035` through `GAP-039` are complete.

That means the first landed hybrid productization boundary is now present. It does not mean every upstream host already has a full runtime-owned real-write execution path.

This repository is usable today as a local governed runtime with the first attach-first productization slice landed; `Strategy Alignment Gates / GAP-040..044` are complete on the current branch baseline and remain encoded as satisfied hardening dependencies around that result.

Positioning and non-goals:

- governance/runtime layer for AI coding agents, not another execution host
- not a wrapper-first orchestration product
- not a generation-guardrail product
- strategy doc: [Positioning And Competitive Layering](docs/strategy/positioning-and-competitive-layering.md)
- borrowing matrix: [Runtime Governance Borrowing Matrix](docs/research/runtime-governance-borrowing-matrix.md)
- boundary ADR: [ADR-0007 Source-Of-Truth And Runtime Contract Bundle](docs/adrs/0007-source-of-truth-and-runtime-contract-bundle.md)

Available now:

- Repository verification over docs, schemas, catalog, scripts, and runtime contract tests.
- Foundation-grade build and doctor gates.
- A first scripted read-only trial baseline.
- Codex capability readiness surfaced from runtime status/doctor (adapter tier, flow kind, degrade reasons, remediation hints).
- Runtime-managed gate execution through session bridge (`run_quick_gate` / `run_full_gate`, with optional `plan_only`).
- Runtime-managed attached write governance flow through session bridge (`write_request` / `write_approve` / `write_execute` / `write_status`) with approval/evidence/handoff/replay refs.
- A safe-mode Codex adapter smoke trial that reports task, binding, evidence, and verification wiring.
- A profile-based multi-repo trial runner that reports per-repo posture, adapter tier, verification refs, evidence refs, and follow-ups.
- Attachment of an external target repo such as `..\ClassroomToolkit`, including `.governed-ai` light-pack generation or validation plus status/doctor/session-bridge posture checks.
- A CLI-first governed runtime smoke path with persisted artifacts, verification outputs, evidence bundles, handoff packages, replay references, and runtime status.
- Python contract primitives for task intake, repo profiles, approvals, write governance, execution runtime, artifact/replay persistence, verification, delivery handoff, eval/trace, second-repo pilot checks, and a minimal control-console facade.

Not available yet:

- No database or multi-machine workflow worker.
- The package bundle is a local distribution directory, not an installer or published channel.
- The richer operator UI is a local HTML surface, not a long-running web service.
- Full runtime-owned replacement of upstream Codex host UX is not implemented.
- `native_attach` is environment-dependent; degraded posture (`process_bridge` / `manual_handoff`) remains valid when host capability is weaker.
- Universal full-takeover claims across all external repos and high-risk workflows are still out of scope.
- `GAP-045..060` is the direct path to full hybrid final-state closure and is complete; `GAP-061..068` is the governance-only follow-on lane after `GAP-060` and is also complete (2026-04-20), without being back-written into the final-state closure proof itself.
- `GAP-090..092` is complete as the long-term gap trigger-audit queue; `GAP-093`, the `GAP-094` execution-containment contract slice, and the `GAP-095` provenance floor are complete; no `LTP-01..06` package starts now, and all remain deferred pending future trigger evidence.

## Can I Use This With Another Repo?
Yes, with the current boundary.

For a repo such as `..\ClassroomToolkit`, you can already:

- generate or validate `.governed-ai/repo-profile.json` and `.governed-ai/light-pack.json`
- bind repo-local declarations to machine-local runtime state
- inspect attachment posture through `status` and `doctor`
- execute runtime-managed gate flows through `session-bridge`
- execute governed write flows with explicit approval/evidence/handoff/replay linkage
- run Codex smoke-trial and multi-repo trial surfaces against that attached posture

What you should **not** claim yet:

- not that this runtime fully replaces Codex host execution in every environment
- that all external repos and all high-risk workflows are universally runtime-owned end-to-end

## Quick Usage Paths (Recommended)
- Path A (governance sidecar, least friction): keep coding in Codex/Claude Code and run `bootstrap + doctor + verify-repo -Check All + status`.
- Path B (attach-first for external repos): run `attach-target-repo`, then use `runtime-flow.ps1 -FlowMode daily` as your daily governance chain.
- Path C (risky writes): run `govern-attachment-write -> decide-attachment-write -> execute-attachment-write` for medium/high-risk mutations.

## Concrete AI-Coding Assistance
- Capability visibility before execution: see `adapter_tier`, `flow_kind`, and degrade reasons early.
- Canonical acceptance chain: runtime-managed `build -> test -> contract/invariant -> hotspot`.
- Risky write safeguards: policy + approval + fail-closed behavior for medium/high tiers.
- Traceable delivery: approval/evidence/handoff/replay refs are linked to task/run identity.
- Multi-repo reuse: apply the same governance contract via `.governed-ai` light packs and preset flows.
- Host-decoupled governance: preserves user-owned upstream auth and avoids host lock-in.

## How To Use

### 1. Verify The Repository
Run from the repository root:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/bootstrap-runtime.ps1
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/install-repo-hooks.ps1
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
- [Single-Machine Runtime Quickstart (Chinese)](docs/quickstart/single-machine-runtime-quickstart.zh-CN.md)
- [AI Coding Usage Guide](docs/quickstart/ai-coding-usage-guide.md)
- [AI 编码使用指南](docs/quickstart/ai-coding-usage-guide.zh-CN.md)
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

### 3. Run The Codex Adapter Smoke Trial
This trial defaults to safe mode. It proves the direct-adapter contract surface, not a real high-risk write path.

```powershell
python scripts/run-codex-adapter-trial.py `
  --repo-id "python-service" `
  --task-id "task-codex-trial" `
  --binding-id "binding-python-service"
```

Expected output includes:

- `adapter_tier`
- `task_id`
- `binding_id`
- `evidence_refs`
- `verification_refs`
- `unsupported_capability_behavior`

### 4. Run One Governed Task End To End
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

### 5. Run The Multi-Repo Trial Runner
The runner defaults to the two sample repo profiles already present in the repository.

```powershell
python scripts/run-multi-repo-trial.py
```

Expected per-repo output includes:

- `attachment_posture`
- `adapter_tier`
- `verification_refs`
- `evidence_refs`
- `handoff_refs`
- `follow_ups`

### 6. Use It With An Existing Repo
For an external repo such as `..\ClassroomToolkit`, start here:

- [Use With An Existing Repo](docs/quickstart/use-with-existing-repo.md)
- [Use With An Existing Repo (Chinese)](docs/quickstart/use-with-existing-repo.zh-CN.md)
- [Target Repo Attachment Flow](docs/product/target-repo-attachment-flow.md)
- [Target Repo Attachment Flow (Chinese)](docs/product/target-repo-attachment-flow.zh-CN.md)

That guide includes a concrete `ClassroomToolkit` attachment command.

Daily one-command check:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-check.ps1 `
  -AttachmentRoot "..\ClassroomToolkit" `
  -AttachmentRuntimeStateRoot ".runtime\attachments\classroomtoolkit" `
  -Mode "quick"
```

Two-mode one-command flow:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow.ps1 `
  -FlowMode "daily" `
  -AttachmentRoot "..\ClassroomToolkit" `
  -AttachmentRuntimeStateRoot ".runtime\attachments\classroomtoolkit" `
  -Mode "quick"
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-classroomtoolkit.ps1 -FlowMode "daily"
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target "skills-manager" -FlowMode "daily" -SkipVerifyAttachment
```

### 7. Use Runtime Contract Primitives
Core code lives in:

```text
packages/contracts/src/governed_ai_coding_runtime_contracts/
```

Planning entrypoints:
- [Hybrid Final-State Master Outline](docs/architecture/hybrid-final-state-master-outline.md)
- [Direct-To-Hybrid Final-State Roadmap](docs/roadmap/direct-to-hybrid-final-state-roadmap.md)
- [Direct-To-Hybrid Final-State Implementation Plan](docs/plans/direct-to-hybrid-final-state-implementation-plan.md)
- [Governance Optimization Lane Roadmap](docs/roadmap/governance-optimization-lane-roadmap.md)
- [Governance Optimization Lane Implementation Plan](docs/plans/governance-optimization-lane-implementation-plan.md)

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
3. [AI Coding Usage Guide](docs/quickstart/ai-coding-usage-guide.md)
4. [First Read-Only Trial](docs/product/first-readonly-trial.md)
5. [Use With An Existing Repo](docs/quickstart/use-with-existing-repo.md)
6. [Use With An Existing Repo (Chinese)](docs/quickstart/use-with-existing-repo.zh-CN.md)
7. [Codex Direct Adapter](docs/product/codex-direct-adapter.md)
8. [Multi-Repo Trial Loop](docs/product/multi-repo-trial-loop.md)
9. [Write Policy Defaults](docs/product/write-policy-defaults.md)
10. [Approval Flow](docs/product/approval-flow.md)
11. [Write-Side Tool Governance](docs/product/write-side-tool-governance.md)
12. [Verification Runner](docs/product/verification-runner.md)
13. [Delivery Handoff](docs/product/delivery-handoff.md)
14. [Runbooks](docs/runbooks/README.md)

For product planning:

1. [90-Day Plan](docs/roadmap/governed-ai-coding-runtime-90-day-plan.md)
2. [Issue-Ready Backlog](docs/backlog/issue-ready-backlog.md)
3. [PRD](docs/prd/governed-ai-coding-runtime-prd.md)
4. [Target Architecture](docs/architecture/governed-ai-coding-runtime-target-architecture.md)
5. [Positioning And Competitive Layering](docs/strategy/positioning-and-competitive-layering.md)
6. [Generic Target-Repo Attachment Blueprint](docs/architecture/generic-target-repo-attachment-blueprint.md)
7. [Interactive Session Productization Implementation Plan](docs/plans/interactive-session-productization-implementation-plan.md)
8. [Governance Runtime Strategy Alignment Plan](docs/plans/governance-runtime-strategy-alignment-plan.md)

## Completion Level
Completed:

- MVP contract and verification slices through `Phase 4`
- `Full Runtime / GAP-024` through `GAP-028`
- `Public Usable Release / GAP-029` through `GAP-032`
- `Maintenance Baseline / GAP-033` through `GAP-034`

Current productization slice:

- `Interactive Session Productization / GAP-035` through `GAP-039` are complete on the current branch baseline
- `Strategy Alignment Gates / GAP-040` through `GAP-044` are complete on the current branch baseline

Current verification baseline:

- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
- `python -m unittest discover -s tests/runtime -p "test_*.py" -v`

## Maintenance Policy
- [Codex CLI/App Integration Guide](docs/product/codex-cli-app-integration-guide.md)
- [Codex CLI/App 集成指南](docs/product/codex-cli-app-integration-guide.zh-CN.md)
- [Runtime Compatibility And Upgrade Policy](docs/product/runtime-compatibility-and-upgrade-policy.md)
- [Maintenance, Deprecation, And Retirement Policy](docs/product/maintenance-deprecation-and-retirement-policy.md)

