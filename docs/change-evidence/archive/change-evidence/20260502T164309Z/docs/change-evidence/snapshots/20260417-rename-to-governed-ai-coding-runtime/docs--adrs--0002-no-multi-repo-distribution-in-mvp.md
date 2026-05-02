# ADR-0002: No Multi-Repo Distribution In MVP

## Status
Accepted

## Date
2026-04-17

## Context
`repo-governance-hub` is a governance mother-repo with source mirroring, distribution, backflow, and shared templates across multiple repositories. `governed-agent-platform` has a different primary goal: provide a governed runtime for AI coding.

## Decision
Do not include multi-repo distribution, backflow, or template sync in the MVP.

The MVP will support:
- one platform kernel
- multiple repo profiles
- governed execution per target repo
- bounded repo-specific overrides

It will not act as a source-of-truth distribution hub.

## Alternatives Considered
### Rebuild repo-governance-hub inside the new platform
- Pros: reuse familiar structure
- Cons: imports the wrong product shape and too much operational complexity
- Rejected: not aligned with the product's first value proposition

### Build distribution support in parallel with runtime
- Pros: future-proofing
- Cons: splits focus, increases surface area, delays core loop validation
- Rejected: violates Phase 1 scope discipline

## Consequences
- easier initial architecture
- cleaner product boundary
- future integration with external governance hubs remains possible through adapters or imported policy packs
