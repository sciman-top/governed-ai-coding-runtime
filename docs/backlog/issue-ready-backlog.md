# Issue-Ready Backlog

## Parent Initiative
Governed AI Coding Runtime Full Functional Lifecycle

## Assumptions
- `Phase 0` through `Phase 4` remain complete through `GAP-017`
- this is a personal free open-source project, so the plan stays function-first and intentionally light on non-functional operations
- the local single-machine runtime through `GAP-034` is baseline, not final completion
- the target product is a generic, portable, interactive governed runtime with repo-local light packs and machine-wide runtime state
- internal runtime boundaries remain service-shaped even though the default delivery shape is attach-first rather than service-first
- Codex compatibility remains the first direct adapter priority, but final product completeness cannot be Codex-only
- non-goals remain non-goals: no enterprise org model, no marketplace, no default multi-agent orchestration, no memory-first product identity
- governance-optimization lane `GAP-061` through `GAP-068` was the follow-on queue after `GAP-060` and is now complete on the current branch baseline (verified on 2026-04-20), while older lifecycle `GAP` entries remain completion history
- post-closeout optimization queue `GAP-069` through `GAP-074` is complete on the current branch baseline (verified on 2026-04-20) and does not reopen hybrid final-state closure
- optimized best-state near-term gap horizon queue `NTP-01..10` is complete on the current branch baseline (`GAP-080` through `GAP-084`, verified on 2026-04-21; `GAP-085` through `GAP-089`, verified on 2026-04-22)
- long-term gap trigger audit queue `GAP-090` through `GAP-092` is complete; all `LTP-01..05` packages remain deferred pending future trigger evidence
  - optimized hybrid long-term implementation queue `GAP-093` through `GAP-103` is complete on the current branch baseline; `LTP-01..06` remain trigger-based until fresh scope-fence evidence exists

## Current Baseline
- PRD, architecture, ADRs, specs, runtime contract primitives, repo verifier entrypoints, sample repo profiles, and a runtime-consumable control pack already exist.
- The MVP governance-kernel backlog is complete through `GAP-017`.
- `Vision / GAP-018` and `GAP-019` are complete through lifecycle planning alignment and capability freeze.
- `Foundation / GAP-020` through `GAP-023` are now complete on the current branch baseline.
- `Full Runtime / GAP-024` through `GAP-028` are now complete on the current branch baseline.
- `Public Usable Release / GAP-029` through `GAP-032` are now complete on the current branch baseline.
- `Maintenance Baseline / GAP-033` through `GAP-034` are now complete on the current branch baseline.
- `Strategy Alignment Gates / GAP-040` through `GAP-044` are now complete on the current branch baseline.
- `Interactive Session Productization / GAP-035` through `GAP-039` are complete on the current branch baseline.
- `Direct-To-Hybrid-Final-State Mainline / GAP-045` is complete on the current branch baseline as the planning rebaseline closeout.
- `Direct-To-Hybrid-Final-State Mainline / GAP-046` through `GAP-060` are complete on the current branch baseline (verified on 2026-04-20).
- `Governance Optimization Lane / GAP-061` through `GAP-068` are complete on the current branch baseline (verified on 2026-04-20).
- `Post-Closeout Optimization Queue / GAP-069` through `GAP-074` is complete on the current branch baseline (verified on 2026-04-20).
- `Near-Term Gap Horizon Queue / GAP-080` through `GAP-089` are complete on the current branch baseline (`GAP-080` through `GAP-084` verified on 2026-04-21; `GAP-085` through `GAP-089` verified on 2026-04-22).
- `Long-Term Gap Trigger Audit Queue / GAP-090` through `GAP-092` is complete; all `LTP-01..05` packages remain deferred pending future trigger evidence.
- `Optimized Hybrid Long-Term Implementation Queue / GAP-093` through `GAP-103` is complete on the current branch baseline; no `LTP-01..06` implementation package was selected.
- `Complete Hybrid Final-State Realization Queue / GAP-104` through `GAP-111` is the active post-`GAP-103` implementation queue. It is the first queue that can legitimately turn the optimized target into complete final-state closure if every acceptance criterion is implemented and verified.

## Direct-To-Hybrid-Final-State Mainline

The entries below record the executed queue for complete hybrid final-state and governance-optimization closure, plus the post-closeout optimization queue and completed near-term gap horizon queue. The historical lifecycle backlog remains below as completion history and dependency context.

### Phase 0: Canonical Re-Baseline

### GAP-045 Phase 0 Planning Sync And Mainline Backlog Alignment
- Type: AFK
- Blocked by: GAP-039, GAP-044
- User stories: 1, 23, 29, 31
- Status: complete on current branch baseline as the direct-to-final-state planning closeout
- What to build:
  - align backlog, issue seeds, and seeding script to the direct-to-final-state roadmap and implementation plan
  - keep historical lifecycle GAP entries as completion history while promoting `Phase 0` through `Phase 5` as the active queue
  - record planning-sync evidence and validation outputs
- Acceptance criteria:
  - [x] backlog groups active work by `Phase 0` through `Phase 5`
  - [x] issue seeds render the new mainline without colliding with historical GAP ids
  - [x] plans index, backlog, issue seeds, and seeding script agree on the active future-facing queue

### Phase 1: Governed Execution Surface

### GAP-046 Remaining Session Bridge Execution Gaps Closure
- Type: AFK
- Blocked by: GAP-045
- User stories: 1, 5, 41, 43
- Status: complete on current branch baseline (verified on 2026-04-20)
- What to build:
  - preserve the existing session bridge command surface while promoting quick/full gate paths from plan-only output to runtime-managed execution
  - unify gate, write, approval, evidence, and handoff paths on one stable execution or continuation identity model
  - keep explicit degrade behavior when live-host-backed execution is unavailable
- Acceptance criteria:
  - [x] session bridge commands cover the runtime-owned execution surface needed by attached repos without regressing the already-landed write/evidence/handoff paths
  - [x] execution-like results carry stable execution and continuation identifiers rather than plan-only output
  - [x] unsupported capabilities still degrade explicitly instead of implying execution

### GAP-047 Live-Session-Bound Attached Write Chain
- Type: HITL
- Blocked by: GAP-046
- User stories: 8, 10, 27, 43
- Status: complete on current branch baseline (verified on 2026-04-20)
- What to build:
  - keep the already-landed bridge-backed attached write flow as the canonical path
  - bind task id, adapter or session identity, approval ref, artifact refs, handoff ref, and replay ref for each real attached write
  - make CLI write paths wrappers around the same runtime-owned live-session-bound flow instead of parallel logic
- Acceptance criteria:
  - [x] one write request can be initiated, escalated, approved, resumed, and executed through the runtime-owned session surface with live session identity preserved
  - [x] high-risk writes fail closed when approval state is absent or stale
  - [x] attached write evidence stays on one task model from request through replay

### GAP-048 Governed Shell, Git, And Package Execution Coverage
- Type: AFK
- Blocked by: GAP-047
- User stories: 8, 10, 17, 31
- Status: complete on current branch baseline (verified on 2026-04-20)
- What to build:
  - extend governed execution beyond file writes to shell, git, and selected package-manager actions
  - keep allow, escalate, and deny semantics on one evidence and rollback model
  - start with bounded happy-path and fail-closed allowlist coverage rather than broad command support
- Acceptance criteria:
  - [x] shell, git, and at least one package-manager dry-run path use the same governance model as file writes
  - [x] allow, escalate, and deny paths emit consistent evidence and rollback metadata
  - [x] the execution surface remains explicitly bounded and does not silently broaden

### GAP-049 Attached-Repo End-To-End Governed Loop
- Type: HITL
- Blocked by: GAP-048
- User stories: 14, 38, 42, 46
- Status: complete on current branch baseline (verified on 2026-04-20)
- What to build:
  - prove one attached repo can complete `attach -> request write -> approve -> execute -> verify -> handoff -> replay`
  - keep the output on the same runtime-owned task model as local runtime work
  - record exact command sequence and resulting refs as evidence
- Acceptance criteria:
  - [x] one attached repo can complete the governed medium-risk loop end to end
  - [x] the end-to-end output distinguishes real execution from smoke or fallback paths
  - [x] evidence shows the exact attached-repo command chain and refs

### Phase 2: Live Host Adapter Reality

### GAP-050 Live Codex Handshake And Continuation Identity
- Type: HITL
- Blocked by: GAP-049
- User stories: 2, 11, 31, 41, 43
- Status: complete on current branch baseline (verified on 2026-04-20)
- What to build:
  - move the direct Codex adapter from declared posture to a real handshake or probe path
  - preserve session id, resume id, and continuation identity in the runtime task model
  - keep live attach, process bridge, and manual handoff explicitly distinguishable
