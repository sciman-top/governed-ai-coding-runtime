# 20260614 Continuous Execution Two-Repo Trials

## Goal
- current landing: `D:\CODE\governed-ai-coding-runtime`
- target home:
  - `docs/plans/continuous-execution-readiness-and-rollout-plan.md`
  - `docs/change-evidence/20260614-continuous-execution-two-repo-trials.md`
  - `docs/change-evidence/README.md`
- verification path: complete `Task 7` by proving two low-risk attached trials under `runtime-flow-preset daily quick` without changing the selector or widening the host boundary

## Why This Slice Was Needed
- After `Task 6`, Phase 2 was fully closed, but Phase 3 still lacked the two target-repo attachment proofs required by the readiness trigger.
- The smallest safe next move was not a broad rollout. It was two low-risk, bounded `daily/quick` trials with explicit evidence and rollback references.
- The lowest-risk pair on the current host was:
  - `classroomtoolkit`
  - `github-toolkit`

## Change Summary
1. Trial A: `classroomtoolkit`
- Command:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target classroomtoolkit -FlowMode daily -Mode quick`
- Result:
  - overall: `pass`
  - attachment: `healthy`
  - gate order: `test -> contract`
  - outcome: `pass`
- Evidence and rollback refs recorded by the runtime:
  - `artifacts/task-20260614233523/session-bridge-request/verification-output/test.txt`
  - `artifacts/task-20260614233523/session-bridge-request/verification-output/contract.txt`
  - `artifacts/task-20260614233523/run-20260614233523/verification-output/contract.txt`
  - rollback remained the runtime-owned attached flow boundary; no target write or override was required

2. Trial B: `github-toolkit`
- Command:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target github-toolkit -FlowMode daily -Mode quick`
- Result:
  - overall: `pass`
  - attachment: `healthy`
  - gate order: `test -> contract`
  - outcome: `pass`
- Evidence and rollback refs recorded by the runtime:
  - `artifacts/task-20260614233808/session-bridge-request/verification-output/test.txt`
  - `artifacts/task-20260614233808/session-bridge-request/verification-output/contract.txt`
  - `artifacts/task-20260614233808/run-20260614233808/verification-output/contract.txt`
  - rollback remained the runtime-owned attached flow boundary; no target write or override was required

3. Trial boundary confirmation
- Both trials stayed inside the same hard boundaries:
  - no host restart
  - no target write flow
  - no approval override
  - no selector change
  - no heavy LTP promotion
- Both trials used live attach with healthy posture and explicit session/resume/continuation identity in the returned payloads.

4. Plan reconciliation
- Marked `Task 7` complete in `docs/plans/continuous-execution-readiness-and-rollout-plan.md`.
- Marked the first Phase 3 checkpoint bullet complete:
  - two-repo trial proof is present
- Left `Task 8` and the final readiness/active-loop claims unchecked, because current `planning-status.json` still keeps the selector at `defer_ltp_and_refresh_evidence`.

## Verification
### Trial commands
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target classroomtoolkit -FlowMode daily -Mode quick`
  - result: pass
  - key output includes:
    - `Overall: pass`
    - `Attachment: healthy`
    - `outcome: "pass"`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target github-toolkit -FlowMode daily -Mode quick`
  - result: pass
  - key output includes:
    - `Overall: pass`
    - `Attachment: healthy`
    - `outcome: "pass"`

### Main repo gates
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
- result: pass
- key output:
  - build: passed
  - runtime: passed
  - contract: passed
  - hotspot: passed

## Queue Boundary
- This slice completes `Task 7`.
- This slice does **not** claim `Task 8` is complete.
- This slice does **not** change `planning-status.json` or the selector away from `defer_ltp_and_refresh_evidence`.

## Risk
- risk_level: `low`
- reason:
  - both trials were quick, read-mostly, and attachment-scoped
  - no target write path was exercised
  - no approval bypass or host mutation was required

## Rollback
- revert:
  - `docs/plans/continuous-execution-readiness-and-rollout-plan.md`
  - `docs/change-evidence/20260614-continuous-execution-two-repo-trials.md`
  - `docs/change-evidence/README.md`
- re-run:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target classroomtoolkit -FlowMode daily -Mode quick`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target github-toolkit -FlowMode daily -Mode quick`
