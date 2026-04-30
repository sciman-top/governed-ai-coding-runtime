# AI Coding Usage Guide

## Purpose
Show how to use this runtime with Codex/Claude Code style host workflows and what concrete help it provides during real coding tasks.

## Root Principle
- The root operating principle for this repository's host-facing workflow is `efficiency first`.
- In practice that means: low interruption, continuous execution, lower token and cost burn, and high throughput.
- Current defaults such as `gpt-5.4 + medium + never` are only temporary implementation choices under that principle.
- If future models, reasoning settings, compact thresholds, or host tooling change, keep this principle stable first; replace the current implementation only when safety and gates do not regress.

## Recommended Modes

### Entrypoint Cheat Sheet
- Operator aggregate entrypoint: `scripts/operator.ps1`
- Host feedback summary: `scripts/operator.ps1 -Action FeedbackReport`
- Target-repo daily runs and batch one-command apply: `scripts/runtime-flow-preset.ps1`
- Global/project AI rule sync: `scripts/sync-agent-rules.ps1`
- Self-repo full verification: `scripts/verify-repo.ps1 -Check All`

Common one-command flows:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action Help

pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action Readiness

pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action OperatorUi -OpenUi

pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action OperatorUi -OpenUi -UiLanguage en

pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action FeedbackReport

pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -ListTargets

pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 `
  -AllTargets `
  -ApplyGovernanceBaselineOnly `
  -Json

pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 `
  -AllTargets `
  -ApplyAllFeatures `
  -FlowMode "daily" `
  -MilestoneTag "milestone" `
  -Json

pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -Apply
```

### Operator UI
Open the default Chinese interactive console:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action OperatorUi -OpenUi
```

Open the English interactive console:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action OperatorUi -OpenUi -UiLanguage en
```

This UI runs a persistent local `127.0.0.1` interactive service. Later visits can use `http://127.0.0.1:8770/?lang=en` directly; use `scripts/operator-ui-service.ps1 -Action Status|Stop|Restart` to inspect or control the service. It can run allowlisted actions for readiness, target listing, rule drift checks, rule sync, governance baseline rollout, daily, and all-feature apply. It can target all repos or one selected target repo, exposes settings for language, mode, parallelism, fail-fast, dry-run, and milestone tag, records results in the output panel and local browser history, and refs can be clicked to preview evidence/artifact/verification files. Remove `-OpenUi` when you only want to generate a read-only `.runtime/artifacts/operator-ui/index.html` snapshot.
The `Codex` tab treats `efficiency first` as the long-lived rule and renders the current model combo only as the present implementation choice, so future model updates do not replace the underlying principle.

### Host feedback summary
If you want one place to judge whether a feature is really working in Codex and Claude, whether a problem is host-local or runtime-local, and what should be optimized next, generate the unified report instead of reading isolated logs:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action FeedbackReport
```

It summarizes:
- local Codex status
- local Claude status
- rule manifest and synchronized global targets
- latest target repo run evidence
- recommended next actions

The markdown report is written to:
- `.runtime/artifacts/host-feedback-summary/latest.md`

### Mode A: Governance Sidecar (lowest friction)
Use your host tool normally, and run this runtime for readiness, verification, and traceability.

1. Bootstrap and health checks:
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/bootstrap-runtime.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/install-repo-hooks.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```
2. Inspect runtime/Codex capability posture:
```powershell
python scripts/run-governed-task.py status --json
```

### Mode B: Attach-First Daily Flow (recommended for external repos)
Attach a target repo and run one-command daily governance flow.

1. Attach or validate target repo light pack:
```powershell
python scripts/attach-target-repo.py `
  --target-repo "<target-repo-root>" `
  --runtime-state-root "<machine-local-runtime-state-root>" `
  --repo-id "<repo-id>" `
  --primary-language "<language>" `
  --build-command "<build>" `
  --test-command "<test>" `
  --contract-command "<contract>" `
  --adapter-preference "native_attach"
```
2. Run daily governance chain:
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow.ps1 `
  -FlowMode "daily" `
  -AttachmentRoot "<target-repo-root>" `
  -AttachmentRuntimeStateRoot "<machine-local-runtime-state-root>" `
  -Mode "quick"
```

### Mode C: Governed Write Flow (for risky edits)
Use runtime-managed request/approve/execute flow for medium/high-risk writes.

1. Evaluate write governance posture:
```powershell
python scripts/run-governed-task.py govern-attachment-write `
  --attachment-root "<target-repo-root>" `
  --attachment-runtime-state-root "<machine-local-runtime-state-root>" `
  --task-id "<task-id>" `
  --tool-name "apply_patch" `
  --target-path "<target-path>" `
  --tier "medium" `
  --rollback-reference "<rollback-ref>" `
  --json
```
2. Approve (if escalated) and execute:
```powershell
python scripts/run-governed-task.py decide-attachment-write `
  --attachment-runtime-state-root "<machine-local-runtime-state-root>" `
  --approval-id "<approval-id>" `
  --decision "approve" `
  --decided-by "operator" `
  --json

python scripts/run-governed-task.py execute-attachment-write `
  --attachment-root "<target-repo-root>" `
  --attachment-runtime-state-root "<machine-local-runtime-state-root>" `
  --task-id "<task-id>" `
  --tool-name "write_file" `
  --target-path "<target-path>" `
  --tier "medium" `
  --rollback-reference "<rollback-ref>" `
  --approval-id "<approval-id>" `
  --content "<content>" `
  --json
```

## Concrete Assistance For AI Coding

| AI coding stage | Runtime assistance | Practical value |
|---|---|---|
| Session readiness | Codex capability probe/readiness and adapter-tier visibility in `status`/`doctor` | detect degrade posture early before execution |
| Repo onboarding | attach-first light-pack generation/validation | consistent repo policy/gate metadata for host sessions |
| Rule sync | `sync-agent-rules.ps1` distributes `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` from the manifest | reduce multi-host and multi-repo rule drift |
| Repeated-issue prevention | governance baseline distributes Windows process environment, canonical entrypoint, low-token, and fast/full gate policies | turn recurring fixes into target-repo state instead of reminders |
| Efficiency-first defaults | one stable default plus manual escalation only when needed | preserve continuity and lower token burn without removing an upgrade path |
| Verification | runtime-managed gate flow (`build -> test -> contract/invariant -> hotspot`) | stable acceptance checks and reproducible gate artifacts |
| Risky writes | policy + approval + fail-closed behavior for medium/high tiers | prevents silent high-risk mutations |
| Delivery evidence | evidence/handoff/replay refs linked to task/run | auditable handoff and rollback trail |
| Multi-repo operations | preset/daily flows and multi-repo trial surfaces | repeatable governance posture across repositories |

## Boundary
- This runtime is a governance/runtime layer over upstream hosts, not a replacement host UI.
- Native attach remains environment-dependent and may degrade to `process_bridge` or `manual_handoff`.
- Do not claim universal full takeover across all repos/environments/high-risk workflows.

## Related
- [Use With An Existing Repo](./use-with-existing-repo.md)
- [在现有仓库中使用](./use-with-existing-repo.zh-CN.md)
- [Codex CLI/App Integration Guide](../product/codex-cli-app-integration-guide.md)
- [Codex / Claude Host Feedback Loop](../product/host-feedback-loop.md)
- [Codex CLI/App 集成指南](../product/codex-cli-app-integration-guide.zh-CN.md)