- Acceptance criteria:
  - [x] the adapter can probe or handshake with a real Codex surface instead of relying only on manual flags
  - [x] live session and continuation identity are preserved in the runtime-owned task model
  - [x] unavailable live attach remains explicit posture rather than implied support

### GAP-051 Real Adapter Event Ingestion And Evidence Export
- Type: AFK
- Blocked by: GAP-050
- User stories: 13, 14, 15, 31, 43
- Status: complete on current branch baseline (verified on 2026-04-20)
- What to build:
  - ingest real tool, diff, gate, approval, and handoff events from the adapter path
  - export richer evidence into the runtime-owned task, evidence, and delivery model
  - keep manual-handoff and live-ingestion evidence distinguishable
- Acceptance criteria:
  - [x] tool calls, diffs, gate runs, and approval interruptions can be linked back to one runtime-owned task
  - [x] unsupported or partial events are recorded explicitly rather than dropped
  - [x] delivery handoff and replay readers can consume the richer evidence shape

### GAP-052 Executable Adapter Registry And Multi-Host Selection
- Type: AFK
- Blocked by: GAP-051
- User stories: 20, 31, 37, 44
- Status: complete on current branch baseline (verified on 2026-04-20)
- What to build:
  - turn adapter selection, discovery, probing, and delegation into executable runtime behavior
  - support `native_attach`, `process_bridge`, and `manual_handoff` tiers through one registry interface
  - keep Codex first without making the runtime Codex-only
- Acceptance criteria:
  - [x] adapter selection is a runtime decision based on repo and host capability, not only static projection
  - [x] Codex and at least one non-Codex fixture share the same registry interface
  - [x] degrade behavior is part of the runtime interface rather than documentation only

### Phase 3: Real Multi-Repo And Machine-Local Sidecar Reality

### GAP-053 Attached Multi-Repo Trial Runner
- Type: HITL
- Blocked by: GAP-052
- User stories: 14, 37, 38, 39, 45
- Status: complete on current branch baseline (verified on 2026-04-20)
- What to build:
  - convert the multi-repo runner from profile summary into an attached-repo execution loop
  - run attach, doctor or status, gate request, attachment verification, optional write probe, and evidence aggregation per repo
  - capture differentiated onboarding friction and follow-up actions from real repo runs
- Acceptance criteria:
  - [x] the trial runner can accept attached repo roots or bindings instead of only repo profile paths
  - [x] at least two attached external repos can run without kernel rewrites
  - [x] trial outputs capture real gate failures, approval friction, replay quality, and follow-up items

### GAP-054 Machine-Local Runtime Roots And Migration
- Type: AFK
- Blocked by: GAP-053
- User stories: 1, 17, 29, 38
- Status: complete on current branch baseline (verified on 2026-04-20)
- What to build:
  - normalize task, artifact, replay, and workspace placement around one machine-local runtime-root model
  - keep repo-root `.runtime/` as compatibility mode rather than primary posture
  - document and test migration plus rollback behavior
- Acceptance criteria:
  - [x] machine-local runtime roots become the default posture for self-runtime and attached-runtime flows
  - [x] repo-root defaults remain available only as compatibility mode
  - [x] migration and rollback behavior are documented and testable

### Phase 4: Service-Shaped Runtime Extraction

### GAP-055 Service-Shaped Control And Session API Boundary
- Type: AFK
- Blocked by: GAP-054
- User stories: 1, 11, 13, 14, 17, 39
- Status: complete on current branch baseline (verified on 2026-04-20)
- What to build:
  - extract a service-shaped API boundary for session operations and operator reads
  - make CLI entrypoints wrappers or clients rather than the only control surface
  - introduce tracing hooks at the new boundary without breaking contract parity
- Acceptance criteria:
  - [x] session operations and operator reads are exposed through a service API boundary
  - [x] CLI and API paths preserve contract parity
  - [x] observability hooks exist at the new runtime boundary

### GAP-056 Service-Shaped Persistence And Local Deployment Scaffold
- Type: AFK
- Blocked by: GAP-055
- User stories: 1, 5, 24, 29, 30, 39
- Status: complete on current branch baseline (verified on 2026-04-20)
- What to build:
  - add local service deployment scaffolding for control-plane and worker boundaries
  - move durable metadata and artifact handling behind stable persistence abstractions
  - introduce transition-stack dependencies only where the service boundary requires them
- Acceptance criteria:
  - [x] local service deployment can run the extracted runtime stack with durable metadata storage
  - [x] filesystem artifact handling remains supported through an abstraction layer
  - [x] the existing contract bundle and evidence model stay consumable after the persistence split

### Phase 5: Hardening And Closeout

### GAP-057 Attachment-Scoped Operator Query Surfaces
- Type: AFK
- Blocked by: GAP-056
- User stories: 14, 27, 34, 40
- Status: complete on current branch baseline (verified on 2026-04-20)
- What to build:
  - add attachment-scoped queries for approvals, evidence, handoff, replay, and posture
  - stop degrading `inspect_evidence` for the primary attached path
  - keep operator surfaces read-only unless explicit escalation is required elsewhere
- Acceptance criteria:
  - [x] attachment-scoped queries can list approvals, evidence refs, handoff refs, replay refs, and posture summary
  - [x] `inspect_evidence` works on the primary attached path without default degradation
  - [x] operator read surfaces remain stable enough for later console reuse

### GAP-058 Runtime Reader And CI Same-Contract Parity
- Type: AFK
- Blocked by: GAP-057
- User stories: 11, 12, 22, 36, 44
- Status: complete on current branch baseline (verified on 2026-04-20)
- What to build:
  - extend same-contract parity beyond verifier boundaries to runtime readers, adapters, and attachment consumers
  - add CI coverage for session bridge, runtime status, adapter, and attachment reader paths
  - fail loudly on incompatible contract shapes instead of silently defaulting
- Acceptance criteria:
  - [x] runtime readers fail loudly on missing or incompatible contract fields
  - [x] CI coverage proves session bridge, adapter, and attachment readers consume the declared contract shape
  - [x] parity is demonstrable beyond verifier-only scope

### GAP-059 Remediation-Capable Attachment Doctor
- Type: AFK
- Blocked by: GAP-058
- User stories: 11, 12, 16, 24, 39
- Status: complete on current branch baseline (verified on 2026-04-20)
- What to build:
  - add guided remediation and fail-closed enforcement for missing, invalid, and stale attachment posture
  - map remediation steps back to exact commands or documents
  - keep remediation evidence-backed and rollback-aware
- Acceptance criteria:
  - [x] missing, invalid, and stale bindings each have an explicit remediation path
  - [x] fail-closed posture is used when execution should not continue
  - [x] remediation actions are evidence-backed and rollback-aware

### GAP-060 Final-State Closeout And Claim Discipline
- Type: HITL
- Blocked by: GAP-059
- User stories: 18, 29, 37, 44, 46
- Status: complete on current branch baseline (verified on 2026-04-20; full final-state claim gated by closeout evidence)
- What to build:
  - sync backlog, roadmap, master outline, issue seeds, and closeout evidence to only verified completed work
  - record final commands, outputs, residual risks, and rollback notes
  - make final-state claims depend on executable proof rather than narrative alone
- Acceptance criteria:
  - [x] roadmap, master outline, backlog, issue seeds, evidence, and gate results agree on what is complete
  - [x] final-state claims are made only when exit criteria are actually met
  - [x] closeout evidence records commands, outputs, residual risks, and rollback paths

## Governance Optimization Lane

### GAP-061 Governance Optimization Lane Canonicalization
- Type: AFK
- Blocked by: GAP-060
- User stories: 21, 23, 29, 31, 40
- Status: complete on current branch baseline (verified on 2026-04-20)
- What to build:
  - canonical roadmap and implementation plan for the governance-optimization lane
  - backlog, issue-seed, and template alignment for `GAP-061` through `GAP-068`
  - dedicated epic-rendering support for the governance lane after `Phase 5`
  - planning evidence that explains the lane boundary and rollback
- Acceptance criteria:
  - [x] the lane has canonical roadmap, implementation plan, backlog, seeds, template, and evidence assets
  - [x] `GAP-045` through `GAP-060` remain the active executable mainline
  - [x] GitHub issue rendering can emit a governance-lane epic without redefining the direct-to-hybrid closure queue
  - [x] future governance optimization work can reference one authoritative planning package

### GAP-062 Trace Grading And Improvement Baseline
- Type: AFK
- Blocked by: GAP-061
- User stories: 13, 15, 22, 39, 44
- Status: complete on current branch baseline (verified on 2026-04-20)
- What to build:
  - stronger trace grading requirements for replay-readiness, policy visibility, and outcome quality
  - explicit postmortem input model for failed runs, reviewer feedback, and repeated failure signatures
  - governance-loop update that places trace grading and improvement proposal generation after evidence persistence
