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

Complete hybrid final-state certification posture:

- `GAP-104..111` are complete on the current branch baseline; the certification evidence is `docs/change-evidence/20260427-gap-111-complete-hybrid-final-state-certification.md`.
- Certification means the repo-local contract bundle, machine-local durable governance kernel, attach-first host adapters, and same-contract verification/delivery plane are backed by current runtime code, docs, tests, all-target workload evidence, and claim-drift gates.
- This does not mean this project takes over upstream Codex host UI ownership. Upstream authentication remains user-owned, and `native_attach` still degrades explicitly to `process_bridge` / `manual_handoff` when host capability is absent.
- It does not claim unconditional takeover of every future external repo or every future high-risk workflow. New LTP implementation queues must use ids beyond `GAP-111` and pass a scope fence.
- `LTP-01..06` remain trigger-based candidates: this certification lands or covers the required transition-stack capabilities without introducing Temporal, OPA, event bus, object store, full operations stack, or external signing as mandatory packages.

## Current Controlled-Evolution Posture
`GAP-120..129` put 30-day evolution review, AI coding experience capture, and low-risk proposal/disabled-skill materialization under governance. They still do not auto-apply policy, auto-enable skills, sync target repos, push, or merge.

`GAP-130` is complete as the scope rebaseline and `GAP-131` is complete as the machine-checkable capability portfolio classifier baseline; `GAP-132..139` are the planned `Governance Hub + Reusable Contract + Controlled Evolution` implementation queue. Codex and Claude Code are cooperation hosts, not competitors; Claude Code is treated as local use through third-party Anthropic-compatible providers such as GLM or DeepSeek, not as an official subscription dependency; Hermes/OpenHands/SWE-agent/Letta/Mem0/Aider-style projects are selective mechanism sources. Completion requires real target-repo effect feedback, not only new docs or generated candidates. Self-evolution must evaluate the existing capability portfolio and decide `add/keep/improve/merge/deprecate/retire/delete_candidate` from evidence instead of only adding features.

The best engineering final state is now fixed as `Governance Hub + Reusable Contract + Controlled Evolution loop + outer AI intelligent review/generation capability`: a governance center, reusable control contract, controlled evolution loop, and outer-AI review/generation capability, not a new host product.

The core principle is now strengthened as `Automation-first, outer-AI-assisted, gate-controlled evolution`: this project should highly automate its deterministic governance work and may automatically trigger outer AI for intelligent review, knowledge extraction, candidate generation, and evolution proposals; outer AI output must first become a structured candidate and pass risk classification, machine gates, evidence, rollback, and required review boundaries before it can take effect.

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

## Current Main Entrypoints And One-Command Apply
- Operator aggregate entrypoint: `scripts/operator.ps1`. It collects readiness checks, rule drift/sync, target-repo batch flows, and operator UI rendering behind one action-oriented entrypoint; default `-Action Help`.
- Core-principle change candidate entrypoint: `scripts/operator.ps1 -Action CorePrincipleMaterialize`. By default it only reports a dry-run candidate; after explicit permission, add `-ConfirmCorePrincipleProposalWrite` to write reviewable proposal/manifest files; for audit-only evidence, add `-WriteCorePrincipleDryRunReport` to write only the dry-run report. These paths still do not directly change active core-principles policy, specs, verifiers, or target repositories.
- Target-repo daily/batch entrypoint: `scripts/runtime-flow-preset.ps1`. It reads `docs/targets/target-repos-catalog.json` and supports one target or all active targets.
- Agent-rule sync entrypoint: `scripts/sync-agent-rules.ps1`. It reads `rules/manifest.json` and syncs global/project `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md`.
- Self-repo verification entrypoint: `scripts/verify-repo.ps1 -Check All`.

Inspect the operator entrypoint and recommended paths:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action Help
```

AI recommended local readiness:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action Readiness
```

Open the interactive local operator UI. It defaults to Chinese and starts a localhost service:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action OperatorUi -OpenUi
```

Open the English interactive UI:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action OperatorUi -OpenUi -UiLanguage en
```

How to use the UI: `-OpenUi` starts a persistent local `127.0.0.1` interactive control console and opens the browser; later visits can use `http://127.0.0.1:8770/?lang=en` directly. Use `scripts/operator-ui-service.ps1 -Action Status|Stop|Restart` to inspect or control the service, and `-Action EnableAutoStart|DisableAutoStart|AutoStartStatus` to manage logon autostart. The page can run allowlisted actions for repo readiness, target listing, rule drift checks, rule sync, governance baseline rollout, daily, and all-feature apply. It can target all repos or one selected target repo, exposes settings for language, mode, parallelism, fail-fast, dry-run, and milestone tag, records results in the output panel and local browser history, and refs can be clicked to preview evidence/artifact/verification files. The `Codex` tab shows local account, usage, and config health, and now separates the long-lived core principle from the current implementation: the principle is efficiency first, meaning low interruption, continuous execution, lower token and cost burn, and high throughput; `gpt-5.4 + medium + never` is shown only as the current temporary choice, and `model_auto_compact_token_limit = 220000` remains the paired compact threshold. When future models, parameters, or tooling become the new default, preserve that principle first and replace the current implementation only when safety and gates do not regress. The `Claude` tab now centralizes third-party provider status, provider switching, recommended-config preview/apply, and safe previews for local `settings.json`, `provider-profiles.json`, and the switcher script. Without `-OpenUi`, the script only writes a read-only `.runtime/artifacts/operator-ui/index.html` snapshot and prints a JSON `file_url`.

List available targets first:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -ListTargets
```

Force-sync governance baseline only:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 `
  -AllTargets `
  -ApplyGovernanceBaselineOnly `
  -Json
```

Apply all current target-repo features:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 `
  -AllTargets `
  -ApplyAllFeatures `
  -FlowMode "daily" `
  -MilestoneTag "milestone" `
  -Json
```

Sync Codex/Claude/Gemini global and project rules:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -Apply
```

Check rule drift without writing:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -FailOnChange
```

## Concrete AI-Coding Assistance
- Capability visibility before execution: see `adapter_tier`, `flow_kind`, and degrade reasons early.
- Canonical acceptance chain: runtime-managed `build -> test -> contract/invariant -> hotspot`.
- Stable rule distribution: manage global/project agent rules through `rules/manifest.json` so Codex, Claude, and Gemini read consistent repo rules.
- Repeated-issue prevention: sync Windows process environment, canonical entrypoint, low-token interaction, milestone commit, and fast/full gate policies into target repos instead of relying on chat reminders.
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

