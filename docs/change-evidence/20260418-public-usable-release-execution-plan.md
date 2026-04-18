# 2026-04-18 Public Usable Release Execution Plan

## Goal
- Close `Public Usable Release / GAP-029` through `GAP-032` on the active branch baseline.
- Move the active next-step queue from `Public Usable Release / GAP-029` to `Maintenance / GAP-033`.

## Scope
- Single-machine bootstrap path and quickstart.
- Richer local operator surface on top of the runtime read model.
- Sample repo profile and runtime operator snapshot examples.
- Local package bundle and explicit public usable release criteria.
- Adapter degrade policy and doctor-visible compatibility posture.

## End-To-End Commands
| step | command | exit_code | key_output |
|---|---|---:|---|
| bootstrap | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/bootstrap-runtime.ps1` | 0 | emitted `.runtime` paths and runtime status JSON |
| governed run | `python scripts/run-governed-task.py run --json` | 0 | delivered `task-3676ac80` / `run-17da85286b0b` |
| operator UI | `python scripts/serve-operator-ui.py` | 0 | wrote `.runtime/artifacts/operator-ui/index.html` |
| package | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/package-runtime.ps1` | 0 | wrote `.runtime/dist/public-usable-release` |
| full gates | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All` | 0 | `build`, `test`, `contract`, `doctor`, docs, script checks all passed |

## Public Usable Release Outcome
- A new user path now exists through:
  - `scripts/bootstrap-runtime.ps1`
  - `docs/quickstart/single-machine-runtime-quickstart.md`
  - `python scripts/run-governed-task.py run --json`
  - `python scripts/serve-operator-ui.py`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/package-runtime.ps1`
- Latest delivered demo task:
  - `task_id`: `task-3676ac80`
  - `run_id`: `run-17da85286b0b`
  - `state`: `delivered`
  - `workspace_root`: `.governed-workspaces/python-service-sample/task-3676ac80/run-17da85286b0b`
- Key runtime outputs:
  - `.runtime/artifacts/operator-ui/index.html`
  - `.runtime/dist/public-usable-release/`
  - `.runtime/artifacts/artifacts/task-3676ac80/run-17da85286b0b/evidence/bundle.json`
  - `.runtime/artifacts/artifacts/task-3676ac80/run-17da85286b0b/handoff/package.json`
  - `.runtime/artifacts/artifacts/task-3676ac80/run-17da85286b0b/verification-output/build.txt`
  - `.runtime/artifacts/artifacts/task-3676ac80/run-17da85286b0b/verification-output/test.txt`
  - `.runtime/artifacts/artifacts/task-3676ac80/run-17da85286b0b/verification-output/contract.txt`
  - `.runtime/artifacts/artifacts/task-3676ac80/run-17da85286b0b/verification-output/doctor.txt`

## Changes
- Added public usable release entrypoints:
  - `scripts/bootstrap-runtime.ps1`
  - `scripts/serve-operator-ui.py`
  - `scripts/package-runtime.ps1`
- Added public docs:
  - `docs/quickstart/single-machine-runtime-quickstart.md`
  - `docs/product/public-usable-release-criteria.md`
  - `docs/product/adapter-degrade-policy.md`
- Added local richer operator surface:
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py`
- Added sample/demo assets:
  - `schemas/examples/repo-profile/governed-ai-coding-runtime.example.json`
  - `schemas/examples/runtime-operator-surface/status-snapshot.example.json`
- Hardened compatibility posture:
  - unsupported adapter capabilities now fail closed by default when degrade behavior is absent
  - `doctor-runtime.ps1` now emits `OK adapter-posture-visible`
- Hardened packaging:
  - package copying now filters `__pycache__` and `*.pyc` so runtime tests and packaging can coexist in one verification run

## Risks
- The richer operator surface is still local HTML, not a long-running web service.
- Packaging is a local distribution directory, not an installer or published package manager artifact.
- Historical failed runtime tasks remain in `.runtime/tasks/`; they are useful evidence but may need cleanup for demo-only environments.

## Rollback
- Revert the public usable release changeset and move the active queue references back from `Maintenance / GAP-033` to `Public Usable Release / GAP-029`.
- Remove local runtime artifacts as needed:
  - `.runtime/`
  - `.governed-workspaces/`

## Evidence Fields
- `issue_id`: `GAP-029..GAP-032`
- `attempt_count`: `1`
- `clarification_mode`: `direct_fix`
- `clarification_scenario`: `n/a`
- `clarification_questions`: `[]`
- `clarification_answers`: `[]`