- Acceptance criteria:
  - [x] traces can distinguish missing evidence, poor outcome, policy misses, and replay-readiness gaps
  - [x] failed runs and review feedback can feed structured postmortem inputs
  - [x] the optimization lane has a trace-driven improvement baseline rather than an anecdotal one

### GAP-063 Repo Admission And Compatibility Signal Hardening
- Type: AFK
- Blocked by: GAP-062
- User stories: 11, 12, 38, 44, 46
- Status: complete on current branch baseline (verified on 2026-04-20)
- What to build:
  - stronger repo-admission minimums for compatibility, knowledge readiness, eval readiness, and attachment hygiene
  - clearer compatibility signal boundaries for warning versus blocking conditions
  - explicit preservation of repo-specific stricter overrides without weakening kernel rules
- Acceptance criteria:
  - [x] repo admission can accept, warn, or block attached repos using machine-readable criteria
  - [x] knowledge and eval readiness are explicit signals rather than hidden assumptions
  - [x] repo overrides remain stricter-only and do not weaken kernel guarantees

### GAP-064 Control Rollout Matrix And Waiver Recovery
- Type: AFK
- Blocked by: GAP-063
- User stories: 7, 21, 23, 27, 40
- Status: complete on current branch baseline (verified on 2026-04-20)
- What to build:
  - rollout-state semantics for `observe`, `canary`, `enforce`, and rollback
  - stronger control-lifecycle metadata for review cadence and health
  - waiver recovery rules tied to expiry, recovery plan, and promotion gates
- Acceptance criteria:
  - [x] progressive controls can move from observe to enforce with explicit evidence and rollback posture
  - [x] waivers remain temporary and cannot silently become permanent defaults
  - [x] maintenance and retirement policy stays aligned with rollout and recovery semantics

### GAP-065 Knowledge Registry And Repo-Map Context Shaping
- Type: AFK
- Blocked by: GAP-064
- User stories: 2, 20, 31, 37, 44
- Status: complete on current branch baseline (verified on 2026-04-20)
- What to build:
  - knowledge-source trust, freshness, precedence, and drift rules
  - repo-map context shaping as a governed knowledge input instead of an implicit agent behavior
  - guardrails that keep memory-like sources non-authoritative
- Acceptance criteria:
  - [x] knowledge sources are typed, versioned, and reviewable
  - [x] repo-map context shaping is reusable across repos without leaking into kernel truth semantics
  - [x] memory-like sources remain explicitly non-authoritative

### GAP-066 Provenance And Attestation For Governance Assets
- Type: AFK
- Blocked by: GAP-065
- User stories: 21, 31, 37, 38, 44
- Status: complete on current branch baseline (verified on 2026-04-20)
- What to build:
  - provenance minimums for control packs, schema bundles, and release-adjacent governance artifacts
  - stronger linkage between provenance, verification state, and rollback visibility
  - clear statement that provenance augments rather than replaces evidence and approval records
- Acceptance criteria:
  - [x] governance assets can carry provenance records with stable references
  - [x] provenance status can be used in promotion or review decisions when present
  - [x] provenance does not displace evidence, approval, or rollback records

### GAP-067 Controlled Improvement Proposal Pipeline
- Type: HITL
- Blocked by: GAP-066
- User stories: 13, 14, 15, 39, 45
- Status: complete on current branch baseline (verified on 2026-04-20)
- What to build:
  - structured proposal pipeline fed by traces, postmortems, reviewer feedback, and repeated failures
  - proposal buckets for skills, hooks, policy, controls, knowledge, and repo follow-ups
  - human-review boundary that prevents autonomous kernel mutation
- Acceptance criteria:
  - [x] the runtime can emit structured improvement proposals from evidence-backed inputs
  - [x] proposal outputs are clearly separated from automatic policy or kernel mutations
  - [x] proposal categories preserve the boundary between unified governance and repo-specific follow-up work

### GAP-068 Governance Optimization Lane Closeout And Claim Discipline
- Type: HITL
- Blocked by: GAP-067
- User stories: 18, 21, 29, 37, 44
- Status: complete on current branch baseline (verified on 2026-04-20)
- What to build:
  - final lane closeout criteria, residual risk summary, and deferred-item ledger
  - optimization claim discipline that distinguishes controlled improvement from autonomous self-mutation
  - evidence-backed rollback notes for the lane outputs
- Acceptance criteria:
  - [x] allowed and prohibited optimization claims are explicit
  - [x] deferred non-goals remain visible instead of leaking into closeout language
  - [x] lane closeout references real verification evidence and rollback notes

## Post-Closeout Optimization Queue

### GAP-069 Host-Neutral Governance Boundary Hardening
- Type: AFK
- Blocked by: GAP-068
- User stories: 20, 31, 37, 44, 46
- Status: complete on current branch baseline (verified on 2026-04-20)
- What to build:
  - codify host-neutral governance guarantees so the runtime stays a governance layer rather than a host replacement shell
  - tighten adapter capability boundaries and degrade semantics around `native_attach`, `process_bridge`, and `manual_handoff`
  - add claim-boundary checks so docs and runtime outputs cannot imply universal host takeover
- Acceptance criteria:
  - [x] governance-layer-only positioning is explicit in product docs, contracts, and operator-facing surfaces
  - [x] adapter capability boundaries remain explicit and fail closed when host-level capabilities are missing
  - [x] over-claim statements about replacing upstream AI coding products are blocked by verification hooks

### GAP-070 Default-On Onboarding And Auto-Apply Guardrails
- Type: AFK
- Blocked by: GAP-069
- User stories: 14, 38, 42, 45, 46
- Status: complete on current branch baseline (verified on 2026-04-20)
- What to build:
  - one-command attach-first onboarding with inferred defaults for common repo profiles
  - first-run doctor and trial flows that auto-produce prioritized remediation hints
  - safe default behavior that keeps low-risk actions automatic and high-risk writes escalation-bound
- Acceptance criteria:
  - [x] a new target repo can reach first governed trial without manual policy stitching
  - [x] onboarding outputs include explicit next actions for unresolved readiness gaps
  - [x] high-risk writes remain approval-bound even when onboarding is mostly automatic

### GAP-071 Evidence Replay SLO And Recoverability Hardening
- Type: AFK
- Blocked by: GAP-070
- User stories: 13, 14, 15, 39, 45
- Status: complete on current branch baseline (verified on 2026-04-20)
- What to build:
  - measurable SLO thresholds for evidence completeness, replay fidelity, and handoff readability
  - regression checks that fail when evidence bundles lose required references or replay-critical fields
  - operator-facing recovery playbooks for replay and rollback paths that fail the threshold
- Acceptance criteria:
  - [x] evidence bundles can be graded against explicit SLO thresholds
  - [x] replay can reconstruct representative governed runs from persisted artifacts only
  - [x] verification fails when recoverability signals regress below declared thresholds

### GAP-072 Claim-Drift Sentinel And Continuous Doc-Runtime Sync
- Type: HITL
- Blocked by: GAP-071
- User stories: 18, 21, 29, 37, 44
- Status: complete on current branch baseline (verified on 2026-04-20)
- What to build:
  - claim catalog mapping each externally visible product claim to executable proof commands and evidence links
  - drift sentinel checks that compare docs claims with runtime probe and verification outputs
  - periodic human-reviewed closeout snapshots for residual risk and deferred-claim visibility
- Acceptance criteria:
  - [x] docs and README claim lines are linked to concrete command outputs and evidence files
  - [x] drift sentinel checks fail on stale or over-claimed statements before merge
  - [x] periodic review evidence records remaining risk, deferred claims, and rollback notes

### GAP-073 Dynamic Post-Closeout Evidence Scope And Queue Discovery
- Type: AFK
- Blocked by: GAP-072
- User stories: 13, 15, 21, 39, 44
- Status: complete on current branch baseline (verified on 2026-04-20)
- What to build:
  - remove hard-coded post-closeout gap id lists from docs checks and derive the queue scope from backlog and issue seeds
  - keep evidence SLO checks fail-closed for all completed post-closeout tasks, including newly added IDs
  - preserve the same required verification and rollback anchors in closeout evidence
- Acceptance criteria:
  - [x] docs checks discover post-closeout GAP scope dynamically instead of relying on fixed id ranges
  - [x] completed post-closeout tasks are all subject to the same closeout evidence requirements
  - [x] adding a new post-closeout ID no longer requires immediate verifier code edits just to include it in scope

