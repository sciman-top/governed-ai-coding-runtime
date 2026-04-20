# 20260420 Multi-Target One-Click Autonomous Validation

## Goal
Autonomously run the project one-click flow across multiple target repos and validate practical effectiveness with machine-verifiable outputs.

## Date
- Execution date: 2026-04-20

## Targets
- `classroomtoolkit` -> `D:\OneDrive\CODE\ClassroomToolkit`
- `self-runtime` -> `D:\OneDrive\CODE\governed-ai-coding-runtime`
- `skills-manager` -> `D:\OneDrive\CODE\skills-manager`

## One-Click Entry
- `scripts/runtime-flow-preset.ps1`
- Flow combinations executed:
  - `onboard` + `quick` + `allow`
  - `daily` + `quick` + `allow` + write probe

## Run Artifacts
- Raw per-target JSON outputs:
  - `docs/change-evidence/target-repo-runs/*-onboard-*.json`
  - `docs/change-evidence/target-repo-runs/*-daily-*.json`
- Summaries:
  - `docs/change-evidence/target-repo-runs/summary-latest.json`
  - `docs/change-evidence/target-repo-runs/summary-allowedscope.json`

## Effectiveness Checks

### Check A: Out-of-scope write should be denied (guardrail effectiveness)
Write probe path used: `.governed-ai/runtime-probe-<timestamp>.txt`.

Results:
- `classroomtoolkit`: `onboard=pass`, `daily=fail`, `write_execution_status=denied`
  - reason: `write path is outside allowed scopes`
- `self-runtime`: `onboard=pass`, `daily=fail`, `write_execution_status=denied`
  - reason: `write path is outside allowed scopes`
- `skills-manager`: `onboard=pass`, `daily=fail`, `write_execution_status=denied`
  - reason: `write path is outside allowed scopes`

Interpretation:
- Governance policy is active and fail-closed on path scope violations.
- Denial is policy behavior, not runtime crash.

### Check B: Allowed-scope write should execute (runtime usefulness)
Write probe path used: `docs/runtime-probe-<timestamp>.txt` (inside `write_allow: docs/**`).

Results:
- `classroomtoolkit`: `daily=pass`, `attachment_health=healthy`, `verify={contract:pass,test:pass}`, `write_execution_status=executed`
- `self-runtime`: `daily=pass`, `attachment_health=healthy`, `verify={contract:pass,test:pass}`, `write_execution_status=executed`
- `skills-manager`: `daily=pass`, `attachment_health=healthy`, `verify={contract:pass,test:pass}`, `write_execution_status=executed`

File landing verification:
- `D:\OneDrive\CODE\ClassroomToolkit\docs\runtime-probe-20260420230050.txt` exists
- `D:\OneDrive\CODE\governed-ai-coding-runtime\docs\runtime-probe-20260420230134.txt` exists
- `D:\OneDrive\CODE\skills-manager\docs\runtime-probe-20260420230317.txt` exists

Evidence pointers (daily allowed-scope runs):
- `classroomtoolkit`
  - evidence: `artifacts/task-classroomtoolkit-daily-allowedscope-20260420230050/run-classroomtoolkit-daily-allowedscope-20260420230050/verification-output/contract.txt`
  - handoff: `artifacts/task-classroomtoolkit-daily-allowedscope-20260420230050/task-classroomtoolkit-daily-allowedscope-20260420230050-write-0c03e22fd77b/handoff/write-flow.json`
  - replay: `artifacts/task-classroomtoolkit-daily-allowedscope-20260420230050/task-classroomtoolkit-daily-allowedscope-20260420230050-write-0c03e22fd77b/replay/write-flow.json`
- `self-runtime`
  - evidence: `artifacts/task-self-runtime-daily-allowedscope-20260420230134/run-self-runtime-daily-allowedscope-20260420230134/verification-output/contract.txt`
  - handoff: `artifacts/task-self-runtime-daily-allowedscope-20260420230134/task-self-runtime-daily-allowedscope-20260420230134-write-0daa755fc201/handoff/write-flow.json`
  - replay: `artifacts/task-self-runtime-daily-allowedscope-20260420230134/task-self-runtime-daily-allowedscope-20260420230134-write-0daa755fc201/replay/write-flow.json`
- `skills-manager`
  - evidence: `artifacts/task-skills-manager-daily-allowedscope-20260420230317/run-skills-manager-daily-allowedscope-20260420230317/verification-output/contract.txt`
  - handoff: `artifacts/task-skills-manager-daily-allowedscope-20260420230317/task-skills-manager-daily-allowedscope-20260420230317-write-b4590d5e9c88/handoff/write-flow.json`
  - replay: `artifacts/task-skills-manager-daily-allowedscope-20260420230317/task-skills-manager-daily-allowedscope-20260420230317-write-b4590d5e9c88/replay/write-flow.json`

## Conclusion
- One-click attach-first flow is practically reusable across multiple target repos.
- Governance guardrails are effective: out-of-scope writes are denied consistently.
- Within allowed scopes, daily governed loop reaches execution and leaves handoff/replay evidence.

## Rollback / Cleanup
If probe files should be removed:
1. Delete:
   - `D:\OneDrive\CODE\ClassroomToolkit\docs\runtime-probe-20260420230050.txt`
   - `D:\OneDrive\CODE\governed-ai-coding-runtime\docs\runtime-probe-20260420230134.txt`
   - `D:\OneDrive\CODE\skills-manager\docs\runtime-probe-20260420230317.txt`
2. Optionally keep raw JSON evidence in `docs/change-evidence/target-repo-runs/` for audit replay.
