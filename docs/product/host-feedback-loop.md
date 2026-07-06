# Host Feedback Loop

## Purpose
Provide one repeatable repo-local loop for judging host health, rule drift, runtime gate health, and the next bounded maintenance action.

## Current Boundary
- host feedback is now host-only and repo-local
- it does not depend on target-repo daily runs
- it does not require attachment posture or session-bridge evidence
- it remains evidence-first and fail-closed

## Recommended Loop
1. Run readiness:
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action Readiness -OpenUi`
2. Check global rule drift:
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action RulesDryRun`
3. Generate the unified feedback report:
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action FeedbackReport`
4. Close out with the full repo gate:
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`

## What The Report Should Answer
- Are Codex and Claude locally healthy enough for the current workload?
- Are global rule copies in sync with `rules/manifest.json`?
- Did the repo-local hard-gate chain pass?
- Is self-evolution still blocked, reviewable, or ready for bounded materialization?
- What is the next safe action according to `select-next-work`?

## Primary Evidence
- `.runtime/artifacts/host-feedback-summary/latest.md`
- latest self-evolution recommendation artifact
- latest self-evolution promotion artifact
- `scripts/verify-repo.ps1 -Check All`

## Minimum Acceptance
- `FeedbackReport` succeeds
- `RulesDryRun` shows no unexpected drift
- `verify-repo.ps1 -Check All` passes
- the feedback report gives a concrete next action instead of an ambiguous manual interpretation

## Related
- [AI Coding Usage Guide](../quickstart/ai-coding-usage-guide.md)
- [Agent Continuity Guide](./agent-continuity.md)