### GAP-074 Post-Closeout Queue Sync Sentinel And Seed Drift Guard
- Type: AFK
- Blocked by: GAP-073
- User stories: 21, 23, 29, 31, 44
- Status: complete on current branch baseline (verified on 2026-04-20)
- What to build:
  - add a docs sentinel check that detects posture drift between issue seeds and key backlog or roadmap summaries for post-closeout queue completion state
  - keep the sentinel fail-closed when summary docs stop reflecting the current seed-backed queue range
  - sync script label mapping and backlog seed metadata so queue expansion remains renderable
- Acceptance criteria:
  - [x] docs checks fail when post-closeout queue summary lines drift away from the current seed-backed id range
  - [x] post-closeout queue expansion remains renderable by issue seeding script without label-mapping gaps
  - [x] backlog and roadmap summaries consistently reflect the same post-closeout queue completion range

## Near-Term Gap Horizon Queue (Optimized Best-State)

### GAP-080 NTP-01 Live Host Closure
- Type: HITL
- Blocked by: GAP-074
- User stories: 2, 11, 13, 14, 43
- Status: complete on current branch baseline (verified on 2026-04-21)
- What to build:
  - prove one real live-session governed loop from handshake through handoff/replay without breaking runtime-owned identity
  - preserve stable session, continuation, and task linkage across request, approval, execution, verification, and replay
  - export runtime-owned evidence snapshots that distinguish real live execution from fallback paths
- Acceptance criteria:
  - [x] one live attached path preserves session identity and continuation across request, approval, execute, verify, handoff, and replay
  - [x] runtime evidence can link all live-loop events back to one governed task with stable refs
  - [x] fallback or manual paths remain explicit and cannot be mistaken for live closure

### GAP-081 NTP-02 Non-Codex Conformance
- Type: AFK
- Blocked by: GAP-080
- User stories: 20, 31, 37, 44, 46
- Status: complete on current branch baseline (verified on 2026-04-21)
- What to build:
  - build shared adapter conformance checks that apply to Codex and at least one non-Codex adapter
  - make non-Codex guarantee levels auditable through the same gate and evidence model
  - keep adapter registry output comparable across hosts without weakening fail-closed semantics
- Acceptance criteria:
  - [x] at least one non-Codex adapter passes the same conformance gate family used by Codex
  - [x] non-Codex trials emit equivalent runtime evidence linkage fields
  - [x] parity matrix clearly records supported, degraded, and blocked capabilities per host

### GAP-082 NTP-03 Service-Primary Convergence
- Type: AFK
- Blocked by: GAP-081
- User stories: 1, 11, 13, 17, 39
- Status: complete on current branch baseline (runtime service-primary convergence acceptance closed on 2026-04-21 with wrapper dispatch tests and drift guards)
- What to build:
  - enforce API-first runtime boundaries and keep CLI as a wrapper-only compatibility surface
  - add API/CLI parity guards for execution-like commands and operator reads
  - detect and block contract drift between service paths and wrapper paths
- Acceptance criteria:
  - [x] API and CLI execution-like commands remain parity-checked in CI
  - [x] CLI behavior is implemented through service boundaries rather than parallel runtime logic
  - [x] parity drift fails verification before merge

### GAP-083 NTP-04 Operator Remediation Depth
- Type: AFK
- Blocked by: GAP-082
- User stories: 11, 12, 14, 27, 40
- Status: complete on current branch baseline (operator remediation-depth acceptance closed on 2026-04-21 with write-status query parity, deterministic doctor actions, and remediation evidence persistence)
- What to build:
  - expand attachment-scoped query coverage for approvals, evidence, replay, and posture diagnostics
  - deepen doctor remediation flows with deterministic recovery actions and retry guidance
  - capture remediation outcomes as evidence-backed artifacts for follow-up decisions
- Acceptance criteria:
  - [x] operator queries can diagnose and track posture or recovery state without raw-log reconstruction
  - [x] doctor outputs include deterministic remediation actions for missing, stale, and invalid posture states
  - [x] remediation retries produce auditable evidence suitable for handoff and replay

### GAP-084 NTP-05 Claim Drift Guard
- Type: HITL
- Blocked by: GAP-083
- User stories: 18, 21, 29, 31, 44
- Status: complete on current branch baseline (claim drift, evidence freshness, and claim exception path checks are all enforced by docs CI on 2026-04-21)
- What to build:
  - enforce claim-to-evidence alignment for roadmap, plan, backlog, and closeout language in CI
  - add freshness checks so final-state claims automatically downgrade when evidence stales
  - keep human review checkpoints for claim exceptions, waiver expiry, and rollback readiness
- Acceptance criteria:
  - [x] CI fails when completion or capability claims outrun executable evidence
  - [x] stale closeout evidence is detected and flagged before release-facing claim updates
  - [x] claim exception paths remain time-bounded, reviewable, and rollback-linked

### GAP-085 NTP-06 Deny-Loop Compression
- Type: AFK
- Blocked by: GAP-084
- User stories: 11, 14, 27, 39, 45
- Status: complete on current branch baseline (deny-certain preflight interception, deterministic remediation hints, and one-command retry linkage closed on 2026-04-22)
- What to build:
  - add preflight path-scope checks that detect deny-certain write requests before full flow execution
  - emit deterministic remediation actions that point to minimal command or path adjustments
  - add one-command retry path that reuses task identity and links denial-to-retry evidence
- Acceptance criteria:
  - [x] denied write attempts with deterministic path violations are intercepted preflight
  - [x] remediation output includes exact next command and expected writable scope
  - [x] denial and retry records stay linked in one runtime-owned evidence chain

### GAP-086 NTP-07 Incremental Gate And Cache Pipeline
- Type: AFK
- Blocked by: GAP-085
- User stories: 11, 12, 22, 36, 44
- Status: complete on current branch baseline (incremental cache-hit gate reuse with fail-closed uncertainty behavior closed on 2026-04-22)
- What to build:
  - add changed-scope-aware gate planning so quick checks run first and full checks are conditional
  - cache gate artifacts by repo state and gate mode to avoid repeating unchanged expensive checks
  - keep cache invalidation explicit and fail-closed on uncertain state
- Acceptance criteria:
  - [x] `quick/l1` and `full/l3` gate routes are deterministic and evidence-backed
  - [x] unchanged inputs can reuse cache entries without skipping required checks
  - [x] cache uncertainty forces recompute rather than silent pass

### GAP-087 NTP-08 Claude-Code First-Class Adapter Path
- Type: HITL
- Blocked by: GAP-086
- User stories: 2, 20, 31, 37, 44
- Status: complete on current branch baseline (Claude Code adapter parity and conformance-family linkage closed on 2026-04-22)
- What to build:
  - add a first-class non-Codex adapter path for Claude Code under the existing adapter registry and tier model
  - preserve session identity and continuation linkage under the same conformance family used by Codex
  - keep explicit degrade posture when live attach is unavailable
- Acceptance criteria:
  - [x] Claude-Code adapter path passes the same conformance gate family as Codex and generic fallback adapters
  - [x] runtime evidence includes identity, gate, and handoff linkage parity fields
  - [x] unsupported capabilities remain explicit and machine-readable

### GAP-088 NTP-09 Repo-Map Context Precompile
- Type: AFK
- Blocked by: GAP-087
- User stories: 13, 20, 31, 39, 44
- Status: complete on current branch baseline (attachment-time context pack precompile plus status/query visibility closed on 2026-04-22)
- What to build:
  - compile attachment-time repo context packs (repo-map, hot files, dominant commands, failure signatures)
  - expose context packs through runtime status and operator queries for session startup reuse
  - keep context-pack provenance and refresh age visible in evidence
- Acceptance criteria:
  - [x] attached repos can emit a context pack without changing target-repo source-of-truth contracts
  - [x] operator and status surfaces can read context-pack summary fields
  - [x] stale context-pack data is detectable and refreshable

### GAP-089 NTP-10 Runtime Speed KPI Baseline
- Type: AFK
- Blocked by: GAP-088
- User stories: 13, 14, 15, 21, 44
- Status: complete on current branch baseline (speed KPI schema + export snapshots + measured-window claim linkage closed on 2026-04-22)
- What to build:
  - define and persist speed KPI records for onboarding latency, first-pass latency, deny-to-success retries, fallback rate, and medium-risk loop success ratio
  - add lightweight summary export for `target-repo-runs` to track trend windows
  - enforce claim wording to reference measured windows instead of anecdotal speed claims
- Acceptance criteria:
  - [x] KPI payload schema and sample records are versioned and documented
  - [x] summary export can produce latest and rolling-window KPI snapshots
  - [x] speed-related claims are tied to measurable evidence snapshots

## Long-Term Gap Trigger Audit Queue

