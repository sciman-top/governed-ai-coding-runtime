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
1. Record `**项目契约**: 2.0`, `**全局规则复核**: 9.55`, landing, target, repository truth, real gates, evidence, and rollback in the target root `AGENTS.md`.
2. Keep `AGENTS.md` host-neutral and retain the fixed `build -> test -> contract/invariant -> hotspot` order. Do not duplicate global R/E text or host-loading tutorials.
3. Make the first physical line of target `CLAUDE.md` the raw, BOM-free `@AGENTS.md` import. Keep it to that single line when no real repository-specific Claude delta exists.
4. Add targets explicitly to `rules/target-project-rule-coordination.json`, including `github_repository` and `ci_workflow_path`. The control repo audits but does not store or blindly overwrite target bodies.
5. Copy the reviewed `rules/templates/github/agent-rule-contract.yml` bytes to the target's declared workflow path and mention that path in `AGENTS.md`. The local workflow verifies only the rule contract and never replaces product gates.
6. Keep rollout evidence in each target; keep global-sync backups, aggregate-CI evidence, and loading-probe evidence in this control repo.

The current allowlist contains `ai-content-delivery-studio`, `classroom-answer-toolkit`, `ClassroomToolkit`, `github-toolkit`, `k12-question-graph`, `local-ai-dev-orchestrator`, `qq-codex-bot`, `skills-manager`, and `vps-ssh-launcher`. Other sibling directories still receive user-level rules but are not project-rule targets.

## Commands To Use Here
```powershell
python scripts/verify-agent-rule-family.py
python scripts/verify-target-project-rules.py --require-all
python scripts/export-target-rule-ci-matrix.py
python scripts/sync-agent-rules.py --scope All --fail-on-change
```

Only after those checks pass, run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -Apply`, verify zero drift, and run fresh Codex/Claude loading probes.

Rollback is layered: restore global copies from the sync backup plus the reverted source release; revert only each target's `AGENTS.md / CLAUDE.md / rollout evidence`; never restore unrelated dirty-worktree changes.

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
