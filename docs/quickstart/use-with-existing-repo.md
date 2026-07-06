# Use With An Existing Repo

## Short Answer
Not through this repository's old one-click rollout path.

As of July 6, 2026, this repository no longer attaches to external target repos, no longer writes governance baselines into them, and no longer exposes attachment, session-bridge, or apply-all flows.

## What Still Works
- global user-rule sync for `~/.codex` and `~/.claude`
- target-project rule coordination audit for repositories that keep `AGENTS.md` as the shared body and `CLAUDE.md` as a thin wrapper
- self-repo verification and operator workflows in this repository
- repo-local task/status/evidence generation through `scripts/run-governed-task.py`
- host feedback, self-evolution, continuity, and packaging surfaces

## If Another Repo Needs Governance
Use that repository directly.

Recommended approach:
1. Keep that repo's own `build -> test -> contract/invariant -> hotspot` chain in that repo.
2. Keep `AGENTS.md` as the shared project-rule body there, and keep `CLAUDE.md` as a thin wrapper instead of expecting this repo to distribute project rules.
3. Use this repo to audit drift and boundaries, not to blindly overwrite target-repo rule files.
4. Keep rollout evidence and acceptance proof in that repo, not here.

## Commands To Use Here
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -Apply
```

```powershell
python scripts/verify-target-project-rules.py --targets local-ai-dev-orchestrator
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action Readiness -OpenUi
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action FeedbackReport
```

```powershell
python scripts/run-governed-task.py status --json
```

## Retired Commands
The following names are intentionally retired and now fail closed with explicit messages:
- `runtime-flow-preset`
- `runtime-flow`
- `attach-target-repo`
- `session-bridge`
- `verify-attachment`
- `govern-attachment-write`
- `decide-attachment-write`
- `execute-attachment-write`
- `ApplyAllFeatures`
- `DailyAll`
- `GovernanceBaselineAll`
- `CleanupTargets`
- `UninstallGovernance`

## Related
- [Single-Machine Runtime Quickstart](./single-machine-runtime-quickstart.md)
- [AI Coding Usage Guide](./ai-coding-usage-guide.md)
- [Host Feedback Loop](../product/host-feedback-loop.md)
