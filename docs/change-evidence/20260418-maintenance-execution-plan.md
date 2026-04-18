# 20260418 Maintenance Execution Plan

## Goal
- close `Maintenance / GAP-033` through `GAP-034`
- make compatibility, upgrade, maintenance, deprecation, and retirement policy explicit in docs and visible through runtime status plus doctor checks

## Basis
- `docs/backlog/issue-ready-backlog.md`
- `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- `docs/plans/maintenance-implementation-plan.md`
- `docs/change-evidence/20260418-public-usable-release-execution-plan.md`

## Current Landing
- worktree: `D:\OneDrive\CODE\governed-ai-coding-runtime\.worktrees\full-runtime-gap-024`
- branch: `feature/full-runtime-gap-024`
- policy docs:
  - `docs/product/runtime-compatibility-and-upgrade-policy.md`
  - `docs/product/maintenance-deprecation-and-retirement-policy.md`
- runtime surface:
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/maintenance_policy.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/runtime_status.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py`
  - `scripts/run-governed-task.py`
  - `scripts/serve-operator-ui.py`
  - `scripts/doctor-runtime.ps1`

## Changes
- added explicit compatibility and upgrade policy for adapters, repo profiles, and persisted runtime state
- added explicit maintenance, triage, deprecation, and retirement policy
- extended runtime status snapshots with a top-level `maintenance` surface and stable policy doc refs
- projected maintenance policy into CLI status output and the local operator HTML page
- extended doctor to fail if the maintenance policy docs or runtime maintenance metadata disappear
- aligned roadmap, backlog, readmes, plans index, and issue seeding text so `GAP-033` and `GAP-034` are marked complete

## Commands And Evidence

| cmd | exit_code | key_output |
|---|---:|---|
| `python -m unittest tests.runtime.test_maintenance_policy tests.runtime.test_runtime_status tests.runtime.test_operator_ui` | 0 | `Ran 9 tests` / `OK` |
| `python scripts/run-governed-task.py status --json` | 0 | `maintenance.stage = completed`; refs point to the two new policy docs |
| `python scripts/serve-operator-ui.py` | 0 | `maintenance_stage = completed`; output `.runtime/artifacts/operator-ui/index.html` |
| `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1` | 0 | `OK python-bytecode`; `OK python-import` |
| `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` | 0 | `Ran 109 tests` / `OK runtime-unittest` |
| `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` | 0 | `OK schema-json-parse`; `OK schema-example-validation`; `OK schema-catalog-pairing` |
| `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1` | 0 | `OK maintenance-policy-visible`; `OK adapter-posture-visible` |

## Runtime Snapshot Evidence
- delivered tasks still visible:
  - `task-3676ac80` / `run-17da85286b0b`
  - `task-b21f2279` / `run-63f11fdd0f90`
- historical failed tasks remain preserved as replay evidence:
  - `task-db9e5bc9`
  - `task-f760f8ac`
- operator UI artifact:
  - `.runtime/artifacts/operator-ui/index.html`

## Risks
- maintenance policy is still doc-backed metadata; it does not yet enforce automated migrations for persisted state
- lifecycle is complete for the current single-machine target, but future feature queues should add a new roadmap or plan instead of silently reopening the lifecycle stages

## Rollback
- prefer git diff or commit-level rollback for policy docs, runtime surface changes, and readme alignment
- if selective rollback is needed, revert:
  - `docs/product/runtime-compatibility-and-upgrade-policy.md`
  - `docs/product/maintenance-deprecation-and-retirement-policy.md`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/maintenance_policy.py`
  - the maintenance-related edits in `runtime_status.py`, `operator_ui.py`, `run-governed-task.py`, and `doctor-runtime.ps1`

## Status
- `GAP-033 Compatibility And Upgrade Policy`: complete
- `GAP-034 Maintenance, Deprecation, And Retirement Policy`: complete
- full lifecycle through `Maintenance / GAP-034`: complete on the current branch baseline
