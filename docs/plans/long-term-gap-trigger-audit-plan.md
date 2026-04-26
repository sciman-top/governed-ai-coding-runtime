# Long-Term Gap Trigger Audit Plan

## Status
- Completed planning and task-list baseline for `GAP-090` through `GAP-092`.
- This plan opens a trigger-audit queue after the completed `GAP-080` through `GAP-089` near-term horizon.
- This plan does not start any long-term implementation package by itself.
- Completion decision: all `LTP-01..05` packages remain deferred after the trigger audit.

## Goal
Refresh final-state evidence, run a sustained real-workload window, and make a gated decision about whether any long-term package is ready to start.

## Boundary
The queue owns:
- final-state claim and evidence freshness review
- real target-repo workload evidence collection
- trigger decision for `LTP-01` through `LTP-05`

The queue does not own:
- implementing Temporal-class orchestration
- implementing OPA/Rego-class policy separation
- implementing event-stream or object-store data-plane expansion
- productizing additional first-class host adapters
- adding production SLO or failover operations depth

Those packages remain deferred until `GAP-092` produces an evidence-backed trigger decision.

## Task List

### GAP-090 Final-State Claim Refresh And Trigger Audit
**Description:** Re-run the repository's final-state evidence chain and compare current runtime behavior against the long-term trigger table before opening any new implementation package.

**Acceptance criteria:**
- [x] closeout, claim-catalog, roadmap, backlog, and README claims agree with fresh executable evidence
- [x] long-term package triggers are recorded as `not_triggered`, `watch`, or `triggered`
- [x] stale or over-broad claims are downgraded before any LTP implementation starts

**Verification:**
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
- [x] trigger audit evidence lands in `docs/change-evidence/`

**Dependencies:** `GAP-089`

**Files likely touched:**
- `docs/change-evidence/*.md`
- `docs/product/claim-catalog.json`
- `docs/product/claim-exceptions.json`
- `docs/README.md`
- `README.md`, `README.en.md`, `README.zh-CN.md`

**Estimated scope:** Medium

### GAP-091 Sustained Real-Workload Evidence Window
**Description:** Run the existing runtime flow against real attached targets to determine whether the system is failing from orchestration complexity, policy complexity, data-plane pressure, host-adapter limits, or operations pressure.

**Acceptance criteria:**
- [x] at least one all-target or representative multi-target evidence window is captured
- [x] failures are grouped by long-term trigger family instead of treated as generic runtime noise
- [x] no LTP is marked triggered without command evidence and rollback notes

**Verification:**
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -FlowMode daily -Json`
- [x] target-run summaries and KPI snapshots are linked from evidence
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`

**Dependencies:** `GAP-090`

**Files likely touched:**
- `docs/change-evidence/target-repo-runs/*`
- `docs/change-evidence/*.md`
- `docs/product/claim-catalog.json`

**Estimated scope:** Medium

### GAP-092 LTP Start Decision And Scope Fence
**Description:** Convert the trigger audit and workload evidence into a yes/no decision for the first eligible long-term package, with a scope fence that prevents broad platform work from starting by default.

**Acceptance criteria:**
- [x] exactly one next LTP is selected, or all LTPs remain deferred with explicit reasons
- [x] selected LTP has a bounded implementation plan, verification floor, rollback path, and evidence owner
- [x] non-selected LTPs stay visible as deferred, not silently promoted into active work

**Verification:**
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- [x] decision evidence lands in `docs/change-evidence/`

**Dependencies:** `GAP-091`

**Files likely touched:**
- `docs/plans/*.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/issue-seeds.yaml`
- `docs/change-evidence/*.md`

**Estimated scope:** Medium

## Checkpoint
After `GAP-090` through `GAP-092`:
- [x] all repository gates are green in the project order `build -> test -> contract/invariant -> hotspot`
- [x] the active queue either stops with all LTPs deferred or starts exactly one new LTP package
- [x] backlog, seeds, issue rendering, evidence, and README posture agree

## Trigger Table
| package id | trigger signal | default decision |
|---|---|---|
| `LTP-01 orchestration-depth` | pause, resume, compensation, or retry graphs repeatedly exceed local runtime-flow maintainability | defer |
| `LTP-02 policy-runtime-separation` | policy cardinality or audit burden exceeds local decision-surface maintainability | defer |
| `LTP-03 data-plane-scaling` | event, replay, query, or retention pressure exceeds current persistence path | defer |
| `LTP-04 multi-host-first-class` | non-Codex parity is stable and real product demand requires deeper host coverage | defer |
| `LTP-05 operations-hardening` | transition runtime is stable under sustained workloads and operational failures become the main blocker | defer |

## Risks And Mitigations
| Risk | Impact | Mitigation |
|---|---|---|
| Trigger audit becomes a new unlimited roadmap | High | Keep `GAP-090..092` as the only active queue and require a single selected LTP before implementation. |
| Evidence refresh is mistaken for product completion | Medium | Tie completion claims to fresh command output and downgrade stale claims. |
| Real workload runs mix target-repo business failures with runtime failures | Medium | Classify failures by trigger family and link raw target-run evidence. |
| Long-term stack is introduced before need is proven | High | Keep default LTP decision as `defer` unless evidence meets the trigger table. |
