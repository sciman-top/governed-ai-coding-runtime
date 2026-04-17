# 2026-04-17 Foundation Execution Plan

## Goal
- Close `Foundation / GAP-020` through `GAP-023` on the active branch baseline.
- Leave the repository with live Foundation gate commands, durable lifecycle substrate primitives, and mechanically checkable control or evidence maturity.
- Move the active next-step queue from `Foundation` to `Full Runtime / GAP-024`.

## Basis
- `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- `docs/plans/foundation-runtime-substrate-implementation-plan.md`
- `docs/backlog/issue-ready-backlog.md`
- `AGENTS.md`
- Prior Foundation slice evidence:
  - `docs/change-evidence/20260417-gap-020-task-1-clarification-compatibility-evidence.md`
  - `docs/change-evidence/20260417-gap-021-task-2-build-doctor-gates.md`
  - `docs/change-evidence/20260417-gap-022-task-3-durable-task-store.md`
  - `docs/change-evidence/20260417-gap-023-task-4-control-registry-completeness.md`

## Files Changed
- `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/full-lifecycle-backlog-seeds.md`
- `docs/backlog/post-mvp-backlog-seeds.md`
- `docs/backlog/issue-seeds.yaml`
- `docs/backlog/README.md`
- `docs/plans/foundation-runtime-substrate-implementation-plan.md`
- `docs/plans/README.md`
- `docs/README.md`
- `README.md`
- `README.zh-CN.md`
- `README.en.md`
- `docs/change-evidence/README.md`
- `docs/change-evidence/20260417-full-lifecycle-functional-planning.md`
- `docs/change-evidence/20260417-post-mvp-lifecycle-planning.md`
- `scripts/github/create-roadmap-issues.ps1`

## Foundation Outcome
- `GAP-020` complete:
  - clarification protocol spec, schema, example, and Python helpers landed
  - repo-profile and adapter compatibility posture now support mechanical checks
  - evidence completeness can distinguish missing mandatory inputs from weak outcomes
- `GAP-021` complete:
  - `scripts/build-runtime.ps1` is live and validates byte-compilation plus importability of the current Python runtime substrate
  - `scripts/doctor-runtime.ps1` is live and validates current runtime prerequisites, schema/catalog visibility, and active gate command presence
  - `scripts/verify-repo.ps1` routes `Build`, `Runtime`, `Contract`, and `Doctor` checks in canonical order
- `GAP-022` complete:
  - file-backed task persistence landed through `task_store.py`
  - workflow skeleton landed through `workflow.py`
  - lifecycle metadata now covers pause, resume, retry, timeout, and deterministic transition history
- `GAP-023` complete:
  - control lifecycle and health checks landed through `control_registry.py`
  - evidence completeness helpers now fail missing rollback or required evidence independently from task outcome
- Planning baseline closed:
  - roadmap, backlog, issue seeds, seeding script, plans index, docs index, and root READMEs now agree that `Foundation` is complete and `Full Runtime / GAP-024` is the next queue

## Verification Commands
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
5. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
6. `git diff --check`

## Verification Result
| command | exit_code | result | key_output |
|---|---:|---|---|
| `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1` | 0 | pass | `OK python-bytecode`, `OK python-import` |
| `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` | 0 | pass | `OK runtime-unittest`, `Ran 87 tests` |
| `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` | 0 | pass | `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing` |
| `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1` | 0 | pass | `OK python-command`, `OK gate-command-build`, `OK gate-command-test`, `OK gate-command-contract`, `OK gate-command-doctor` |
| `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All` | 0 | pass | `OK runtime-build`, `OK runtime-unittest`, `OK runtime-doctor`, `OK active-markdown-links`, `OK backlog-yaml-ids`, `OK powershell-parse`, `Ran 87 tests` |
| `git diff --check` | 0 | pass | CRLF normalization warnings only; no whitespace errors |

## Gate Status
| gate | status | command | result | reason | alternative_verification | evidence_link | expires_at |
|---|---|---|---|---|---|---|---|
| build | `active` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1` | pass | Foundation build now validates the real Python runtime substrate the repo currently ships | `python -m compileall packages/contracts/src scripts/run-readonly-trial.py` | `docs/change-evidence/20260417-foundation-execution-plan.md` | `n/a` |
| test | `active` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` | pass | runtime contract tests cover the active Foundation substrate additions | `python -m unittest discover -s tests/runtime -p "test_*.py"` | `docs/change-evidence/20260417-foundation-execution-plan.md` | `n/a` |
| contract/invariant | `active` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` | pass | schema, example, catalog, and spec pairing remain the active hard machine contract gate | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All` | `docs/change-evidence/20260417-foundation-execution-plan.md` | `n/a` |
| hotspot | `active` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1` | pass | Foundation doctor now validates current runtime readiness without over-claiming service health | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Doctor` | `docs/change-evidence/20260417-foundation-execution-plan.md` | `n/a` |

## Residual Risks
- `Full Runtime / GAP-024` through `GAP-028` is still open:
  - no execution worker
  - no managed runtime workspace orchestration beyond current substrate helpers
  - no artifact store or replay pipeline
  - no operator UI
  - no runtime health/status query surface
- Foundation `build` and `doctor` are intentionally narrow:
  - they prove the current Python runtime substrate is present and mechanically runnable
  - they do not prove package publishing, deployment health, or service operability
- Persistent task state is currently file-backed and single-machine by design; future runtime stages will need explicit migration and rollback planning before introducing stronger storage layers

## Rollback
- Revert this Foundation closeout by restoring the previous versions of:
  - roadmap, backlog, plans index, docs index, root READMEs, issue seeds, and seeding script
- If the Foundation queue must be re-opened:
  - change the active queue back from `Full Runtime / GAP-024` to `Foundation / GAP-020`
  - keep the landed code and gate primitives, but re-open only the backlog or roadmap status markers that proved incomplete
- All code changes remain recoverable through git history on `feature/gap-020-task-1`; no non-git rollback snapshot was required for this closeout
