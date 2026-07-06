# Governed AI Coding Runtime English Guide

## Current Boundary
- The single planning truth remains `docs/architecture/planning-status.json`.
- Single source of planning truth: `docs/architecture/planning-status.json`.
- current active queue: `Continuous-Execution`
- `current decision gate`: `defer_ltp_and_refresh_evidence`
- The repository is now intentionally narrowed to three live surfaces:
  - self-repo governance: `build -> test -> contract/invariant -> hotspot`
  - global user-rule synchronization for `~/.codex`, `~/.claude`, and `~/.gemini`
  - host/self-evolution/continuity read-only feedback, evidence, and gates
- Historical `docs/change-evidence/**` records remain archived, but they no longer imply that target-repo rollout, attachment, or session-bridge write flows are still live features.

## Fastest Path
```powershell
.\run.ps1
```

```powershell
.\run.ps1 fast
```

```powershell
.\run.ps1 readiness -OpenUi
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/governance/preflight.ps1 -DisableAutoCommit
```

- `run.ps1`: root shortcut into `scripts/operator.ps1`
- `run.ps1 fast`: runs `build + RuntimeQuick`
- `run.ps1 readiness -OpenUi`: runs the full hard-gate chain and opens the operator UI
- `preflight.ps1`: release-style closeout on top of the full gate

## What This Repo Does
- runs the canonical self-repo gate chain through `scripts/build-runtime.ps1`, `scripts/verify-repo.ps1`, and `scripts/doctor-runtime.ps1`
- produces repo-local task, evidence, handoff, and status artifacts through `scripts/run-governed-task.py`
- syncs global rule files through `scripts/sync-agent-rules.ps1`
- generates host feedback, self-evolution recommendations, continuity evidence, and the operator UI
- packages the portable runtime release through `scripts/package-runtime.ps1`
- keeps only the retired Codex shim cleanup/absence checks
- Codex and Claude Code are cooperation hosts, not competitors.
- Codex/Cockpit Direct OAuth, Direct API, and Cockpit API service switching remain owned by `Cockpit Tools`.

## Retired Codex/Cockpit Shims
- The only retained paths are `Disable-CodexProjectInterop.ps1` and `Test-CodexGuardAbsence.ps1`.
- Do not restore or recommend: `CodexProjectionSmoke`, `CodexApiProjectionRepair`, `CodexOauthProjectionRepair`, `CodexLaunchBindingRepair`, `Manage-LiteLLMGateway.ps1`, `codex-mode-*`, `--migrate-provider-bucket`, `SQLite provider trigger`, `no-op launcher`, `restart wrapper`.

## Retired Surface
- no more target-repo `daily`, `governance-baseline`, `apply-all`, `cleanup-targets`, or `uninstall-governance`
- no more attachment, light-pack, session-bridge, or attached-write bridge flows
- `rules/manifest.json` no longer distributes any `rules/projects/**` project copies
- target-run, KPI, and effect artifacts remain historical evidence only

Retired command names remain fail-closed and return explicit retirement messages.

## Main Entrypoints
- `run.ps1`
- `scripts/operator.ps1`
- `scripts/verify-repo.ps1`
- `scripts/governance/preflight.ps1`
- `scripts/sync-agent-rules.ps1`
- `scripts/run-governed-task.py`
- `scripts/package-runtime.ps1`

## Verification
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
```

## Read Next
- [docs/README.md](docs/README.md)
- [Single-Machine Runtime Quickstart](docs/quickstart/single-machine-runtime-quickstart.md)
- [Use With An Existing Repo](docs/quickstart/use-with-existing-repo.md)
- [Host Feedback Loop](docs/product/host-feedback-loop.md)
- [Agent Continuity Guide](docs/product/agent-continuity.md)
- [20260617 Active Queue Evidence-Upkeep Refresh](docs/change-evidence/20260617-active-queue-evidence-upkeep-refresh.md)
- [20260617 Planning EntryPoint Proof Refresh](docs/change-evidence/20260617-planning-entrypoint-proof-refresh.md)