### GAP-090 Final-State Claim Refresh And Trigger Audit
- Type: AFK
- Blocked by: GAP-089
- User stories: 18, 21, 29, 37, 44
- Status: complete on current branch baseline (verified on 2026-04-26; no LTP implementation started)
- What to build:
  - refresh final-state claim evidence, closeout posture, roadmap, backlog, README, and claim-catalog consistency
  - evaluate `LTP-01..05` trigger signals without starting implementation work
  - record stale-claim downgrades, not-triggered decisions, watch decisions, and triggered decisions with evidence links
- Acceptance criteria:
  - [x] fresh gate output backs any complete final-state claim that remains visible
  - [x] each `LTP-01..05` trigger is classified as `not_triggered`, `watch`, or `triggered`
  - [x] stale or over-broad claims are downgraded before any long-term implementation starts

### GAP-091 Sustained Real-Workload Evidence Window
- Type: HITL
- Blocked by: GAP-090
- User stories: 13, 14, 15, 38, 45
- Status: complete on current branch baseline (verified on 2026-04-26; initial target command drift remediated, final all-target daily green)
- What to build:
  - run an all-target or representative multi-target runtime evidence window through existing `runtime-flow-preset` entrypoints
  - group failures by long-term trigger family: orchestration, policy, data-plane, host-adapter, or operations
  - link target-run summaries, KPI snapshots, command output, and rollback notes
- Acceptance criteria:
  - [x] representative real-workload evidence exists for the current target set or a documented subset
  - [x] runtime failures are separated from target-repo business gate failures
  - [x] no LTP is marked triggered without command evidence and rollback notes

### GAP-092 LTP Start Decision And Scope Fence
- Type: HITL
- Blocked by: GAP-091
- User stories: 20, 21, 23, 31, 44
- Status: complete on current branch baseline (verified on 2026-04-26; all LTP packages deferred)
- What to build:
  - decide whether exactly one long-term package should start or all LTPs remain deferred
  - create a bounded implementation-plan stub only for the selected LTP, if any
  - keep non-selected LTPs visible as deferred with reasons and next review trigger
- Acceptance criteria:
  - [x] exactly one next LTP is selected, or all LTPs remain deferred with explicit reasons
  - [x] any selected LTP has a bounded scope fence, verification floor, rollback path, and evidence owner
  - [x] backlog, seeds, issue rendering, evidence, and README posture agree after the decision

## Optimized Hybrid Long-Term Implementation Queue

### GAP-093 Optimized Hybrid Long-Term Planning Baseline
- Type: AFK
- Blocked by: GAP-092
- User stories: 1, 23, 29, 31
- Status: complete on current branch baseline (validated on 2026-04-27)
- What to build:
  - create the optimized hybrid long-term roadmap and implementation plan
  - add `GAP-093..102` to backlog, issue seeds, plan index, docs index, and evidence
  - extend issue-seeding label mapping for the new queue
  - keep `LTP-01..06` trigger-based rather than starting implementation
- Acceptance criteria:
  - [x] roadmap, implementation plan, backlog, issue seeds, plan index, and docs index agree on `GAP-093..102`
  - [x] issue rendering validates all task bodies without GitHub calls
  - [x] evidence records commands, changed files, residual risks, and rollback

### GAP-094 Execution Containment Contract And Tool Coverage Floor
- Type: AFK
- Blocked by: GAP-093
- User stories: 8, 10, 17, 27, 31
- Status: complete on current branch baseline (contract slice validated on 2026-04-27)
- What to build:
  - inventory governed executable tool families such as file write, shell, git, package manager, browser automation, and MCP or tool bridges where present
  - define shared containment fields for workspace roots, path roots, environment policy, network posture, timeout, approval class, evidence refs, and rollback refs
  - make unclassified executable tool families fail closed or require explicit waiver
- Acceptance criteria:
  - [x] every governed executable tool family has a declared containment profile
  - [x] unclassified executable tools fail closed or require explicit waiver
  - [x] execution evidence records containment metadata and rollback metadata
  - [x] containment contract has schema/spec/test coverage

### GAP-095 Provenance And Light-Pack Release Evidence Floor
- Type: AFK
- Blocked by: GAP-094
- User stories: 18, 21, 31, 37, 38, 44
- Status: complete on current branch baseline (validated on 2026-04-27)
- What to build:
  - define provenance records for generated repo-local light packs, control packs, and release-adjacent artifacts
  - record source ref, generator version, input hash, output hash, target repo binding, and waiver metadata
  - make doctor or verifier output distinguish missing provenance from unsupported provenance
- Acceptance criteria:
  - [x] generated light packs and control packs can carry provenance metadata
  - [x] release-adjacent artifacts have either provenance or an explicit waiver
  - [x] verifier/doctor output distinguishes missing provenance from unsupported provenance
  - [x] documentation explains rollback and regeneration behavior

### GAP-096 Service-Shaped Transition Stack Convergence Gate
- Type: AFK
- Blocked by: GAP-095
- User stories: 1, 11, 13, 17, 39, 44
- Status: complete on current branch baseline (verified on 2026-04-27)
- What to build:
  - define when transition-stack dependencies are allowed for API boundary, typed runtime validation, durable metadata, tracing, and containment
  - keep local single-machine use functional without forcing service infrastructure
  - add drift checks for API/CLI parity and boundary-owned validation
- Acceptance criteria:
  - [x] `FastAPI` is allowed only for active service API boundaries
  - [x] `Pydantic v2` is used at API/runtime validation boundaries, not as duplicate schema truth
  - [x] SQLite/filesystem remain valid for local use while PostgreSQL is scoped to service-shaped metadata pressure
  - [x] tracing hooks exist at runtime/API boundaries without requiring a full observability stack
  - [x] CLI and API paths share the same contract behavior for execution-like commands

### GAP-097 Orchestration And Policy Trigger Review
- Type: HITL
- Blocked by: GAP-096
- User stories: 13, 15, 21, 23, 39, 44
- Status: complete on current branch baseline (verified on 2026-04-27)
- What to build:
  - evaluate `LTP-01 orchestration-depth` and `LTP-02 policy-runtime-separation`
  - use real runtime traces, failure signatures, policy count, waiver count, retry or compensation complexity, and review burden
  - classify each package as `not_triggered`, `watch`, or `triggered`
- Acceptance criteria:
  - [x] orchestration trigger decision is evidence-backed
  - [x] policy trigger decision is evidence-backed
  - [x] no workflow engine or external policy runtime is started without a selected scope fence
  - [x] decision evidence includes rollback and next review trigger

### GAP-098 Data Plane And Operations Trigger Review
- Type: HITL
- Blocked by: GAP-097
- User stories: 13, 14, 15, 21, 39, 45
- Status: complete on current branch baseline (verified on 2026-04-27)
- What to build:
  - evaluate `LTP-03 data-plane-scaling` and `LTP-05 operations-hardening`
  - use event volume, replay retention, artifact size, query latency, evidence recovery, sustained workload, SLO, and failure-remediation signals
  - separate runtime failures from target-repo business failures
- Acceptance criteria:
  - [x] data-plane trigger decision is evidence-backed
  - [x] operations-hardening trigger decision is evidence-backed
  - [x] no event bus, semantic store, or full observability suite is introduced without trigger evidence
  - [x] decision evidence separates runtime failures from target-repo business failures

### GAP-099 Multi-Host And Protocol Trigger Review
- Type: HITL
- Blocked by: GAP-098
- User stories: 2, 20, 31, 37, 44, 46
- Status: complete on current branch baseline (verified on 2026-04-27)
- What to build:
  - evaluate `LTP-04 multi-host-first-class` and protocol boundary depth
  - check Codex and non-Codex conformance parity, adapter evidence, MCP/A2A boundary pressure, and product demand
  - preserve kernel-owned task lifecycle, approval, rollback, and evidence semantics
- Acceptance criteria:
  - [x] multi-host trigger decision is evidence-backed
  - [x] protocol-boundary decision is evidence-backed
  - [x] MCP/A2A are treated as integration protocols, not runtime governance owners
  - [x] selected next steps preserve adapter conformance and fail-closed behavior

### GAP-100 Selected LTP Scope Fence And Architecture ADR
- Type: HITL
- Blocked by: GAP-097, GAP-098, GAP-099
- User stories: 18, 21, 23, 29, 31, 44
- Status: complete on current branch baseline (verified on 2026-04-27; all `LTP-01..06` deferred)
- What to build:
  - select exactly one `LTP-01..06` package for implementation, or defer all packages with evidence
  - create an architecture decision, bounded scope, verification floor, rollback plan, and owner/evidence path for any selected package
  - update backlog and issue seeds for the selected package without widening unrelated packages
- Acceptance criteria:
  - [x] exactly one package is selected, or all packages are deferred with reasons
  - [x] selected package has a bounded vertical slice and explicit non-goals
  - [x] selected package has verification, rollback, compatibility, and evidence requirements
  - [x] non-selected packages remain visible as deferred/watch, not silently dropped

