# 20260427 GAP-104..111 Complete Hybrid Final-State Realization Planning

## Goal
Answer whether the current optimized hybrid final state and stack are the best target, and turn the answer into an implementation-ready post-`GAP-103` queue.

## Decision
The current optimized hybrid target remains the best engineering direction:

`repo-local contract bundle + machine-local durable governance kernel + attach-first host adapters + same-contract verification/delivery plane`

The improvement is not a clean-sheet rewrite or a one-shot platform-stack expansion. The improvement is a stricter realization queue:
- keep the verified local baseline until a real boundary requires transition-stack depth
- make service/API behavior primary before broader live-host and data-plane claims
- prove live Codex continuity and at least one non-Codex adapter path
- broaden governed executable tool coverage under containment metadata
- make data, artifact, replay, release, and provenance evidence reproducible
- require sustained workload and recovery evidence before final certification

## Changed Files
- `docs/architecture/hybrid-final-state-master-outline.md`
- `docs/roadmap/optimized-hybrid-final-state-long-term-roadmap.md`
- `docs/plans/optimized-hybrid-final-state-long-term-implementation-plan.md`
- `docs/plans/README.md`
- `docs/backlog/README.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/issue-seeds.yaml`
- `docs/README.md`
- `docs/change-evidence/README.md`
- `docs/change-evidence/20260427-gap-104-111-realization-planning.md`
- `scripts/github/create-roadmap-issues.ps1`

## New Queue
| gap id | purpose | claim boundary |
|---|---|---|
| `GAP-104` | full realization rebaseline | planning only; no final-state claim |
| `GAP-105` | service-primary runtime boundary | transition-stack adoption only where runtime behavior exists |
| `GAP-106` | live Codex attach continuity | live-host evidence required |
| `GAP-107` | non-Codex adapter parity | host-neutral conformance required |
| `GAP-108` | governed executable tool coverage | containment and rollback evidence required |
| `GAP-109` | data-plane and provenance release path | migration, replay, retention, provenance, and rollback evidence required |
| `GAP-110` | operations recovery and sustained soak | workload and remediation evidence required |
| `GAP-111` | complete final-state certification | certify only if every target has fresh evidence; otherwise downgrade |

## External Source Check
The queue preserves the 2026-04-27 external benchmark conclusion:
- Codex project instructions support layered repo-local guidance.
- OpenAI Agents SDK guardrails are useful defense-in-depth but do not replace runtime-owned policy and evidence.
- MCP roots/protocol surfaces are integration boundaries, not governance-kernel ownership.
- A2A discovery/task semantics remain adapter/protocol concerns, not local approval or rollback semantics.
- SLSA-style provenance supports the release and generated-artifact evidence track.

## Verification
Commands:
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
- `git diff --check`

Key output:
- issue rendering: `issue_seed_version=4.4`, `rendered_tasks=89`, `completed_task_count=81`, `active_task_count=8`
- docs gate: `OK active-markdown-links`, `OK backlog-yaml-ids`, `OK gap-evidence-slo`, `OK claim-drift-sentinel`, `OK claim-evidence-freshness`, `OK post-closeout-queue-sync`
- full gate: `OK runtime-build`, `OK runtime-unittest`, `OK runtime-service-parity`, `OK schema-catalog-pairing`, `OK dependency-baseline`, `OK transition-stack-convergence`, `OK target-repo-governance-consistency`, `OK runtime-doctor`, `OK issue-seeding-render`
- full tests: `Ran 422 tests ... OK (skipped=5)`, `Ran 10 tests ... OK`
- `git diff --check`: no whitespace errors; Git reported CRLF normalization warnings for existing text files

## Residual Risks
- `GAP-104..111` are a realization plan, not completed implementation.
- Some tasks require live host behavior and sustained workload evidence; those can fail because of host capability drift, adapter limits, or target-repo failures.
- If any required evidence fails, `GAP-111` must downgrade final-state claims instead of marking complete closure.

## Rollback
Revert this evidence file and the `GAP-104..111` additions in roadmap, implementation plan, backlog, issue seeds, indexes, and issue-rendering label mapping.
