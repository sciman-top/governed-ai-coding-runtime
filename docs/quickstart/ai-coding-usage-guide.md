# AI Coding Usage Guide

## Purpose
Describe the live, repo-local workflow for using this repository alongside host tools such as Codex and Claude Code.

## Current Product Boundary
- This repository is a governance/runtime sidecar, not a replacement host.
- It no longer rolls changes out into external target repos.
- It no longer owns attachment, session-bridge, or governed write bridge flows.
- It still owns self-repo gates, global rule sync, host feedback, self-evolution evidence, continuity, and packaging.

## Recommended Entry Points
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action Help
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action Readiness -OpenUi
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action FeedbackReport
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action SelfEvolutionRecommend
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -Apply
```

## Practical Modes

### Mode A: Self-Repo Readiness
Use this when changing code in this repository.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
```

### Mode B: Host Feedback
Use this when you need one place to judge host health, rule drift, and the next bounded maintenance action.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action FeedbackReport
```

Outputs:
- `.runtime/artifacts/host-feedback-summary/latest.md`
- latest self-evolution recommendation and promotion artifacts

### Mode C: Repo-Local Task Execution
Use this for runtime-managed task/evidence/handoff generation inside this repository.

```powershell
python scripts/run-governed-task.py run --mode quick --json
```

## Retired Workflows
Do not use this repository for:
- target-repo attach or baseline rollout
- target-repo daily or batch apply-all
- session-bridge posture, evidence, or handoff commands
- governed attached-write request/approve/execute flows

Retired names remain fail closed with explicit retirement messages.

## Related
- [Use With An Existing Repo](./use-with-existing-repo.md)
- [Host Feedback Loop](../product/host-feedback-loop.md)
- [Agent Continuity Guide](../product/agent-continuity.md)