### GAP-101 Selected LTP Implementation Batch 1
- Type: HITL
- Blocked by: GAP-100
- User stories: 8, 10, 13, 14, 15, 31, 44
- Status: complete as deferred-no-implementation on current branch baseline (verified on 2026-04-27)
- What to build:
  - implement the first vertical slice of the package selected by `GAP-100`
  - cover contract, runtime behavior, operator/evidence surface, tests, and rollback
  - keep all other long-term packages out of scope
- Acceptance criteria:
  - [x] implementation touches only the selected package scope
  - [x] contract, runtime, evidence, and operator surfaces agree
  - [x] fallback or rollback behavior is explicit and tested
  - [x] closeout evidence includes commands, outputs, risks, and compatibility notes

### GAP-102 Sustained Optimized Hybrid Release Readiness Closeout
- Type: HITL
- Blocked by: GAP-101
- User stories: 13, 14, 18, 21, 29, 37, 44, 45
- Status: complete on current branch baseline (verified on 2026-04-27)
- What to build:
  - run a sustained evidence window against self-runtime and representative target repos
  - refresh final-state claims, roadmap labels, backlog statuses, issue seeds, and evidence links
  - confirm that containment, provenance, transition-stack boundaries, and any selected LTP implementation remain reproducible
- Acceptance criteria:
  - [x] fresh gates support every visible optimized final-state claim
  - [x] target-repo or representative workload evidence is linked
  - [x] claim catalog, roadmap, implementation plan, backlog, issue seeds, and evidence agree
  - [x] residual risks and next review triggers are explicit

### GAP-103 Fresh All-Target Sustained Workload Window
- Type: HITL
- Blocked by: GAP-102
- User stories: 13, 14, 15, 38, 45
- Status: complete on current branch baseline (verified on 2026-04-27)
- What to build:
  - rerun the all-target daily runtime-flow window after the optimized long-term queue closeout
  - record target count, failure count, timeout posture, governance sync posture, and per-target flow exit codes
  - keep `LTP-01..06` deferred unless the fresh window produces trigger evidence
- Acceptance criteria:
  - [x] all configured target repos run through the daily preset with `failure_count=0`
  - [x] evidence records command, timing, timeout controls, and per-target exit posture
  - [x] final-state wording distinguishes fresh all-target evidence from heavy LTP implementation
  - [x] issue rendering, docs/scripts gates, and repo gates agree after the new queue item

### GAP-104 Full Hybrid Final-State Realization Rebaseline
- Type: AFK
- Blocked by: GAP-103
- User stories: 1, 13, 23, 29, 31, 44
- Status: planned active queue item
- What to build:
  - convert the post-`GAP-103` conclusion into a complete realization baseline that separates `healthy optimized baseline`, `transition implementation`, and `complete final-state closure`
  - freeze the realization acceptance matrix for service boundary, live Codex continuity, non-Codex parity, governed tool coverage, data/provenance release flow, operations recovery, and final claim certification
  - keep `LTP-01..06` trigger-based, but map each package to the first concrete implementation batch that would satisfy its trigger if evidence later justifies it
- Acceptance criteria:
  - [ ] roadmap, implementation plan, backlog, issue seeds, and evidence all list `GAP-104..111` with matching dependencies
  - [ ] final-state wording states that `GAP-093..103` did not implement heavy `LTP` packages
  - [ ] complete closure criteria are objective enough to fail if live-host, adapter, execution, data, recovery, or provenance evidence is missing

### GAP-105 Service-Primary Runtime Boundary Batch 1
- Type: AFK
- Blocked by: GAP-104
- User stories: 1, 11, 13, 17, 39, 44
- Status: planned active queue item
- What to build:
  - make the control/session/operator API boundary the primary execution path for execution-like commands while keeping CLI and PowerShell wrappers as compatibility entrypoints
  - introduce or expand `FastAPI`, `Pydantic v2`, PostgreSQL, and tracing only where the service boundary owns real runtime behavior
  - add parity tests proving CLI, service facade, and API routes share the same contract behavior
- Acceptance criteria:
  - [ ] execution-like CLI paths dispatch through the service/control boundary or fail a drift guard
  - [ ] service metadata persistence has local fallback and PostgreSQL-backed test coverage where enabled
  - [ ] API/CLI parity tests are part of the runtime gate for touched surfaces

### GAP-106 Live Codex Attach Continuity Batch 1
- Type: HITL
- Blocked by: GAP-105
- User stories: 2, 13, 20, 31, 37, 44
- Status: planned active queue item
- What to build:
  - replace posture-only Codex evidence with a live attach or launch handshake that records session identity, continuation identity, event ingestion, task linkage, and handoff linkage
  - make Codex host capability drift visible through adapter conformance evidence and downgrade rules
  - run at least one real target-repo medium-risk loop through the live Codex path
- Acceptance criteria:
  - [ ] live Codex evidence links request, approval, execution, verification, evidence, replay, rollback, and handoff ids
  - [ ] continuity id preservation meets the declared target or downgrades final-state claims
  - [ ] failures classify host limitation, adapter defect, and runtime policy denial separately

### GAP-107 Non-Codex Adapter Parity Batch 1
- Type: HITL
- Blocked by: GAP-106
- User stories: 2, 20, 31, 37, 44, 46
- Status: planned active queue item
- What to build:
  - select one non-Codex adapter path and make it pass the same conformance gate family as the Codex path
  - keep host-specific features behind capability-tiered adapter contracts rather than branching kernel semantics
  - record honest degraded-mode behavior where the host cannot support attach, continuation, or evidence export
- Acceptance criteria:
  - [ ] at least one non-Codex path passes adapter conformance, governed execution, and evidence linkage gates
  - [ ] missing host capabilities are explicit degraded posture, not silent success
  - [ ] no adapter can bypass runtime-owned approval, verification, rollback, or evidence semantics

### GAP-108 Governed Execution Tool Coverage Batch 1
- Type: AFK
- Blocked by: GAP-105
- User stories: 8, 10, 13, 14, 15, 31, 44
- Status: planned active queue item
- What to build:
  - move shell, git, package-manager, browser automation, and MCP/tool-bridge execution onto the same governed containment and evidence surface as file-write execution
  - enforce workspace roots, allowed path roots, environment policy, network posture, timeout, approval class, rollback refs, and evidence refs for every supported executable family
  - fail closed for unsupported executable tool families unless an explicit waiver exists
- Acceptance criteria:
  - [ ] every supported executable family has contract, schema, runtime, and test coverage for containment metadata
  - [ ] unsupported or unclassified executable families fail closed
  - [ ] evidence snapshots include command class, containment profile, approval decision, verification result, and rollback posture

### GAP-109 Data Plane And Provenance Release Batch 1
- Type: AFK
- Blocked by: GAP-105, GAP-108
- User stories: 14, 18, 21, 31, 38, 44
- Status: planned active queue item
- What to build:
  - promote durable task, evidence, artifact, replay, and provenance records from local proof shape into service-shaped persistence boundaries
  - implement release-adjacent provenance for generated light packs, control packs, and packaged runtime artifacts
  - add retention and query checks before considering event bus, semantic store, or object-store promotion
- Acceptance criteria:
  - [ ] data-plane read/write paths have migration, replay, retention, and rollback tests
  - [ ] generated release-adjacent artifacts have provenance or explicit waiver evidence
  - [ ] scale components remain trigger-based unless query, retention, artifact-size, or release-promotion evidence justifies them

### GAP-110 Operations Recovery And Sustained Soak Batch 1
- Type: HITL
- Blocked by: GAP-106, GAP-107, GAP-108, GAP-109
- User stories: 13, 14, 15, 21, 39, 45
- Status: planned active queue item
- What to build:
  - run a sustained workload window across self-runtime and all configured target repos after the service, adapter, execution, and data-plane batches
  - prove doctor/operator remediation for representative posture, policy, dependency, persistence, and adapter failures
  - record SLO-like success, recovery, timeout, and claim-freshness metrics without introducing a full operations stack prematurely
- Acceptance criteria:
  - [ ] sustained workload evidence covers multiple targets and more than one execution class
  - [ ] at least 90% of classified posture failures have guided remediation and retry evidence or explicit waiver
  - [ ] operational failures trigger claim downgrade until recovery evidence is regenerated

### GAP-111 Complete Hybrid Final-State Certification
- Type: HITL
- Blocked by: GAP-110
- User stories: 13, 14, 18, 21, 29, 37, 44, 45
- Status: planned active queue item
- What to build:
  - certify complete hybrid final-state closure only after `GAP-104..110` produce fresh, reproducible evidence
  - reconcile master outline, roadmap, implementation plan, claim catalog, backlog, issue seeds, product docs, and evidence indexes
  - decide whether any `LTP-01..06` package can be marked implemented, partially implemented, deferred, or superseded by transition-stack work
