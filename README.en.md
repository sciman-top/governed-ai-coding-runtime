# Governed AI Coding Runtime English Guide

## Current Snapshot
- Single source of planning truth: `docs/architecture/planning-status.json`
- current active queue: `Continuous-Execution` (`Continuous Execution Readiness And Rollout`)
- `current decision gate`: `defer_ltp_and_refresh_evidence`
- `current live posture`: target-run freshness is `fresh`; Codex target runs are `native_attach` / ready; Claude workload probe is `native_attach` / ready
- certified baseline: `GAP-104..111`
- latest completed governance hardening slice: `GAP-169..172`
  - the repo now carries a repo-owned `reference-basis`, a release-style `preflight`, and CI `release-preflight`

## Fastest Path
If you only need to know what to run next, start with these four entrypoints:

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

Recommended interpretation:
- `run.ps1`: repository-root shortcut that forwards to `scripts/operator.ps1`
- `run.ps1 fast`: inner-loop feedback, running `build + RuntimeQuick`
- `run.ps1 readiness -OpenUi`: runs the hard-gate order `build -> test -> contract/invariant -> hotspot`, then opens the default Chinese operator UI
- `scripts/governance/preflight.ps1 -DisableAutoCommit`: release-style closeout that adds `Docs`, `Scripts`, and `git diff --check` on top of the full gate

## What This Repo Is
- This repository is an AI coding governance runtime / control plane, not another execution host.
- It centralizes governance contracts, gates, evidence, rollout flows, target-repo attachment, and host feedback into one repo-owned rules-and-scripts baseline.
- The best engineering end state remains `Governance Hub + Reusable Contract + Capability-First Host Adapters + Controlled Evolution + Evidence-First Delivery`.
- Codex and Claude Code are cooperation hosts, not competitors; this repo governs their attach, gate, evidence, handoff, and degrade posture without copying or replacing host UI, accounts, providers, or model loops.
- It does not own local account, provider, gateway, or host switching:
  - Codex/Cockpit Direct OAuth, Direct API, and API service roundtrips stay in `Cockpit Tools`.
  - Claude Code / Claude Desktop account and provider switching stay in `CC Switch`.

## Retired Codex/Cockpit Shims
- The only retained paths are `Disable-CodexProjectInterop.ps1` and `Test-CodexGuardAbsence.ps1`, which clean up and verify absence of old project interop shims.
- Do not restore or recommend old paths: `CodexProjectionSmoke`, `CodexApiProjectionRepair`, `CodexOauthProjectionRepair`, `CodexLaunchBindingRepair`, `Manage-LiteLLMGateway.ps1`, `codex-mode-*`, `--migrate-provider-bucket`, `SQLite provider trigger`, `no-op launcher`, `restart wrapper`.

## What It Can Do Today
- run canonical repository verification through `scripts/verify-repo.ps1`
- run release-style closeout through `scripts/governance/preflight.ps1`
- aggregate readiness, feedback, rule sync, target flows, and operator UI behind `scripts/operator.ps1`
- attach external target repos and run attach-first governance flows
- sync `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` from `rules/manifest.json`
- create and initialize portable packages with:
  - `.\release.ps1 -Version <version> -Channel portable`
  - `.\install.ps1 -Mode Portable`

## What It Does Not Own
- Codex/Cockpit account, provider, gateway, history-bucket, or launcher state
- Claude Code / Claude Desktop account, provider, config-root, or history migration
- universal runtime-owned takeover claims for every external repo and every high-risk workflow

## Hard Gates And Reference Discipline
- delivery floor: `build -> test -> contract/invariant -> hotspot`
- Canonical acceptance chain: runtime-managed `build -> test -> contract/invariant -> hotspot`.
- canonical verifier: `scripts/verify-repo.ps1`
  - `Build`: `scripts/build-runtime.ps1`
  - `Runtime`: runtime and service tests
  - `Contract`: source, repo, and target-governance invariants
  - `Doctor`: `scripts/doctor-runtime.ps1`
  - `Docs` / `DocsLinks` / `Scripts`: markdown links, planning consistency, PowerShell parsing, and similar integrity checks
- high-drift changes are now fail-closed:
  - `scripts/verify-reference-required-changes.py` enforces same-diff official-source, primary-reference, and local-runtime-evidence review
  - `scripts/verify-reference-basis.py` enforces same-diff named local reference-id review
