# Current Best-End-State Blueprint

## Purpose
Use this page as the fastest authoritative review sheet when asking:
- does the PRD still describe the right product?
- does the roadmap still point at the right target?
- should a host/protocol/reference-repo change create a new backlog queue, or only a wording refresh?

This document is intentionally short. It summarizes the current target definition, host posture, mechanism intake rules, and planning implications without replacing the deeper PRD, architecture, roadmap, or backlog documents.

## One-Line Definition
`governed-ai-coding-runtime` should be understood as:

`a capability-first, host-family-aware governance runtime for AI coding`

It is not:
- a competing AI coding host
- a wrapper-first orchestration product
- a generation-guardrail product

## Best-End-State Blueprint
The current best engineering end state is:

`Governance Hub + Reusable Contract + Capability-First Host Adapters + Controlled Evolution + Evidence-First Delivery`

### 1. Governance Hub
The runtime kernel owns:
- task semantics
- policy and approval semantics
- verification order
- evidence, rollback, replay, and handoff semantics

These must not silently drift with host product changes.

### 2. Reusable Contract
The stable contract boundary is:
- repo-local declarations or light packs
- machine-local durable runtime state
- same-contract local and CI verification

The kernel should not be copied into every target repo, and host-specific assumptions should not become hidden contract forks.

### 3. Capability-First Host Adapters
Hosts are modeled as families plus capability declarations, not as product-name-specific kernel branches.

Canonical host families:
- `Codex family`
- `Claude family`
- `Antigravity family`
- `Gemini CLI` as a legacy migration bridge

Minimum capability fields:
- `surface_class`
- `attach_mode`
- `tool_visibility`
- `event_stream_visibility`
- `approval_delegateability`
- `sandbox_delegateability`
- `continuation_model`
- `evidence_exportability`
- `execution_locality`

### 4. Controlled Evolution
External change should become:
- a reviewed interpretation
- a structured proposal
- a bounded document or runtime change
- evidence with rollback

It should not become an implicit product drift caused by memory, one-off conversations, or unreviewed community imitation.

### 5. Evidence-First Delivery
Completion claims should expose:
- host family
- adapter tier
- degrade reason
- verification refs
- evidence refs

Historical certification is useful, but it must not override the current live posture.

## Current Host Interpretation

### Codex Family
Interpret Codex as a host family, not a CLI-only tool.

The relevant official surface now spans:
- CLI
- App
- IDE extension
- cloud/web
- app-server
- automations
- worktrees
- browser/computer-use-related surfaces

### Claude Family
Interpret Claude as a host family, not a terminal-only CLI.

The relevant surface now spans:
- terminal
- IDE
- desktop/Cowork
- collaboration and automation surfaces

### Google Direction
Use the strongest currently justified wording:
- `Antigravity family` is the long-term Google direction
- `Gemini CLI` remains a real compatibility and migration bridge
- do not write that Gemini is gone unless stronger official evidence exists

## Current Live Posture Rule
The single source of current posture is:
- `docs/architecture/planning-status.json`

Current practical reading:
- historical certification: `GAP-104..111`
- current active queue: `GAP-159..164`
- current decision gate: `wait_for_host_capability_recovery`
- current live posture: Codex target runs are still `process_bridge / degraded`; latest Claude workload probe is `native_attach / ready`

Implication:
- do not reopen implementation queues just because historical closure exists
- do not claim recovered Codex native attach until fresh evidence says so

## Mechanism Intake Rule
Borrow mechanisms, not product identities.

Take first from:
- official product docs
- first-party repos
- protocol specs and SDKs
- live target-run evidence

Community projects are still valuable, but mainly for:
- sandbox vocabulary
- edit loop ergonomics
- durable execution patterns
- repo-map/context shaping
- self-improvement and memory ideas

They should not redefine the project's identity.

## What Should Trigger Planning Changes

### Usually wording-only refresh
- official host surface broadens, but kernel boundary stays the same
- a reference repo reinforces an already-adopted mechanism
- a host direction becomes clearer, but current compatibility posture remains the same

Claim upgrade requires fresh evidence. A wording-only refresh must not strengthen the current live-host posture when the latest posture is still degraded, missing canonical surface fields, or supported only by historical certification.

### Usually backlog or queue candidate
- a new host family requires a new capability field or adapter invariant
- official docs materially change approval, sandbox, MCP, or continuity assumptions
- current live posture changes what the repo is allowed to claim
- a repeated real-world target-run failure shows the existing contract is insufficient
- a new mechanism source answers a gap the current runtime cannot explain or govern

## Review Checklist
When reviewing future product docs, ask:

1. Does the document describe the project as a governance runtime instead of a competing host?
2. Does it model hosts as families plus capabilities instead of product-name branches?
3. Does it keep `Antigravity` as long-term Google direction and `Gemini CLI` as bridge wording unless newer official evidence changes that?
4. Does it separate historical certification from current live posture?
5. Does it require evidence-backed completion claims rather than wording-only closure?
6. Does it preserve the rule: borrow mechanisms, not identities?

## Companion Docs
- [AI Coding PRD](../prd/governed-ai-coding-runtime-prd.md)
- [Interaction Model](../product/interaction-model.md)
- [Positioning And Competitive Layering](./positioning-and-competitive-layering.md)
- [Host Family Capability Surface Blueprint](../architecture/host-family-capability-surface-blueprint.md)
- [planning-status.json](../architecture/planning-status.json)
- [External Reference Repo One-Page Overview](../research/external-reference-repo-one-page-overview.md)
- [External Reference Repo Tiering](../research/external-reference-repo-tiering.md)