- Acceptance criteria:
  - [ ] every quantified final-state target in the master outline has fresh evidence or an explicit downgrade
  - [ ] live Codex, non-Codex parity, governed execution coverage, data/provenance, and operations recovery all pass their gates
  - [ ] the repository can truthfully claim complete hybrid final-state closure without relying on narrative-only evidence

## Vision

### GAP-018 Final Product Lifecycle Alignment
- Type: AFK
- Blocked by: None
- User stories: 1, 23, 29
- Status: complete in planning baseline
- What to build:
  - align roadmap, backlog, issue seeds, script, and entry docs around a full functional lifecycle
  - freeze the final product shape around a governed runtime target without collapsing it into repo-local scripts only
- Acceptance criteria:
  - [x] active planning docs describe the same lifecycle stages
  - [x] the project is described as a complete governed runtime target, not only as contracts/tooling
  - [x] the active queue was re-based away from MVP closure without re-opening MVP semantics

### GAP-019 Final Product Capability Boundary Freeze
- Type: HITL
- Blocked by: GAP-018
- User stories: 18, 29, 37
- Status: complete in planning baseline
- What to build:
  - freeze the final product capability boundary and explicit non-goals
  - define what counts as final product completeness
- Acceptance criteria:
  - [x] the final capability boundary is explicit and stable
  - [x] non-goals are explicit and remain outside the active queue
  - [x] final product completeness can be judged without ad hoc interpretation

## Foundation

### GAP-020 Clarification, Rollout, Compatibility, And Evidence Maturity
- Type: AFK
- Blocked by: GAP-019
- User stories: 4, 7, 23, 39
- Status: complete in Foundation runtime substrate
- What to build:
  - clarification protocol
  - rollout and promotion policy
  - compatibility signals
  - evidence maturity semantics
- Acceptance criteria:
  - [x] clarification is formal runtime policy rather than conversational convention
  - [x] rollout state supports `observe`, `advisory`, and `enforced`
  - [x] repo and adapter compatibility can be checked mechanically
  - [x] evidence quality can distinguish missing evidence from weak outcomes

### GAP-021 Real Build And Doctor Gates
- Type: AFK
- Blocked by: GAP-020
- User stories: 11, 12, 16, 24
- Status: complete in Foundation runtime substrate
- What to build:
  - real build command
  - real `doctor` or `hotspot_or_health_check` command
  - gate routing that uses live commands instead of `gate_na`
- Acceptance criteria:
  - [x] `build` no longer depends on `gate_na`
  - [x] `hotspot` no longer depends on `gate_na`
  - [x] canonical gate order can execute through live commands

### GAP-022 Durable Task Store And Workflow Skeleton
- Type: AFK
- Blocked by: GAP-020, GAP-021
- User stories: 1, 5, 24, 29, 30, 39
- Status: complete in Foundation runtime substrate
- What to build:
  - durable task persistence skeleton
  - workflow skeleton for pause, resume, timeout, retry, and compensation
- Acceptance criteria:
  - [x] task state survives process boundaries
  - [x] workflow transitions stay deterministic
  - [x] lifecycle data is no longer trapped in in-memory primitives

### GAP-023 Control Registry Lifecycle And Evidence Completeness Checks
- Type: AFK
- Blocked by: GAP-020, GAP-021
- User stories: 13, 21, 27, 33
- Status: complete in Foundation runtime substrate
- What to build:
  - control lifecycle metadata
  - evidence completeness checks
  - recurring review semantics for control health
- Acceptance criteria:
  - [x] controls track lifecycle and review state
  - [x] evidence completeness can fail missing required fields
  - [x] rollback and observability links are explicit per control

## Full Runtime

### GAP-024 Execution Worker And Managed Workspace Runtime
- Type: AFK
- Blocked by: GAP-022, GAP-023
- User stories: 8, 10, 17, 30, 31
- Status: complete in Full Runtime baseline
- What to build:
  - execution worker
  - managed workspace or worktree runtime
  - governed task execution path on real runtime state
- Acceptance criteria:
  - [x] governed tasks can execute through a worker rather than only through contract objects
  - [x] workspaces are lifecycle-bound and policy-aware
  - [x] worker execution preserves approval and rollback semantics

### GAP-025 Artifact Store, Evidence Bundle, And Replay Pipeline
- Type: AFK
- Blocked by: GAP-024
- User stories: 13, 14, 15, 27, 34, 39
- Status: complete in Full Runtime baseline
- What to build:
  - artifact store
  - persisted evidence bundles
  - replay references and failure signatures
- Acceptance criteria:
  - [x] artifacts persist outside stdout or transcript-only output
  - [x] evidence bundles can reference real artifacts and replay cases
  - [x] failed tasks leave enough persisted data for replay-oriented diagnosis

### GAP-026 Operational Quick And Full Gate Runner
- Type: AFK
- Blocked by: GAP-024, GAP-025
- User stories: 11, 12, 22, 36
- Status: complete in Full Runtime baseline
- What to build:
  - operational quick/full gate runner
  - artifact classification for risky outputs such as dependency, CI, and release-adjacent changes
- Acceptance criteria:
  - [x] quick and full gates run against real task executions
  - [x] gate artifacts are persisted and queryable
  - [x] risky files or artifacts are surfaced distinctly in delivery state

### GAP-027 Minimal Operator Surface For Task, Approval, Evidence, And Replay
- Type: AFK
- Blocked by: GAP-025, GAP-026
- User stories: 14, 27, 34, 40
- Status: complete in Full Runtime baseline
- What to build:
  - minimal operator surface
  - task list
  - approval queue
  - evidence and replay views
  - CLI-first operator path backed by stable runtime read models
- Acceptance criteria:
  - [x] operators can inspect tasks, approvals, evidence, and replay without raw log digging
  - [x] the surface remains control-plane focused
  - [x] a failed task can be inspected from the operator surface without reconstructing history manually
  - [x] the first delivery can be CLI-first as long as it preserves a stable read model for a later UI

### GAP-028 Health, Status, And Runtime Query Surface
- Type: AFK
- Blocked by: GAP-024, GAP-025
- User stories: 1, 11, 13, 14, 17, 39
- Status: complete in Full Runtime baseline
- What to build:
  - runtime health/status surface
  - task query surface
  - runtime-level visibility for current and past governed runs
- Acceptance criteria:
  - [x] the runtime exposes health or doctor results through a stable surface
  - [x] task state and query history are inspectable without direct database access
  - [x] operators can tell whether the runtime is healthy enough to accept new tasks

## Public Usable Release

### GAP-029 Single-Machine Deployment And Quickstart
- Type: AFK
- Blocked by: GAP-026, GAP-027, GAP-028
- User stories: 14, 27, 34, 40
- Status: complete in Public Usable Release baseline
- What to build:
  - single-machine deployment path
  - quickstart instructions
  - bootstrapping path for the complete runtime
  - first richer operator UI shell on top of the Full Runtime read model
- Acceptance criteria:
  - [x] the complete runtime can be started on one machine with a documented path
  - [x] quickstart covers task creation, execution, approval, verification, and evidence inspection
  - [x] the setup path does not depend on private maintainer knowledge
  - [x] operator-facing runtime flows are no longer limited to the CLI-first control surface

### GAP-030 Sample Repo Profiles And End-To-End Demo Flow
- Type: AFK
- Blocked by: GAP-029
- User stories: 2, 18, 37, 38
- Status: complete in Public Usable Release baseline
- What to build:
  - sample repo profiles
  - end-to-end demo flow for a real governed coding task
  - sample operator path for second-repo onboarding
- Acceptance criteria:
  - [x] at least one sample repo profile can run the documented quickstart
  - [x] the demo flow exercises the complete runtime path rather than only contracts
  - [x] second-repo onboarding follows profile inputs instead of kernel changes

### GAP-031 Public Usable Release Criteria And Packaging
- Type: AFK
- Blocked by: GAP-029, GAP-030
- User stories: 18, 31, 37, 38
- Status: complete in Public Usable Release baseline
- What to build:
  - public usable release criteria
  - package or distribution layout for the single-machine runtime
  - release-readiness checklist for the full runtime
- Acceptance criteria:
  - [x] public usable release criteria are explicit
  - [x] packaging or distribution layout matches the documented quickstart
  - [x] the release checklist covers the full product capability boundary

### GAP-032 Adapter Baseline And Fallback Or Degrade Behavior
- Type: AFK
- Blocked by: GAP-029, GAP-030
- User stories: 20, 27, 35
- Status: complete in Public Usable Release baseline
- What to build:
  - adapter baseline for the full runtime
  - explicit fallback or degrade behavior when adapter capabilities are weak
  - operator-visible compatibility posture
