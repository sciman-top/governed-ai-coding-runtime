# 20260426 GAP-092 LTP Start Decision

## Goal
Close `GAP-092` by deciding whether the trigger-audit evidence justifies starting exactly one long-term implementation package.

## Decision
All `LTP-01..05` packages remain deferred. No long-term implementation package starts from this audit.

## Rationale
`GAP-090` refreshed final-state claim evidence and found no stale or over-broad claim that required downgrade in this slice. `GAP-091` then ran a real all-target daily window and found a concrete shell-compatibility drift in target gate commands, which was fixed through catalog/profile synchronization and proved green with a second all-target daily run.

That evidence supports remediation of current target command configuration, not promotion of Temporal-class orchestration, OPA/Rego-class policy separation, event-stream/object-store data-plane expansion, deeper first-class host adapters, or production SLO/failover operations work.

## Scope Fence
| package id | decision | reason | next review trigger |
|---|---|---|---|
| `LTP-01 orchestration-depth` | deferred, watch | All-target orchestration passed after profile repair; no repeated graph-maintainability failure. | repeated runtime-flow orchestration failures after target command drift is excluded |
| `LTP-02 policy-runtime-separation` | deferred | No policy cardinality or audit-burden pressure appeared in the audit window. | policy decision surface becomes too large to audit locally |
| `LTP-03 data-plane-scaling` | deferred, watch | No event, replay, query, or retention pressure appeared in the audit window. | sustained KPI or target-run volume proves current persistence path is insufficient |
| `LTP-04 multi-host-first-class` | deferred, watch | The observed drift was target command wrapping inside existing execution paths, not stable demand for deeper non-Codex host productization. | explicit product demand plus repeated parity gap evidence |
| `LTP-05 operations-hardening` | deferred | Final all-target daily and repo gates pass after remediation; operations failure is not the main blocker. | operational failures dominate after functional/runtime drift is excluded |

## Verification
- `cmd`: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
  - `exit_code`: `0`
  - `key_output`: `issue_seed_version=4.1`; `rendered_tasks=70`; `rendered_issue_creation_tasks=0`; `completed_task_count=70`; `active_task_count=0`
- `cmd`: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  - `exit_code`: `0`
  - `key_output`: `OK active-markdown-links`; `OK backlog-yaml-ids`; `OK gap-evidence-slo`; `OK post-closeout-queue-sync`

## Rollback
- Revert this evidence file and the `GAP-092` completion/status updates in backlog, plan, README, and evidence indexes.
- If a future LTP becomes justified, add a new issue id beyond `GAP-092` and link fresh trigger evidence instead of modifying this closed decision in place.
