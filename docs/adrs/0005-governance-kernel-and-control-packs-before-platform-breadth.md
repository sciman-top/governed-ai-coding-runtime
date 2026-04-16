# ADR-0005: Governance Kernel And Control Packs Before Platform Breadth

## Status
Accepted

## Date
2026-04-17

## Context
The repository already has three accepted decisions:
- control-plane-first
- no multi-repo distribution in the MVP
- single-agent baseline first

The latest project assessment confirms that the main product risk is not missing platform breadth. The main risk is turning the repository into a generic agent platform before the governance kernel is executable.

The repository already has the right baseline shape:
- docs-first and contracts-first planning assets
- a governance boundary matrix
- initial schemas for task, risk, tool, evidence, gates, and evals

What is still missing is the contract family that makes multi-repository reuse controlled rather than ad hoc:
- hook contracts
- skill manifests
- knowledge source contracts
- waiver and exception records
- provenance and attestation records
- repo-map and context-shaping rules

## Decision
Evolve `governed-ai-coding-runtime` as a governance kernel for AI coding, not as a general-purpose agent platform.

The first-class architecture concepts are:
- `governance kernel`: task lifecycle, approval semantics, risk taxonomy, tool contract semantics, evidence schema, gate order, eval taxonomy, provenance minimums, and rollback semantics
- `control packs`: reusable, versioned bundles of policy, hooks, skills, gates, evals, and knowledge controls that execute behind kernel contracts
- `repo profiles`: repository-specific commands, path policies, tool defaults, context inputs, stricter local approvals, and repo-specific eval additions

Boundary rules:
- the kernel owns cross-repo semantics and minimum guarantees
- target repositories inherit repo-specific values through profiles
- overrides may only tighten restrictions or add controls
- overrides may not weaken kernel guarantees, bypass approvals, or change canonical gate order

Proof of reuse will be based on one kernel running against multiple compatible repo profiles. It will not be based on source mirroring, template distribution, or backflow sync in the MVP.

The following are explicitly deferred from the platform identity:
- memory-first architecture
- default multi-agent orchestration
- skill marketplace or promotion lifecycle
- broad deployment automation as the product core
- multi-repo distribution hub behavior

## Alternatives Considered
### Expand directly into a broad agent platform
- Pros: larger demo surface and more feature parity with community products
- Cons: weakens governance focus, increases product ambiguity, and delays the smallest auditable loop
- Rejected: breadth before control would undermine the repo's thesis

### Recreate a multi-repo governance distribution hub
- Pros: stronger configuration reuse story
- Cons: conflicts with ADR-0002 and imports a different product identity
- Rejected: distribution is not the MVP value proposition

### Make memory and self-improvement a first-class runtime plane now
- Pros: attractive long-term differentiation
- Cons: low immediate ROI, higher audit ambiguity, and weaker determinism during core-loop validation
- Rejected: memory remains optional and cannot become the system fact source

## Consequences
- The roadmap and backlog must prioritize missing governance contracts before broad runtime implementation.
- Sample repo profiles, sample control packs, and compatibility validation become MVP-critical, not optional nice-to-haves.
- Runtime bootstrap work should happen around the governance kernel, not ahead of it.
- Future features such as subagents, memory, or broader automation must plug into the kernel contracts instead of redefining them.