- Acceptance criteria:
  - [x] Codex-first compatibility remains explicit
  - [x] unsupported adapter capabilities degrade or fail closed explicitly
  - [x] compatibility posture is visible in docs and runtime outputs

## Maintenance

### GAP-033 Compatibility And Upgrade Policy
- Type: AFK
- Blocked by: GAP-031, GAP-032
- User stories: 21, 31, 37, 38
- Status: complete in Maintenance baseline
- What to build:
  - compatibility policy
  - upgrade policy for adapters, repo profiles, and persisted runtime state
- Acceptance criteria:
  - [x] upgrade expectations are explicit
  - [x] compatibility-breaking changes require an explicit note or migration path
  - [x] adapter and repo profile evolution does not silently break the full runtime

### GAP-034 Maintenance, Deprecation, And Retirement Policy
- Type: AFK
- Blocked by: GAP-033
- User stories: 21, 22, 27, 40
- Status: complete in Maintenance baseline
- What to build:
  - maintenance boundary
  - deprecation policy
  - retirement or removal policy for outdated capabilities
- Acceptance criteria:
  - [x] maintenance expectations are documented
  - [x] deprecated capabilities include replacement or migration guidance
  - [x] retired capabilities do not disappear without traceability

## Interactive Session Productization

### GAP-035 Generic Target-Repo Attachment Pack And Onboarding Flow
- Type: AFK
- Blocked by: GAP-032, GAP-034, GAP-042
- User stories: 18, 38, 42, 46
- Status: complete on current branch baseline
- What to build:
  - repo-local declarative light pack
  - target-repo bootstrap and attach flow
  - machine-local runtime binding that keeps mutable state out of the target repo
- Acceptance criteria:
  - [x] a new target repo can be attached without copying the runtime into it
  - [x] repo-local light pack contents are explicit, minimal, and portable
  - [x] target-repo onboarding produces a stable runtime binding and doctor-visible posture

### GAP-036 Attach-First Session Bridge And Governed Interaction Surface
- Type: AFK
- Blocked by: GAP-035, GAP-043
- User stories: 1, 5, 41, 43
- Status: complete on current branch baseline
- What to build:
  - attach-first session bridge
  - governed in-session commands for task start, approval, gate runs, and evidence inspection
  - launch-second fallback when live session attach is unavailable
  - PolicyDecision normalization so execution-like session commands expose `allow` / `escalate` / `deny` instead of raw local-baseline `allowed` / `paused` / fail-closed outcomes
- Acceptance criteria:
  - [x] the preferred user flow runs inside an active AI coding session rather than only through batch CLI
  - [x] governed actions are callable without replacing the upstream AI tool UI
  - [x] launch mode remains available as an explicit compatibility fallback
  - [x] execution-like session commands expose `PolicyDecision` outcomes rather than raw legacy write-governance statuses

### GAP-037 Direct Codex Adapter And Evidence Mapping
- Type: HITL
- Blocked by: GAP-035, GAP-036, GAP-043
- User stories: 2, 11, 31, 41, 43
- Status: complete on current branch baseline
- What to build:
  - direct Codex adapter for interactive governed use
  - session-to-task binding and mutation capture
  - evidence mapping for Codex-driven file changes, tool calls, and gate runs
- Acceptance criteria:
  - [x] at least one real Codex path is direct rather than manual-handoff only
  - [x] runtime evidence can attribute Codex-driven changes and verification output to one governed task
  - [x] unsupported Codex capabilities degrade explicitly instead of being implied silently

### GAP-038 Capability-Tiered Adapter Framework For Multiple AI Tools
- Type: AFK
- Blocked by: GAP-035, GAP-036, GAP-044
- User stories: 20, 31, 37, 44
- Status: complete on current branch baseline
- What to build:
  - capability tiers for native attach, process bridge, and manual handoff
  - adapter registry updates for non-Codex tools
  - explicit governance guarantees per capability tier
- Acceptance criteria:
  - [x] adapters can declare attach strength without changing kernel semantics
  - [x] non-Codex tools have an honest compatibility posture
  - [x] degrade and fail-closed behaviors remain explicit and operator-visible

### GAP-039 Multi-Repo Trial Loop And Generic Onboarding Kit
- Type: HITL
- Blocked by: GAP-035, GAP-036, GAP-037, GAP-038, GAP-044
- User stories: 14, 37, 38, 39, 45
- Status: complete on current branch baseline as the first productization slice; full external attached-repo closure is tracked by `GAP-053`
- What to build:
  - reusable onboarding kit for arbitrary target repos
  - multi-repo trial execution and feedback capture
  - evidence-backed iteration path for onboarding friction, adapter gaps, and gate drift
- Acceptance criteria:
  - [x] profile-based multi-repo trial loops can run without kernel rewrites and preserve per-repo structured evidence outputs
  - [x] onboarding, adapter, and gate failures are captured as structured trial evidence
  - [x] the product can evolve from real trial data instead of repo-specific one-off fixes

## Strategy Alignment Gates

### GAP-040 Runtime Governance Borrowing Matrix
- Type: AFK
- Blocked by: None
- User stories: 29, 31, 37, 44
- Status: complete in Strategy Alignment baseline
- What to build:
  - borrowing matrix for Microsoft Agent Governance Toolkit, OPA, Keycard, Coder AI Governance, MCP, GAAI-style repo files, OpenHands, SWE-agent, Hermes-like agents, oh-my-codex or oh-my-claudecode-style wrappers, NeMo Guardrails, and Guardrails AI
  - product-layer classification for each reference
  - explicit borrow and avoid guidance
- Acceptance criteria:
  - [x] each reference is classified by layer rather than copied as product identity
  - [x] each row includes borrow, avoid, impact, confidence, and official or primary source
  - [x] matrix conclusions preserve the project's runtime/action governance identity

### GAP-041 Source-Of-Truth And Runtime Bundle ADR
- Type: HITL
- Blocked by: GAP-040
- User stories: 18, 21, 29, 38
- Status: complete in Strategy Alignment baseline
- What to build:
  - ADR-0007 for source-of-truth versus runtime contract bundle boundaries
  - decision that `docs/`, `schemas/`, and `packages/contracts/` remain the repository source of truth
  - decision that repo-local light packs or `.governed-ai/`-style bundles are generated or validated runtime-consumable attachment surfaces
- Acceptance criteria:
  - [x] ADR rejects hand-maintaining two competing contract copies
  - [x] ADR links the decision to ADR-0005 and ADR-0006
  - [x] ADR gives GAP-035 a stable boundary for repo-local light packs

### GAP-042 Repo-Native Contract Bundle Architecture
- Type: AFK
- Blocked by: GAP-041
- User stories: 18, 31, 38, 46
- Status: complete in Strategy Alignment baseline
- What to build:
  - architecture document for repo-native contract bundle contents
  - mapping from repo profile, gates, write policy, approval policy, adapter capabilities, PolicyDecision, evidence, handoff, and rollback references to existing source-of-truth docs and schemas
  - state placement rules for repo-local declarations versus machine-local runtime state
- Acceptance criteria:
  - [x] GAP-035 light-pack scope is described as the runtime bundle attachment shape
  - [x] mutable task, run, approval, artifact, and replay state remains machine-local
  - [x] local and CI consumers are described as reading the same contract inputs

### GAP-043 PolicyDecision Contract
- Type: AFK
- Blocked by: GAP-042
- User stories: 7, 8, 20, 27, 31, 43
- Status: complete in Strategy Alignment baseline
- What to build:
  - PolicyDecision spec, JSON Schema, Python contract, and runtime tests
  - `allow`, `escalate`, and `deny` decision statuses
  - decision basis, evidence reference, approval reference, and remediation hint fields
- Acceptance criteria:
  - [x] `allow`, `escalate`, and `deny` are schema-backed and tested
  - [x] `deny` fails closed and does not produce an executable action
  - [x] `escalate` carries approval intent without conflating approval with execution

### GAP-044 Local/CI Same-Contract Verification And Alignment Closeout
- Type: AFK
- Blocked by: GAP-042, GAP-043
- User stories: 11, 12, 22, 36, 44
- Status: complete in Strategy Alignment baseline
- What to build:
  - verification spec update for local and CI same-contract inputs
  - docs/script regression coverage for non-ASCII markdown path collection and ignored worktree docs
  - backlog, issue-seed, and seeding script reconciliation for the strategy alignment gates
- Acceptance criteria:
  - [x] local and CI verification are described as consuming the same repo contract inputs
  - [x] docs verification handles non-ASCII markdown paths and ignored worktree markdown robustly
  - [x] issue seeding renders GAP-040 through GAP-044 without changing GAP-035 through GAP-039 semantics
