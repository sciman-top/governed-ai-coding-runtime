# Codex / Claude Host Feedback Loop

## Purpose
Explain how to get a clear, repeatable feedback loop for this repository when coding through `Codex` and `Claude Code`, instead of relying on scattered command output.

## Core Principles
- Keep `efficiency first` as the higher-order rule for host-facing defaults: low interruption, continuous execution, lower token and cost burn, and high throughput.
- Treat concrete model combos, reasoning levels, compact thresholds, and provider choices as temporary implementations under that rule.
- Separate host problems, rule drift, runtime degradation, and target-repo governance failures.
- Make optimization decisions from machine evidence first: `status`, `adapter_tier`, `closure_state`, `write_status`, and evidence refs.
- Keep one fixed entrypoint and one fixed evidence shape so every review uses the same yardstick.

## Recommended Loop
1. Generate readiness and the interactive operator surface:
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action Readiness -OpenUi`
2. Check rule distribution drift:
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action RulesDryRun`
3. Generate the host feedback summary:
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action FeedbackReport`
4. Run real target-repo daily evidence:
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action DailyAll -Mode quick -OpenUi`
5. Close out with the full gate:
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`

## Standard Feedback Dimensions

| Dimension | Main question | Evidence |
|---|---|---|
| Host entrypoint | Are we using the real `codex` / `claude` entrypoint we think we are using? | local config, provider/account status, executable path |
| Rule effect | Did the rules only change at source, or were they synchronized downstream? | `rules/manifest.json`, drift check, synchronized global copies |
| Capability posture | Is the current host in `native_attach`, `process_bridge`, or `manual_handoff`? | `adapter_tier`, `flow_kind`, `unsupported_capabilities` |
| Claude workload probe | Can Claude Code actually expose managed settings/hooks, session/resume, and structured evidence for this repo? | `claude_workload.readiness`, `probe_commands`, trial refs |
| Gate execution | Did we actually run the full gate chain? | `build -> test -> contract/invariant -> hotspot` |
| Write governance | Did risky edits really pass through request/approve/execute? | `approval_status`, `write_status`, handoff/replay refs |
| Evidence clarity | Can the output explain why a path passed, degraded, or blocked? | `evidence_link`, `artifact_refs`, `verification_refs` |
| Dual-host parity | Are Codex and Claude equally supported in governance outcome? | parity matrix, latest target runs, feedback summary |
| Batch stability | Does the same posture survive all-target daily execution? | `target-repo-runs/*.json`, governance consistency checks |

## Unified Report Entrypoint

### One-command feedback report
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action FeedbackReport
```

It runs:

```powershell
python scripts/host-feedback-summary.py --assert-minimum --write-markdown .runtime/artifacts/host-feedback-summary/latest.md
```

The report summarizes:
- local Codex status
- local Claude status
- live Claude Code workload adapter readiness
- rule manifest and synchronized global targets
- Codex/Claude parity documentation surface
- latest target-repo run evidence
- recommended next actions

The markdown report is written to:
- `.runtime/artifacts/host-feedback-summary/latest.md`

## Reading The Result

### Host status unhealthy, target runs still healthy
Treat it as a host-local configuration problem first, not as a runtime regression.

### Current combo looks outdated, but the loop still works
Update the concrete host default if needed, but preserve the higher-order `efficiency first` rule instead of replacing it with model-specific wording.

### Manifest healthy, synchronized copies missing
Run:
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -Apply
```

### `adapter_tier` degraded, gates still passing
The governance outcome is still valid, but the host capability is not at its best posture. Improve the host boundary before claiming the whole feature regressed.

### Claude host is healthy, but `claude_workload` is degraded or blocked
The Claude CLI/provider/MCP layer can be healthy while the coding workload path is still incomplete. Use `claude_workload.readiness.status`, `adapter_tier`, `unsupported_capabilities`, and `probe_commands` to decide whether the problem is missing managed settings/hooks, missing session/resume flags, or missing structured hook-event evidence.

### No target-run evidence
You only have static self-health, not real workload feedback. Do not use that to claim Codex/Claude effectiveness.

### Target-run evidence exists but is stale
`host-feedback-summary.py` selects the newest `daily*` / `onboard` evidence per target repo and prefers `daily` when timestamps are equal, because `daily` represents real workload feedback. If the newest evidence is older than 168 hours, the report returns `target_runs=attention` and `freshness_status=stale`.

In that state, do not claim that the current real effect is clear. The correct conclusion is that the feedback entrypoint works, but real workload evidence must be refreshed.

## Minimum Acceptance
The feedback loop is only complete when all four are true:
- `FeedbackReport` succeeds
- `RulesDryRun` has no unexpected drift
- `claude_workload.readiness.status` is not `blocked`
- `target_runs.freshness_status=fresh`, with latest runs selected from the newest `daily` workload evidence
- `verify-repo.ps1 -Check All` passes

## Related Files
- [Adapter Conformance Parity Matrix](./adapter-conformance-parity-matrix.md)
- [AI Coding Usage Guide](../quickstart/ai-coding-usage-guide.md)
- [Codex CLI/App Integration Guide](./codex-cli-app-integration-guide.md)