- key policy entrypoints:
  - `docs/architecture/reference-required-change-policy.json`
  - `docs/architecture/reference-basis-policy.json`
  - `docs/research/reference-basis-matrix.md`
  - `docs/research/reference-basis-catalog.json`
- same-diff evidence must be written under `docs/change-evidence/*.md`
  - common fields: `official_sources_reviewed`, `primary_references_reviewed`, `local_runtime_evidence_reviewed`, `source_decision`
  - when a guarded `reference-basis` surface changes, also add `reference_basis_surface_ids`, `required_local_reference_ids_reviewed`, and `reference_adoption_decision`
- GitHub Actions currently runs both:
  - `scripts/verify-repo.ps1 -Check All`
  - `scripts/governance/preflight.ps1 -DisableAutoCommit`

## Main Entrypoints
- `run.ps1`
  - root shortcut for daily use
- `scripts/operator.ps1`
  - aggregates `Readiness`, `FeedbackReport`, `RulesDryRun`, `RulesApply`, `DailyAll`, `ApplyAllFeatures`, `SelfEvolutionPromotionPlan`, `CorePrincipleMaterialize`, and `OperatorUi`
- `scripts/verify-repo.ps1`
  - canonical self-repo verification surface
- `scripts/governance/preflight.ps1`
  - release-style closeout surface
- `scripts/runtime-flow-preset.ps1`
  - attach, daily, baseline, and apply-all flows for the managed target catalog
- `scripts/sync-agent-rules.ps1`
  - sync surface for `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md`
- `claude-provider continuity`
  - read-only Claude continuity check
- `scripts/Disable-CodexProjectInterop.ps1` and `scripts/Test-CodexGuardAbsence.ps1`
  - cleanup and absence verification for retired Codex shims only

## Quick Usage Paths (Recommended)
- Path A (governance sidecar, least friction): keep coding in Codex/Claude Code and run `bootstrap + doctor + verify-repo -Check All + status`.
- Path B (attach-first for external repos): run `attach-target-repo`, then use `runtime-flow.ps1 -FlowMode daily` as your daily governance chain.
- Path C (risky writes): run `govern-attachment-write -> decide-attachment-write -> execute-attachment-write` for medium/high-risk mutations.

## External Repo Boundary
For external repos such as `..\ClassroomToolkit`, the supported posture is attach-first governance:
- attach the target repo and generate or validate `.governed-ai` assets
- run daily gates, governance baseline sync, rule sync, and governed write flows
- keep approval, evidence, handoff, and replay refs

Do not claim:
- not that this runtime fully replaces Codex host execution in every environment
- that every external repo and every high-risk workflow is already runtime-owned end to end

## Read Next
- current navigation:
  - [docs/README.md](docs/README.md)
  - [planning-status.json](docs/architecture/planning-status.json)
- quickstarts:
  - [Single-Machine Runtime Quickstart](docs/quickstart/single-machine-runtime-quickstart.md)
  - [Use With An Existing Repo](docs/quickstart/use-with-existing-repo.md)
  - [Multi-Repo Trial Quickstart](docs/quickstart/multi-repo-trial-quickstart.md)
  - [Agent Continuity Guide](docs/product/agent-continuity.md)
  - [Shared Context Continuity Guide (Chinese)](docs/product/agent-continuity.zh-CN.md)
- recent hardening:
  - [20260614 Continuous Execution Promotion](docs/change-evidence/20260614-continuous-execution-promotion.md)
  - [20260614 Active Queue Evidence-Upkeep Refresh](docs/change-evidence/20260614-active-queue-evidence-upkeep-refresh.md)
  - [20260609 Live Posture Recovery](docs/change-evidence/20260609-live-posture-recovery.md)
  - [20260609 Reference Basis And Preflight Hardening](docs/change-evidence/20260609-reference-basis-and-preflight-hardening.md)
- reference governance:
  - [Reference Basis Matrix](docs/research/reference-basis-matrix.md)
  - [Reference Governance And Release Preflight Roadmap](docs/roadmap/reference-governance-and-preflight-roadmap.md)
  - [Reference Governance And Release Preflight Plan](docs/plans/reference-governance-and-preflight-plan.md)
- history and evidence:
  - [Completed GAP History](docs/archive/completed-gap-history.md)
  - [Change Evidence Index](docs/change-evidence/README.md)

## Verification Shortcuts
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check RuntimeQuick
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/governance/preflight.ps1 -DisableAutoCommit
```
